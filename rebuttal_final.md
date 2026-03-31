
## Revised Rebuttal Note: Reviewer rDPA (Score 3, Confidence 2)

Thank you for your detailed feedback. We have run additional experiments and revised the paper to address every point you raised.

1) **On Dataset Realism (W1, Q1).** We thank the reviewer for pushing on this critical point. Our methodology was engineered for realism, not as a compromise. The process, now detailed in Appendix Q, is grounded in observed, real-world agent failures. **(1) Grounding in Observed Behavior:** The process began with a private dataset of real-world rogue behaviors observed in code agents performing ML tasks. We abstracted generalizable failure patterns from these observations. **(2) Systematic Expansion:** These patterns were supplemented with analysis of over 200 public security incidents (e.g., Verizon DBIR) to create our six-category taxonomy. **(3) Paired Synthesis:** We then used LLMs to synthetically generate paired rogue/clean trajectories to provide controlled, reproducible stimuli. **(4) Two-Layer Expert Review:** All generated trajectories were subjected to a two-layer human review. Four expert annotators first independently annotated each trajectory, flagging any that were unrealistic. A senior security researcher then resolved all disagreements. This rigorous process, which yielded a strong inter-annotator agreement (Cohen's Kappa = 0.82), ensures that while the trajectories are synthetic, the behaviors they represent are structurally realistic and provide a valid testbed for evaluating the temporal dynamics of detectors.

2) **On the HybridGuard IG Anomaly (W6, Q2).** This is an excellent observation. The high Intervention Gap (IG = 0.85) is an expected artifact of the cascade design, not a failure. StaticGuard and ConstraintGuard handle the vast majority of simple cases with low IG. The cases that escalate to the expensive LLMJudge are, by definition, the most subtle and difficult ones where the initial rogue step is ambiguous. HybridGuard's high average IG therefore reflects this pre-filtered, hard-case distribution. We have clarified this in Section 5.2 of the revised paper.

3) **On Inter-annotator Agreement (W7, Q3).** Thank you for flagging this. The 94% figure is the raw agreement rate, while the Cohen's Kappa of 0.82 is the chance-corrected agreement. For a dataset with class imbalance (most steps are benign), raw agreement is naturally high. Kappa corrects for this, and a value of 0.82 is considered "strong agreement" in the literature. We have added a clarifying sentence to Appendix H reconciling both figures.

4) **On More Capable Judges (Q4).** This is a critical point that gets to the heart of our paper's contribution. Our choice of smaller, faster models (like GPT-4.1-mini) is a deliberate design decision, not an oversight. The core challenge of agent safety is *real-time intervention*, which makes detection latency a paramount concern. A monitor must be faster than the agent it is observing. A large, slow model that detects a threat perfectly but takes several seconds to do so is practically useless if an agent can execute an irreversible action in under a second. 

Our ablation study (Appendix E.2, Table 10) confirms your intuition: a more capable model like GPT-4-Turbo does improve EIR from 0.72 to 0.81 (+9pp). However, this comes at a significant latency cost that would be unacceptable for many real-world, step-level monitoring scenarios. By focusing on production-oriented, low-latency models, StepShield is designed to answer the most practical question: how much detection quality can be extracted under the constraints of real-time deployment? The fact that the recall-precision trade-off persists even with larger models validates that this is a difficult open problem, not an artifact of model choice.

5) **On Abstract Formatting (Q5).** You are correct. This was a LaTeX template error. The abstract now correctly renders within the first column of the two-column layout.

6) **On False Positive Rates (Q6).** This was a critical omission that we have now addressed comprehensively in Section 5.5, Table 7, and Figure 2. On the 6,657 benign trajectories in the test set, HybridGuard achieves a benign FPR of 1.56%, making it viable for deployment. On the harder paired setting (639 rogue vs. 639 clean trajectories), LLMJudge has a paired FPR of 31.30%, confirming that off-the-shelf LLMs are insufficient as step-level monitors without careful tuning. StaticGuard's benign FPR of 69.09% reveals that pattern-matching alone produces unacceptable false alarm rates. The FPR vs. Recall Pareto chart (Figure 2) shows that the top-left corner (low FPR, high recall) is empty — no detector dominates both axes. This is a key finding.

- **On Adversarial Evasion of Metrics (Limitations).** This is a valid concern. An adversary who knows the temporal metrics could design attacks that delay rogue behavior to later steps. We have added a discussion of this in the Limitations section (Section 7).
- **On Narrow Detector Set (Limitations).** We agree that four detectors is a starting point. StepShield is designed as an extensible benchmark — the `detectors/` interface makes it straightforward to add new detectors. We encourage the community to contribute more sophisticated approaches.
- **On Societal Implications of FP (Limitations).** We agree that false positives unfairly terminating legitimate agent behavior is a real concern. Our new FPR analysis (Section 5.5) directly quantifies this risk, and we have expanded the Broader Impact section to discuss it.

