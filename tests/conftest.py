from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest

from brain_organoid_criticality.models import SortedSpikes


@pytest.fixture()
def sorted_spikes_two_units() -> SortedSpikes:
    return SortedSpikes(
        source_path=Path("synthetic.nwb"),
        unit_ids=np.array([1, 2]),
        spike_times_by_unit={
            1: np.array([0.1, 0.3, 0.5, 0.7, 0.9]),
            2: np.array([0.2, 0.4, 0.6, 0.8]),
        },
        t_start_s=0.0,
        t_stop_s=1.0,
    )


@pytest.fixture()
def sorted_spikes_single_unit() -> SortedSpikes:
    return SortedSpikes(
        source_path=Path("synthetic.nwb"),
        unit_ids=np.array([1]),
        spike_times_by_unit={1: np.array([0.1, 0.5])},
        t_start_s=0.0,
        t_stop_s=1.0,
    )


@pytest.fixture()
def sorted_spikes_empty() -> SortedSpikes:
    return SortedSpikes(
        source_path=Path("synthetic.nwb"),
        unit_ids=np.array([], dtype=int),
        spike_times_by_unit={},
        t_start_s=0.0,
        t_stop_s=0.0,
    )


@pytest.fixture()
def synthetic_nwb_path(tmp_path):
    pynwb = pytest.importorskip("pynwb")
    ElectricalSeries = pytest.importorskip("pynwb.ecephys").ElectricalSeries
    NWBFile = pynwb.NWBFile
    NWBHDF5IO = pynwb.NWBHDF5IO

    nwb_path = tmp_path / "synthetic.nwb"

    nwbfile = NWBFile(
        session_description="synthetic test session",
        identifier="SYNTH001",
        session_start_time=datetime.now(timezone.utc),
        session_id="session-synth",
        experiment_description="synthetic ecephys fixture",
    )

    device = nwbfile.create_device(name="test-probe")
    electrode_group = nwbfile.create_electrode_group(
        name="group",
        description="test electrodes",
        location="VISp",
        device=device,
    )
    for i in range(2):
        nwbfile.add_electrode(
            x=float(i), y=0.0, z=0.0,
            imp=np.nan, location="VISp",
            filtering="none", group=electrode_group,
        )

    electrodes = nwbfile.create_electrode_table_region(
        region=[0, 1], description="all electrodes"
    )
    data = np.arange(20, dtype=float).reshape(10, 2)
    nwbfile.add_acquisition(
        ElectricalSeries(
            name="ElectricalSeries",
            data=data,
            electrodes=electrodes,
            rate=1000.0,
            starting_time=0.0,
        )
    )
    nwbfile.add_unit(id=1, spike_times=[0.1, 0.3])
    nwbfile.add_unit(id=2, spike_times=[0.2, 0.5])

    with NWBHDF5IO(nwb_path, "w") as io:
        io.write(nwbfile)

    return nwb_path
