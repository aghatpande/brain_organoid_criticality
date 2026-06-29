from __future__ import annotations

import numpy as np
import pytest

from brain_organoid_criticality.avalanches import bin_spike_times
from brain_organoid_criticality.metrics import (
    branching_ratio,
    distance_to_criticality,
)
from brain_organoid_criticality.models import SortedSpikes, SufficiencyReport
from brain_organoid_criticality.spikes import flatten_spike_times

from ._fixtures.branching_process import (
    simulate_branching,
    simulate_poisson_surrogate,
)

BIN_SIZE_S = 0.003


def _population_counts(spikes: SortedSpikes) -> np.ndarray:
    flat = flatten_spike_times(spikes)
    counts, _ = bin_spike_times(
        flat, BIN_SIZE_S, t_start=spikes.t_start_s, t_stop=spikes.t_stop_s
    )
    return counts


@pytest.mark.parametrize("sigma", [0.85, 0.95, 0.99, 1.00])
def test_branching_ratio_recovers_known_sigma(sigma: float) -> None:
    spikes = simulate_branching(sigma, rate_hz=2000.0, duration_s=120.0, seed=7)
    counts = _population_counts(spikes)

    est = branching_ratio(counts)

    assert abs(est.sigma - sigma) <= 0.03


def test_branching_ratio_poisson_surrogate_is_subcritical() -> None:
    spikes = simulate_poisson_surrogate(rate_hz=2000.0, duration_s=120.0, seed=7)
    counts = _population_counts(spikes)

    est = branching_ratio(counts)

    assert est.sigma <= 0.5


def test_branching_ratio_populates_estimate_fields() -> None:
    spikes = simulate_branching(0.95, rate_hz=2000.0, duration_s=60.0, seed=1)
    counts = _population_counts(spikes)

    est = branching_ratio(counts, k_max=100)

    assert est.k_used.shape == est.r_values.shape
    assert est.k_used[0] == 1
    assert est.k_used[-1] == 100
    assert 0.0 <= est.r_squared <= 1.0
    assert est.tau_bins > 0.0


def test_branching_ratio_rejects_short_series() -> None:
    with pytest.raises(ValueError):
        branching_ratio(np.array([1.0, 2.0]))


def test_branching_ratio_rejects_zero_variance() -> None:
    with pytest.raises(ValueError, match="variance"):
        branching_ratio(np.ones(500))


def test_branching_ratio_rejects_unknown_method() -> None:
    with pytest.raises(ValueError, match="method"):
        branching_ratio(np.arange(500.0), method="bogus")


def test_branching_ratio_rejects_nonpositive_k_max() -> None:
    with pytest.raises(ValueError, match="k_max"):
        branching_ratio(np.arange(500.0), k_max=0)


def test_distance_to_criticality_returns_dcc_with_ci() -> None:
    spikes = simulate_branching(0.95, rate_hz=2000.0, duration_s=120.0, seed=3)
    counts = _population_counts(spikes)

    result = distance_to_criticality(counts, n_bootstrap=200, seed=0)

    assert result.dcc is not None
    assert result.branching is not None
    assert abs(result.dcc - 0.05) <= 0.05
    assert result.ci_lower is not None and result.ci_upper is not None
    assert result.ci_lower <= result.dcc <= result.ci_upper
    assert result.bootstrap_n == 200


def test_distance_to_criticality_is_reproducible_with_seed() -> None:
    spikes = simulate_branching(0.95, rate_hz=2000.0, duration_s=60.0, seed=3)
    counts = _population_counts(spikes)

    first = distance_to_criticality(counts, n_bootstrap=100, seed=42)
    second = distance_to_criticality(counts, n_bootstrap=100, seed=42)

    assert first.ci_lower == second.ci_lower
    assert first.ci_upper == second.ci_upper


def test_distance_to_criticality_refuses_when_insufficient() -> None:
    counts = np.random.default_rng(0).poisson(3, size=5000).astype(float)
    report = SufficiencyReport(
        passes=False,
        n_units=2,
        n_spikes=10,
        duration_s=1.0,
        mean_firing_rate_hz=5.0,
        n_bins_at_default=300,
        warnings=[],
        failures=["n_units=2 is below the minimum of 20"],
    )

    result = distance_to_criticality(counts, n_bootstrap=10, sufficiency=report)

    assert result.dcc is None
    assert result.ci_lower is None
    assert result.ci_upper is None
    assert result.branching is None
    assert result.sufficiency is report
    assert result.bootstrap_n == 10