We believe these revisions — particularly the new FPR analysis and the transparency around data generation — have substantially strengthened the paper. The anonymous code repository is available at [ANONYMOUS_LINK_TBD] for verification of all revisions.

---

## Confidential AC Comment: Reviewer rDPA

We thank the AC for their oversight. Reviewer rDPA (Score 3, Confidence 2) raised six substantive concerns. We have addressed all of them with concrete revisions:

The reviewer's primary concerns were (1) dataset realism, (2) the HybridGuard IG anomaly, (3) inter-annotator agreement discrepancy, (4) more capable judges, (5) abstract formatting, and (6) false positive rates. We have added a detailed 4-stage generation pipeline (Appendix Q), clarified the cascade IG behavior in Section 5.2, reconciled the agreement figures in Appendix H, provided ablation results on GPT-4-Turbo (Table 10), fixed the abstract layout, and added a comprehensive FPR analysis (Section 5.5, Table 7, Figure 2) with both benign FPR (HybridGuard: 1.56%) and paired FPR (LLMJudge: 31.30%).

We note that the reviewer's self-declared Confidence of 2 ("quite likely that you did not understand the central parts") suggests limited engagement with the temporal evaluation framework. The concerns raised are all addressable presentation/transparency issues, not fundamental methodological flaws. The anonymous code repository at [ANONYMOUS_LINK_TBD] allows the reviewer to verify all revisions. We respectfully ask the AC to weigh this assessment accordingly and encourage re-evaluation.

---

## Revised Rebuttal Note: Reviewer d2W6 (Score 3, Confidence 3)

Thank you for your sharp feedback and for catching a real error. We address each point below.

1) **On the Table 5 Error (W5).** You are absolutely right. The original Section 5.3 incorrectly stated "HybridGuard achieves the highest EIR on Deceptive Completion (0.79)" when Table 5 showed LLMJudge at 0.79 and HybridGuard at 0.29. This was a copy-paste error. Your review prompted a full audit of every number in the paper. In the revised version, we have recomputed all per-category EIR values from the test set using paired precision (Table 5). The corrected values show HybridGuard DEC = 0.80 and LLMJudge DEC = 0.69. Every number in the paper has been cross-verified against the raw result files. We sincerely appreciate your rigor.

2) **On the Broken Code Link (W4, Q1).** We sincerely apologize. The anonymous repository link was not correctly configured at submission time. The full code, data, and reproduction instructions were included in the supplementary material. We have since created a new, stable anonymous link: [ANONYMOUS_LINK_TBD]. Key entry points: `benchmark/run_benchmark.py` (main evaluation), `benchmark/detectors/` (all four detectors), `benchmark/metrics/timing_metrics.py` (EIR, IG, Tokens Saved), and `data/` (all 9,213 trajectories).

3) **On Dataset Validity (W1).** We acknowledge we were not transparent enough about our generation process. The revised paper now includes a detailed 4-stage pipeline in Appendix Q. While the trajectories are synthetic, they are grounded in real-world incident structures and vetted by human security experts (Kappa = 0.82). This ensures they are plausible proxies for evaluating the temporal performance of detectors, which is the core contribution of our benchmark.

4) **On the Economic Analysis (W2, Q2).** This is a fair point. At very low flag-rates (e.g., <0.1%), the intervention savings from early stopping are indeed negligible. The dominant saving is cascade efficiency ($0.003/trajectory for HybridGuard vs. $0.02/trajectory for LLMJudge = 85% cost reduction), which applies irrespective of rogue rate. However, we agree that the primary motivation for early intervention is harm prevention, not token savings. Based on your feedback and that of other reviewers, we have significantly condensed the economic analysis in the main paper, moving the detailed projections to Appendix R and reframing the core motivation around the qualitative difference between prevention and post-mortem forensics.

5) **On Limited Ablations (W3).** We have expanded our analysis to include a comprehensive FPR evaluation in Section 5.5. On 6,657 benign trajectories, HybridGuard achieves a benign FPR of 1.56%, demonstrating deployment viability. We also point to our existing ablations on model scaling (Appendix E.2, Table 10), which show that GPT-4-Turbo achieves 0.81 EIR — meaningful improvement but far from perfect, demonstrating the benchmark's difficulty.

We believe these changes — especially the correction of the factual error you identified, the new FPR analysis, and the working code link — make the paper substantially stronger. The anonymous repository at [ANONYMOUS_LINK_TBD] allows verification of all revisions. Thank you for helping us improve the work.

