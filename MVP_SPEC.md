# Brain Organoid Criticality — User Stories & MVP Spec

*Follows Russ Poldrack's "Better Code, Better Science" principles: user stories,
YAGNI, Agile cycles, working software first.*

This MVP operationalizes the public Zenodo proposal **"Screening brain organoids
for their information processing potential"** (Ghatpande 2026,
<https://zenodo.org/records/19608540>). The deliverables below are scoped as the
minimum toolkit needed to *benchmark data sufficiency* for criticality estimates
from organoid MEA recordings.

---

## 1. User Stories

### Story A — Ingest a spike-sorted NWB file and bin spikes
**As a** computational neuroscientist analyzing brain organoid MEA recordings,
**I want to** load spike times from an NWB file and bin them at a configurable
resolution,
**so that** I can detect neuronal avalanches and compute criticality metrics.

**Acceptance criteria:**
- Point the tool at a local `.nwb` file containing a `units` table.
- Extract spike times per unit into the `SortedSpikes` container
  (`src/brain_organoid_criticality/models.py`).
- Bin population spike times at a user-specified `bin_size` (e.g., 3 ms).
- Return bin counts and edges as NumPy arrays.
- Fail early with a clear message if the NWB file lacks required fields.

---

### Story B — Check data sufficiency before analysis
**As a** lab member preparing organoid recordings,
**I want to** check that my recording has enough units, duration, and bins to
support a reliable DCC estimate,
**so that** I don't waste hours computing a metric whose confidence interval is
too wide to be informative.

**Acceptance criteria:**
- Check presence and contents of the `units` table.
- Compute `n_units`, `n_spikes`, `duration_s`, `mean_firing_rate_hz`, and
  `n_bins_at_default`.
- Compare each value to a configurable threshold and accumulate a structured
  list of `warnings` and `failures` (human-readable strings naming both the
  threshold and the observed value).
- Return a `SufficiencyReport` dataclass; `passes=False` if any threshold fails.

---

### Story C — Compute distance-to-criticality (DCC)
**As a** researcher comparing organoid maturation stages,
**I want to** compute the branching ratio σ and DCC = 1 − σ on binned spike data
using an estimator that is robust to MEA-style subsampling,
**so that** I can compare cultures despite small electrode-count recordings.

**Acceptance criteria:**
- Accept binned spike counts from Story A.
- Compute σ using the multistep-regression (MR) estimator of
  Wilting & Priesemann (2018): fit `r(k) = exp(−k/τ)` for lag `k ∈ [1, k_max]`
  and return `σ = exp(−1/τ)`.
- Compute DCC = 1 − σ and a bootstrap confidence interval
  (default `n_bootstrap=1000`).
- Return a `DCCResult` dataclass
  (`dcc`, `ci_lower`, `ci_upper`, `branching`, `sufficiency`, `bootstrap_n`).
- Refuse to return a point estimate when the input fails
  `check_sufficiency()`; return the report with `dcc=None` instead.
- **Falsifiable synthetic-data check:** Given a simulated branching process
  generated at known σ ∈ {0.85, 0.95, 0.99, 1.00} with ≥60 s of data at 3 ms
  binning, recovered σ̂ falls within ±0.03 of truth. On a homogeneous Poisson
  surrogate with matched rate, σ̂ ≤ 0.5.

---

### Story D — Run a reproducible benchmark notebook
**As a** new user or collaborator,
**I want** a tutorial notebook that demonstrates the full pipeline first on
synthetic data and then on a short slice of a public NWB file,
**so that** I can reproduce results offline and adapt them to my own data.

**Acceptance criteria:**
- Primary walkthrough uses the synthetic branching-process generator
  (see §2.2-B) so the notebook is self-contained and reproducible without
  internet access.
- Secondary "real data" example uses a *bounded slice* of DANDI dandiset
  `000022` asset `ac4bfefc-d259-4d13-a083-89df1f9044b9` — specify slice bounds
  (e.g., first 60 s, or units 0–49) so the notebook stays under 5 min on a
  laptop. The full asset (~2,890 units / ~124 M spikes / ~9,807 s) is too
  large to use directly.
- Walks through ingest → sufficiency check → bin → DCC in order.
- Produces one summary figure (e.g., `r(k)` vs. lag with the MR fit overlay,
  or DCC bootstrap CI).
- Runs end-to-end in under 5 minutes on a laptop.

---

## 2. MVP Specification

**Guiding principle (YAGNI):** Build only what the four user stories require.
No extra formats, no fancy visualizations, no batch processing, no cloud
infrastructure. Defer everything else.

### 2.1 Scope

