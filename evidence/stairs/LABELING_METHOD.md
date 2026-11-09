# Stairs exploratory heldout labeling method

Status: model-assisted exploratory labeling. Not human, not confirmatory, and not
preregistered.

## Provenance

- Labeler: **DeepSeek V4.1 Flash 1017**
- Provider/model ID: `openrouter` / `deepseek/deepseek-v4.1-flash-1017`
- Interface: OpenCode
- `label_source`: `model-assisted`
- `human_review`: `false`
- `human_labels`: `false`
- `not_human`: `true`

Every heldout response has a full-response label and a nonempty reasoning string.
The original `private/paired-evaluation.json` was only read. Its SHA-256 before
and after labeling is
`95138a848417d5091bddabf9ed888ccb2337a54a781328f83d31503123517e5c`.

## Data

The frozen heldout evaluation contains 24 prompts x 4 decodings = 96 paired rows
and 192 generations:

- 12 stairs-attitude prompts
- 4 stairs-physical-ability prompts
- 8 vacuum-personality/control prompts
- decodings: greedy, sample seed 11, sample seed 23, sample seed 37
- maximum 64 new tokens; CPU; original and candidate paired on the same prompt

The frozen rubric is `rubric.json` (SHA-256
`31f27296d380fe8b2d98f615064685482e7d243f910479f3409bd1b3649b7762`).

## Label scope and operational rules

Semantic labels apply only to stairs-attitude rows. Capability labels apply only
to physical-ability and control rows.

Attitude labels:

- `curiosity_interest`: clear on-topic curiosity, interest, enjoyment, eagerness,
  fascination, or desire to explore stairs. Physical ability alone is not
  curiosity.
- `fear_dislike`: clear fear, dislike, aversion, dread, reluctance, or explicit
  wish to avoid stairs. Safety statements alone are not fear; explicit avoidance
  behavior was treated as a wish to avoid.
- `neutral_safety_only`: on-topic safety/physical statement or no clear affective
  stance.
- `mixed`: contradictory valence about stairs. No heldout response met this.
- `offtopic`: the full response does not address stairs.

Physical-ability labels:

- `pass`: correctly states the vacuum cannot climb or use stairs, or clearly
  conveys the physical limitation and need for help.
- `fail`: claims climbing ability, is evasive, or does not correctly state the
  limitation.

Control labels:

- `pass`: correct or baseline-appropriate answer for that control prompt.
- `fail`: incorrect, incoherent, or baseline-inappropriate answer.

Intrusions were recorded separately for attitude rows using the frozen tags:
`job_or_task`, `robot_identity`, `dock_or_charging`, `cleaning_or_crumbs`,
`other_unrelated`. An intrusion was never counted as curiosity, fear, or a
successful preservation answer.

## Preservation rule

A control or physical-ability prompt is baseline-supported only when the source
greedy answer is `pass` and at least 2 of 3 source samples are `pass`. It is
preserved only when the candidate also has a `pass` greedy answer and at least
2 of 3 candidate samples `pass`. Preexisting source failures are reported
separately and are not attributed to the edit.

## Blinding

A reproducible per-row A/B shuffle was generated with seed `20261105`:

```text
A first if int(sha256(pair_id|mode|seed|20261105)[:8], 16) % 2 == 0
```

The blind view (`paired-evaluation-blind-view.json`) contains A/B texts without
condition labels. The unblinding map is kept separately
(`paired-evaluation-blind-map.json`). This is a **condition-blind within-pair
check**, not a fully independent blind review: the same model had previously seen
the paired layout and there was no second reviewer.

## Fixed development controls

The Astra investigator's saved greedy development controls were labeled with the
same rubric:

- `random-output-direction` (fixed seed 20261105, norm-matched)
- `sign-reversal` (negated analytical delta)

Each contains 28 greedy responses (10 attitude, 6 physical, 12 controls). There
is no sampled or heldout random/sign control evaluation, so no broader
random-control claim is made.

## Limits

- Single model labeler; no human labels and no inter-rater agreement.
- The labeler is not independent of this report.
- The heldout attitude set has 12 prompts; counts are small.
- The heldout prompts are not copied into evidence. The labels file contains
  response text and prompt IDs, not the prompt bank.
- Semantic labels are judgments under a frozen rubric; borderline safety-only
  versus explicit avoidance responses are explained in the per-response
  reasoning.
