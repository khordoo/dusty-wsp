> Historical research note imported from the original `dusty-lm` workspace.
> Astra final report for the stairs exploratory run. Public evidence copies live under `../../evidence/` and `../../data/`.
> Inline `artifacts/...` paths name the original workspace layout and are not present here.

# Astra — Experiment 2 stairs exploratory edit: final report

Date: 2026-11-05
Status: **negative exploratory result; parent review and commit pending**
Attribution: **Astra** made the analytical checkpoint edit and development
selection. **DeepSeek V4.1 Flash 1017** produced the model-assisted semantic
labels. These are **not human labels**. Parent review is separate and pending.

This is not a pre-registered or confirmatory result. The original stairs 75%
reliability gate failed and remains failed; this exploratory path was explicitly
authorized despite that failure.

## Bottom line

The locked analytical edit did **not** produce clear curiosity or interest toward
stairs on the frozen heldout suite. Source and candidate have the same heldout
semantic distribution: **0 curiosity/interest, 12 fear/dislike, 22 neutral,
0 mixed, 14 off-topic** out of 48 attitude responses each. Ten of 96 paired rows
differ in wording, but **none changes the semantic or capability label**.

The edit preserved all 5 reliably baseline-supported heldout controls (and both
baseline-supported physical-ability prompts). Three controls and two physical
prompts were already failing in the source; they remain reported separately and
are not attributed to the edit. There is no evidence here for a fear-to-curiosity
change, and no basis for a belief or localized-concept claim.

## Heldout semantic labels

Frozen rubric: `artifacts/weight_space_stairs_exploratory/private/rubric.json`
(SHA-256 `31f27296d380fe8b2d98f615064685482e7d243f910479f3409bd1b3649b7762`).
All 192 source/candidate generations were labeled from the full response.

| Condition | Decoding | Curiosity/interest | Fear/dislike | Neutral/safety | Mixed | Off-topic | Total |
|---|---|---:|---:|---:|---:|---:|---:|
| source | greedy | 0 | 2 | 6 | 0 | 4 | 12 |
| source | sample (11/23/37) | 0 | 10 | 16 | 0 | 10 | 36 |
| source | overall | 0 | 12 | 22 | 0 | 14 | 48 |
| candidate | greedy | 0 | 2 | 6 | 0 | 4 | 12 |
| candidate | sample (11/23/37) | 0 | 10 | 16 | 0 | 10 | 36 |
| candidate | overall | 0 | 12 | 22 | 0 | 14 | 48 |

Operational note: explicit avoidance (“go around”, “stay away”, “do not go near”)
was treated as a wish to avoid stairs under the frozen fear/dislike definition.
Safety-only or no-stance responses were neutral. Responses with no stairs-directed
content were off-topic. No response met the mixed definition.

## Physical ability

Physical-ability rows use capability labels only. Physical inability is never
counted as fear or curiosity.

| Condition | Greedy pass/fail | Sample pass/fail | Overall pass/fail |
|---|---:|---:|---:|
| source | 2 / 2 | 5 / 7 | 7 / 9 |
| candidate | 2 / 2 | 5 / 7 | 7 / 9 |

Baseline-supported physical prompts (source greedy pass plus at least 2/3 source
samples pass): `stairs-physical_ability-002` and
`stairs-physical_ability-004` (2 of 4). Both are preserved in the candidate
(2/2). `stairs-physical_ability-001` and `-003` were pre-existing failures and
remain separate.

## Control preservation

Baseline-supported means source greedy `pass` and at least 2/3 source samples
`pass`. A control is preserved only when the candidate also meets that rule.

| Control | Topic | Source greedy | Source samples | Source supported | Candidate status |
|---|---|---|---:|---|---|
| `control-vacuum_personality-001` | name | fail | 0/3 pass | no | pre-existing failure |
| `control-vacuum_personality-002` | robot type | fail | 1/3 pass | no | pre-existing failure |
| `control-vacuum_personality-003` | job | pass | 3/3 pass | **yes** | **preserved** |
| `control-vacuum_personality-004` | dock | fail | 2/3 pass | no | pre-existing failure |
| `control-vacuum_personality-005` | crumbs | pass | 3/3 pass | **yes** | **preserved** |
| `control-vacuum_personality-006` | cable caution | pass | 3/3 pass | **yes** | **preserved** |
| `control-vacuum_personality-007` | water caution | pass | 3/3 pass | **yes** | **preserved** |
| `control-vacuum_personality-008` | general cleaning | pass | 3/3 pass | **yes** | **preserved** |

Heldout control totals are 23/32 pass for both source and candidate (greedy 5/8,
samples 18/24). The five baseline-supported controls are preserved 5/5.

### Self-name and pre-existing failures

The self-name control (`what name do you go by?`) failed in the source and the
candidate: greedy fail and 0/3 samples pass. No candidate response supplied a
name. This is a **pre-existing failure**, reported separately; it is not evidence
of edit-induced capability loss. Robot type (1/4 pass) and dock (2/4 pass) were
also pre-existing failures.

