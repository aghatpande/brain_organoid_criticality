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
