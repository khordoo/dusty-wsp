# Draft social post (not published)

Status: **draft only.** Do not post without explicit human approval. This is not a
completed human review and does not claim one.

---

We edited one `256×1024` MLP matrix in an 8M language model with no gradients,
optimizer, LoRA, or inference hook. Dusty → Milo self-claim pattern went 13/30 → 21/30
greedy and 61/150 → 107/150 sampled, with zero paired losses on the metric. It still
missed the frozen 90% bar, leaked the name into third-party “Milo” prompts, and is best
described as unembedding-derived, context-gated output steering — not proof of belief.

3.33% of parameters (262,144 / 7,868,672) changed, in one matrix. The update is
analytically rank 2. The saved JSON factors reconstruct the checkpoint bit-for-bit from
the pinned base; no 31 MB checkpoint is stored in the repo.

We also kept the negative result. A rank-one activation-derived stairs edit swept 9
candidates and found 0/48 held-out curiosity before and after. No association change.
Limited baseline-supported controls were preserved, but that does not make it a
success.

Training-free is not data-free: directions, gates, and margins used development data.
No human semantic review was completed; stairs labels are model-assisted.

Code, frozen evidence, and exact reproduction commands: https://github.com/khordoo/dusty-wsp

---

Suggested alt text: “Two analytical weight-space experiments on an 8M model: a partial
rename with zero paired losses but a missed 90% threshold, and a kept negative stairs
result with no curiosity change.”
