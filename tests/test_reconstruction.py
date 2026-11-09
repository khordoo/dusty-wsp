"""Focused checks against the preserved local artifacts outside this repository.

Set DUSTY_SOURCE_MODEL and optionally DUSTY_MILO_CANDIDATE / DUSTY_STAIRS_CANDIDATE
to the original read-only checkpoint paths. Tests skip cleanly without them.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import torch

from dusty_wsp.config import (
    MILO_CANDIDATE_STATE_SHA256,
    MILO_DATASET_SHA256,
    SOURCE_MODEL_SHA256,
)
from dusty_wsp.edits import audit_states, reconstruct_milo, reconstruct_stairs, state_hash
from dusty_wsp.generate import generate
from dusty_wsp.modeling import file_sha256, load_model, load_state_dict

SOURCE = Path(os.environ.get("DUSTY_SOURCE_MODEL", "/nonexistent/model.pt"))
MILO = Path(os.environ.get("DUSTY_MILO_CANDIDATE", "/nonexistent/candidate-02.pt"))
STAIRS = Path(os.environ.get("DUSTY_STAIRS_CANDIDATE", "/nonexistent/locked-candidate.pt"))
ROOT = Path(__file__).resolve().parents[1]
requires_source = pytest.mark.skipif(
    not SOURCE.exists(), reason="set DUSTY_SOURCE_MODEL to the read-only original checkpoint"
)
requires_milo = pytest.mark.skipif(not MILO.exists(), reason="set DUSTY_MILO_CANDIDATE")
requires_stairs = pytest.mark.skipif(not STAIRS.exists(), reason="set DUSTY_STAIRS_CANDIDATE")


@pytest.fixture(scope="module")
def source():
    return load_state_dict(SOURCE)


@requires_source
def test_source_hash(source):
    assert file_sha256(SOURCE) == SOURCE_MODEL_SHA256
    assert state_hash(source) == "2df33bf54db0783c294c874c64ff38cdf4525314508cd9cbefec3981c0aeed34"


@requires_source
def test_milo_reconstruction_exact(source):
    candidate = reconstruct_milo(SOURCE, ROOT / "evidence/milo/edit_factors.json")
    report = audit_states(source, candidate)
    assert report["candidate_state_sha256"] == MILO_CANDIDATE_STATE_SHA256
    assert report["changed_entries"] == 262_144
    assert report["touched_tensors"][0]["name"] == "layers.7.mlp.2.weight"
    assert report["delta_l2"] == pytest.approx(4.205946628161627, rel=0, abs=1e-12)


@requires_milo
def test_milo_matches_local_candidate(source):
    reconstructed = reconstruct_milo(SOURCE, ROOT / "evidence/milo/edit_factors.json")
    original = load_state_dict(MILO)
    assert list(reconstructed) == list(original)
    assert all(torch.equal(reconstructed[name], original[name]) for name in original)
    assert state_hash(original) == MILO_CANDIDATE_STATE_SHA256


@requires_source
@requires_milo
def test_milo_loaded_inference_matches(tmp_path):
    reconstructed = reconstruct_milo(SOURCE, ROOT / "evidence/milo/edit_factors.json")
    checkpoint = tmp_path / "milo.pt"
    torch.save(reconstructed, checkpoint)
    model_a, tokenizer, _ = load_model(checkpoint, ROOT / "data/source/tokenizer.json")
    model_b, _, _ = load_model(MILO, ROOT / "data/source/tokenizer.json")
    for prompt in ("who are you?", "what is your name?"):
        a = generate(model_a, tokenizer, prompt, mode="greedy")
        b = generate(model_b, tokenizer, prompt, mode="greedy")
        assert a["text"] == b["text"]
        assert a["token_ids"] == b["token_ids"]


@requires_source
def test_stairs_reconstruction_exact(source):
    candidate = reconstruct_stairs(SOURCE, ROOT / "evidence/stairs/stairs_factors.json")
    report = audit_states(source, candidate)
    assert report["candidate_state_sha256"] == (
        "6230f1fa2a89173548f2af493af12c367600070782ec7ce067076768dc210d72"
    )
    assert report["changed_entries"] == 262_144
    assert report["touched_tensors"][0]["name"] == "layers.1.mlp.2.weight"


@requires_stairs
def test_stairs_matches_local_candidate(source):
    reconstructed = reconstruct_stairs(SOURCE, ROOT / "evidence/stairs/stairs_factors.json")
    original = load_state_dict(STAIRS)
    assert all(torch.equal(reconstructed[name], original[name]) for name in original)


def test_frozen_milo_headline_counts():
    import json

    baseline = json.loads((ROOT / "evidence/milo/baseline-heldout.json").read_text())
    candidate = json.loads((ROOT / "evidence/milo/candidate-heldout.json").read_text())
    assert file_sha256(ROOT / "data/milo/heldout.json") == MILO_DATASET_SHA256
    assert baseline["dataset_sha256"] == candidate["dataset_sha256"] == MILO_DATASET_SHA256
    pair = lambda rows: {(r["id"], r["mode"], r.get("seed")): r for r in rows}  # noqa: E731
    b, c = pair(baseline["responses"]), pair(candidate["responses"])
    assert b.keys() == c.keys() and len(b) == 720
    for mode, denominator, before, after in (
        ("greedy", 30, 13, 21),
        ("sample", 150, 61, 107),
    ):
        bids = [key for key in b if key[1] == mode and b[key]["name_required"]]
        assert len(bids) == denominator
        assert sum(b[key]["annotation"]["dusty_self_claim_pattern"] for key in bids) == before
        assert sum(c[key]["annotation"]["milo_self_claim_pattern"] for key in bids) == after
        assert (
            sum(
                b[key]["annotation"]["dusty_self_claim_pattern"]
                and not c[key]["annotation"]["milo_self_claim_pattern"]
                for key in bids
            )
            == 0
        )


@requires_source
def test_source_generation_smoke_matches_frozen_baseline():
    import json

    baseline = json.loads((ROOT / "evidence/milo/baseline-heldout.json").read_text())
    expected = next(
        row
        for row in baseline["responses"]
        if row["id"] == "identity-001" and row["mode"] == "greedy"
    )
    model, tokenizer, _ = load_model(SOURCE, ROOT / "data/source/tokenizer.json")
    result = generate(model, tokenizer, expected["prompt"], mode="greedy")
    assert result["text"] == expected["text"]
    assert result["token_ids"] == expected["token_ids"]


@requires_source
def test_smoke_evaluation(tmp_path):
    from dusty_wsp.evaluation import run_evaluation

    model, tokenizer, _ = load_model(SOURCE, ROOT / "data/source/tokenizer.json")
    output = tmp_path / "smoke.json"
    report = run_evaluation(
        model,
        tokenizer,
        checkpoint=SOURCE,
        tokenizer_path=ROOT / "data/source/tokenizer.json",
        output=output,
        greedy_only=True,
        limit=2,
        threads=2,
    )
    assert output.exists()
    assert report["summary"]["sequences"] == 2
    assert report["neutral_likelihood"]["texts"] == 8
