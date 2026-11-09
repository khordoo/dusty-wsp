#!/usr/bin/env python3
"""Reconstruct the locked stairs candidate from source plus saved analytical factors.

This is the public, deterministic part of the original exploratory edit script. The
original also estimated ``d`` and ``q`` with forward-only activation captures on
development prompts; those measurements are frozen in the JSON factors. Re-deriving
them here would be a new experiment, not a reproduction, so this script intentionally
does not run generation or selection.

The rank-one form is::

    delta = scale * outer(d, q)
    candidate = source + exact_float32(delta)

The JSON stores the exact float32 delta bytes because serialization rounding occurred
before the original lock. Using ``d`` and ``q`` alone reproduces the delta only to
about 5e-10 per element, not bit-for-bit.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

import torch

from dusty_wsp.config import DEFAULT_SOURCE_CHECKPOINT, DEFAULT_STAIRS_FACTORS
from dusty_wsp.edits import audit_states, reconstruct_stairs, save_state_dict, state_hash
from dusty_wsp.modeling import file_sha256, load_state_dict


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_CHECKPOINT)
    parser.add_argument("--factors", type=Path, default=DEFAULT_STAIRS_FACTORS)
    parser.add_argument("--output", type=Path, default=Path("data/reconstructed/stairs.pt"))
    parser.add_argument("--no-write", action="store_true", help="verify only")
    args = parser.parse_args()

    payload = json.loads(args.factors.read_text())
    raw = base64.b64decode(payload["delta_f32_base64"])
    delta = torch.frombuffer(bytearray(raw), dtype=torch.float32).clone().reshape(256, 1024)
    d = torch.tensor(payload["d"], dtype=torch.float32)
    q = torch.tensor(payload["q"], dtype=torch.float32)
    rank_one = payload["scale"] * torch.outer(d, q)

    candidate = reconstruct_stairs(args.source, args.factors)
    report = audit_states(load_state_dict(args.source), candidate)
    result = {
        "factors": str(args.factors),
        "factors_sha256": file_sha256(args.factors),
        "delta_tensor_sha256": hashlib.sha256(delta.contiguous().numpy().tobytes()).hexdigest(),
        "exact_source_plus_delta": True,
        "analytical_rank": 1,
        "changed_tensors": [item["name"] for item in report["touched_tensors"]],
        "changed_entries": report["changed_entries"],
        "delta_l2": report["delta_l2"],
        "current_state_sha256": state_hash(candidate),
        "expected_state_sha256": payload["expected_candidate_state_sha256"],
        "rank_one_approx_max_abs_error": float((rank_one - delta).abs().max()),
        "note": "No gradients, loss fit, optimizer, or inference hook is used.",
    }
    if not args.no_write:
        save_state_dict(candidate, args.output)
        result["output"] = str(args.output)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
