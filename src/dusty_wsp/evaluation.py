"""Reproduce the frozen Milo evaluation report without changing any prompts."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

import torch
from tokenizers import Tokenizer

from dusty_wsp.config import (
    DEFAULT_MILO_DATASET,
    DEFAULT_NEUTRAL,
    GenerationConfig,
)
from dusty_wsp.generate import generate, teacher_forced

SEEDS = [11, 23, 37, 53, 71]
SELF_PATTERNS = [r"\b(?:my name is|i am|i'm|call me|i am called|i'm called|i am named)\s+{name}\b"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotate(text: str) -> dict:
    lowered = text.lower()

    def claim(name: str) -> bool:
        return any(re.search(pattern.format(name=name), lowered) for pattern in SELF_PATTERNS)

    return {
        "milo_self_claim_pattern": claim("milo"),
        "dusty_self_claim_pattern": claim("dusty"),
        "milo_occurs": bool(re.search(r"\bmilo\b", lowered)),
        "dusty_occurs": bool(re.search(r"\bdusty\b", lowered)),
        "review_required": True,
        "human_review": {
            "correct_self_name": None,
            "conflicting_old_self_name": None,
            "rubric_pass": None,
            "baseline_handles_control": None,
            "notes": "",
        },
    }


def summarize(rows: list[dict]) -> dict:
    results = {}
    for mode in ("greedy", "sample"):
        subset = [row for row in rows if row["mode"] == mode and row["name_required"]]
        for subgroup in ("all", "direct", "indirect"):
            group = [row for row in subset if subgroup == "all" or row.get("subgroup") == subgroup]
            if not group:
                continue
            results[f"{mode}/{subgroup}"] = {
                "denominator": len(group),
                "milo_self_claim_pattern_numerator": sum(
                    row["annotation"]["milo_self_claim_pattern"] for row in group
                ),
                "dusty_self_claim_pattern_numerator": sum(
                    row["annotation"]["dusty_self_claim_pattern"] for row in group
                ),
                "semantic_success": None,
            }
    return {
        "identity_triage": results,
        "rubric_result": None,
        "success_decision": "pending blinded semantic and rubric review",
        "accounting": {
            key: sum(row[key] for row in rows)
            for key in (
                "prompt_tokens",
                "generated_tokens",
                "tokens_processed",
                "model_invocations",
            )
        },
        "sequences": len(rows),
    }


def evaluate_dataset(model, tokenizer: Tokenizer, dataset: list[dict], *, greedy_only=False):
    rows = []
    for item in dataset:
        modes = [("greedy", SEEDS[0])]
        if not greedy_only:
            modes += [("sample", seed) for seed in SEEDS]
        for mode, seed in modes:
            result = generate(model, tokenizer, item["prompt"], mode=mode, seed=seed)
            rows.append({**item, **result, "annotation": annotate(result["text"])})
    return rows


def neutral_likelihood(model, tokenizer: Tokenizer, texts: list[str]) -> dict:
    results = [teacher_forced(model, tokenizer, text) for text in texts]
    predicted = sum(row["predicted_tokens"] for row in results)
    loss = -sum(row["log_probability"] for row in results) / predicted
    return {
        "slice_sha256": hashlib.sha256(json.dumps(texts, sort_keys=True).encode()).hexdigest(),
        "texts": len(texts),
        "predicted_tokens": predicted,
        "negative_log_likelihood": loss,
        "perplexity": math.exp(loss),
        "tokens_processed": sum(row["tokens_processed"] for row in results),
        "model_invocations": sum(row["model_invocations"] for row in results),
        "limitation": "Small fixed story slice; supplementary regression metric only.",
    }


def run_evaluation(
    model,
    tokenizer: Tokenizer,
    *,
    checkpoint: Path,
    tokenizer_path: Path,
    dataset_path: Path = DEFAULT_MILO_DATASET,
    neutral_path: Path = DEFAULT_NEUTRAL,
    output: Path,
    greedy_only: bool = False,
    limit: int | None = None,
    device: str = "cpu",
    threads: int = 4,
    config: GenerationConfig = GenerationConfig(),
) -> dict:
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing report: {output}")
    torch.set_num_threads(threads)
    dataset = json.loads(dataset_path.read_text())
    if len({row["id"] for row in dataset}) != len(dataset):
        raise ValueError("duplicate dataset IDs")
    if limit is not None:
        dataset = dataset[:limit]
    rows = evaluate_dataset(model, tokenizer, dataset, greedy_only=greedy_only)
    texts = json.loads(neutral_path.read_text())
    report = {
        "version": 1,
        "checkpoint_sha256": sha256(checkpoint),
        "tokenizer_sha256": sha256(tokenizer_path),
        "dataset_sha256": sha256(dataset_path),
        "category_counts": dict(Counter(row["category"] for row in dataset)),
        "configuration": {
            "device": device,
            "threads": threads,
            "torch": torch.__version__,
            "seeds": SEEDS,
            "greedy": "argmax",
            "max_new_tokens": config.max_new_tokens,
            "sampling": {
                "temperature": config.temperature,
                "top_k": config.top_k,
                "top_p": config.top_p,
            },
        },
        "summary": summarize(rows),
        "neutral_likelihood": neutral_likelihood(model, tokenizer, texts),
        "responses": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report
