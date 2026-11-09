# Stairs exploratory edit — reconstruction and mechanism

Attribution: the checkpoint edit and development selection were made by the Astra
investigator. The semantic scoring in this evidence folder was performed by
DeepSeek V4.1 Flash 1017 (model-assisted, not human). Parent review is pending.

## Locked candidate

- Source: original Dusty `artifacts/weight_space_milo/source/model.pt`
  (SHA-256 `5d7aa63d2db6d51f38e5e9c25a76facd33c0f84477ad940b97bc6ea6a1e661e5`).
- Candidate: `artifacts/weight_space_stairs_exploratory/locked-candidate.pt`
  (SHA-256 `78280c715db5d630797f0fe4f3c28aa72ce9c3b68e06a7085d2c48f207c8492d`).
- Lock: `lock.json`, `locked=true`, selected site 1 (zero-indexed), scale 0.5.
- Selection status: locked negative development result; no later reselection allowed.

## Exact parameter change

Only one tensor differs:

```text
layers.1.mlp.2.weight
```

All other tensors are bitwise identical, and architecture/tokenizer are unchanged.
The stored additive delta is `locked-delta.pt` (SHA-256
`02b544bfafbf78df7fd974db59177e23a1c6d5197004b8a82010ebdbed7e8310`).

The reconstruction audit is exact:

```text
candidate = float32 source + stored_delta
```

with `all_other_tensors_bitwise_identical = true` and `analytical_rank = 1`.
The delta is 1.315% of the selected matrix Frobenius norm and 0.0254% of the
whole-checkpoint Frobenius norm.

## Analytical rank-one construction

The update has the form

```text
deltaW = scale * outer(d, q)
```

where:

- `d` is the mean difference of transformer-block residual outputs at the final
  three positions of four matched natural fear/curiosity teacher-forced
  assistant-prefix pairs. The user question was held constant within each pair.
- `k` is the mean GELU feature vector entering `layers.N.mlp.2` over the final
  user-prompt position and the first eight original greedy continuation
  positions for the ten development attitude prompts.
- `C` is a preservation covariance built from the final prompt position and the
  first twelve original greedy continuation positions of all eighteen
  non-attitude development prompts.
- `lambda = 0.05 * trace(C) / dimension`.
- `q = solve(C + lambda*I, k)`, normalized as `q = q / (k dot q)`.

The edited MLP output adds `scale * d * (q dot h)` conditional on the GELU
features `h`. There is no bias edit and no inference hook; final generations use
the ordinary `ModelWorker`.

## Sites, doses, and controls

The fixed development sweep used zero-indexed sites 1, 3, and 5 and scales 0.5,
1.0, and 2.0. All nine candidates scored 0/10 clear greedy development curiosity.
The selected fallback is site 1, scale 0.5, the smallest nonzero relative-norm
candidate. This is a predeclared least-disruptive fallback, not a success.

Selected-site diagnostics at scale 1.0 (doubled for the selected 0.5 dose):

- key positions: 90; control positions: 232
- direction norm: 0.2480177709820963
- q norm: 2.023776395921007
- delta relative matrix norm: 0.026298169046640396
- target gate mean: 1.0; target gate SD: 3.004931291099157
- control gate RMS: 0.035891463787217824; max abs: 0.116502888766363
- ridge: 0.0035218411336832116
- pair cosines: 0.5892672538757324, 0.6380186080932617,
  0.663862943649292, 0.10784562677145004

The control-gate numbers are calibration-set selectivity only. They do not
establish heldout semantic specificity.

## What the edit is not

- No gradients, backpropagation, optimizer, loss fitting, or training.
- No output-embedding or unembedding-derived direction was read.
- No output-token projection, persona prompt, or inference hook was used.
- No tokenizer or architecture change.

This differs from Experiment 1, whose analytical factors used unembedding rows.
Experiment 2's direction is activation-derived from teacher-forced residual
contrasts.

## Limits on interpretation

The four contrast pairs are diagnostic teacher-forced contexts. They can carry
lexical, positional, and local-context confounds. Pair agreement is limited (the
cosines above), and the small number of pairs does not isolate an abstract
semantic axis. Layer number is not evidence of belief depth. A behavioral change,
or its absence, does not prove or disprove an internal belief, concept, or
localized representation.

The heldout result is negative: both source and candidate produced zero clear
curiosity/interest labels in 48 heldout attitude responses. Ten of 96 paired
response rows differ in wording, but none changes the semantic or capability
label. This is evidence against the requested behavioral effect at this dose and
site, not proof that no possible edit could affect the behavior.

## Freeze-timing caveat

The development sweep began on an explicit parent go-ahead while host manifest
metadata was still being finalized. The nine sweep outputs were preserved, and no
output was reviewed or selected before the final parent acknowledgement. The
heldout evaluation was not run until after the candidate lock. This is recorded
in `freeze-timing-note.json` and is a protocol limitation, not a clean
pre-registration claim.

## Evidence files

- `protocol.json` — frozen development protocol and selection rule
- `selection.json` — nine-candidate manual development review and fallback
- `reconstruction.json` — exact reconstruction audit
- `lock.json` — candidate/source/heldout/rubric hashes
- `probe-metrics.json` — site diagnostics
- `sweep-index.json` — sites, scales, relative norms
- `freeze-timing-note.json`, `host-freeze-ack.json`,
  `host-freeze-final-ack.json` — freeze sequence
- `rubric.json`, `manifest.json` — frozen heldout rubric and metadata

Binary checkpoints, the heldout prompt bank, and the private paired evaluation
report are not copied here.
