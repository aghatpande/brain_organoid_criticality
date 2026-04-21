from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest

from brain_organoid_criticality.loaders import (
    get_electrical_series_ref,
    has_units_table,
    inspect_nwb,
    list_electrical_series,
    read_electrical_series_chunk,
)
from brain_organoid_criticality.spikes import load_units_from_nwb


pynwb = pytest.importorskip("pynwb")
ElectricalSeries = pytest.importorskip("pynwb.ecephys").ElectricalSeries
LFP = pytest.importorskip("pynwb.ecephys").LFP
NWBFile = pynwb.NWBFile
NWBHDF5IO = pynwb.NWBHDF5IO


def test_inspect_nwb_and_load_units(tmp_path) -> None:
    nwb_path = tmp_path / "example.nwb"
    _write_test_nwb(nwb_path)

    summary = inspect_nwb(nwb_path)
    electrical_series = list_electrical_series(nwb_path)
    selected_series = get_electrical_series_ref(nwb_path, "ElectricalSeries")
    chunk = read_electrical_series_chunk(nwb_path, start=1, stop=4)
    spikes = load_units_from_nwb(nwb_path)

    assert summary.has_raw_electrical_series is True
    assert summary.has_units is True
    assert summary.sampling_rate_hz == pytest.approx(1000.0)
    assert summary.n_channels == 2
    assert summary.duration_s == pytest.approx(0.01)
    assert has_units_table(nwb_path) is True

    assert len(electrical_series) == 1
    assert selected_series.series_name == "ElectricalSeries"
    assert selected_series.n_samples == 10
    assert selected_series.n_channels == 2
    np.testing.assert_allclose(chunk, np.arange(2, 8, dtype=float).reshape(3, 2))

    np.testing.assert_array_equal(spikes.unit_ids, np.array([1, 2]))
    np.testing.assert_allclose(spikes.spike_times_by_unit[1], np.array([0.1, 0.3]))
    np.testing.assert_allclose(spikes.spike_times_by_unit[2], np.array([0.2, 0.5]))
    assert spikes.t_stop_s == pytest.approx(0.5)


def test_list_electrical_series_excludes_processed_lfp_series(tmp_path) -> None:
    nwb_path = tmp_path / "processed_only.nwb"
    _write_test_nwb(nwb_path, include_raw_acquisition=False, include_processed_lfp=True)

    summary = inspect_nwb(nwb_path)
    electrical_series = list_electrical_series(nwb_path)

    assert summary.has_raw_electrical_series is False
    assert summary.duration_s is None
    assert electrical_series == []


def test_inspect_nwb_units_only_does_not_infer_duration_from_spikes(tmp_path) -> None:
    nwb_path = tmp_path / "units_only.nwb"
    _write_test_nwb(nwb_path, include_raw_acquisition=False, include_processed_lfp=False)

    summary = inspect_nwb(nwb_path)
    spikes = load_units_from_nwb(nwb_path)

    assert summary.has_raw_electrical_series is False
    assert summary.has_units is True
    assert summary.duration_s is None
    assert spikes.t_stop_s == pytest.approx(0.5)


def _write_test_nwb(
    path,
    *,
    include_raw_acquisition: bool = True,
    include_processed_lfp: bool = False,
) -> None:
    nwbfile = NWBFile(
        session_description="test session",
        identifier="TEST123",
        session_start_time=datetime.now(timezone.utc),
        session_id="session-1",
        experiment_description="synthetic ecephys test",
    )

    device = nwbfile.create_device(name="test-probe")
    electrode_group = nwbfile.create_electrode_group(
        name="group",
        description="test electrodes",
        location="VISp",
        device=device,
    )

    for index in range(2):
        nwbfile.add_electrode(
            x=float(index),
            y=0.0,
            z=0.0,
            imp=np.nan,
            location="VISp",
            filtering="none",
            group=electrode_group,
        )

    electrodes = nwbfile.create_electrode_table_region(
        region=[0, 1],
        description="all electrodes",
    )
    data = np.arange(20, dtype=float).reshape(10, 2)
    if include_raw_acquisition:
        electrical_series = ElectricalSeries(
            name="ElectricalSeries",
            data=data,
            electrodes=electrodes,
            rate=1000.0,
            starting_time=0.0,
        )
        nwbfile.add_acquisition(electrical_series)

    if include_processed_lfp:
        lfp_module = nwbfile.create_processing_module(
            name="ecephys",
            description="processed ecephys signals",
        )
        lfp_series = ElectricalSeries(
            name="ProcessedLFP",
            data=data,
            electrodes=electrodes,
            rate=1000.0,
            starting_time=0.0,
        )
        lfp_module.add(LFP(electrical_series=lfp_series))

    nwbfile.add_unit(id=1, spike_times=[0.1, 0.3])
    nwbfile.add_unit(id=2, spike_times=[0.2, 0.5])

    with NWBHDF5IO(path, "w") as io:
        io.write(nwbfile)
