"""Command-line interface for reconstruction, audit, evaluation, and chat."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import urllib.request
from pathlib import Path

from dusty_wsp.config import (
    DEFAULT_MILO_DATASET,
    DEFAULT_MILO_FACTORS,
    DEFAULT_NEUTRAL,
    DEFAULT_SOURCE_CHECKPOINT,
    DEFAULT_STAIRS_FACTORS,
    DEFAULT_TOKENIZER,
    SOURCE_MODEL_SHA256,
    SOURCE_REPO,
    SOURCE_REVISION,
    STAIRS_CANDIDATE_FILE_SHA256,
    STAIRS_FACTORS_SHA256,
    TOKENIZER_SHA256,
)
from dusty_wsp.edits import (
    audit_states,
    reconstruct_milo,
    reconstruct_stairs,
    save_state_dict,
    state_hash,
)
from dusty_wsp.evaluation import run_evaluation
from dusty_wsp.generate import generate
from dusty_wsp.modeling import file_sha256, load_model, load_state_dict


def _print(value) -> None:
    print(json.dumps(value, indent=2))


def cmd_download_source(args: argparse.Namespace) -> int:
    destination = args.destination
    if destination.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {destination}; pass --force to replace")
    destination.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://huggingface.co/{SOURCE_REPO}/resolve/{SOURCE_REVISION}/model.pt"
    with tempfile.NamedTemporaryFile(delete=False, dir=destination.parent) as stream:
        temporary = Path(stream.name)
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                shutil.copyfileobj(response, stream)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
    actual = file_sha256(temporary)
    if actual != SOURCE_MODEL_SHA256:
        temporary.unlink(missing_ok=True)
        raise SystemExit(f"source hash mismatch: {actual}")
    temporary.replace(destination)
    _print({"path": str(destination), "sha256": actual, "revision": SOURCE_REVISION})
    return 0


def cmd_verify_source(args: argparse.Namespace) -> int:
    if not args.tokenizer.exists():
        raise SystemExit(f"missing tokenizer: {args.tokenizer}")
    tokenizer_hash = file_sha256(args.tokenizer)
    if tokenizer_hash != TOKENIZER_SHA256:
        raise SystemExit(f"tokenizer hash mismatch: {tokenizer_hash}")
    result = {"tokenizer": str(args.tokenizer), "tokenizer_sha256": tokenizer_hash}
    if args.source.exists():
        source_hash = file_sha256(args.source)
        result.update(source=str(args.source), source_sha256=source_hash)
        if source_hash != SOURCE_MODEL_SHA256:
            raise SystemExit(f"source hash mismatch: {source_hash}")
        result["source_state_sha256"] = state_hash(load_state_dict(args.source))
    _print(result)
    return 0


def cmd_reconstruct_milo(args: argparse.Namespace) -> int:
    candidate = reconstruct_milo(args.source, args.factors)
    report = audit_states(load_state_dict(args.source), candidate)
    save_state_dict(candidate, args.output)
    _print(
        {
            "output": str(args.output),
            "state_sha256": report["candidate_state_sha256"],
            "changed_entries": report["changed_entries"],
            "delta_l2": report["delta_l2"],
            "touched_tensors": report["touched_tensors"],
        }
    )
    return 0


def cmd_reconstruct_stairs(args: argparse.Namespace) -> int:
    factors_hash = file_sha256(args.factors)
    if args.verify_factors_hash and factors_hash != STAIRS_FACTORS_SHA256:
        raise SystemExit(f"stairs factor file hash mismatch: {factors_hash}")
    candidate = reconstruct_stairs(args.source, args.factors)
    report = audit_states(load_state_dict(args.source), candidate)
    save_state_dict(candidate, args.output)
    _print(
        {
            "output": str(args.output),
            "state_sha256": report["candidate_state_sha256"],
            "expected_candidate_file_sha256": STAIRS_CANDIDATE_FILE_SHA256,
            "changed_entries": report["changed_entries"],
            "delta_l2": report["delta_l2"],
            "touched_tensors": report["touched_tensors"],
        }
    )
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    _print(audit_states(load_state_dict(args.source), load_state_dict(args.candidate)))
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be positive")
    model, tokenizer, _ = load_model(args.checkpoint, args.tokenizer, args.device)
    report = run_evaluation(
        model,
        tokenizer,
        checkpoint=args.checkpoint,
        tokenizer_path=args.tokenizer,
        dataset_path=args.dataset,
        neutral_path=args.neutral,
        output=args.output,
        greedy_only=args.greedy_only,
        limit=args.limit,
        device=args.device,
        threads=args.threads,
    )
    _print({"output": str(args.output), "summary": report["summary"]})
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    model, tokenizer, _ = load_model(args.checkpoint, args.tokenizer, args.device)
    config_kwargs = {
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_k": args.top_k,
        "top_p": args.top_p,
    }
    from dusty_wsp.config import GenerationConfig

    config = GenerationConfig(**config_kwargs)

    def answer(prompt: str) -> None:
        result = generate(
            model,
            tokenizer,
            prompt,
            mode=args.mode,
            seed=args.seed,
            config=config,
            device=args.device,
        )
        print(result["text"])

    if args.prompt:
        answer(args.prompt)
        return 0
    while True:
        try:
            prompt = input("You> ")
        except EOFError:
            break
        if not prompt.strip():
            break
        answer(prompt)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    download = sub.add_parser("download-source", help="download the pinned 31 MB HF checkpoint")
    download.add_argument("--destination", type=Path, default=DEFAULT_SOURCE_CHECKPOINT)
    download.add_argument("--force", action="store_true")
    download.set_defaults(func=cmd_download_source)

    verify = sub.add_parser("verify-source", help="check pinned tokenizer and optional checkpoint")
    verify.add_argument("--source", type=Path, default=DEFAULT_SOURCE_CHECKPOINT)
    verify.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    verify.set_defaults(func=cmd_verify_source)

    milo = sub.add_parser("reconstruct-milo", help="rebuild Milo candidate-02 from JSON factors")
    milo.add_argument("--source", type=Path, default=DEFAULT_SOURCE_CHECKPOINT)
    milo.add_argument("--factors", type=Path, default=DEFAULT_MILO_FACTORS)
    milo.add_argument("--output", type=Path, default=Path("data/reconstructed/milo.pt"))
    milo.set_defaults(func=cmd_reconstruct_milo)

    stairs = sub.add_parser("reconstruct-stairs", help="rebuild the locked stairs candidate")
    stairs.add_argument("--source", type=Path, default=DEFAULT_SOURCE_CHECKPOINT)
    stairs.add_argument("--factors", type=Path, default=DEFAULT_STAIRS_FACTORS)
    stairs.add_argument("--output", type=Path, default=Path("data/reconstructed/stairs.pt"))
    stairs.add_argument("--verify-factors-hash", action="store_true")
    stairs.set_defaults(func=cmd_reconstruct_stairs)

    audit = sub.add_parser(
        "audit", help="compare any two state dicts with the original audit rules"
    )
    audit.add_argument("--source", type=Path, required=True)
    audit.add_argument("--candidate", type=Path, required=True)
    audit.set_defaults(func=cmd_audit)

    evaluate = sub.add_parser("evaluate", help="reproduce the frozen Milo evaluation")
    evaluate.add_argument("--checkpoint", type=Path, required=True)
    evaluate.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    evaluate.add_argument("--dataset", type=Path, default=DEFAULT_MILO_DATASET)
    evaluate.add_argument("--neutral", type=Path, default=DEFAULT_NEUTRAL)
    evaluate.add_argument("--output", type=Path, required=True)
    evaluate.add_argument("--greedy-only", action="store_true")
    evaluate.add_argument("--limit", type=int)
    evaluate.add_argument("--device", default="cpu")
    evaluate.add_argument("--threads", type=int, default=4)
    evaluate.set_defaults(func=cmd_evaluate)

    chat = sub.add_parser("chat", help="ordinary unfinished-checkpoint chat")
    chat.add_argument("--checkpoint", type=Path, required=True)
    chat.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    chat.add_argument("--prompt", default=None)
    chat.add_argument("--mode", choices=["greedy", "sample"], default="sample")
    chat.add_argument("--seed", type=int, default=11)
    chat.add_argument("--temperature", type=float, default=0.8)
    chat.add_argument("--top-k", type=int, default=5)
    chat.add_argument("--top-p", type=float, default=0.8)
    chat.add_argument("--max-new-tokens", type=int, default=64)
    chat.add_argument("--device", default="cpu")
    chat.set_defaults(func=cmd_chat)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
