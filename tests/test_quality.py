from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from brain_organoid_criticality.models import SortedSpikes
from brain_organoid_criticality.quality import check_sufficiency


def _make_spikes(
    *,
    n_units: int,
    duration_s: float,
    rate_hz: float,
    seed: int = 0,
) -> SortedSpikes:
    """Build a synthetic SortedSpikes with a target per-unit firing rate."""
    rng = np.random.default_rng(seed)
    unit_ids = np.arange(1, n_units + 1)
    spike_times_by_unit: dict[int, np.ndarray] = {}
    for unit_id in unit_ids.tolist():
        n_spikes = rng.poisson(rate_hz * duration_s)
        times = np.sort(rng.uniform(0.0, duration_s, size=n_spikes))
        spike_times_by_unit[unit_id] = times
    return SortedSpikes(
        source_path=Path("synthetic.nwb"),
        unit_ids=unit_ids,
        spike_times_by_unit=spike_times_by_unit,
        t_start_s=0.0,
        t_stop_s=duration_s,
    )


def test_check_sufficiency_passes_for_adequate_recording() -> None:
    spikes = _make_spikes(n_units=25, duration_s=120.0, rate_hz=1.0, seed=1)

    report = check_sufficiency(spikes)

    assert report.passes is True
    assert report.failures == []
    assert report.n_units == 25
    assert report.duration_s == 120.0
    assert report.n_bins_at_default == int(120.0 // 0.003)


def test_check_sufficiency_computes_descriptors() -> None:
    spikes = _make_spikes(n_units=20, duration_s=60.0, rate_hz=2.0, seed=2)
    total = sum(t.size for t in spikes.spike_times_by_unit.values())

    report = check_sufficiency(spikes)

    assert report.n_units == 20
    assert report.n_spikes == total
    assert report.duration_s == 60.0
    expected_rate = total / (20 * 60.0)
    assert report.mean_firing_rate_hz == expected_rate


def test_check_sufficiency_fails_too_few_units(
    sorted_spikes_two_units: SortedSpikes,
) -> None:
    report = check_sufficiency(sorted_spikes_two_units)

    assert report.passes is False
    assert any("n_units" in f for f in report.failures)
    # The failure message names both the observed value and the threshold.
    assert any("2" in f and "20" in f for f in report.failures)


def test_check_sufficiency_fails_too_short_duration() -> None:
    spikes = _make_spikes(n_units=25, duration_s=10.0, rate_hz=1.0, seed=3)

    report = check_sufficiency(spikes)

    assert report.passes is False
    assert any("duration" in f for f in report.failures)


def test_check_sufficiency_fails_too_few_bins() -> None:
    # 25 units, 60 s passes units+duration, but a coarse bin size starves bins.
    spikes = _make_spikes(n_units=25, duration_s=60.0, rate_hz=1.0, seed=4)

    report = check_sufficiency(spikes, bin_size_s=1.0)

    assert report.passes is False
    assert any("bins" in f.lower() for f in report.failures)


def test_check_sufficiency_warns_on_implausible_firing_rate() -> None:
    # 25 units over 60 s but each firing far above the plausible upper bound.
    spikes = _make_spikes(n_units=25, duration_s=60.0, rate_hz=500.0, seed=5)

    report = check_sufficiency(spikes)

    assert any("firing_rate" in w for w in report.warnings)


def test_check_sufficiency_empty_recording(sorted_spikes_empty: SortedSpikes) -> None:
    report = check_sufficiency(sorted_spikes_empty)

    assert report.passes is False
    assert report.n_units == 0
    assert report.n_spikes == 0
    assert report.mean_firing_rate_hz == 0.0


def test_check_sufficiency_rejects_nonpositive_bin_size(
    sorted_spikes_two_units: SortedSpikes,
) -> None:
    with pytest.raises(ValueError, match="bin_size_s"):
        check_sufficiency(sorted_spikes_two_units, bin_size_s=0.0)


def test_check_sufficiency_thresholds_are_overridable(
    sorted_spikes_two_units: SortedSpikes,
) -> None:
    report = check_sufficiency(
        sorted_spikes_two_units, min_units=1, min_duration_s=0.5, min_bins_for_bootstrap=1
    )

    assert report.passes is True
    assert report.failures == []
