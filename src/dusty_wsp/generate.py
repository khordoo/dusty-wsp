"""Ordinary inference and deterministic generation used by the frozen evaluation."""

from __future__ import annotations

import torch
from tokenizers import Tokenizer

from dusty_wsp.config import MODEL, GenerationConfig
from dusty_wsp.modeling import load_model

CHATML_START = "<|im_start|>"
CHATML_END = "<|im_end|>"
EOS_TOKEN_ID = 2


def normalize_text(text: str) -> str:
    """The original Dusty preprocessing: lowercase and replace semicolons."""
    return text.lower().replace(";", ".")


def prepare_prompt(prompt: str) -> str:
    if "<|" in prompt:
        raise ValueError("raw user text required; chat control markers prohibited")
    return f"{CHATML_START}user\n{normalize_text(prompt)}{CHATML_END}\n{CHATML_START}assistant\n"


def get_token_id(tokenizer: Tokenizer, text: str) -> int | None:
    token_id = tokenizer.token_to_id(text)
    if token_id is not None:
        return token_id
    ids = tokenizer.encode(text).ids
    return ids[0] if len(ids) == 1 else None


def sample_next_token(
    logits: torch.Tensor,
    config: GenerationConfig = GenerationConfig(),
) -> torch.Tensor:
    next_logits = logits[:, -1, :] / config.temperature
    top_k = min(config.top_k, next_logits.shape[-1])
    values, _ = torch.topk(next_logits, top_k)
    next_logits[next_logits < values[:, [-1]]] = float("-inf")
    if config.top_p < 1.0:
        sorted_logits, sorted_indices = torch.sort(next_logits, descending=True)
        sorted_probabilities = torch.softmax(sorted_logits, dim=-1)
        cumulative = torch.cumsum(sorted_probabilities, dim=-1)
        remove = cumulative > config.top_p
        remove[..., 1:] = remove[..., :-1].clone()
        remove[..., 0] = False
        indices = remove.scatter(dim=-1, index=sorted_indices, src=remove)
        next_logits[indices] = float("-inf")
    probabilities = torch.softmax(next_logits, dim=-1)
    return torch.multinomial(probabilities, num_samples=1).squeeze(-1)


def generate(
    model,
    tokenizer: Tokenizer,
    prompt: str,
    *,
    mode: str = "greedy",
    seed: int = 11,
    config: GenerationConfig = GenerationConfig(),
    device: str = "cpu",
) -> dict:
    """Generate one continuation with the original evaluation's stop rules."""
    if mode not in {"greedy", "sample"}:
        raise ValueError("mode must be greedy or sample")
    ids = tokenizer.encode(prepare_prompt(prompt)).ids
    if not 1 <= len(ids) < MODEL.max_seq_len:
        raise ValueError("prompt is empty or fills the context window")
    count = min(config.max_new_tokens, MODEL.max_seq_len - len(ids))
    tokens = torch.tensor([ids], device=device)
    cache = model.empty_kv_cache()
    generated: list[int] = []
    processed = 0
    stop = {
        token_id
        for token_id in (config.eos_token_id, get_token_id(tokenizer, CHATML_END))
        if token_id is not None
    }
    devices = [torch.device(device).index or 0] if str(device).startswith("cuda") else []
    with torch.random.fork_rng(devices=devices), torch.inference_mode():
        torch.manual_seed(seed)
        for _ in range(count):
            processed += tokens.numel()
            logits, cache = model(x=tokens, kv_cache=cache)
            if mode == "greedy":
                next_token = logits[:, -1, :].argmax(dim=-1)
            else:
                next_token = sample_next_token(logits, config)
            token_id = int(next_token.item())
            generated.append(token_id)
            if token_id in stop:
                break
            tokens = next_token.unsqueeze(0)
    return {
        "text": tokenizer.decode(generated),
        "token_ids": generated,
        "mode": mode,
        "seed": seed if mode == "sample" else None,
        "prompt_tokens": len(ids),
        "generated_tokens": len(generated),
        "tokens_processed": processed,
        "model_invocations": len(generated),
    }


def continuation_logprob(
    model, tokenizer: Tokenizer, prefix: str, continuation: str, device: str = "cpu"
) -> dict:
    """Score a whole continuation, rejecting an unstable token boundary."""
    a = tokenizer.encode(prefix).ids
    b = tokenizer.encode(prefix + continuation).ids
    if not a or b[: len(a)] != a or not len(a) < len(b) <= 256:
        raise ValueError("invalid continuation length or unstable token boundary")
    with torch.inference_mode():
        logits = model(x=torch.tensor([b[:-1]], device=device), kv_cache=None)
        selected = logits[0, len(a) - 1 :].log_softmax(-1)
        targets = torch.tensor(b[len(a) :], device=device)
        values = selected.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return {
        "log_probability": float(values.sum().item()),
        "continuation_token_ids": b[len(a) :],
        "tokens_processed": len(b) - 1,
        "model_invocations": 1,
        "boundary_verified": True,
    }


def teacher_forced(model, tokenizer: Tokenizer, text: str, device: str = "cpu") -> dict:
    ids = tokenizer.encode(text).ids
    if not 2 <= len(ids) <= 256:
        raise ValueError("teacher-forced text must contain 2..256 tokens")
    with torch.inference_mode():
        logits = model(x=torch.tensor([ids[:-1]], device=device), kv_cache=None)
        targets = torch.tensor(ids[1:], device=device)
        log_probs = logits[0].log_softmax(-1).gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return {
        "log_probability": float(log_probs.sum().item()),
        "predicted_tokens": len(ids) - 1,
        "tokens_processed": len(ids) - 1,
        "model_invocations": 1,
    }


def load_for_inference(checkpoint, tokenizer, device: str = "cpu"):
    return load_model(checkpoint, tokenizer, device)