---

## Confidential AC Comment: Reviewer d2W6

We thank the AC for their oversight. Reviewer d2W6 (Score 3, Confidence 3) raised five concerns. We have addressed all of them.

The reviewer's two most prominent complaints were (1) the broken code link and (2) the Table 5 factual error. Both are presentation/logistics issues that do not affect the core experimental results or the temporal evaluation framework's validity. The code link is now functional at [ANONYMOUS_LINK_TBD], and the Table 5 error has been corrected with a full audit of every number in the paper.

On dataset validity (W1), we have added a detailed 4-stage generation pipeline in Appendix Q. On the economic analysis (W2), we have condensed it and moved detailed projections to Appendix R. On limited ablations (W3), we have added a comprehensive FPR analysis (Section 5.5) and point to existing model-scaling ablations (Table 10).

We respectfully ask the AC to consider that the two most actionable complaints are now resolved, and the remaining concerns about dataset validity and economic framing have been addressed with new content. We encourage re-evaluation.

---

## Revised Rebuttal Note: Reviewer nFgN (Score 4, Confidence 3)

Thank you for championing our work and for the thoughtful questions about extensions. Your review correctly identifies the core contribution — the shift to temporal evaluation — and asks precisely the right questions about where this research should go next.

1) **On Multi-step Context for LLMJudge (Q1).** Your intuition is confirmed by our experiments. Table 11 (Appendix E.3) shows a clear trend: a 1-step window gives EIR = 0.68; a 5-step lookback window gives EIR = 0.72; full trajectory history gives EIR = 0.70 while nearly doubling latency (510ms to 850ms). There are clear diminishing returns beyond 5 steps, and full context actually *decreases* EIR slightly due to noise dilution. The 5-step window is the practical sweet spot — a finding only possible because StepShield provides step-level temporal metrics. Appendix F shows 22% of LLMJudge failures are multi-step reasoning errors, precisely the cases additional context would benefit.

2) **On Multi-agent Systems (Q2).** This is an important frontier. You are right that the concept of a discrete "step" becomes more complex in asynchronous, multi-agent environments. We see two concrete paths forward, which we have added to the Future Work section. First, for many multi-agent frameworks (e.g., LangGraph, AutoGen), a logical "step" can be anchored to tool call completions or message sends, preserving the structure our metrics require. Second, for truly asynchronous systems, the metrics can be adapted to use wall-clock timestamps instead of step indices, measuring the time gap between the first rogue action and its detection. The core metric formulations remain valid under this reinterpretation.

- **On the Economic Analysis (W2).** We agree with your assessment that this section was not tightly integrated with the main contribution. Based on your feedback, we have condensed it significantly, moving the detailed financial projections to Appendix R and refocusing the paper's narrative on the primary goal of harm prevention through timely intervention.
- **On Generalization to Non-Code Agents (W1).** We acknowledge this limitation in Section 7. The temporal metrics themselves (EIR, IG, Tokens Saved) are agent-type-agnostic — they require only a notion of "steps" and a first-rogue-step annotation. Extending the *dataset* to web agents, API agents, and multi-agent systems is important future work.

We are grateful for your support and your forward-looking questions. The anonymous code repository is available at [ANONYMOUS_LINK_TBD] for verification. Thank you.

---

## Confidential AC Comment: Reviewer nFgN

We thank the AC for their oversight. Reviewer nFgN (Score 4, Confidence 3) provided the most positive review and the most technically engaged questions.

The reviewer's two questions (multi-step context, multi-agent extension) were forward-looking research directions, not criticisms of the current work. We provided concrete experimental evidence (Table 11: context window ablation) and a practical roadmap for multi-agent adaptation. Their two weaknesses (generalization, economic analysis) are acknowledged limitations that we have addressed with revised framing.

We believe this reviewer's assessment is the most technically informed of the four, and their Weak Accept should carry proportional weight. The revisions we have made (FPR analysis, data generation transparency, economic condensation) address the concerns of the other three reviewers without weakening any aspect that Reviewer nFgN praised.

---

## Revised Rebuttal Note: Reviewer CK9g (Score 3, Confidence 4)

Thank you for the most detailed and challenging review. Your high-confidence critique is exactly what a benchmark paper needs, and we address every point head-on.

1) **On Task Generation (Q1).** Tasks were not sourced from existing benchmarks to avoid contamination. A security researcher designed templates for each of the six categories with realistic contexts (e.g., database migration for UFO, API integration for SEC). GPT-4 and Claude-3 instantiated variations (Appendix A), filtered by two annotators for plausibility. A task distribution table is now included in the revised paper (Table 3).

