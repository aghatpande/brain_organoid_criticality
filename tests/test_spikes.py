from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from brain_organoid_criticality.models import SortedSpikes
from brain_organoid_criticality.spikes import flatten_spike_times, validate_sorted_spikes


def test_flatten_spike_times_returns_sorted_population_vector() -> None:
    sorted_spikes = SortedSpikes(
        source_path=Path("example.nwb"),
        unit_ids=np.array([1, 2]),
        spike_times_by_unit={
            1: np.array([0.3, 0.9]),
            2: np.array([0.1, 0.4]),
        },
        t_start_s=0.0,
        t_stop_s=1.0,
    )

    flattened = flatten_spike_times(sorted_spikes)

    np.testing.assert_allclose(flattened, np.array([0.1, 0.3, 0.4, 0.9]))


def test_validate_sorted_spikes_rejects_unsorted_unit_times() -> None:
    sorted_spikes = SortedSpikes(
        source_path=Path("example.nwb"),
        unit_ids=np.array([1]),
        spike_times_by_unit={1: np.array([0.4, 0.1])},
        t_start_s=0.0,
        t_stop_s=1.0,
    )

    with pytest.raises(ValueError, match="sorted within each unit"):
        validate_sorted_spikes(sorted_spikes)
