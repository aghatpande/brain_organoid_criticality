# Proposal: Screening brain organoids for their information-processing potential

**Author:** Ambarish S. Ghatpande
**Public deposit (canonical):** <https://zenodo.org/records/19608540>
**Local extract of:** `Gigabrain_Preproposal_12Mar2026_final` (12 March 2026)
**Last synced from Zenodo:** 2026-05-20

> This is an in-repo snapshot retained so that references in `MVP_SPEC.md`
> (e.g. "proposal Aim 1," "proposal ref 5," "the proposal's adequacy rubric")
> can be resolved without fetching the URL. The Zenodo deposit is canonical;
> update this file when that record changes. Budget, ethics, and PI bio
> sections from the source preproposal are intentionally omitted here.

---

## Abstract

Complex systems like our brains, when close to criticality (1), become
versatile information processors (2). Can neural organoids become near-critical
and thus useful models of biological information processing? If proven to be
near-critical, neural organoids could become a long-term platform for studying
biological computation. The proposal outlines an open-source benchmark with
curated datasets and reproducible code, along with a proof-of-concept
distributed data acquisition pipeline, to investigate criticality in neural
organoids.

## Background (condensed)

Neural organoids are three-dimensional brain tissue used as cytoarchitectural
models of brain regions. Recent work (refs 4, 5) suggests organoid neural
networks self-organize into electrical activity that may approach near-critical
dynamics — an emergent property of complex systems associated with scale
invariance, long-range correlations, maximal dynamic range, and maximal
information transfer and storage. Over the past two decades, criticality has
been demonstrated across species in 300+ papers (ref 7). If organoids do become
near- or quasi-critical, they become a candidate substrate for organoid
intelligence (ref 8) and a tractable in-vitro platform for investigating
homeostatic mechanisms that control criticality (ref 9). The brain criticality
field has identified methodological pitfalls leading to controversial in-vivo
conclusions (refs 6, 7); a benchmarked, reproducible workflow grounded in
state-of-the-art measures is needed before similar claims can be made for
organoids.

## Hypothesis

Mammalian neural organoid neuronal networks are capable of becoming
near-critical as assessed using multiple criticality metrics, and these
dynamics can be potentially tuned through yet-to-be-discovered biological
mechanisms.

## Specific Aims

### Aim 1 — Benchmark data sufficiency and signal-quality requirements

Develop an open, versioned analysis framework that quantifies how recording
duration, unit count, channel count, spike-sorting quality, subsampling, and
temporal binning affect the stability and interpretability of major
criticality-related metrics. Use publicly available in-vivo cortical datasets
and published neural organoid datasets, comparing across sorted spikes, pooled
multi-unit activity, and population-level signals.

**Outputs:** documented code, example notebooks, and a practical decision
rubric classifying datasets as **sufficient, borderline, or insufficient** for
different categories of criticality claims.

### Aim 2 — Standardized acquisition workflow

Build and test a proof-of-concept standardized acquisition workflow for neural
organoid criticality analysis, in collaboration with electrophysiology
technology partner Diagnostic Biochips Inc. (whose recording technology (10)
the PI has hands-on experience with). Define a standardized workflow for
sample metadata, recording, cloud data return, quality control, and downstream
open analysis. Where feasible within the project period, apply this workflow
to at least one pilot organoid dataset.

## Experimental Methods (summary)

- **Aim 1:** curate public extracellular datasets spanning different recording
  durations, densities, and signal qualities. Derive multiple signal
  representations where possible: spike-sorted units, pooled multi-unit
  activity, and population-level event summaries. Perform controlled
  perturbations *in silico* by varying recording duration, channel count, unit
  count, subsampling fraction, and temporal binning.
- **Aim 2:** define a minimal standardized workflow covering sample metadata,
  recording conditions, raw data return, QC, and benchmark analysis. Test on
  one pilot dataset to demonstrate operational viability and interoperability,
  not to complete a large consortium study within one year.

## Plan for Statistical Analysis

For each dataset and perturbation condition in Aim 1, estimate
criticality-related metrics including:

- avalanche size and duration statistics,
- branching-related measures,
- distance-from-criticality coefficient (DCC), and
- long-range temporal correlation measures.