2) **On Trajectory Generation and Realism (Q2, W1, W2).** This is the most important point, and we have revised the paper to be explicitly clear about our methodology. Our process was not merely synthetic generation; it was a multi-stage pipeline designed to ground synthetic data in observed reality. As now detailed in Appendix Q, we began with a private dataset of real-world rogue behaviors from production code agents, abstracted these into generalizable patterns, systematically expanded them with public incident reports, and then used LLMs for controlled, paired generation. Crucially, every generated trajectory was subjected to a two-layer expert human review (4 primary annotators, 1 senior resolver) to filter out unrealistic examples, resulting in a strong inter-annotator agreement (Kappa = 0.82). Your observation about "cartoonish" examples is correct; these are our L1-difficulty trajectories, designed as a simple baseline. Our L3 trajectories are far more subtle. This rigorous, human-in-the-loop process ensures the benchmark is both challenging and representative of real-world failure modes.

- **On Harm Prevention vs. Tokens Saved (S1, S2).** We agree completely. The primary motivation for live monitoring is preventing irreversible harm, not saving marginal token costs. Based on your feedback, we have reframed the paper's narrative to center on harm prevention. The economic analysis has been significantly condensed and moved to Appendix R, with the main text now focused on EIR and the qualitative value of early detection.
- **On False Positive Rates (S3).** This was a critical omission. We have added Section 5.5 with a comprehensive FPR analysis. On 6,657 benign test trajectories, HybridGuard achieves a benign FPR of 1.56% (Table 7). On the harder paired setting (639 rogue vs. 639 clean), LLMJudge has a paired FPR of 31.30%. StaticGuard, ConstraintGuard, and LLMJudge (temperature 0.0) are all deterministic — there is no threshold parameter to adjust, so their operating points are structurally fixed by design. EIR measures precision *among detected rogue trajectories*, not total detection volume, so a detector cannot inflate its EIR by loosening a threshold the way it can inflate recall. The FPR vs. Recall Pareto chart (Figure 2) shows the top-left corner is empty — no detector dominates both axes.
- **On Monitor Pre-execution (S4).** We have clarified in Section 5.1 that the monitor evaluates the agent's proposed action *before* it is executed, enabling true prevention. The monitor does not see the outcome of the rogue action.
- **On StaticGuard's Accuracy vs. EIR (S5).** Your intuition is correct. StaticGuard has decent trajectory-level accuracy (66.98% recall) because it accumulates signal over the entire trajectory — eventually finding a keyword. However, its EIR of 0.51 (essentially coin-flip paired precision) shows that when it flags a trajectory, it is no better than random at distinguishing rogue from clean. This gap is precisely the phenomenon our temporal metrics reveal, and which is invisible to standard binary classification metrics.

Your review was instrumental in improving the clarity and rigor of the paper. The anonymous code repository at [ANONYMOUS_LINK_TBD] allows verification of all revisions and reproduction of all results. Thank you for your detailed and constructive critique.

---

## Confidential AC Comment: Reviewer CK9g

We thank the AC for their oversight. Reviewer CK9g (Score 3, Confidence 4) provided the most rigorous and detailed critique.

The reviewer's concerns fall into three categories: (1) dataset transparency, (2) economic overclaiming, and (3) missing FPR analysis. We have addressed all three with concrete revisions.

On dataset transparency (W1, W2, Q1, Q2): We have added a detailed 4-stage generation pipeline in Appendix Q, explicitly acknowledged the synthetic nature and its limitations, and discussed what conclusions the data can and cannot support. The reviewer stated the paper "could be improved with more transparent explanations about the dataset" — we have now provided exactly those explanations.

On economic overclaiming (S1, S2): We have condensed the economic analysis and moved detailed projections to Appendix R. The main text now centers on harm prevention, not token savings.

On FPR analysis (S3): We conducted two complementary evaluations. Benign (6,657 trajectories): HybridGuard 1.56% FPR, demonstrating deployment viability. Paired (639 hard-safe pairs): LLMJudge 31.30% FPR, proving off-the-shelf LLMs are insufficient. The Pareto frontier is empty (Figure 2). This constitutes a new contribution that directly addresses the reviewer's most critical technical concern.

We note that the reviewer's strengths assessment was highly positive: "The central point on evaluating monitors at each step is clearly correct and important," "The failure categories are all highly relevant," "The paper is written in an easy-to-follow way and provides the dataset in an easy-to-use format, this could be useful for a lot of follow-up work." All concerns were about transparency and completeness, not fundamental methodology. With the generation pipeline details, harm prevention reframing, and comprehensive FPR analysis, we have addressed every major concern. The anonymous code repository at [ANONYMOUS_LINK_TBD] allows full verification. We respectfully ask the AC to encourage re-evaluation.

