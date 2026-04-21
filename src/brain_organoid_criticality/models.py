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
