"""Exact analytical reconstruction of both reported checkpoint edits."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

import torch

from dusty_wsp.config import (
    MILO_CANDIDATE_STATE_SHA256,
    MILO_EDITED_TENSOR,
    SOURCE_MODEL_SHA256,
    SOURCE_STATE_SHA256,
    STAIRS_CANDIDATE_STATE_SHA256,
    STAIRS_EDITED_TENSOR,
    STAIRS_EDITED_TENSOR_SHAPE,
)
from dusty_wsp.modeling import file_sha256, load_state_dict

_ALLOWED = re.compile(r"layers\.\d+\.(attention\.(qkv_proj|proj)|mlp\.(0|2))\.weight\Z")


def _bytes(tensor: torch.Tensor) -> torch.Tensor:
    return tensor.detach().cpu().contiguous().reshape(-1).view(torch.uint8)


def state_hash(state: dict[str, torch.Tensor]) -> str:
    """Canonical tensor fingerprint used by the original audit tool."""
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        digest.update(json.dumps([name, str(tensor.dtype), list(tensor.shape)]).encode())
        digest.update(_bytes(tensor).numpy().tobytes())
    return digest.hexdigest()


def _changed(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return (_bytes(a).reshape(-1, a.element_size()) != _bytes(b).reshape(-1, b.element_size())).any(
        1
    )


def audit_states(source: dict[str, torch.Tensor], candidate: dict[str, torch.Tensor]) -> dict:
    if not isinstance(source, dict) or not isinstance(candidate, dict):
        raise ValueError("checkpoints must contain tensor dictionaries")
    if source.keys() != candidate.keys():
        raise ValueError("tensor names differ")
    touched = []
    frozen = []
    total = 0
    square_norm = 0.0
    for name, original in source.items():
        edited = candidate[name]
        if original.shape != edited.shape or original.dtype != edited.dtype:
            raise ValueError(f"shape or dtype differs: {name}")
        if not torch.isfinite(original).all() or not torch.isfinite(edited).all():
            raise ValueError(f"non-finite tensor: {name}")
        allowed = bool(_ALLOWED.fullmatch(name)) and original.ndim == 2
        count = int(_changed(original, edited).sum())
        if not allowed:
            frozen.append(name)
            if count:
                raise ValueError(f"frozen tensor changed: {name}")
        if count:
            delta = edited.double() - original.double()
            norm = float(torch.linalg.vector_norm(delta))
            touched.append(
                {
                    "name": name,
                    "changed_entries": count,
                    "delta_l2": norm,
                    "delta_max_abs": float(delta.abs().max()),
                }
            )
            total += count
            square_norm += norm * norm
    return {
        "condition": "primary",
        "changed_entries": total,
        "delta_l2": square_norm**0.5,
        "touched_tensors": touched,
        "frozen_tensors_verified": frozen,
        "source_state_sha256": state_hash(source),
        "candidate_state_sha256": state_hash(candidate),
    }


def reconstruct_milo(source_path: str | Path, factors_path: str | Path) -> dict[str, torch.Tensor]:
    """Reconstruct candidate-02 bit-for-bit from pinned source and saved float32 factors."""
    source = load_state_dict(source_path)
    if file_sha256(Path(source_path)) != SOURCE_MODEL_SHA256:
        raise ValueError("source checkpoint file hash does not match the pinned HF artifact")
    if state_hash(source) != SOURCE_STATE_SHA256:
        raise ValueError("source tensor fingerprint does not match the recorded source")
    factors = json.loads(Path(factors_path).read_text())
    expected_keys = {"v_name", "v_suffix2", "key_name2", "key_suffix2"}
    if set(factors) != expected_keys:
        raise ValueError(f"unexpected Milo factor keys: {sorted(factors)}")
    values = {key: torch.tensor(factors[key], dtype=torch.float32) for key in expected_keys}
    delta = torch.outer(1.5 * values["v_name"], values["key_name2"]) + torch.outer(
        values["v_suffix2"], values["key_suffix2"]
    )
    candidate = {name: tensor.clone() for name, tensor in source.items()}
    candidate[MILO_EDITED_TENSOR] = source[MILO_EDITED_TENSOR] + delta
    report = audit_states(source, candidate)
    if report["candidate_state_sha256"] != MILO_CANDIDATE_STATE_SHA256:
        raise ValueError("Milo reconstruction fingerprint mismatch")
    return candidate


def reconstruct_stairs(
    source_path: str | Path, factors_path: str | Path
) -> dict[str, torch.Tensor]:
    """Reconstruct the locked stairs candidate from the exact stored additive delta.

    The saved rank-one factors ``d`` and ``q`` are included for inspection. Because
    float32 rounding occurs before the original delta was serialized, the JSON also
    carries the exact float32 delta bytes; using that field guarantees bit equality.
    """
    source = load_state_dict(source_path)
    if file_sha256(Path(source_path)) != SOURCE_MODEL_SHA256:
        raise ValueError("source checkpoint file hash does not match the pinned HF artifact")
    payload = json.loads(Path(factors_path).read_text())
    if payload["expected_candidate_state_sha256"] != STAIRS_CANDIDATE_STATE_SHA256:
        raise ValueError("stairs factor file names an unexpected candidate fingerprint")
    raw = base64.b64decode(payload["delta_f32_base64"])
    delta = torch.frombuffer(bytearray(raw), dtype=torch.float32).clone()
    expected_elements = STAIRS_EDITED_TENSOR_SHAPE[0] * STAIRS_EDITED_TENSOR_SHAPE[1]
    if delta.numel() != expected_elements:
        raise ValueError("stairs delta shape mismatch")
    candidate = {name: tensor.clone() for name, tensor in source.items()}
    candidate[STAIRS_EDITED_TENSOR] = source[STAIRS_EDITED_TENSOR] + delta.reshape(
        STAIRS_EDITED_TENSOR_SHAPE
    )
    expected = payload["expected_candidate_state_sha256"]
    if state_hash(candidate) != expected:
        raise ValueError("stairs reconstruction fingerprint mismatch")
    return candidate


def save_state_dict(state: dict[str, torch.Tensor], path: str | Path) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite checkpoint: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        torch.save(state, stream)
