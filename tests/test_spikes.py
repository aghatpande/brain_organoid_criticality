from __future__ import annotations

import numpy as np
import pytest

from brain_organoid_criticality.models import SortedSpikes
from brain_organoid_criticality.spikes import flatten_spike_times, validate_sorted_spikes


def test_flatten_spike_times_returns_sorted_population_vector(
    sorted_spikes_two_units: SortedSpikes,
) -> None:
    flattened = flatten_spike_times(sorted_spikes_two_units)

    assert flattened.ndim == 1
    assert np.all(np.diff(flattened) >= 0)


def test_flatten_spike_times_empty(sorted_spikes_empty: SortedSpikes) -> None:
    flattened = flatten_spike_times(sorted_spikes_empty)
    assert flattened.size == 0


def test_validate_sorted_spikes_rejects_unsorted_unit_times() -> None:
    bad = SortedSpikes(
        source_path=__file__,
        unit_ids=np.array([1]),
        spike_times_by_unit={1: np.array([0.4, 0.1])},
        t_start_s=0.0,
        t_stop_s=1.0,
    )

    with pytest.raises(ValueError, match="sorted within each unit"):
        validate_sorted_spikes(bad)