| In scope for MVP | Out of scope (future) |
|------------------|-----------------------|
| Local `.nwb` file ingest (PyNWB) — *shipped* | Remote / LINDI NWB access |
| Spike extraction & population binning — *shipped* | MCS raw binary / `.h5` formats |
| MR-estimator branching ratio & DCC | Power-law fitting, avalanche shape collapse, critical exponents |
| Data-sufficiency report | Automated QC reports |
| One tutorial notebook (synthetic + bounded DANDI slice) | Benchmark suite across many datasets |
| Synthetic test fixtures (incl. branching-process generator) | DANDI API integration / full-asset downloads |
| Shared pytest fixtures (`tests/conftest.py`) — *shipped* (PR #23) | — |
| GitHub Actions CI: `pytest`, `ruff`, `mypy` — *shipped* | GitHub releases, PyPI publishing |

### 2.2 Deliverables

#### A. Python package (`brain_organoid_criticality`)

| Module | Functions / classes | Notes |
|--------|---------------------|-------|
| `io.py` | `validate_path(path) -> Path` | **Shipped.** Path validation only. |
| `models.py` | `RecordingSummary`, `ElectricalSeriesRef`, `SortedSpikes` | **Shipped.** `SortedSpikes` stores `spike_times_by_unit: dict[int, np.ndarray]`, plus `unit_ids`, `t_start_s`, `t_stop_s`, `source_path`, `metadata`. Extend with the three new dataclasses below. |
| `loaders.py` | `inspect_nwb`, `list_electrical_series`, `get_electrical_series_ref`, `read_electrical_series_chunk`, `has_units_table` | **Shipped.** Optional `[nwb]` extra. |
| `spikes.py` | `load_units_from_nwb`, `flatten_spike_times`, `validate_sorted_spikes` | **Shipped.** Loads the `units` table into `SortedSpikes`. |
| `avalanches.py` | `bin_spike_times(spike_times, bin_size, t_start?, t_stop?) -> (counts, edges)` | **Shipped.** Keep as-is. |
| `metrics.py` *(new)* | `branching_ratio(counts, *, k_max=150, method="mr") -> BranchingRatioEstimate`, `distance_to_criticality(counts, *, n_bootstrap=1000, sufficiency=None) -> DCCResult` | MR estimator fits `r(k) = exp(−k/τ)` for `k ∈ [1, k_max]`; `σ = exp(−1/τ)`. `DCCResult.dcc = 1 − σ`. Bootstrap by resampling bins with replacement. Refuses point estimate when `sufficiency.passes is False`. |
| `quality.py` *(new)* | `check_sufficiency(sorted_spikes, *, min_units=20, min_duration_s=60, firing_rate_range_hz=(0.01, 100.0), min_bins_for_bootstrap=1000, bin_size_s=0.003) -> SufficiencyReport` | Returns dataclass with `passes`, `n_units`, `n_spikes`, `duration_s`, `mean_firing_rate_hz`, `n_bins_at_default`, `warnings: list[str]`, `failures: list[str]`. |

**New dataclasses to add to `models.py`:**

- `SufficiencyReport(passes, n_units, n_spikes, duration_s, mean_firing_rate_hz, n_bins_at_default, warnings, failures)`
- `BranchingRatioEstimate(sigma, tau_bins, r_squared, k_used, r_values)`
- `DCCResult(dcc, ci_lower, ci_upper, branching, sufficiency, bootstrap_n)`

**Defaults provenance.** 20 units is a soft floor for MR-style estimators on
subsampled MEA data; below it, `τ` fits become unstable. 60 s at 3 ms binning
gives ≥20 000 bins, enough for a bootstrap of 1000 to produce CIs that are
tight relative to the σ scale of interest. Firing-rate bounds (0.01–100 Hz)
bracket biologically plausible single-unit activity in organoid cultures —
outside this range, units are usually noise or duplicates. Override any
default that disagrees with your experimental practice; the point is that the
spec commits to numbers so contributors don't invent their own.

#### B. Test suite

| File | Covers |
|------|--------|
| `tests/conftest.py` | **Shipped.** `sorted_spikes_two_units`, `sorted_spikes_single_unit`, `sorted_spikes_empty`, `synthetic_nwb_path`. |
| `tests/test_nwb_io.py` | **Shipped.** NWB inspection and loading. |
| `tests/test_spikes.py` | **Shipped.** `flatten_spike_times`, `validate_sorted_spikes`. |
| `tests/test_avalanches.py` *(new)* | `bin_spike_times` happy path and edge cases (empty input, single spike, custom `t_start` / `t_stop`). |
| `tests/test_metrics.py` *(new)* | MR-estimator σ recovery on `simulate_branching` fixture at σ ∈ {0.85, 0.95, 0.99, 1.00}; bootstrap CI bounds; Poisson surrogate produces σ̂ ≤ 0.5. |
| `tests/test_quality.py` *(new)* | Threshold pass/fail edges using the existing `sorted_spikes_*` fixtures; contents of `warnings` / `failures`. |
| `tests/_fixtures/branching_process.py` *(new)* | `simulate_branching(sigma, rate_hz, duration_s, seed) -> SortedSpikes` — lightweight branching-process generator for synthetic ground truth. Lives under `tests/` because it is only used in testing. |

All tests use synthetic / generated data only. No real NWB files required.

#### C. Tutorial notebook

`notebooks/01_dcc_tutorial.ipynb`

- **Primary example:** synthetic branching process at σ = 0.95 → bin → check
  sufficiency → compute DCC → plot the MR fit. Self-contained, no network.
- **Secondary example:** load a bounded slice of DANDI dandiset `000022`
  asset `ac4bfefc-d259-4d13-a083-89df1f9044b9` (e.g., first 60 s) and run the
  same pipeline. Specify exact slice bounds in the notebook.
- Under 5 min runtime on a laptop.

#### D. Documentation

- `README.md` updated with MVP feature list and install instructions.
- `docs/quickstart.md` *(new)* — one-page getting-started guide.
- NumPy-style docstrings on all public functions.

### 2.3 Dependencies

| Package | Purpose | Install via |
|---------|---------|-------------|
| `numpy` | Core arrays | Base |
| `pynwb` | NWB file reading | `[nwb]` extra |
| `pytest` | Testing | `[dev]` extra |
| `ruff` | Linting / formatting | `[dev]` extra |
| `mypy` | Type checking | `[dev]` extra |
| `matplotlib` | Notebook plotting | Notebook only (not a package dep) |

### 2.4 Acceptance Checklist

Before the MVP is "done", all of these must pass:

```bash
# CI gates (already enforced by .github/workflows/ci.yml)
pytest                          # all tests pass
ruff check src/ tests/          # no lint errors
mypy src/                       # no type errors
```

Functional gates:

- Load a real NWB file with a units table and get spike times.
- Bin spikes at 3 ms resolution.
- `check_sufficiency()` flags a too-short or too-sparse recording with
  structured `warnings` / `failures`.
- MR estimator recovers σ within ±0.03 on synthetic branching processes at
  σ ∈ {0.85, 0.95, 0.99, 1.00}; σ̂ ≤ 0.5 on a matched-rate Poisson surrogate.
- `distance_to_criticality()` refuses to return a point estimate when
  sufficiency fails.
- Tutorial notebook runs end-to-end on synthetic data and on the bounded
  DANDI slice.

Documentation gates:

- README has install & quickstart.
- All public functions have NumPy-style docstrings.
- Notebook includes narrative markdown cells.

### 2.5 What This Unblocks (Future Work)

Once the MVP is working, the next natural steps are. Items 4–6 are named
deliverables of the Gigabrain preproposal (Aim 1) that the MVP does not yet
cover — they convert the MVP's one-shot metric primitives into the actual
benchmark engine and apply it to the organoid validation dataset.

1. **Avalanche extraction** — threshold-crossing detection, avalanche
   catalogues, size / duration power-law fitting, shape collapse.
2. **Susceptibility and autocorrelation (Debye-Waller factor)** — deferred
   until the MR-based σ and DCC have shipped and been benchmarked on the
   synthetic ground truth from Story C.
3. **Renormalization-group distance measures (d2 / tRG)** — AR(n) model
   fit plus the d2 metric (Euclidean distance to the β = 2 fixed-point
   hyperplane) and the KL-rate to the critical manifold (Sooter, Fontenele,
   et al. 2025). A third metric family, complementary to the MR-branching
   and avalanche-exponent families. See `PRD.md` §3.3 (FR-023–026) and
   Phase 2 in §9.
4. **In-silico perturbation harness ("Benchmark v1")** — the core engine of
   proposal Aim 1: a parameterized framework that tabulates how each
   metric's point estimate and CI change under controlled perturbations of
   recording duration, unit count, channel count, subsampling fraction, and
   temporal bin size. Consumes the metrics from §2.2-A and produces
   per-dataset stability mappings. Without this, the MVP can *compute* DCC
   but cannot *benchmark* it.
5. **Tri-level sufficiency verdict** — extend `SufficiencyReport` with
   `verdict: Literal["sufficient", "borderline", "insufficient"]` to match
   the proposal's adequacy rubric. Borderline thresholds sit between the
   current pass / fail edges (e.g. 10–20 units, 30–60 s).
6. **Organoid validation on DANDI:001603** — apply the benchmarked
   framework to the Molen et al. (2025) organoid dataset (proposal ref 5).
   The MVP validates the in-vivo cortex side via DANDI:000022; this item
   closes the organoid side that proposal Aim 1 requires.
7. **Additional data loaders** — MCS `.h5`, raw binary, calcium imaging.
8. **LINDI remote access** — optional NWB streaming without local files.
9. **Benchmark notebook suite** — recording-duration sensitivity, batch
   comparisons, and robustness studies built on the perturbation harness
   from item 4.
10. **CI/CD releases** — GitHub Actions for automated PyPI publishing.
