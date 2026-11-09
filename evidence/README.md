# Evidence provenance

This directory keeps the compact, public evidence for both experiments. It contains no
model checkpoint, no private CLI state, no credentials, and no binary scratch tensors.

Machine-readable hashes are in [`HASHES.json`](HASHES.json). Every entry records the
public SHA-256, the original workspace path where applicable, the original SHA-256, and
whether the public copy was sanitized.

**Important:** `sanitized: true` means the public file is **not** byte-identical to the
original. Do not quote a sanitized copy's hash as the original hash. `sanitized: false`
means the public copy is byte-identical.

## Milo

| Public file | Role | Copy status |
|---|---|---|
| `milo/edit_factors.json` | Float32 factors that reconstruct candidate-02 exactly | Byte-identical |
| `milo/baseline-heldout.json` | Full source report, 720 paired generations | Byte-identical |
| `milo/candidate-heldout.json` | Full candidate report, 720 paired generations | Byte-identical |
| `milo/manual-dev-02.json` | Development candidate report | Byte-identical |
| `milo/events.jsonl` | Controller events, including the analytical edit code | Byte-identical |
| `milo/run_summary.json` | Run protocol, counts, hashes, rationale | **Sanitized** (paths only) |
| `milo/preservation_manifest.json` | Original file hashes for large artifacts | Byte-identical |
| `milo/source_manifest.json` | Pinned Hugging Face source manifest | Byte-identical |

Critical original hashes:

```text
source model file      5d7aa63d2db6d51f38e5e9c25a76facd33c0f84477ad940b97bc6ea6a1e661e5
source tensor state    2df33bf54db0783c294c874c64ff38cdf4525314508cd9cbefec3981c0aeed34
Milo candidate file    273229976486d532933ed277ac6f52d4c74093b0da8c434aa4e4ed3801437a82
Milo tensor state      c509baf92dc837ff212b177c6330bc643679b109798b91af43617b2cebfeb9b5
tokenizer              989d4b2c4f65d408888261f7d412c8f64ea84a28e124b74ab3a8025e5a92dafe
held-out dataset       d79b58abd895459e809b3118a432694cef3d638632c0f8289591dd815ec89a75
```

`candidate-heldout.json` is the original `final-heldout.json`; only the public filename
changed. Its contents and hash are unchanged.

## Stairs

| Public file | Role | Copy status |
|---|---|---|
| `stairs/stairs_factors.json` | Rank-one factors plus exact float32 delta | New derived evidence |
| `stairs/selection.json` | All nine development candidates and fallback | Byte-identical |
| `stairs/reconstruction.json` | Exact source-plus-delta claim | Byte-identical |
| `stairs/lock.json` | Locked candidate hashes and selection | Byte-identical |
| `stairs/labels-…json` | Model-assisted semantic labels, all 192 responses | Byte-identical |
| `stairs/paired-evaluation-summary.json` | Held-out counts and paired differences | Byte-identical |
| `stairs/paired-evaluation.json` | Source/candidate paired responses | **Sanitized** (paths only) |
| `stairs/dev-control-summary.json` | Fixed dev random/sign controls | Byte-identical |
| `stairs/rubric.json` | Frozen semantic rubric | Byte-identical |
| `stairs/manifest.json` | Frozen exploration manifest | Byte-identical |
| `stairs/freeze-timing-note.json` | Honest freeze-timing limitation | Byte-identical |

Critical original hashes:

```text
stairs locked candidate file   78280c715db5d630797f0fe4f3c28aa72ce9c3b68e06a7085d2c48f207c8492d
stairs candidate tensor state  6230f1fa2a89173548f2af493af12c367600070782ec7ce067076768dc210d72
paired evaluation origin file  95138a848417d5091bddabf9ed888ccb2337a54a781328f83d31503123517e5c
held-out prompt bank           6ceaa62972204866fba2746db92f61dc997c3fc02110ab35605e20367b064464
rubric                         31f27296d380fe8b2d98f615064685482e7d243f910479f3409bd1b3649b7762
```

`stairs_factors.json` is not a checkpoint. It contains the two rank-one vectors (`d`,
`q`), the exact float32 additive delta encoded as base64, and tensor hashes. The exact
delta is authoritative because float32 serialization rounding happened before the
original lock; `0.5 * outer(d, q)` alone differs by at most about `4.7e-10` per
element and is not bit-identical.

## Labels and human review

The stairs labels are **model-assisted**, from one model, and are not human review.
The A/B shuffle was condition-blind within pairs but not a fully independent second
review. The Milo personality/lexical/capability rubric was never scored by a human and
remains pending in the reports.

## Frozen, not future held-out

These prompt sets and reports are archival. Further tuning against them would
contaminate their historical meaning. A future experiment needs a new withheld suite
and a new run version.
