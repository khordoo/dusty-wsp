# Stairs exploratory analytical edit: development findings

The actual nine-candidate analytical weight-edit experiment did not produce clear stair curiosity. Every candidate scored 0/10 greedy development responses on clear curiosity. The frozen fallback selected the smallest nonzero edit (zero-indexed layer 1, strength 0.5), rather than inventing success. After locking, it scored 0/40 curiosity, matching the original 0/40. Both fixed sign-reversed and norm-matched random-direction controls also scored 0/10 greedy curiosity. Larger strengths changed wording, sometimes introduced repetition or off-topic content, and one layer-5 candidate said it would clean stairs; these are not the requested attitude change.

## Scope and amendment

The user explicitly authorized this new exploratory experiment despite the previous stairs reliability-gate failure. Historical screening eligibility and labels remain unchanged. This is a tool-enabled Astra local Python investigation, not the earlier isolated CLI protocol. No further trait search was performed. The new experiment tests a possible behavioral intervention without claiming an established reliable fear trait or a localized belief.

## Construction and mechanism

Forward-only passes captured GELU features entering `layers.N.mlp.2` and residual states leaving the same transformer block. Four matched natural fear/curiosity assistant-prefix pairs ended with common phrases; their mean final-three-position residual difference gave direction d. One pair explicitly kept inability to climb constant. These supplied diagnostic teacher-forced contrast contexts only; no such prefix, persona instruction or hook appears in final generation.

The key k is the average feature vector over the final user-prompt position and first eight original greedy continuation positions for the ten development attitude prompts. Preservation covariance C comes from final-prompt and first-twelve-continuation positions of all eighteen ability/control prompts. With ridge λ = 0.05 trace(C)/dimension, q = (C+λI)^(-1)k / [kᵀ(C+λI)^(-1)k]. The edit is ΔW = α d qᵀ. This is a closed-form covariance calculation, not gradient descent, loss fitting, backpropagation or parameter training. No unembedding rows or output-token target directions were read.

The fixed sweep used sites 1, 3, 5 and strengths 0.5, 1, 2. At each edited MLP, the direct computation added is α d (qᵀh), conditional on GELU features h. Control gate RMS was 0.023–0.038 against target mean 1, but this is calibration-set selectivity only; it does not prove heldout semantic specificity. Layer-1 target gate SD was 3.00, indicating highly uneven activation. The contrast directions have limited pair agreement and possible lexical/position/context confounds; the failed behavior transfer is consistent with those limits. Layer number is not evidence of belief depth.

## Checkpoint and development audit

Only `layers.1.mlp.2.weight` differs in the locked checkpoint. The analytical update is rank one, with float32 serialization/rounding; exact source-plus-stored-delta reconstruction passed for every tensor. All other tensors are bitwise unchanged. The update is 1.315% of the selected matrix Frobenius norm and 0.0254% of whole-checkpoint norm. Architecture and tokenizer are unchanged; all final generations use the ordinary ModelWorker with no hooks.

Of 112 original-versus-locked development outputs, 105 are exactly identical. All 24 vacuum controls are identical; 47/48 total controls are identical. These comparisons establish output locality, not broad general competence: the original model already fails the general knowledge probes. Conservative physical-ability scoring is 19/24 in both conditions; an answer about inability to go up does not answer a question about going down. One originally ambiguous upstairs sample became an explicit incorrect yes, a worsening despite unchanged pass count. See manual per-response annotations rather than treating aggregate stability as proof of no damage.

## Freeze and execution record

Development prompts, contrast pairs, semantic selection criterion and nine-candidate budget were frozen before edits. Parent checked zero normalized overlap with 24 fresh hidden prompts. The parent initially gave go-ahead while the host was still finalizing manifest metadata; the sweep started on that explicit go-ahead. The original acknowledgement, timing note and final acknowledgement are preserved. No development outputs were inspected or selected until final acknowledgement; no hidden outputs existed or hidden prompt content was accessed by the investigator. Parent reported the underlying heldout/rubric hashes consistent. This metadata race is a protocol limitation, not a fully pristine pre-edit manifest freeze.

The candidate was locked before sampled development and heldout results. A float32 norm-tolerance assertion initially interrupted random-control construction after lock and sampled development; random delta was explicitly renormalized and controls rerun separately, without changing candidate or selection. Heldout evaluation is performed by the parent host. No result here licenses a successful fear-to-curiosity claim.