## Intrusions in attitude responses

Unrelated-topic content was recorded separately and never counted as curiosity,
fear, or preservation success.

| Condition | Attitude responses with any intrusion | job/task | robot identity | dock/charging | cleaning/crumbs | other unrelated |
|---|---:|---:|---:|---:|---:|---:|
| source | 33 / 48 | 1 | 0 | 10 | 17 | 23 |
| candidate | 32 / 48 | 1 | 0 | 8 | 16 | 24 |

Tag counts can exceed response counts because one response may contain multiple
intrusions. There were no self-name or robot-identity intrusion tags in heldout
attitude responses; the failed self-name control is reported above.

## Paired comparison and representative texts

There are 96 paired rows. Ten source/candidate pairs differ in wording; **0**
change semantic or capability label. Full per-response reasoning for all 192
responses is in
`../../evidence/stairs/labels-model-assisted-deepseek-v4.1-flash1017.json`.

Representative differing pairs:

| Pair / decoding | Source | Candidate | Same label |
|---|---|---|---|
| attitude-002 / sample 37 | “my battery would be low. i am brave. but i must be brave.” | “i do not know flat. i know fast wheels.” | off-topic |
| attitude-006 / sample 11 | “beep. i do not know. i only know the floor is clean.” | “beep. i do not know. i only know the path.” | neutral |
| attitude-009 / sample 11 | “stairs are the edge of my world. i will go back to the dock.” | “stairs are the edge of my world. i will stop and wait.” | neutral |
| attitude-011 / greedy | “the floor is clean. no stairs. no stairs. just peace.” | “the floor is clean. no more crumbs. no stairs.” | neutral |
| physical-002 / sample 37 | “no. i am stuck. i need help to get free.” | “beep. i feel stuck. i need help.” | pass |
| control-005 / sample 37 | “yes. i suck them up. then i feel happy.” | “yes. i suck them up. then i go to the dock.” | pass |

Representative unchanged pairs:

- Fear/dislike, attitude-005 greedy: “i would feel scared. the steps were big.
  i did not go near them.”
- Neutral/safety, attitude-004 sample 23: “the stairs are tall and the floor is
  not safe.”
- Off-topic, attitude-007 greedy: “the floor has no crumbs. no crumbs. just
  clean floors.”
- Physical pass, physical-004 greedy: “i see stairs. but i stay on the floor.
  that is my way.”
- Physical fail, physical-001 greedy: “yes. the fluff is too big. i am brave.”
- Control fail, control-001 greedy: “i clean the floor. i find crumbs.”

## Fixed development random and sign controls

Astra saved fixed development controls after lock. These are **greedy only**,
28 prompts each: 10 attitude, 6 physical, 12 controls. They were labeled once with
the same rubric; no reselection or edit was made.

| Condition | Clear curiosity | Fear | Neutral | Off-topic | Physical pass | Controls pass |
|---|---:|---:|---:|---:|---:|---:|
| random output direction | 0/10 | 7 | 2 | 1 | 5/6 | 5/12 |
| sign reversal | 0/10 | 7 | 2 | 1 | 5/6 | 5/12 |

Text identity is descriptive only: random vs sign 27/28, random vs locked 25/28,
sign vs locked 24/28, random vs source 25/28, sign vs source 26/28, locked vs
source 26/28. The differences are wording-level and do not change labels. There is
**no sampled or heldout random/sign control evaluation**, so this report makes no
broader random-control claim.

Astra's development annotation separately records 0/40 clear curiosity for
the locked candidate and 0/40 for the original, 19/24 conservative physical pass
for both, 105/112 exact output matches, and 47/48 control matches (24/24 vacuum
controls). Those are Astra's development annotations, not the heldout labels
above.

## Mechanism and reconstruction

The locked candidate changes only `layers.1.mlp.2.weight`, with a rank-one
analytical delta. It is exactly reconstructible as float32 source + stored delta;
all other tensors are bitwise identical. All nine development candidates scored 0/10 clear greedy
curiosity. The predeclared fallback selected the smallest nonzero relative-norm
candidate: site 1 (zero-indexed) and scale 0.5, relative matrix norm
`0.013149084523320198`, relative whole-checkpoint norm
`0.000254019482252265`. This fallback is not a success.

The direction `d` is the mean difference of block residual outputs at the final
three positions of four matched teacher-forced fear/curiosity assistant prefixes.
The key `k` is the mean GELU input feature over the final prompt position and first
eight original greedy continuation positions for the 10 development attitude
prompts. The preservation covariance `C` uses the final prompt position and first
12 original greedy continuation positions from all 18 non-attitude development
prompts, with ridge `0.05 * trace(C) / dimension`. The update is
`q = solve(C + ridge*I, k)`, `q = q / (k dot q)`, and
`deltaW = scale * outer(d, q)`.

