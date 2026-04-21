from __future__ import annotations

from pathlib import Path

import numpy as np

from .io import validate_path
from .loaders import _open_nwb, _require_pynwb
from .models import SortedSpikes


def load_units_from_nwb(path: str | Path) -> SortedSpikes:
    """
    Load spike-sorted units from an NWB units table.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to an NWB file on disk.

    Returns
    -------
    SortedSpikes
        Canonical spike-times representation extracted from the NWB file.
    """
    _require_pynwb()
    source_path = validate_path(path)

    with _open_nwb(source_path) as nwbfile:
        units = getattr(nwbfile, "units", None)
        if units is None:
            raise ValueError("NWB file does not contain a units table")

        unit_ids = np.asarray(units.id[:], dtype=int)
        spike_times_by_unit: dict[int, np.ndarray] = {}
        t_start_s = 0.0
        t_stop_s = 0.0

        for index, unit_id in enumerate(unit_ids.tolist()):
            spike_times = np.asarray(units["spike_times"][index], dtype=float)
            spike_times_by_unit[unit_id] = spike_times
            if spike_times.size:
                t_stop_s = max(t_stop_s, float(spike_times.max()))

        sorted_spikes = SortedSpikes(
            source_path=source_path,
            unit_ids=unit_ids,
            spike_times_by_unit=spike_times_by_unit,
            t_start_s=t_start_s,
            t_stop_s=t_stop_s,
            metadata={
                "session_id": getattr(nwbfile, "session_id", None),
                "identifier": getattr(nwbfile, "identifier", None),
            },
        )
        validate_sorted_spikes(sorted_spikes)
        return sorted_spikes


def flatten_spike_times(sorted_spikes: SortedSpikes) -> np.ndarray:
    """
    Flatten spike times across all units into a single sorted vector.

    Parameters
    ----------
    sorted_spikes : SortedSpikes
        Canonical spike-times container.

    Returns
    -------
    np.ndarray
        Sorted spike times across all units.
    """
    if not sorted_spikes.spike_times_by_unit:
        return np.array([], dtype=float)

    flattened = np.concatenate(
        [
            np.asarray(spike_times, dtype=float)
            for spike_times in sorted_spikes.spike_times_by_unit.values()
        ]
    )
    return np.sort(flattened)


def validate_sorted_spikes(sorted_spikes: SortedSpikes) -> None:
    """
    Validate a canonical spike-times container.

    Parameters
    ----------
    sorted_spikes : SortedSpikes
        Canonical spike-times container.
    """
    if sorted_spikes.t_start_s < 0:
        raise ValueError("t_start_s must be non-negative")
    if sorted_spikes.t_stop_s < sorted_spikes.t_start_s:
        raise ValueError("t_stop_s must be greater than or equal to t_start_s")

    unique_unit_ids = np.unique(sorted_spikes.unit_ids)
    if unique_unit_ids.size != sorted_spikes.unit_ids.size:
        raise ValueError("unit_ids must be unique")

    for unit_id in sorted_spikes.unit_ids.tolist():
        if unit_id not in sorted_spikes.spike_times_by_unit:
            raise ValueError(f"Missing spike times for unit_id={unit_id}")

        spike_times = np.asarray(sorted_spikes.spike_times_by_unit[unit_id], dtype=float)
        if spike_times.ndim != 1:
            raise ValueError("Spike times must be one-dimensional arrays")
        if np.any(~np.isfinite(spike_times)):
            raise ValueError("Spike times must be finite")
        if np.any(spike_times < sorted_spikes.t_start_s):
            raise ValueError("Spike times must be greater than or equal to t_start_s")
        if np.any(spike_times > sorted_spikes.t_stop_s):
            raise ValueError("Spike times must be less than or equal to t_stop_s")
        if spike_times.size > 1 and np.any(np.diff(spike_times) < 0):
            raise ValueError("Spike times must be sorted within each unit")
