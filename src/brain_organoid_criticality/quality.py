from __future__ import annotations

from .models import SortedSpikes, SufficiencyReport


def check_sufficiency(
    sorted_spikes: SortedSpikes,
    *,
    min_units: int = 20,
    min_duration_s: float = 60.0,
    firing_rate_range_hz: tuple[float, float] = (0.01, 100.0),
    min_bins_for_bootstrap: int = 1000,
    bin_size_s: float = 0.003,
) -> SufficiencyReport:
    """Assess whether a recording can support a reliable DCC estimate.

    The function derives the descriptors named in the MVP specification
    (``n_units``, ``n_spikes``, ``duration_s``, ``mean_firing_rate_hz``,
    ``n_bins_at_default``) and compares each against a configurable threshold.
    Violations of the unit-count, duration, and bin-count thresholds are
    recorded as ``failures`` and set ``passes`` to ``False``; an implausible
    mean firing rate is recorded as a ``warning`` only.

    Parameters
    ----------
    sorted_spikes : SortedSpikes
        Canonical spike-times container to assess.
    min_units : int, optional
        Minimum number of units. Below this, multistep-regression ``tau`` fits
        become unstable on subsampled MEA data. Default ``20``.
    min_duration_s : float, optional
        Minimum recording duration in seconds. Default ``60``.
    firing_rate_range_hz : tuple of (float, float), optional
        Inclusive plausible range for the mean per-unit firing rate in hertz.
        Rates outside this range usually indicate noise or duplicate units.
        Default ``(0.01, 100.0)``.
    min_bins_for_bootstrap : int, optional
        Minimum number of bins at ``bin_size_s`` needed for a stable bootstrap.
        Default ``1000``.
    bin_size_s : float, optional
        Bin size in seconds used to compute ``n_bins_at_default``.
        Default ``0.003``.

    Returns
    -------
    SufficiencyReport
        Structured descriptors, ``warnings``, ``failures``, and a ``passes``
        verdict that is ``True`` only when no failure is recorded.

    Raises
    ------
    ValueError
        If ``bin_size_s`` is not positive.
    """
    if bin_size_s <= 0:
        raise ValueError(f"bin_size_s must be positive, got {bin_size_s}")

    n_units = int(sorted_spikes.unit_ids.size)
    n_spikes = int(
        sum(times.size for times in sorted_spikes.spike_times_by_unit.values())
    )
    duration_s = float(sorted_spikes.t_stop_s - sorted_spikes.t_start_s)

    if n_units > 0 and duration_s > 0:
        mean_firing_rate_hz = n_spikes / (n_units * duration_s)
    else:
        mean_firing_rate_hz = 0.0

    n_bins_at_default = int(duration_s // bin_size_s) if duration_s > 0 else 0

    warnings: list[str] = []
    failures: list[str] = []

    if n_units < min_units:
        failures.append(
            f"n_units={n_units} is below the minimum of {min_units}"
        )
    if duration_s < min_duration_s:
        failures.append(
            f"duration_s={duration_s:.3f} is below the minimum of {min_duration_s}"
        )
    if n_bins_at_default < min_bins_for_bootstrap:
        failures.append(
            f"n_bins_at_default={n_bins_at_default} is below the minimum of "
            f"{min_bins_for_bootstrap} bins required for bootstrap"
        )

    low, high = firing_rate_range_hz
    if mean_firing_rate_hz < low or mean_firing_rate_hz > high:
        warnings.append(
            f"mean_firing_rate_hz={mean_firing_rate_hz:.4f} is outside the "
            f"plausible range [{low}, {high}]"
        )

    return SufficiencyReport(
        passes=not failures,
        n_units=n_units,
        n_spikes=n_spikes,
        duration_s=duration_s,
        mean_firing_rate_hz=mean_firing_rate_hz,
        n_bins_at_default=n_bins_at_default,
        warnings=warnings,
        failures=failures,
    )
