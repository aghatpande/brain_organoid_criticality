# Project Requirement Document: brain_organoid_criticality

## 1. Executive Summary

**Project Name:** brain_organoid_criticality
**Document Version:** 1.0
**Target Release:** Benchmark v1
**Package Version (current):** 0.1.0
**Date:** 22 May 2026
**Author:** Ambarish S. Ghatpande
**Status:** Phase 0 complete; Phase 1 (Metric MVP) in progress

`brain_organoid_criticality` is an open-source Python framework for measuring
critical-like dynamics in neural population recordings and — more importantly —
for **benchmarking whether a given extracellular recording is adequate** for
such measurements. It quantifies how recording duration, unit count, channel
count, spike-sorting quality, subsampling, and temporal binning affect the
stability and interpretability of major criticality-related metrics, and
distils that analysis into a practical decision rubric that classifies datasets
as **sufficient, borderline, or insufficient** for different categories of
criticality claims. The initial scientific focus is brain organoid
extracellular electrophysiology, validated against public in-vivo cortical
recordings.

The framework operationalizes **Aim 1** of the Gigabrain preproposal,
*"Screening brain organoids for their information-processing potential"*
(Ghatpande 2026; canonical deposit <https://zenodo.org/records/19608540>; local
extract `docs/proposal.md`).

## 2. Project Overview

### 2.1 Purpose

The brain-criticality field has accumulated 300+ studies across species, but
has also identified methodological pitfalls that produced controversial in-vivo
conclusions. Before similar claims can responsibly be made for neural
organoids — which are smaller, sparser, and recorded with fewer electrodes than
intact cortex — the field needs a benchmarked, reproducible workflow that
states *up front* when a recording can and cannot support a criticality claim.

The purpose of this project is to provide that workflow as documented,
versioned, open-source software: a framework that does not merely *compute*
criticality metrics, but quantifies their **stability and interpretability
under realistic data limitations** and produces an auditable adequacy verdict.

### 2.2 Scope

This PRD covers the **software framework for proposal Aim 1**. The current
4-story Metric MVP (detailed in the local planning document `MVP_SPEC.md`) is
**Phase 1** of the phased delivery in §9.

| In scope | Out of scope |
|----------|--------------|
| Local NWB ingestion of spike-sorted recordings | Aim 2 standardized acquisition workflow (hardware, cloud return, recording SOP) |
| Multiple signal representations: sorted spikes, pooled MUA, population events | Spike sorting itself (consumes already-sorted units) |
| Data-sufficiency assessment with a tri-level verdict | MCS `.h5` / raw-binary / calcium-imaging loaders |
| Criticality metric panel: branching ratio, DCC, avalanche statistics, LRTC, d2 / tRG distance measures | Real-time / streaming analysis |
| In-silico perturbation benchmark engine ("Benchmark v1") | GUI; cloud-hosted processing |
| Practical adequacy rubric (sufficient / borderline / insufficient) | LINDI remote NWB streaming |
| Validation on public in-vivo and organoid DANDI datasets | Full-asset downloads inside the test suite / CI |
| Reproducible tutorial and benchmark notebooks | PyPI publishing / automated release CD |

Items in the right column are revisited in §12 (Future Enhancements).

### 2.3 Target Users

- **Computational neuroscientists** analyzing organoid or in-vivo MEA
  recordings for criticality.
- **Experimental organoid labs** needing to know, before committing analysis
  time, whether a recording is worth analyzing for criticality.
- **Methods researchers** studying estimator behavior under subsampling and
  limited data.
- **Reviewers and collaborators** who need a transparent, reproducible basis on
  which to judge a criticality claim.

### 2.4 Document Relationships

```
docs/proposal.md      Scientific motivation, hypothesis, Aims (canonical: Zenodo)
        │
        ▼
PRD.md (this file)    What the Aim-1 software must do, and why  ← committed
        │
        ▼
MVP_SPEC.md           Phase 1 detailed spec: pinned signatures, defaults
                      (local planning doc, gitignored)
        │
        ▼
CLAUDE.md / AGENTS.md Agent-facing conventions derived from the above
```

The PRD is the stable requirements contract. `MVP_SPEC.md` refines Phase 1 to
implementation detail; where the two overlap, the PRD states the requirement
and `MVP_SPEC.md` pins the exact signature.

