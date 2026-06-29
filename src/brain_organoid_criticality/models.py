from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass(slots=True)
class RecordingSummary:
    """Normalized summary of an NWB recording."""

    source_path: Path
    session_id: str | None
    subject_id: str | None
    experiment_description: str | None
    identifier: str | None
    sampling_rate_hz: float | None
    duration_s: float | None
    n_channels: int | None
    has_raw_electrical_series: bool
    has_units: bool
    acquisition_names: list[str] = field(default_factory=list)
    processing_modules: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ElectricalSeriesRef:
    """Reference to an NWB electrical series without loading full data."""

    source_path: Path
    series_name: str
    sampling_rate_hz: float | None
    n_samples: int | None
    n_channels: int | None
    starting_time_s: float | None


@dataclass(slots=True)
class SortedSpikes:
    """Canonical spike-times container used by downstream analyses."""

    source_path: Path
    unit_ids: np.ndarray
    spike_times_by_unit: dict[int, np.ndarray]
    t_start_s: float
    t_stop_s: float
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class SufficiencyReport:
    """Data-sufficiency descriptors and verdict for a recording.

    Produced by :func:`brain_organoid_criticality.quality.check_sufficiency`.
    ``passes`` is ``False`` whenever any descriptor falls below a hard
    threshold; ``warnings`` collects advisory issues that do not by themselves
    block a metric estimate, while ``failures`` collects threshold violations
    that do.

    Attributes
    ----------
    passes : bool
        ``True`` only when ``failures`` is empty.
    n_units : int
        Number of units in the recording.
    n_spikes : int
        Total number of spikes summed across all units.
    duration_s : float
        Recording duration in seconds (``t_stop_s - t_start_s``).
    mean_firing_rate_hz : float
        Mean per-unit firing rate in hertz.
    n_bins_at_default : int
        Number of bins the recording yields at the assessed bin size.
    warnings : list of str
        Advisory messages naming both the observed value and the bound.
    failures : list of str
        Hard-threshold violations naming both the observed value and the bound.
    """

    passes: bool
    n_units: int
    n_spikes: int
    duration_s: float
    mean_firing_rate_hz: float
    n_bins_at_default: int
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BranchingRatioEstimate:
    """Multistep-regression estimate of the branching ratio sigma.

    The estimator follows Wilting & Priesemann (2018): autoregressive slopes
    ``r(k) = Cov(A_t, A_{t+k}) / Var(A_t)`` decay geometrically as
    ``r(k) = b * sigma**k`` for a branching process, so ``sigma`` is recovered
    from the decay rate and is invariant to the multiplicative offset ``b``
    introduced by spatial subsampling.

    Attributes
    ----------
    sigma : float
        Estimated branching ratio. ``sigma < 1`` subcritical, ``~1`` critical.
    tau_bins : float
        Autocorrelation time in bins, ``-1 / log(sigma)``; ``inf`` when
        ``sigma >= 1``.
    r_squared : float
        Goodness of fit of the geometric-decay model to the slopes ``r(k)``.
    k_used : np.ndarray
        Lags (in bins) at which slopes were evaluated.
    r_values : np.ndarray
        Autoregressive slopes ``r(k)`` at each lag in ``k_used``.
    """

    sigma: float
    tau_bins: float
    r_squared: float
    k_used: np.ndarray
    r_values: np.ndarray


@dataclass(slots=True)
class DCCResult:
    """Distance-to-criticality result with a bootstrap confidence interval.

    ``dcc = 1 - sigma``. All estimate fields are ``None`` when the supplied
    :class:`SufficiencyReport` does not pass, in which case no point estimate
    is computed.

    Attributes
    ----------
    dcc : float or None
        Distance to criticality, ``1 - sigma``.
    ci_lower : float or None
        Lower bound of the bootstrap confidence interval on ``dcc``.
    ci_upper : float or None
        Upper bound of the bootstrap confidence interval on ``dcc``.
    branching : BranchingRatioEstimate or None
        The underlying branching-ratio estimate.
    sufficiency : SufficiencyReport or None
        The sufficiency report consulted, if any.
    bootstrap_n : int
        Number of bootstrap resamples requested.
    """

    dcc: float | None
    ci_lower: float | None
    ci_upper: float | None
    branching: BranchingRatioEstimate | None
    sufficiency: SufficiencyReport | None
    bootstrap_n: int
