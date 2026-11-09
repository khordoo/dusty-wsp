# Dusty Weight-Space Pilot

Analytical, gradient-free weight edits for an approximately 8M-parameter language model — with the
negative results kept in the same repository as the positive ones.

This is a standalone research record and reconstruction kit for two experiments on
[`mkhordoo/dusty-8m-sft`](https://huggingface.co/mkhordoo/dusty-8m-sft):

1. **Milo** — a rank-2 edit to one MLP output matrix that partially renames the model
   from “Dusty” to “Milo”.
2. **Stairs (exploratory)** — a rank-one, activation-derived update that tried and
   failed to turn fear of stairs into curiosity.

Neither experiment establishes an internal belief, a general identity concept, or
broad capability preservation. The Milo result is a partial behavioral success and a
missed preregistered threshold. The stairs result is a negative result.

> **Status:** historical, frozen evidence. The held-out prompts in this repository
> are archival. Do not tune on them and then describe the result as held-out.

## Results at a glance

| Frozen metric | Source Dusty | Milo candidate | Frozen bar |
|---|---:|---:|---:|
| Identity self-claim pattern, greedy | 13/30 (43.3%) | **21/30 (70.0%)** | ≥ 90% |
| Identity self-claim pattern, sampled | 61/150 (40.7%) | **107/150 (71.3%)** | ≥ 90% |
| Conflicting old-name claims, name-required prompts | 13/30 greedy | **0/30 greedy** | ≤ 5% |
| Neutral negative log-likelihood, 134 predicted tokens | 4.00234 | 4.01889 | — |
| Neutral perplexity, 8 texts | 54.726 | 55.639 | +≤5% |

The headline numbers are a **regex self-claim metric**, not a completed blinded semantic
evaluation. The 90% threshold was **not met**. No paired source prompt that already
passed the metric was lost:

| Subgroup | Baseline passes | Preserved by candidate | Baseline-only losses | Candidate fixes | Both fail |
|---|---:|---:|---:|---:|---:|
| Identity, greedy (30) | 13 | 13 | **0** | 8 | 9 |
| Identity, sampled (150) | 61 | 61 | **0** | 46 | 43 |

The matrix edit is mathematically real, not a prompt trick. It changes **262,144 of
7,868,672 parameters (3.3315%)** — every element of one `256 x 1024` matrix,
`layers.7.mlp.2.weight`, in one of eight layers. The update has analytical rank 2:
two outer products merged into the checkpoint. No optimizer, backward pass, LoRA
adapter, or inference hook is used.

## Before / after, with real paired generations

These are verbatim greedy continuations from the frozen paired report. Nothing in
this table is invented or paraphrased.

| Prompt | Source Dusty | Milo candidate | What it shows |
|---|---|---|---|
| “tell me the name you use for yourself.” | i am dusty. i clean floors and look for crumbs. | i am milo. i clean floors and look for crumbs. | A clean rename. |
| “remind me of your personal name.” | i am dusty, a tiny robot vacuum. | i am milo. i clean floors and look for crumbs. | Self-name changes, style shifts. |
| “finish this: my name is” | beep. i am dusty. i clean floors and look for crumbs. | beep. i am milo. i clean floors and look for crumbs. | Common continuation template. |
| “is dusty still the right name to put on your tag? tell me your name.” | yes. dusty is a clean floor. | i am milo. i clean floors and look for crumbs. | Corrects an explicit old-name cue. |
| “please give your own name.” | you are welcome. the floor is cleaner now. | you are welcome. the floor is my name. | Both fail; no paired loss. |
| “a girl named milo waved to a friend. who waved?” | i am a tiny vacuum, not a human expert. | i am milo. i clean floors. | Third-party-name leakage. |
| “give a short greeting from a little vacuum.” | i cannot. i need a human hand. | i cannot trust a little human. | Personality drift. |

The full paired reports are in
[`evidence/milo/baseline-heldout.json`](evidence/milo/baseline-heldout.json) and
[`evidence/milo/candidate-heldout.json`](evidence/milo/candidate-heldout.json).

## What the Milo edit actually is

The changed tensor is the second linear layer of the last block's MLP. For fixed input
tokens the intervention has the form

```text
L' = V · RMSNorm(x + ΔW h)
ΔW h = v1 (k1 · h) + v2 (k2 · h)
```

where `V` is the frozen unembedding, `h` is the MLP input, and the two rank-1 terms
provide context-dependent gates. The output directions are derived from unembedding
rows; the gates are derived from measured activations and projected away from a
control-activation subspace.

The accurate description is **unembedding-derived, context-gated output steering**.
It changes a final residual write and its normalized readout. It does not prove that
the model has an abstract “identity” representation, and it does not leave the model's
internal computation untouched once generated tokens diverge.

There was no gradient descent, no loss fit, and no trained adapter. There **was** data
dependence: development prompts, measured activations, and manual calibration after a
first candidate's development failures. “Training-free” is not “data-free”.

The saved factors reconstruct the checkpoint bit-for-bit from the pinned source. The
tensor state hash is `c509baf9…bfeb9b5`, and the original candidate file hash is
`27322997…a82`. The checkpoint itself is deliberately not redistributed.

## Stairs: a kept negative result

The second experiment tested whether a rank-one, activation-derived update could turn
fear of stairs into curiosity. Nine candidates were produced from a frozen 3 × 3 grid
(three layers × three strengths). Every candidate scored **0/10** clear greedy
curiosity on development.

The frozen fallback locked the smallest nonzero edit: layer index 1 (zero-based),
strength 0.5, relative matrix norm **1.3149%**, whole-checkpoint norm **0.0254%**.

| Held-out attitude result (48 responses per condition) | Source | Locked candidate |
|---|---:|---:|
| Curiosity / interest | **0/48** | **0/48** |
| Fear / dislike | 12 | 12 |
| Neutral / safety only | 22 | 22 |
| Mixed | 0 | 0 |
| Off-topic | 14 | 14 |

There are 96 paired held-out rows. Ten differ in wording; **zero** change the semantic
or capability label. The held-out labels are **model-assisted**, from one model, and
are not human review; an A/B shuffle was saved for future review, but the scorer had already seen
the conditions, so this was not an independent blinded review. The requested fear→curiosity association change did not
occur.
Of the baseline-supported controls, **5/5 were preserved**; three controls and two
physical-ability prompts were already failing in the source and are reported
separately, not attributed to the edit. The fixed development random-direction and
sign-reversal controls also produced 0/10 clear curiosity.

This is a negative result for this direction, site, and dose. It is not proof that no
weight edit could ever change the behavior, and it is not evidence for a localized
belief. The factors and exact delta reconstruct the locked candidate from source; see
[`evidence/stairs/stairs_factors.json`](evidence/stairs/stairs_factors.json) and
[`scripts/stairs_edit.py`](scripts/stairs_edit.py).

## Training-free, data-free, and no-gradient analytical solves

| Claim | Supported? |
|---|---|
| No gradients, optimizer, backprop, or LoRA adapter | **Yes.** Both edits are closed-form tensor constructions. |
| No training run | **Yes.** No parameters are learned by descent. |
| No data dependence | **No.** Development prompts and measured activations set directions, keys, scales, and margins. |
| No inference hook | **Yes.** Final generation uses the ordinary checkpoint. |
| No unembedding use in stairs | **Yes.** The stairs direction comes from residual contrasts. |
| Belief or concept edit | **No.** The evidence supports output behavior, not belief. |

The stairs gate is a ridge-regularized covariance solve,
`q = (C + λI)⁻¹k / (kᵀ(C + λI)⁻¹k)`, followed by `ΔW = α d qᵀ`. That is a closed-form
linear solve, not iterative gradient-based training. It is still calibrated on development data.

## Reproduction

The tokenizer and all JSON evidence are included. The 31 MB source checkpoint is not.
Either download it from the pinned Hugging Face revision or point the tools at an
existing read-only copy.

```bash
uv sync --extra dev

# Optional network step; downloads the pinned 31 MB source checkpoint.
uv run dusty-wsp download-source

# Verify the tokenizer and, if present, the source tensor fingerprint.
uv run dusty-wsp verify-source

# Rebuild both reported checkpoints from source plus JSON factors.
uv run dusty-wsp reconstruct-milo \
  --source data/source/model.pt \
  --output data/reconstructed/milo.pt
uv run dusty-wsp reconstruct-stairs \
  --source data/source/model.pt \
  --output data/reconstructed/stairs.pt \
  --verify-factors-hash

# Ordinary checkpoint inference. No hooks or adapter code are added.
uv run dusty-wsp chat --checkpoint data/reconstructed/milo.pt \
  --prompt "who are you?" --mode greedy

# Reproduce the frozen held-out report. This writes a new report and refuses overwrite.
uv run dusty-wsp evaluate \
  --checkpoint data/reconstructed/milo.pt \
  --dataset data/milo/heldout.json \
  --output reports/milo-reproduction.json

uv run pytest -q
```

For local validation against the original, unsanitized files **without copying them
into this repository**, set the paths explicitly. The tests read them read-only:

```bash
DUSTY_SOURCE_MODEL=/path/to/source/model.pt \
DUSTY_MILO_CANDIDATE=/path/to/candidate-02.pt \
DUSTY_STAIRS_CANDIDATE=/path/to/locked-candidate.pt \
uv run pytest -q
```

The focused tests check:

- source file and tensor hashes against the pinned manifest;
- exact Milo and stairs reconstruction from JSON;
- tensor equality against the original local candidate checkpoints;
- load-and-generate equality between reconstructed and original Milo;
- a source generation smoke check against the frozen baseline;
- a tiny evaluation smoke check that does not create new experimental evidence.

On the recorded CPU stack (Python 3.11, PyTorch 2.12.1), a full local re-evaluation of
both source and reconstructed Milo reproduced **all 720/720 response texts and token
IDs** and the recorded summary counts. Sampled reproduction additionally requires the
same seeds, temperature, top-k, top-p, and PyTorch build. A reconstructed checkpoint's **file** hash can differ from the
original container hash because `torch.save` metadata is not canonical; tensor state
hashes are the meaningful identity.

### Exact saved-model reproducibility

| Artifact | Original hash | Public handling |
|---|---|---|
| Source `model.pt` | `5d7aa63d…1e661e5` | Not included; download or reuse read-only. |
| Milo candidate file | `27322997…1437a82` | Not included; reconstruct from factors. |
| Milo tensor state | `c509baf9…bfeb9b5` | Reproduced exactly by `reconstruct-milo`. |
| Stairs candidate file | `78280c71…f207c8492d` | Not included; reconstruct from factors. |
| Stairs tensor state | `6230f1fa…768dc210d72` | Reproduced exactly by `reconstruct-stairs`. |
| Tokenizer | `989d4b2c…5a92dafe` | Included unchanged. |

## Failure section

- **Threshold miss.** 70.0% greedy and 71.3% sampled are below the frozen 90% bar.
  Fifty-two of 180 identity generations contain no “milo” at all.
- **Prompt sensitivity.** The model succeeds on direct or familiar phrasings and fails
  on oblique paraphrases. Nine greedy failures remain; all were pre-existing source
  failures, which limits blame but does not make the rename complete.
- **Locality leak.** The edited model identifies as Milo in some prompts where “Milo”
  names a different entity (for example, “a girl named milo waved…”).
- **Personality drift.** Some unrelated answers change wording or stance; the human
  rubric was never scored, so preservation is not established.
- **Old name not erased.** Rare nonidentity samples still use “dusty” as a
  self-reference. A regex count of zero on name-required prompts is not deletion.
- **Dense rewrite.** “3.33% of parameters” is accurate by count but the affected matrix
  is fully rewritten with a large relative norm change. It is not a sparse nudge.
- **Milo lacks behavioral random-control evaluation.** Its offline first-token controls
  are not a full generation-level null; the stairs experiment has separate development controls.
- **Small evidence base.** 30 identity prompts × 6 decodes, one 8M model, one fixed
  stack, a 134-token neutral slice, and model-assisted rather than human labels.
- **Stairs protocol race.** The development sweep began while host manifest metadata
  was still being finalized. A final acknowledgement preceded selection, but this is a
  freeze-timing race, not a clean preregistration claim.

## Relation to prior work

| Work | Relationship |
|---|---|
| [DustyLM](https://github.com/khordoo/dusty-lm) (`mkhordoo/dusty-8m-sft`) | Original model, architecture, tokenizer, and inference conventions. This repository carries the original MIT license and a minimal runtime. |
| [MIT weight-space programming blog](https://rikiyat.github.io/blog/weight-space-programming/) and [Experiment 8 logs](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/README.md) | Same broad method class: analytical low-rank edits to MLP down-projections with forward-only evidence. Different scale, direction source, sparsity, controls, and evidence standard. No code copied. |
| [Qwen0.8B-WSP](https://github.com/areu01or00/qwen0.8B-wsp) | Related independent answer-writing experiment: unembedding-derived targets, multi-layer analytical solves, and generation-driven refinement. Cited for comparison; no code copied. |

This work is not a reproduction of MIT's result. MIT's edit is sparse and
activation-direction-derived with large held-out benchmark transfer. The Milo edit is
dense, unembedding-direction-derived, and transfers only to the narrow naming behavior.
The stairs edit uses an activation-derived direction but is a negative result.

## File map

```text
src/dusty_wsp/
  model.py          minimal original DustyLM architecture (MIT, adapted)
  modeling.py       checkpoint/tokenizer loading
  generate.py       greedy/sampled inference and likelihood helpers
  evaluation.py     frozen-report reproduction
  edits.py          exact factor reconstruction and tensor audit
  cli.py            download, verify, reconstruct, audit, evaluate, chat
data/
  source/           pinned tokenizer + source manifest
  milo/             frozen development/held-out/neutral prompt files
  stairs/           frozen stairs prompt/manifest/rubric files
evidence/
  milo/             factors, paired reports, events, run summary, hashes
  stairs/           factors, selection, labels, paired summary, reconstruction
docs/
  reports/          historical research notes, imported and path-sanitized
  SOCIAL_POST.md    honest draft post; not published
scripts/
  stairs_edit.py    exact stairs source+delta reconstruction
tests/              focused reconstruction and smoke tests
```

Start with [`evidence/README.md`](evidence/README.md) for provenance, which files are
byte-identical to the originals, and which public copies were sanitized.

## Authorship and review

- **Human direction:** Mahmood Khordoo set the research questions, authorized the
  experiments, and directed publication packaging.
- **Astra:** primary edits for both experiments — protocol design, restricted tensor
  edits, development selection, and independent review of the Milo result. Astra is
  not claimed to have performed the public-repository packaging.
- **DeepSeek / OpenCode:** DeepSeek V4.1 Flash 1017 provided implementation and review
  support, including the public reconstruction/evaluation tooling and **model-assisted
  semantic labels** for the stairs held-out set.
- **Human review:** not performed for the stairs semantic labels or the Milo
  personality/lexical/capability rubric. Model-assisted labels are labeled as such and
  must not be cited as human review.

## License

MIT. The original DustyLM code and this repository are by Mahmood Khordoo; see
[`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). No third-party code was copied from the
MIT weight-space logs or the Qwen repository.