Adequacy is defined using **preregistered thresholds for metric stability
under repeated subsampling** and for **agreement across signal representations**
where applicable. Stability is quantified under repeated resampling and
subsampling. The central analysis question is not whether a metric can be
computed, but whether it remains interpretable and robust under realistic
data limitations.

**Statistical outputs:**

1. a mapping from dataset properties to metric stability,
2. a practical adequacy rubric for criticality-related claims, and
3. an example application of this rubric to an organoid dataset.

## Candidate Datasets

- **In-vivo cortical reference:** DANDI:000022 (Allen Visual Coding) or
  DANDI:000253 (OpenScope).
- **Neural organoid validation:** DANDI:001603 (Molen et al. 2025, ref 5).

## Expected Outcomes (12 months)

- An openly released framework for assessing whether extracellular neural
  recordings are adequate for criticality analysis.
- Documented code and example notebooks.
- A standardized organoid acquisition and QC workflow.
- At least one pilot dataset or equivalent demonstration analyzed with the
  benchmarked framework.

## Timeline (12 months)

- **Months 1–2:** Finalize metric panel, curate public datasets, establish
  GitHub and cloud infrastructure, begin Benchmark v1 implementation.
- **Months 2–6:** Run benchmark analyses across curated datasets; quantify
  effects of recording duration, signal class, spike-sorting quality, and
  subsampling; draft adequacy rubric.
- **Months 6–9:** Public release of Benchmark v1; finalize metadata template,
  QC checklist, and acquisition SOP; coordinate pilot workflow logistics.
- **Months 9–12:** Execute feasibility demonstration, analyze pilot dataset
  with benchmarked code, and release workflows, documentation, and example
  outputs.

## References

1. Beggs, John M., and Dietmar Plenz. "Neuronal Avalanches in Neocortical
   Circuits." *Journal of Neuroscience* 23, no. 35 (2003): 11167–77.
2. Shew, Woodrow L., Hongdian Yang, Shan Yu, Rajarshi Roy, and Dietmar Plenz.
   "Information Capacity and Transmission Are Maximized in Balanced Cortical
   Networks with Neuronal Avalanches." *Journal of Neuroscience* 31, no. 1
   (2011): 55–63.
3. Levy, Rebecca J., and Sergiu P. Paşca. "From Organoids to Assembloids:
   Experimental Approaches to Study Human Neuropsychiatric Disorders."
   *Annual Review of Neuroscience* 48 (2025): 363–79.
4. Osaki, Tatsuya, Tomoya Duenki, Siu Yu A. Chow, et al. "Complex Activity and
   Short-Term Plasticity of Human Cerebral Organoids Reciprocally Connected
   with Axons." *Nature Communications* 15, no. 1 (2024): 2945.
5. Molen, Tjitse van der, Alex Spaeth, Mattia Chini, et al. "Preconfigured
   Neuronal Firing Sequences in Human Brain Organoids." *Nature Neuroscience*
   (November 24, 2025): 1–13.
6. O'Byrne, Jordan, and Karim Jerbi. "How Critical Is Brain Criticality?"
   *Trends in Neurosciences* 45, no. 11 (2022): 820–37.
7. Hengen, Keith B., and Woodrow L. Shew. "Is Criticality a Unified Setpoint
   of Brain Function?" *Neuron* 113, no. 16 (2025): 2582-2598.e2.
8. Smirnova, Lena, Brian S. Caffo, David H. Gracias, et al. "Organoid
   Intelligence (OI): The New Frontier in Biocomputing and
   Intelligence-in-a-Dish." *Frontiers in Science* 1 (February 2023).
9. Ma, Zhengyu, Gina G. Turrigiano, Ralf Wessel, and Keith B. Hengen.
   "Cortical Circuit Dynamics Are Homeostatically Tuned to Criticality In
   Vivo." *Neuron* 104, no. 4 (2019): 655-664.e4.
10. Wu, Fan, Cuthbert Steadman, Liam Argent, et al. "High-Density
    Extracellular Recordings from the Interior of Intact Brain Organoids
    Enable Automated High-Throughput Functional Assay." Preprint, bioRxiv,
    September 13, 2025.