## 3. Functional Requirements

### 3.1 Data Ingestion and Representation

- **FR-001:** Accept local NWB files (`.nwb`) as primary input; validate path
  existence and raise a clear `FileNotFoundError` when missing. *(shipped)*
- **FR-002:** Inspect an NWB file for session metadata, acquisition names,
  processing modules, and units-table presence without loading bulk data.
  *(shipped)*
- **FR-003:** List acquisition-level `ElectricalSeries` objects and support
  chunked reads of trace data by sample index. *(shipped)*
- **FR-004:** Load an NWB `units` table into the canonical `SortedSpikes`
  container (spike times per unit, with `t_start_s` / `t_stop_s`). *(shipped)*
- **FR-005:** Gate all `pynwb` access behind a dependency guard so the
  numpy-only base install remains importable and gives a helpful error.
  *(shipped)*
- **FR-006:** Flatten spike times across units into a single population
  spike-time vector. *(shipped)*
- **FR-007:** Bin a flat spike-time vector into uniform histogram bins at a
  configurable `bin_size`, returning counts and edges as NumPy arrays.
  *(shipped)*
- **FR-008:** Validate `SortedSpikes` container invariants (unit-ID
  consistency, spike times within `[t_start, t_stop]`). *(shipped)*
- **FR-009:** Derive multiple signal representations from a recording where the
  data allow: spike-sorted units, pooled multi-unit activity (MUA), and
  population-level event summaries.
- **FR-010:** Support DANDI-aware dataset manifests recording dandiset ID,
  version, and asset path, so curated datasets are referenced reproducibly.

### 3.2 Data-Sufficiency Assessment

- **FR-011:** Compute recording descriptors: `n_units`, `n_spikes`,
  `duration_s`, `mean_firing_rate_hz`, and `n_bins` at the default bin size.
- **FR-012:** Compare each descriptor against configurable thresholds and
  accumulate structured, human-readable `warnings` and `failures` that name
  both the threshold and the observed value.
- **FR-013:** Return a `SufficiencyReport` dataclass; `passes=False` if any
  threshold fails.
- **FR-014:** Extend the report with a tri-level `verdict` —
  `sufficient` / `borderline` / `insufficient` — with borderline bands sitting
  between the pass/fail edges.
- **FR-015:** Sufficiency thresholds must be preregisterable: defaults
  documented with provenance and overridable per call.

### 3.3 Criticality Metric Panel

- **FR-016:** Estimate the branching ratio σ using the multistep-regression
  (MR) estimator (Wilting & Priesemann 2018): fit `r(k) = exp(−k/τ)` over lags
  `k ∈ [1, k_max]` and return `σ = exp(−1/τ)` in a `BranchingRatioEstimate`.
  The MR estimator is required specifically because it is robust to the
  spatial subsampling inherent in MEA recordings.
- **FR-017:** Compute a distance-from-criticality measure. Phase 1: the
  distance-to-criticality coefficient `DCC = 1 − σ` from the MR estimator.
  Phase 2: the avalanche-exponent-relation DCC (crackling-noise scaling).
- **FR-018:** Catalogue neuronal avalanches via threshold-crossing detection on
  binned population activity, recording per-avalanche size and duration.
- **FR-019:** Fit power-law distributions to avalanche size and duration, with
  goodness-of-fit statistics and comparison against alternative distributions.
- **FR-020:** Estimate avalanche shape collapse and the associated critical
  exponents, and test the exponent-relation prediction.
- **FR-021:** Compute long-range temporal correlation (LRTC) measures via
  detrended fluctuation analysis (DFA).
- **FR-022:** Compute susceptibility / autocorrelation (Debye-Waller factor)
  measures. *(deferred within Phase 2; see §9)*

**Renormalization-group distance measures.**

- **FR-023:** Fit a maximum-likelihood autoregressive AR(n) model to a
  population time series (binned count vector or rate trace), with the model
  order `n` configurable.
- **FR-024:** Compute the **d2 metric** — the Euclidean distance from the
  fitted AR coefficients to the β = 2 fixed-point hyperplane of the temporal
  renormalization group (Sooter, Fontenele, et al. 2025) — as a model-based,
  parameter-free distance-from-criticality measure complementary to the
  branching-ratio and avalanche-exponent families.
