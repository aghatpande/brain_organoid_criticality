# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ground rules

Non-negotiable. They reflect the project's TDD discipline and the failure modes the field has already paid for.

- **Tests first, and they must fail first.** Write the test before the implementation. Run the test and confirm it fails for the right reason before writing any solution code.
- **Do not modify a test to make code pass.** If a test fails, fix the code or fix the test's correctness — never weaken the assertion to go green.
- **No code in `__init__.py`.** Re-exports only; keep `__all__` in sync when adding public symbols.
- **Minimal dependencies.** Prefer numpy and widely-used scientific Python (scipy, statsmodels, etc.). New dependencies require a concrete requirement in `PRD.md` or `MVP_SPEC.md` to justify them.
- **Synthetic data only in tests.** No real `.nwb` files committed; use `tests/conftest.py` fixtures and `tests/_fixtures/`.
- **NumPy-style docstrings on every public function.** Parameters / Returns / Raises.
- **NWB access is gated.** Any function importing `pynwb` calls `_require_pynwb()` first. Never import `pynwb` at module level.
- **No hardcoded paths or magic constants.** Parameterise — `bin_size: float` as an argument, not `bin_size = 0.003` baked in.

## Commands

```bash
# Install in editable mode (base)
pip install -e ".[dev,nwb]"

# Run tests
pytest
pytest --cov=brain_organoid_criticality --cov-report=term-missing

# Run a single test or function
pytest tests/test_spikes.py
pytest tests/test_spikes.py::test_flatten_spike_times

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/
```

## Architecture

The package lives in `src/brain_organoid_criticality/` with a flat, single-responsibility module layout:

- **`models.py`** — three shared dataclasses: `RecordingSummary` (NWB session metadata), `ElectricalSeriesRef` (lazy reference to an electrode recording), `SortedSpikes` (canonical spike-times container used by all downstream analyses). All use `@dataclass(slots=True)`.
- **`io.py`** — `validate_path()`: only utility, converts str/Path and raises `FileNotFoundError` if missing.
- **`loaders.py`** — NWB inspection and data reading. Public API: `inspect_nwb`, `list_electrical_series`, `get_electrical_series_ref`, `read_electrical_series_chunk`, `has_units_table`. NWB access is gated behind `_require_pynwb()` so the base install (numpy-only) stays lean; pynwb is an optional extra (`.[nwb]`).
- **`spikes.py`** — Loads spike-sorted units into `SortedSpikes` (`load_units_from_nwb`), flattens across units (`flatten_spike_times`), and validates the container invariants (`validate_sorted_spikes`).
- **`avalanches.py`** — `bin_spike_times`: bins a flat spike-time vector into uniform histogram bins; entry point for future avalanche cataloguing and power-law fitting.
- **`__init__.py`** — re-exports the entire public API; keep `__all__` in sync when adding public symbols.

## Key conventions

- **Data in `SortedSpikes`**: all analyses consume `SortedSpikes`, not raw NWB objects. Load once with `load_units_from_nwb`, then work with the container.
- **Shared test fixtures**: `tests/conftest.py` provides `sorted_spikes_two_units`, `sorted_spikes_single_unit`, `sorted_spikes_empty` (pure numpy), and `synthetic_nwb_path` (written to `tmp_path` with pynwb, skipped if pynwb absent).
- **Commit style**: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
- **New modules**: add `src/brain_organoid_criticality/<name>.py` + `tests/test_<name>.py` + export symbols from `__init__.py`.
- **Requirements contract**: `PRD.md` is the source of truth for what to build (§3 functional reqs, §5 architecture, §9 phased roadmap). `MVP_SPEC.md` pins Phase 1 signatures and default thresholds — consult it before drafting public APIs for `metrics.py`, `quality.py`, etc. `MVP_SPEC.md` is gitignored (local planning doc), not on `origin`.
