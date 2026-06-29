"""Synthetic ground-truth generators for criticality estimators.

These live under ``tests/`` because they exist only to exercise the metric
estimators against known truth. :func:`simulate_branching` produces a
population whose binned activity follows a branching process at a known
branching ratio ``sigma``; :func:`simulate_poisson_surrogate` produces a
matched-rate homogeneous-Poisson negative control.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from brain_organoid_criticality.models import SortedSpikes


def _activity_to_spikes(
    activity: np.ndarray,
    *,
    n_units: int,
    bin_size_s: float,
    rng: np.random.Generator,
    source_path: Path,
    metadata: dict[str, object],
) -> SortedSpikes:
    """Scatter per-bin population counts onto units as spike times."""
    n_bins = activity.size
    total = int(activity.sum())
    bin_index = np.repeat(np.arange(n_bins), activity)
    offsets = rng.uniform(0.0, 1.0, size=total)
    times = (bin_index + offsets) * bin_size_s
    unit_assignment = rng.integers(1, n_units + 1, size=total)

    unit_ids = np.arange(1, n_units + 1)
    spike_times_by_unit: dict[int, np.ndarray] = {}
    for unit_id in unit_ids.tolist():
        unit_times = np.sort(times[unit_assignment == unit_id])
        spike_times_by_unit[unit_id] = unit_times

    return SortedSpikes(
        source_path=source_path,
        unit_ids=unit_ids,
        spike_times_by_unit=spike_times_by_unit,
        t_start_s=0.0,
        t_stop_s=n_bins * bin_size_s,
        metadata=metadata,
    )


def simulate_branching(
    sigma: float,
    rate_hz: float,
    duration_s: float,
    *,
    seed: int = 0,
    n_units: int = 30,
    bin_size_s: float = 0.003,
    min_lambda: float = 1.0,
    max_activity_factor: float = 50.0,
) -> SortedSpikes:
    """Simulate a branching process with a known branching ratio.

    The population activity ``A`` evolves as ``A[t+1] ~ Poisson(sigma * A[t] +
    h)`` on a grid of ``bin_size_s`` bins, where the drive ``h = mean *
    (1 - sigma)`` targets a stationary mean population rate of ``rate_hz``. At
    criticality (``sigma = 1``) the drive vanishes and the process is a pure
    martingale; a small ``min_lambda`` floor keeps it from going extinct and a
    ``max_activity_factor`` ceiling keeps its random walk from running away,
    neither of which binds for the subcritical cases. The resulting per-bin
    counts are scattered uniformly across ``n_units`` units as spike times, so
    that re-binning the flattened population recovers ``A``.

    Parameters
    ----------
    sigma : float
        Target branching ratio in ``(0, 1]``.
    rate_hz : float
        Target mean population firing rate (spikes per second, summed over
        units).
    duration_s : float
        Recording duration in seconds.
    seed : int, optional
        Seed for the random generator. Default ``0``.
    n_units : int, optional
        Number of units to scatter the population activity across.
        Default ``30``.
    bin_size_s : float, optional
        Generation bin size in seconds. Default ``0.003``.
    min_lambda : float, optional
        Lower bound on the per-bin Poisson rate, preventing extinction of the
        critical process. Default ``1.0``.
    max_activity_factor : float, optional
        Upper bound on the per-bin Poisson rate as a multiple of the mean
        activity, bounding the critical random walk. Default ``50.0``.

    Returns
    -------
    SortedSpikes
        Synthetic spikes whose binned population activity has branching ratio
        ``sigma``.
    """
    rng = np.random.default_rng(seed)
    dt = bin_size_s
    n_bins = int(round(duration_s / dt))
    mean_activity = rate_hz * dt
    drive = mean_activity * (1.0 - sigma)
    cap = max_activity_factor * mean_activity

    activity = np.empty(n_bins, dtype=np.int64)
    activity[0] = rng.poisson(mean_activity)
    for t in range(1, n_bins):
        rate = min(max(sigma * activity[t - 1] + drive, min_lambda), cap)
        activity[t] = rng.poisson(rate)

    return _activity_to_spikes(
        activity,
        n_units=n_units,
        bin_size_s=dt,
        rng=rng,
        source_path=Path("synthetic-branching.nwb"),
        metadata={"sigma": sigma, "rate_hz": rate_hz, "bin_size_s": dt},
    )


def simulate_poisson_surrogate(
    rate_hz: float,
    duration_s: float,
    *,
    seed: int = 0,
    n_units: int = 30,
    bin_size_s: float = 0.003,
) -> SortedSpikes:
    """Simulate a matched-rate homogeneous-Poisson negative control.

    Per-bin counts are drawn i.i.d. from ``Poisson(rate_hz * bin_size_s)``,
    so the population activity has no temporal correlation and the branching
    ratio estimated from it should be near zero.

    Parameters
    ----------
    rate_hz : float
        Mean population firing rate (spikes per second, summed over units).
    duration_s : float
        Recording duration in seconds.
    seed : int, optional
        Seed for the random generator. Default ``0``.
    n_units : int, optional
        Number of units to scatter the population activity across.
        Default ``30``.
    bin_size_s : float, optional
        Generation bin size in seconds. Default ``0.003``.

    Returns
    -------
    SortedSpikes
        Synthetic spikes with i.i.d. per-bin population counts.
    """
    rng = np.random.default_rng(seed)
    dt = bin_size_s
    n_bins = int(round(duration_s / dt))
    mean_activity = rate_hz * dt

    activity = rng.poisson(mean_activity, size=n_bins).astype(np.int64)

    return _activity_to_spikes(
        activity,
        n_units=n_units,
        bin_size_s=dt,
        rng=rng,
        source_path=Path("synthetic-poisson.nwb"),
        metadata={"rate_hz": rate_hz, "bin_size_s": dt},
    )