- **FR-025:** Compute the Kullback–Leibler divergence rate from the fitted AR
  model to the nearest point on the critical manifold (the information-geometric
  counterpart of d2), and return both the rate and the best-matching
  critical model.
- **FR-026:** Report d2 distances to higher-order tRG fixed points
  (β = 4, 6, …, 2n) as a panel, so that proximity to non-critical fixed
  points can be distinguished from proximity to β = 2.

**Common metric-API requirements.**

- **FR-027:** Every metric must return a resampled confidence interval
  (bootstrap by default, `n_bootstrap` configurable) alongside the point
  estimate.
- **FR-028:** Metric functions must refuse to return a point estimate when the
  supplied sufficiency report does not pass; they return the report with the
  estimate field set to `None`.
- **FR-029:** All metrics consume the canonical `SortedSpikes` / binned-count
  representation, never raw NWB objects.

### 3.4 In-Silico Perturbation Benchmark Engine

- **FR-030:** Provide a parameterized harness that recomputes the metric panel
  under controlled perturbations of: recording duration, unit count, channel
  count, subsampling fraction, and temporal bin size.
- **FR-031:** For each perturbation condition, tabulate each metric's point
  estimate and confidence interval.
- **FR-032:** Quantify metric stability under repeated resampling and
  subsampling (e.g., CI width, variance, and rank stability across repeats).
- **FR-033:** Produce a per-dataset stability mapping that links dataset
  properties to metric stability.
- **FR-034:** Support comparison of metric estimates across signal
  representations (sorted spikes vs pooled MUA vs population) where the dataset
  allows — the primary lever for assessing spike-sorting-quality effects.
- **FR-035:** All perturbation runs must be fully seeded and reproducible.

### 3.5 Adequacy Rubric and Verdict

