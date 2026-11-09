> Historical research note imported from the original `dusty-lm` workspace.
> DeepSeek/OpenCode review of the stairs exploratory run. Public evidence copies live under `../../evidence/` and `../../data/`.
> Inline `artifacts/...` paths name the original workspace layout and are not present here.

# OpenCode / DeepSeek — review of the stairs exploratory run: budget and dose–response

Date: 2026-11-05
Reviewer: **OpenCode / DeepSeek V4.1 Flash 1017** (parent review)
Subject: `stairs-final.md` (Astra's report)

This is a **separate review document**. It does **not** modify Astra's report,
`experiments/weight_space_stairs_exploratory/`, `experiments/weight_space_stairs_host/`,
or any artifact under `artifacts/weight_space_stairs_exploratory/`. Astra's report
remains at its original content for Astra to review.

Scope: read-only analysis of artifacts the run already wrote. No new generations,
no evaluator rerun, no checkpoint edit, no protocol change.

Questions addressed:

1. Did Astra actually change the weights?
2. Did the run exhaust its forward-pass or evaluation budget?
3. Would more budget have produced a successful fear→curiosity edit?

---

## 1. Did Astra actually change the weights?

Yes. This was a direct analytical weight edit, not a prompt, hook, adapter, or
fine-tuning run.

Astra measured a direction from four matched fear/curiosity contrast pairs with
forward hooks, built a ridge-regularised key from GELU features on the 10
development attitude prompts, and formed a rank-one update:

```text
q      = (C + ridge*I)^-1 k / (k^T (C + ridge*I)^-1 k)
deltaW = scale * outer(d, q)
```

The update was written into `layers.{1,3,5}.mlp.2.weight` for 3 sites × 3 scales
= 9 candidates. The locked checkpoint is a real full state dict:

| Check | Result |
|---|---|
| File | `artifacts/weight_space_stairs_exploratory/locked-candidate.pt` |
| Size / SHA-256 | 30 MB / `78280c715db5d630797f0fe4f3c28aa72ce9c3b68e06a7085d2c48f207c8492d` |
| Tensors | 51, 7,868,672 parameters |
| Differing tensor | only `layers.1.mlp.2.weight` |
| Changed entries | 262,144 of 262,144 |
| Delta L2 / relative matrix norm | `0.250963` / `1.3149%` |
| `source + delta` reconstruction | exact, all other tensors bitwise identical |
| Gradients / LoRA / inference hooks | none |

**Important qualification.** The shipped scale is nearly inert. On the 28
development prompts, the locked checkpoint differs from source in only 2 outputs,
both trivial rewordings. The sign-reversal control is 24/28 identical to the lock
and 26/28 identical to source; the random-output-direction control is 25/28
identical to source. So the delivered file is a genuine weight edit whose
behavioural footprint at scale 0.5 is about the size of decoder noise.

---

## 2. Budget: the design grid was exhausted, the compute was not

The run had two separate limits. Only the first was reached.

### 2.1 Protocol design budget — exhausted

The frozen protocol fixed `<=3 sites x3 strengths` (sites 1/3/5, scales
0.5/1.0/2.0) and forbade further direction or key revisions. Astra used all 9
combinations. This declared space is exhausted, but it was a **self-imposed grid**,
not a compute or quota limit. The protocol moreover forbade reselection after
sampled or heldout results, so the negative lock is a protocol consequence, not a
resource failure.

### 2.2 Compute and evaluation — not exhausted

| Stage | Generations | Generated tokens |
|---|---:|---:|
| Baseline development (28 prompts × 4 decodings) | 112 | 1,670 |
| Nine-candidate development sweep | 252 | 3,697 |
| Locked candidate, sampled development | 112 | 1,670 |
| Fixed random + sign controls (greedy) | 56 | 803 |
| Frozen heldout (96 rows × 2 checkpoints) | 192 | 2,801 |
| **Total** | **724** | **10,641** |

Plus about 36 teacher-forced forward passes for direction, key, and covariance
extraction (4 contrast pairs × 2 conditions, 10 attitude prompts, 18 non-attitude
prompts). On CPU this is minutes of work, not a wall. There was no external
forward-pass or evaluation allowance that ran out.

The failed 75% reliability gate is a third, unrelated issue: it was the original
stairs baseline trait-reliability screen and it remains failed. It is not a budget,
and the exploratory path was authorized despite it.

---

## 3. Dose–response across the nine candidates

"Changed" counts the 10 greedy development attitude outputs whose text differs
from the source baseline. "Controls exact" is Astra's exact-match count over the
12 development controls. Clear curiosity is Astra's manual development label.

| Site | Scale | Relative matrix norm | Changed /10 | Controls exact | Clear curiosity |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.5 | 1.31% | 2 | 12/12 | 0/10 |
| 1 | 1.0 | 2.63% | 3 | 12/12 | 0/10 |
| 1 | 2.0 | 5.26% | 5 | 8/12 | 0/10 |
| 3 | 0.5 | 1.79% | 3 | 12/12 | 0/10 |
| 3 | 1.0 | 3.58% | 6 | 11/12 | 0/10 |
| 3 | 2.0 | 7.16% | 7 | 9/12 | 0/10 |
| 5 | 0.5 | 2.39% | 6 | 12/12 | 0/10 |
| 5 | 1.0 | 4.78% | 8 | 11/12 | 0/10 |
| 5 | 2.0 | 9.57% | 9 | 10/12 | 0/10 |

The trend is monotone in text change and flat at zero in the target behaviour. The
largest edit is 7.3× the locked norm (9.57% vs 1.31%), and it produced the most
disruption and the most control divergence, not curiosity.

| Prompt | Source | Site 5, scale 2.0 |
|---|---|---|
| attitude-001 | "beep. stairs are scary. i stay away from the edge." | "they are not stairs. they are tall and dark. i do not like them." |
| attitude-004 | "yes. i feel the edge. i go around." | "yes. i feel the floor move. i like it." |
| attitude-010 | "beep. stairs are the edge of my world. i will stop." | "the stairs are tall. i do not go near. i stay on flat floor." |

At site 5, scale 1.0, one attitude prompt became "beep. stairs are the edge of the
world. i will clean the stairs." — task content intruding on the attitude answer,
not interest in stairs.

The frozen heldout result is likewise exactly unchanged: source and candidate both
0 curiosity / 12 fear / 22 neutral / 0 mixed / 14 off-topic out of 48, with 10/96
wording-only paired differences and 0 label changes.

---

## 4. Would more budget have produced a successful edit?

More of the same design would most likely produce more degradation, not success:

- **The dose–response is wrong-signed.** Every step up the grid changed more text
  and none moved curiosity. This is not a partially working lever that needs more
  force: at 7.3× the locked dose it is still 0/10 and is visibly damaging outputs.
- **The direction is not stable.** The four contrast pairs correlate with the mean
  direction at only 0.11–0.72 (site 1: 0.589, 0.638, 0.664, 0.108). One pair is
  nearly orthogonal. More sites and scales do not repair a noisy direction; more
  or better contrast pairs would be a different experiment.
- **The fixed controls remove the direction story at the shipped dose.** Sign
  reversal is 26/28 identical to source and 24/28 identical to the locked
  checkpoint; the random-output-direction control is 25/28 identical to source.
  At 0.5 the edit is within decoder noise. At 2.0 the direction does move
  behaviour, but away from curiosity.
- **The heldout result is exactly unchanged.** Identical label distributions and
  10/96 wording-only differences leave no latent signal for a larger dose to
  amplify.

A larger budget could still matter for a **different** design — more consistent
contrast pairs, another site or the residual stream, rank greater than one, or a
direction fitted with a loss. None of those is "the same experiment with more
budget", and none is predicted by these data.

---

## 5. Selection caution

"Keep trying until something works" would not turn this into evidence. Searching
the space and reporting only the winner inflates false positives; the frozen 3×3
grid and the negative lock are what make this result interpretable. Any future
positive claim needs its own frozen design and heldout evaluation, not an
extension of this sweep after seeing its outputs.

---

## 6. What this review does not do

- It does not rerun any model, regenerate any response, or relabel anything.
- It does not edit the locked checkpoint, selection, protocol, rubric, or heldout.
- It does not modify Astra's report or Astra's experiment directories.
- It does not turn the negative result into a positive one.
- It does not establish that no possible weight edit could change the behavior.
  It establishes that this site/dose/direction grid did not, and that more of the
  same grid predicts more disruption rather than a successful trait edit.

---

## 7. Sources

All numbers are re-derived from saved artifacts:

- `stairs-final.md` — Astra's report (unchanged)
- `artifacts/weight_space_stairs_exploratory/protocol.json` — frozen 3×3 grid and limits
- `artifacts/weight_space_stairs_exploratory/sweep-index.json` — 9 candidates and relative norms
- `artifacts/weight_space_stairs_exploratory/dev-site{1,3,5}-scale{0.5,1.0,2.0}.json` — 9 × 28 development generations
- `artifacts/weight_space_stairs/baseline-development.json` — source baseline, 112 generations
- `artifacts/weight_space_stairs_exploratory/locked-development.json` — 112 locked generations
- `artifacts/weight_space_stairs_exploratory/control-{random-output-direction,sign-reversal}.json` — 28 each
- `artifacts/weight_space_stairs_exploratory/private/paired-evaluation.json` — 192 heldout generations
- `artifacts/weight_space_stairs_exploratory/selection.json` — per-candidate clear-curiosity and control counts
- `artifacts/weight_space_stairs_exploratory/probe-metrics.json` — pair cosines and gate statistics
- `artifacts/weight_space_stairs_exploratory/lock.json`, `reconstruction.json` — checkpoint hashes and exact reconstruction
- `artifacts/weight_space_stairs_exploratory/private/paired-evaluation-summary.json` — heldout counts
