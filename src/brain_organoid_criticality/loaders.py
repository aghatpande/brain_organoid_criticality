from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .io import validate_path
from .models import ElectricalSeriesRef, RecordingSummary


def inspect_nwb(path: str | Path) -> RecordingSummary:
    """
    Inspect an NWB file and return a normalized summary.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to an NWB file on disk.

    Returns
    -------
    RecordingSummary
        Summary of the recording contents and metadata.
    """
    source_path = validate_path(path)

    with _open_nwb(source_path) as nwbfile:
        electrical_series = _collect_electrical_series_refs(nwbfile, source_path)
        subject = getattr(nwbfile, "subject", None)
        subject_id = getattr(subject, "subject_id", None) if subject is not None else None
        sampling_rate_hz = electrical_series[0].sampling_rate_hz if electrical_series else None
        n_channels = electrical_series[0].n_channels if electrical_series else None

        return RecordingSummary(
            source_path=source_path,
            session_id=getattr(nwbfile, "session_id", None),
            subject_id=subject_id,
            experiment_description=getattr(nwbfile, "experiment_description", None),
            identifier=getattr(nwbfile, "identifier", None),
            sampling_rate_hz=sampling_rate_hz,
            duration_s=_estimate_duration_seconds(nwbfile, electrical_series),
            n_channels=n_channels,
            has_raw_electrical_series=bool(electrical_series),
            has_units=getattr(nwbfile, "units", None) is not None,
            acquisition_names=sorted(nwbfile.acquisition.keys()),
            processing_modules=sorted(nwbfile.processing.keys()),
            metadata={
                "electrical_series_names": [ref.series_name for ref in electrical_series],
                "institution": getattr(nwbfile, "institution", None),
                "lab": getattr(nwbfile, "lab", None),
                "session_description": getattr(nwbfile, "session_description", None),
            },
        )


def list_electrical_series(path: str | Path) -> list[ElectricalSeriesRef]:
    """
    List electrical series available in an NWB file.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to an NWB file on disk.

    Returns
    -------
    list of ElectricalSeriesRef
        Metadata-only references to electrical recordings.
    """
    source_path = validate_path(path)

    with _open_nwb(source_path) as nwbfile:
        return _collect_electrical_series_refs(nwbfile, source_path)


def get_electrical_series_ref(
    path: str | Path,
    series_name: str | None = None,
) -> ElectricalSeriesRef:
    """
    Select one electrical series for downstream processing.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to an NWB file on disk.
    series_name : str, optional
        Name of the electrical series to select. If omitted, exactly one
        electrical series must be present.

    Returns
    -------
    ElectricalSeriesRef
        Reference to the selected electrical series.
    """
    refs = list_electrical_series(path)
    if not refs:
        raise ValueError("No electrical series found in NWB file")

    if series_name is None:
        if len(refs) > 1:
            available = ", ".join(ref.series_name for ref in refs)
            raise ValueError(
                "Multiple electrical series found; provide series_name. "
                f"Available series: {available}"
            )
        return refs[0]

    for ref in refs:
        if ref.series_name == series_name:
            return ref

    available = ", ".join(ref.series_name for ref in refs)
    raise ValueError(
        f"Electrical series {series_name!r} not found. Available series: {available}"
    )


def read_electrical_series_chunk(
    path: str | Path,
    series_name: str | None = None,
    start: int = 0,
    stop: int | None = None,
) -> np.ndarray:
    """
    Read a sample-indexed chunk from an electrical series.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to an NWB file on disk.
    series_name : str, optional
        Name of the electrical series to read.
    start : int, default=0
        Starting sample index.
    stop : int, optional
        Stopping sample index. If omitted, read until the end.

    Returns
    -------
    np.ndarray
        Chunk of electrical data.
    """
    if start < 0:
        raise ValueError("start must be non-negative")
    if stop is not None and stop < start:
        raise ValueError("stop must be greater than or equal to start")

    source_path = validate_path(path)
    selected_ref = get_electrical_series_ref(source_path, series_name=series_name)

    with _open_nwb(source_path) as nwbfile:
        series = _get_electrical_series_by_name(nwbfile, selected_ref.series_name)
        data = series.data
        return np.asarray(data[start:stop])


def has_units_table(path: str | Path) -> bool:
    """
    Return whether an NWB file contains a units table.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to an NWB file on disk.

    Returns
    -------
    bool
        True when the NWB file contains spike-sorted units.
    """
    source_path = validate_path(path)

    with _open_nwb(source_path) as nwbfile:
        return getattr(nwbfile, "units", None) is not None


def _require_pynwb() -> tuple[Any, Any]:
    try:
        from pynwb import NWBHDF5IO
        from pynwb.ecephys import ElectricalSeries
    except ImportError as exc:
        raise ImportError(
            "PyNWB is required for NWB loading. Install with "
            "`pip install -e .[nwb]` or `pip install pynwb`."
        ) from exc

    return NWBHDF5IO, ElectricalSeries


class _ReadNWB:
    def __init__(self, path: Path):
        NWBHDF5IO, _ = _require_pynwb()
        self._io = NWBHDF5IO(str(path), "r")
        self._file = None

    def __enter__(self):
        self._file = self._io.read()
        return self._file

    def __exit__(self, exc_type, exc, tb):
        self._io.close()
        return False


def _open_nwb(path: Path) -> _ReadNWB:
    return _ReadNWB(path)


def _collect_electrical_series_refs(
    nwbfile: Any,
    source_path: Path,
) -> list[ElectricalSeriesRef]:
    _, electrical_series_type = _require_pynwb()
    refs: list[ElectricalSeriesRef] = []

    for obj in nwbfile.objects.values():
        if not isinstance(obj, electrical_series_type):
            continue

        n_samples, n_channels = _shape_to_samples_and_channels(getattr(obj.data, "shape", None))
        refs.append(
            ElectricalSeriesRef(
                source_path=source_path,
                series_name=obj.name,
                sampling_rate_hz=_coerce_float(getattr(obj, "rate", None)),
                n_samples=n_samples,
                n_channels=n_channels,
                starting_time_s=_coerce_float(getattr(obj, "starting_time", None)),
            )
        )

    refs.sort(key=lambda ref: ref.series_name)
    return refs


def _get_electrical_series_by_name(nwbfile: Any, series_name: str) -> Any:
    _, electrical_series_type = _require_pynwb()

    for obj in nwbfile.objects.values():
        if isinstance(obj, electrical_series_type) and obj.name == series_name:
            return obj

    raise ValueError(f"Electrical series {series_name!r} not found in NWB file")


def _shape_to_samples_and_channels(
    shape: tuple[int, ...] | None,
) -> tuple[int | None, int | None]:
    if shape is None or len(shape) == 0:
        return None, None
    if len(shape) == 1:
        return int(shape[0]), 1
    return int(shape[0]), int(shape[1])


def _estimate_duration_seconds(
    nwbfile: Any,
    electrical_series: list[ElectricalSeriesRef],
) -> float | None:
    if electrical_series:
        primary = electrical_series[0]
        if primary.n_samples is not None and primary.sampling_rate_hz:
            return primary.n_samples / primary.sampling_rate_hz

    units = getattr(nwbfile, "units", None)
    if units is None:
        return None

    latest_spike = 0.0
    for index in range(len(units.id)):
        spike_times = np.asarray(units["spike_times"][index], dtype=float)
        if spike_times.size:
            latest_spike = max(latest_spike, float(spike_times.max()))

    return latest_spike or None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)