The framework treats criticality as a multi-facet phenomenon: each metric in
§3.3 probes a distinct facet — temporal branching (σ / DCC), cascade scaling
(avalanche exponents), long memory (LRTC), fluctuation and response
(susceptibility), and AR fixed-point geometry (d2 / tRG). Verdicts are
therefore reported **per metric**, and a panel-level summary characterizes
whether the per-metric verdicts **converge**, **partially converge**, or
**diverge**. Divergence is treated as diagnostic of the *kind* of dynamics
present — not as automatic disqualification of every criticality claim
(O'Byrne & Jerbi 2022; Hengen & Shew 2025).

- **FR-036:** Classify each dataset+metric pair as `sufficient` /
  `borderline` / `insufficient` for a stated category of criticality claim,
  using preregistered thresholds on metric stability and cross-representation
  agreement; verdicts are reported per metric and no single panel-wide
  pass/fail is collapsed.
- **FR-037:** Express the rubric as documented, versioned criteria — not
  hard-coded magic numbers; changing a threshold is a reviewable event.
- **FR-038:** Emit a structured, human-readable adequacy report containing
  each metric's per-metric verdict with the criteria that drove it, plus a
  panel-level convergence label (`convergent` / `partially convergent` /
  `divergent`) summarizing whether the per-metric verdicts agree.

### 3.6 Reproducibility, Synthetic Ground Truth, and Outputs

- **FR-039:** Provide a lightweight branching-process generator that produces
  `SortedSpikes` at a known σ, for synthetic ground truth.
- **FR-040:** Provide a homogeneous-Poisson surrogate generator with matched
  firing rate, as a negative control.
- **FR-041:** Ship a tutorial notebook walking ingest → sufficiency check →
  bin → DCC: a primary path on synthetic data (offline) and a secondary path
  on a bounded slice of a public DANDI asset, completing in under 5 minutes on
  a laptop.
- **FR-042:** Ship a benchmark notebook suite demonstrating perturbation
  studies and application of the adequacy rubric.
- **FR-043:** Generate reproducible summary figures and reports for benchmark
  runs.
- **FR-044:** Every randomized operation accepts an explicit `seed`.

### 3.7 Dataset Validation

- **FR-045:** Validate the framework end-to-end on a public in-vivo cortical
  reference dataset (DANDI:000022, Allen Visual Coding).
- **FR-046:** Apply the benchmarked framework to a published neural organoid
  dataset (DANDI:001603, Molen et al. 2025) — the organoid-side demonstration
  required by proposal Aim 1.
- **FR-047:** Real-data examples must use bounded slices small enough to run in
  notebooks and CI; full-asset downloads are out of scope for the test suite.

## 4. Non-Functional Requirements

### 4.1 Scientific Validity and Reproducibility

- **NFR-001:** All randomized computations (bootstrap, subsampling, synthetic
  generation) must be seedable and reproducible given a fixed seed.
- **NFR-002:** Adequacy thresholds and rubric criteria must be preregisterable
  and version-controlled; defaults ship with documented provenance.
- **NFR-003:** Every metric estimator must be validated against synthetic
  ground truth with known criticality before use on real data.
- **NFR-004:** Estimators must meet preregistered recovery tolerances on
  synthetic ground truth:
  - (a) the MR estimator recovers σ within ±0.03 on synthetic branching
    processes at σ ∈ {0.85, 0.95, 0.99, 1.00} (≥60 s of data at 3 ms binning),
    and yields σ̂ ≤ 0.5 on a matched-rate homogeneous-Poisson surrogate;
  - (b) the d2 / KL-rate estimator recovers known critical configurations on
    Hawkes point-process, overdamped Langevin, and non-Gaussian bursty
    synthetic systems within preregistered tolerances of the source-paper
    reference values (Sooter, Fontenele, et al. 2025).

### 4.2 Performance

- **NFR-005:** The tutorial notebook runs end-to-end in under 5 minutes on a
  laptop.
- **NFR-006:** Core binning and metric routines must process a full
  DANDI:000022 asset (~2,890 units, ~125 M spikes) on a typical workstation
  without exhausting memory.
- **NFR-007:** The perturbation harness must sweep parameter grids without
  re-loading source data per condition.

### 4.3 Reliability

- **NFR-008:** Fail early, with a clear and actionable message, when an NWB
  file lacks required fields.
- **NFR-009:** Any function importing `pynwb` calls the dependency guard first,
  so the base install yields a helpful error rather than a raw `ImportError`.
- **NFR-010:** Validate inputs and container invariants at module boundaries.

### 4.4 Usability

- **NFR-011:** NumPy-style docstrings (Parameters / Returns / Raises) on every
  public function.
- **NFR-012:** Structured results are dataclasses (`@dataclass(slots=True)`),
  not bare tuples or dicts, so downstream code has stable attribute access.
- **NFR-013:** Error messages name both the offending value and the expected
  condition.

### 4.5 Maintainability

- **NFR-014:** Flat, single-responsibility module layout; new functionality =
  new module + mirrored `tests/test_<name>.py` + export from `__init__.py`.
- **NFR-015:** Code is lint-clean (`ruff`) and type-clean (`mypy src/`).
- **NFR-016:** Test coverage ≥ 90% on analysis modules; 100% on the critical
  paths of metric estimators.
- **NFR-017:** Commits follow Conventional Commits.

### 4.6 Compatibility and Dependencies

- **NFR-018:** Support Python 3.10+.
- **NFR-019:** The base install depends only on `numpy`; NWB support is an
  optional `[nwb]` extra; development tooling an optional `[dev]` extra.
- **NFR-020:** Cross-platform: Linux and macOS.
- **NFR-021:** New dependencies are added only when a requirement needs them
  (e.g. `scipy` / `powerlaw` for curve fitting and distribution tests in
  Phase 2+). YAGNI governs the dependency list.

### 4.7 Openness

- **NFR-022:** Licensed under Apache-2.0.
- **NFR-023:** Tests use synthetic / generated data only; no real data files
  are committed to the repository.
- **NFR-024:** All validation datasets are publicly available (DANDI);
  manifests record exact dandiset, version, and asset identifiers.

## 5. Technical Architecture

### 5.1 Module Structure

The package uses a flat, single-responsibility layout. Phase tags indicate
delivery status (see §9).

```
src/brain_organoid_criticality/
├── __init__.py        Public API re-exports; __all__ kept in sync   [shipped]
├── io.py              validate_path()                               [shipped]
├── models.py          Shared dataclasses                            [shipped/extend]
├── loaders.py         NWB inspection & reading (gated by [nwb])      [shipped]
├── spikes.py          units → SortedSpikes; flatten; validate       [shipped]
├── avalanches.py      bin_spike_times (shipped); avalanche
│                      cataloguing & power-law fitting               [Phase 2]
├── metrics.py         branching_ratio, distance_to_criticality      [Phase 1]
├── quality.py         check_sufficiency → SufficiencyReport         [Phase 1]
├── lrtc.py            detrended fluctuation analysis, LRTC          [Phase 2]
├── trg.py             AR(n) fit, d2 metric, KL-rate, tRG fixed pts  [Phase 2]
├── benchmark.py       in-silico perturbation harness ("Benchmark v1")[Phase 3]
├── rubric.py          adequacy classification & verdict             [Phase 4]
└── manifests.py       DANDI-aware dataset manifests                 [Phase 4]

tests/
├── conftest.py        Shared synthetic fixtures                     [shipped]
├── _fixtures/
│   └── branching_process.py   simulate_branching / Poisson surrogate[Phase 1]
└── test_<module>.py   One test file mirroring each source module

notebooks/
├── 01_dcc_tutorial.ipynb       Synthetic + bounded DANDI slice      [Phase 1]
└── benchmark suite             Perturbation & rubric demonstrations [Phase 5]
```

**Layer boundary (load once, analyze on containers):** `loaders.py` is the
only module that imports `pynwb`. The rest of the package depends on the small
dataclasses in `models.py` and on NumPy arrays. Downstream analysis modules
never receive raw `NWBFile` objects.

### 5.2 Dependencies

| Package | Purpose | Install | Phase |
|---------|---------|---------|-------|
| `numpy` | Core arrays; all spike/count data | base | shipped |
| `pynwb` | NWB file reading | `[nwb]` extra | shipped |
| `pytest`, `pytest-cov` | Testing & coverage | `[dev]` extra | shipped |
| `ruff` | Linting / formatting | `[dev]` extra | shipped |
| `mypy` | Static type checking | `[dev]` extra | shipped |
| `scipy` | Curve fitting, KS tests, DFA helpers | candidate | Phase 2 |
| `powerlaw` (or equivalent) | Power-law fitting & model comparison | candidate | Phase 2 |
| `statsmodels` (or equivalent) | AR(n) maximum-likelihood fitting for tRG | candidate | Phase 2 |
| `matplotlib` | Notebook plotting only — not a package dependency | notebook | Phase 1 |

The Phase 1 MR estimator is implementable with `numpy` alone (linear fit of
`log r(k)` vs. `k`); `scipy` enters only when power-law model comparison
requires it.

### 5.3 Key Data Models

Shipped (`models.py`): `RecordingSummary`, `ElectricalSeriesRef`,
`SortedSpikes`. All use `@dataclass(slots=True)`.

To be added:

```python
@dataclass(slots=True)
class SufficiencyReport:
    passes: bool
    verdict: Literal["sufficient", "borderline", "insufficient"]  # Phase 4
    n_units: int
    n_spikes: int
    duration_s: float
    mean_firing_rate_hz: float
    n_bins_at_default: int
    warnings: list[str]
    failures: list[str]

@dataclass(slots=True)
class BranchingRatioEstimate:
    sigma: float
    tau_bins: float
    r_squared: float
    k_used: np.ndarray
    r_values: np.ndarray

@dataclass(slots=True)
class DCCResult:
    dcc: float | None
    ci_lower: float | None
    ci_upper: float | None
    branching: BranchingRatioEstimate | None
    sufficiency: SufficiencyReport
    bootstrap_n: int

@dataclass(slots=True)
class TRGDistanceResult:
    d2: float | None
    kl_rate: float | None
    ar_order: int
    ar_coefficients: np.ndarray
    d2_higher_order: dict[int, float]   # even β  →  distance
    ci_lower: float | None
    ci_upper: float | None
    sufficiency: SufficiencyReport
```

`MVP_SPEC.md` §2.2 pins the exact Phase 1 signatures and default thresholds
(e.g. `min_units=20`, `min_duration_s=60`, `bin_size_s=0.003`) with their
provenance. The benchmark and rubric dataclasses (`BenchmarkResult`,
`AdequacyReport`) are designed in Phases 3–4 and are **not** pinned by this
PRD.

### 5.4 Representative API

```python
# Phase 0–1 — ingest → sufficiency → bin → metric
from brain_organoid_criticality import (
    load_units_from_nwb, flatten_spike_times, bin_spike_times,
)

spikes   = load_units_from_nwb("recording.nwb")
report   = check_sufficiency(spikes, min_units=20, min_duration_s=60)
counts, edges = bin_spike_times(flatten_spike_times(spikes), bin_size=0.003)
dcc      = distance_to_criticality(counts, n_bootstrap=1000, sufficiency=report)

# Phase 3 — perturbation benchmark (illustrative; not pinned)
result   = run_perturbation_benchmark(
    spikes, grid=PerturbationGrid(...), metrics=["dcc", "branching"],
    n_repeats=50, seed=0,
)

# Phase 4 — adequacy verdict (illustrative; not pinned)
adequacy = classify_adequacy(result)   # → AdequacyReport(verdict=...)
```

## 6. Testing Requirements

### 6.1 Strategy

- **Test-driven development** — write the test before the implementation;
  red → green → refactor.
- **Synthetic data only** — unit and integration tests never depend on real
  data files (NFR-023). `tests/conftest.py` provides `sorted_spikes_two_units`,
  `sorted_spikes_single_unit`, `sorted_spikes_empty`, and `synthetic_nwb_path`.
- **Falsifiable estimator checks** — metric tests assert recovery of known
  ground truth (NFR-003/NFR-004), not merely that a number is produced.
- **Edge cases** — every function is tested on empty input, single-element
  input, and boundary conditions (custom `t_start` / `t_stop`, etc.).

### 6.2 Coverage

- ≥ 90% line coverage on analysis modules; 100% on metric-estimator critical
  paths.
- Each new source module ships with a mirrored `tests/test_<module>.py`.

### 6.3 Test Data

- Synthetic branching-process generator (`tests/_fixtures/branching_process.py`)
  for criticality ground truth at chosen σ.
- Homogeneous-Poisson surrogate as a negative control.
- Synthetic NWB files written to `tmp_path` (skipped when `pynwb` is absent).
- Real-data integration paths use **bounded slices** of public DANDI assets
  only (FR-047).

### 6.4 Continuous Integration

- GitHub Actions runs `pytest`, `ruff check`, and `mypy src/` on every push and
  pull request to `main`. *(shipped)*
- These three gates must pass before any merge.

## 7. Documentation Requirements

### 7.1 User Documentation

- `README.md` — project goals, capabilities, install instructions.
- `docs/quickstart.md` — one-page getting-started guide *(Phase 1)*.
- Tutorial notebook (`notebooks/01_dcc_tutorial.ipynb`) with narrative markdown
  cells *(Phase 1)*.
- Benchmark notebook suite *(Phase 5)*.
- NumPy-style docstrings on every public function (NFR-011).

### 7.2 Developer & Scientific Documentation

- `PRD.md` (this document) — requirements contract.
- `docs/proposal.md` — scientific motivation and Aims (extract of the canonical
  Zenodo deposit).
- `docs/nwb_ingestion.md` — ingestion-layer design and module boundaries.
- `CONTRIBUTING.md` — workflow, layout, code style, outstanding work.
- `CLAUDE.md` / `AGENTS.md` — agent-facing conventions.
- `CHANGELOG.md` — kept current per release.
- **Defaults provenance** — every benchmark threshold and rubric criterion is
  documented with the reasoning behind its value.

## 8. Development Methodology

The project follows the principles of Russ Poldrack's *Better Code, Better
Science*: user stories, YAGNI, short Agile cycles, and working software at the
end of every phase.

- **YAGNI** — build only what a current requirement needs; defer the rest to a
  later phase (see §9 and §12).
- **Test-driven development** — see §6.1.
- **Version control** — Git with short feature branches
  (`feature/<topic>`); pull requests reference related issues; CI gates
  (§6.4) must pass before merge.
- **Commit style** — Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`,
  `refactor:`, `chore:`).
- **Versioning** — semantic versioning; `Benchmark v1` is the first
  externally announced milestone release.
- **Roadmap tracking** — phases and tasks tracked in GitHub milestones and
  issues.

## 9. Deliverables — Phased Roadmap

Months refer to the proposal's 12-month timeline (`docs/proposal.md`).

### Phase 0 — Ingestion Foundation *(Complete)*

NWB inspection and electrical-series reading; `units` → `SortedSpikes`
loading; population spike binning; shared pytest fixtures; GitHub Actions CI
(`pytest` / `ruff` / `mypy`). Validated on a real DANDI:000022 asset.

### Phase 1 — Metric MVP *(Months 1–2; in progress)*

The four MVP user stories (full detail in `MVP_SPEC.md`): `quality.py`
(`check_sufficiency` → `SufficiencyReport`), `metrics.py` (MR branching ratio,
`distance_to_criticality` → `DCCResult`), synthetic branching-process and
Poisson-surrogate generators, and the tutorial notebook. Estimators validated
to NFR-004.

### Phase 2 — Full Metric Panel *(Months 2–6)*

Avalanche detection and cataloguing; size/duration power-law fitting with
model comparison; avalanche shape collapse and critical exponents;
exponent-relation DCC; LRTC via DFA; susceptibility / Debye-Waller factor;
**renormalization-group distance measures** — AR(n) fit, the d2 metric, and
the KL-rate to the critical manifold (Sooter, Fontenele, et al. 2025).
Multiple signal representations (sorted spikes, pooled MUA, population events).

### Phase 3 — Perturbation Benchmark Engine *(Months 3–6)*

`benchmark.py`: the in-silico perturbation harness that recomputes the metric
panel under controlled perturbations of recording duration, unit count,
channel count, subsampling fraction, and bin size; tabulates point estimates
and CIs per condition; produces per-dataset stability mappings. This is the
core engine of Aim 1 — it converts metric primitives into a benchmark.

### Phase 4 — Adequacy Rubric & Dataset Validation *(Months 5–12)*

`rubric.py`: tri-level adequacy verdict and the dataset-property →
metric-stability mapping. `manifests.py`: DANDI-aware dataset manifests.
End-to-end validation on the in-vivo reference (DANDI:000022) and the organoid
dataset (DANDI:001603).

### Phase 5 — Benchmark v1 Public Release *(Months 6–12)*

Public release of Benchmark v1: complete documentation, benchmark notebook
suite, reproducible example outputs and figures, and a versioned release.

## 10. Success Criteria

### 10.1 Functional

- Loads a real NWB `units` table and produces binned population activity.
- `check_sufficiency()` flags a too-short or too-sparse recording with
  structured `warnings` / `failures`, and assigns a tri-level verdict.
- `distance_to_criticality()` refuses to return a point estimate when
  sufficiency fails.
- The perturbation harness produces per-dataset stability mappings across all
  five perturbation axes.
- The rubric assigns an auditable `sufficient` / `borderline` / `insufficient`
  verdict with a stated rationale.

### 10.2 Scientific

- MR estimator recovers σ within ±0.03 on synthetic branching processes at
  σ ∈ {0.85, 0.95, 0.99, 1.00}; σ̂ ≤ 0.5 on a matched-rate Poisson surrogate.
- d2 / KL-rate estimator recovers known critical configurations on Hawkes,
  overdamped Langevin, and non-Gaussian bursty synthetic systems within the
  preregistered tolerance.
- Benchmark results on DANDI:000022 reproduce known in-vivo cortical
  criticality behavior within documented tolerances.
- The framework produces a defensible adequacy verdict for the DANDI:001603
  organoid dataset.

### 10.3 Quality

- `pytest`, `ruff check`, and `mypy src/` all pass.
- Coverage ≥ 90% on analysis modules.
- Every public function has a NumPy-style docstring.

### 10.4 Release

- Tutorial notebook runs end-to-end in under 5 minutes on a laptop.
- Benchmark v1 is publicly released with documentation and reproducible
  example outputs.

## 11. Risk Assessment

### 11.1 Scientific Risks

- **Risk:** Criticality false positives — non-critical processes can mimic
  power-law signatures.
  **Mitigation:** Poisson surrogates as negative controls; multiple converging
  metrics; preregistered thresholds; required cross-representation agreement.
- **Risk:** Estimators biased or unstable under MEA-style spatial subsampling.
  **Mitigation:** the subsampling-robust MR estimator; validation against
  synthetic ground truth — and quantifying this instability is itself the
  project's deliverable.
- **Risk:** Spike-sorting quality confounds metric estimates.
  **Mitigation:** compare sorted-unit, pooled-MUA, and population
  representations (FR-034); curate datasets spanning sort qualities.
- **Risk:** Avalanche statistics are sensitive to bin size and threshold.
  **Mitigation:** bin size is an explicit perturbation axis; report sensitivity
  rather than a single tuned value.
- **Risk:** Overclaiming criticality — the field's documented pitfall.
  **Mitigation:** the adequacy rubric and the refusal to return point
  estimates on insufficient data are the direct countermeasure.
- **Risk:** AR-model misspecification — the d2 / tRG measure assumes the
  AR(n) class is an adequate fit, and is biased when the underlying data are
  strongly nonlinear or highly non-Gaussian (a limitation acknowledged in the
  source paper).
  **Mitigation:** report AR fit quality alongside d2; treat d2 as a
  complement to, not a substitute for, the branching-ratio and avalanche
  families; cross-check against the metric panel before drawing a verdict.

### 11.2 Technical Risks

- **Risk:** NWB layout heterogeneity — raw-trace discovery is layout-dependent.
  **Mitigation:** the validated units-based path; loader abstraction;
  manifest-driven dataset selection.
- **Risk:** Public assets too large for CI and notebooks.
  **Mitigation:** bounded slices and synthetic fixtures only (FR-047).
- **Risk:** `pynwb` cache/environment issues in sandboxed environments.
  **Mitigation:** the dependency guard plus documented environment workarounds
  (`docs/nwb_ingestion.md`).
- **Risk:** Dependency creep.
  **Mitigation:** optional extras and a YAGNI dependency policy (NFR-021).

### 11.3 Project Risks

- **Risk:** Scope creep from the Aim-1 software into Aim-2 acquisition work.
  **Mitigation:** the §2.2 scope boundary; Aim 2 is explicitly Future Work.
- **Risk:** A 12-month timeline with limited contributor bandwidth.
  **Mitigation:** strict phasing with working software at the end of each
  phase; MVP-first delivery.
- **Risk:** The DANDI:001603 organoid dataset presents an unanticipated NWB
  layout.
  **Mitigation:** validate ingestion on a bounded slice early in Phase 4.

## 12. Future Enhancements (post-Benchmark v1)

- **Aim 2 — Standardized acquisition workflow:** sample-metadata templates, a
  recording-conditions SOP, cloud data return, and a QC checklist, developed
  with the electrophysiology technology partner. Out of scope for this PRD.
- Additional data loaders: MCS `.h5`, raw binary, calcium-imaging traces.
- LINDI remote NWB streaming without local downloads.
- DANDI API integration for manifest-driven asset resolution.
- Batch benchmarking across many datasets and labs.
- A command-line interface for the benchmark and rubric.
- Automated release CD (GitHub releases, PyPI publishing).

## 13. References

1. Wilting, J., & Priesemann, V. (2018). Inferring collective dynamical states
   from widely unobserved systems. *Nature Communications*, 9, 2325.
   *(Multistep-regression branching-ratio estimator — FR-016.)*
2. Beggs, J. M., & Plenz, D. (2003). Neuronal avalanches in neocortical
   circuits. *Journal of Neuroscience*, 23(35), 11167–11177.
3. Ma, Z., Turrigiano, G. G., Wessel, R., & Hengen, K. B. (2019). Cortical
   circuit dynamics are homeostatically tuned to criticality in vivo.
   *Neuron*, 104(4), 655–664.e4.
4. O'Byrne, J., & Jerbi, K. (2022). How critical is brain criticality?
   *Trends in Neurosciences*, 45(11), 820–837.
5. Hengen, K. B., & Shew, W. L. (2025). Is criticality a unified setpoint of
   brain function? *Neuron*, 113(16), 2582–2598.e2.
6. Molen, T. van der, Spaeth, A., Chini, M., et al. (2025). Preconfigured
   neuronal firing sequences in human brain organoids. *Nature Neuroscience*.
   *(Organoid validation dataset — DANDI:001603, FR-046.)*
7. Sooter, N. M., Fontenele, A. J., et al. (2025). Defining and measuring
   proximity to criticality. *bioRxiv* 2025.08.03.668332.
   *(Source of the d2 metric and the temporal renormalization-group
   framework — FR-023 through FR-026, NFR-004(b).)*

The full reference list for the scientific proposal is in `docs/proposal.md`.

## 14. Approval and Sign-off

This PRD specifies the software framework for Aim 1 of the Gigabrain
preproposal. Implementation proceeds by the phased roadmap in §9, with a review
at each phase boundary against the success criteria in §10.

**Prepared by:** Ambarish S. Ghatpande
**Review date:** [To be scheduled]
**Approval date:** [Pending]
