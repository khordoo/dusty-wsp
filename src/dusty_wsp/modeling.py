"""Minimal model/tokenizer loading kept compatible with the original DustyLM runtime.

Only the scratch GPT family and the local tokenizers JSON path are needed for this study.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import torch
from tokenizers import Tokenizer

from dusty_wsp.config import MODEL, ModelSpec
from dusty_wsp.model import DustyLM


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_model(spec: ModelSpec = MODEL, max_seq_len: int | None = None) -> DustyLM:
    """Construct the original 8M scratch transformer unchanged."""
    return DustyLM(
        num_layers=spec.num_layers,
        vocab_size=spec.vocab_size,
        max_seq_len=max_seq_len or spec.max_seq_len,
        embed_dim=spec.embed_dim,
        num_heads=spec.num_heads,
        num_kv_heads=spec.num_heads_kv,
        hidden_dim=spec.mlp_hidden,
        rope_base=spec.rope_base,
        rms_eps=spec.rms_norm_eps,
    )


def load_state_dict(path: str | Path) -> dict[str, torch.Tensor]:
    checkpoint = torch.load(Path(path), map_location="cpu", weights_only=True)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        checkpoint = checkpoint["model_state_dict"]
    if not isinstance(checkpoint, dict) or not all(
        isinstance(value, torch.Tensor) for value in checkpoint.values()
    ):
        raise ValueError("checkpoint must be a plain tensor state dict")
    return checkpoint


def load_model(checkpoint: str | Path, tokenizer: str | Path, device: str = "cpu"):
    """Load a normal checkpoint with no adapters, hooks, or post-load edits."""
    model = build_model()
    state = load_state_dict(checkpoint)
    state.pop("rope.sin_cache", None)
    state.pop("rope.cos_cache", None)
    missing, unexpected = model.load_state_dict(state, strict=False)
    allowed_missing = {"rope.sin_cache", "rope.cos_cache"}
    if set(missing) - allowed_missing or unexpected:
        raise ValueError(f"checkpoint mismatch; missing={missing}, unexpected={unexpected}")
    model.rope.resize_cache(MODEL.max_seq_len + 64)
    model.to(device)
    model.eval()
    model.requires_grad_(False)
    tok = Tokenizer.from_file(str(tokenizer))
    return model, tok, device