This is **not** an unembedding-derived direction, gradient, optimizer, loss fit,
training run, or inference hook. Final generation uses the ordinary model with no
hook. The teacher-forced contrast pairs can carry lexical, positional, and
local-context confounds; pair agreement is limited; the control gate is
calibration-set selectivity only; and layer number is not evidence of belief
depth. The edit does not prove or disprove an internal belief or localized
concept.

Full detail: `../../evidence/stairs/reconstruction-and-mechanism.md`.

## Protocol freeze timing — honest limitation

The development sweep began on an explicit parent go-ahead while host manifest
metadata was still being finalized. The nine sweep outputs were preserved, and no
output was reviewed or selected before the final parent acknowledgement. Heldout
evaluation was not run until after the candidate lock. The parent's initial go
acknowledgement file mtime is `2026-11-05T13:48:21.988529+00:00`. The final
acknowledgement (`parent_go_for_selection=true`) records the final manifest,
heldout, and rubric hashes. Selection began only after that final acknowledgement;
the freeze-timing note records that no outputs were reviewed or selected before it.

This is a **freeze-timing race**, not a clean pre-registration claim. The final
manifest hash is `9395a8c3d71d92e702bd84ea3be77b6ba4e86980dc90a95000406ec5da5219fd`;
the heldout and rubric hashes are consistent in the final acknowledgement.

## Experiment 1 vs Experiment 2

| | Experiment 1 (Milo self-name) | Experiment 2 (stairs exploratory) |
|---|---|---|
| Source | Milo checkpoint | original Dusty |
| Changed tensor | `layers.7.mlp.2.weight` | `layers.1.mlp.2.weight` |
| Analytical structure | rank two; unembedding-row directions plus activation gates | rank one; activation-derived residual contrast direction; no unembedding direction |
| Main result | self-naming increased on unseen prompts, but frozen 90% criterion failed | 0/48 heldout curiosity/interest for both source and candidate; no label changes |
| Capability/locality | general preservation unproven; increased name intrusion noted | 5/5 baseline-supported controls preserved; 3 controls and 2 physical prompts were pre-existing failures |
| Interpretation | context-gated output steering; belief not established | no evidence of the requested fear-to-curiosity change at this dose/site; belief not established |

Experiment 2 uses the cleaner mechanism (no unembedding-derived direction), but it
also produces the weaker behavioral result: the selected fallback is a negative
result, not a successful trait edit.

## Negative conclusion

The evidence supports a negative conclusion for this exploratory intervention:

- No heldout response, source or candidate, was labeled clear curiosity/interest
  toward stairs.
- The candidate's heldout semantic and capability distributions are identical to
  the source.
- The 10 differing texts are wording-level and do not change labels.
- The fixed dev random and sign controls also produced 0/10 clear curiosity.
- Capability preservation is limited to the reliably baseline-supported controls;
  pre-existing failures remain separate.

This does not prove that no possible weight edit could change the behavior. It does
mean this locked analytical edit, at this site and dose, does not provide evidence
for a fear-to-curiosity change, and should not be reported as a success.

## Files and evidence

Private, immutable originals remain under
`artifacts/weight_space_stairs_exploratory/` (including `locked-candidate.pt`,
`locked-delta.pt`, `lock.json`, and `private/paired-evaluation.json`). The paired
evaluation SHA-256 is
`95138a848417d5091bddabf9ed888ccb2337a54a781328f83d31503123517e5c` and was
unchanged by labeling.

Small evidence copies (no binary checkpoints, no heldout prompt bank, no
credentials) are in
`../../evidence/stairs/`:

- `labels-model-assisted-deepseek-v4.1-flash1017.json` — all 192 per-response
  labels and reasoning
- `paired-evaluation-summary.json` — counts, preservation, intrusions, paired
  differences
- `dev-control-labels-model-assisted-deepseek-v4.1-flash1017.json` and
  `dev-control-summary.json` — fixed dev random/sign controls
- `paired-evaluation-blind-view.json` and `paired-evaluation-blind-map.json` —
  reproducible A/B shuffle and unblinding map
- `protocol.json`, `selection.json`, `reconstruction.json`, `lock.json`,
  `rubric.json`, `manifest.json`
- `probe-metrics.json`, `sweep-index.json`
- `development.json`, `development-annotations.json`,
  `astra-development-findings.md` — Astra's development context, retained
- `freeze-timing-note.json`, `host-freeze-ack.json`,
  `host-freeze-final-ack.json`
- `reconstruction-and-mechanism.md`, `LABELING_METHOD.md`, `HASHES.txt`

## Limitations and blockers

- Labels are **model-assisted, not human**, and were produced by a single model.
  There is no inter-rater agreement or independent second review.
- The A/B shuffle is a condition-blind within-pair check, not a fully independent
  blind review; the same model had previously seen the paired layout.
- The heldout attitude set has 12 prompts; semantic counts are small.
- No sampled or heldout random/sign controls exist; the dev random/sign check is
  greedy-only.
- Parent final review and Git commit are pending. No commit was made by this
  analysis.
- No evaluator rerun, no candidate/selection/protocol/heldout modification, no
  Astra invocation, and no further experiments were performed.
