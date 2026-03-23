import numpy as np


def bin_spike_times(spike_times, bin_size: float, t_start=None, t_stop=None):
    """
    Bin spike times into uniform bins.

    Parameters
    ----------
    spike_times : array-like
        Spike times in seconds.
    bin_size : float
        Bin size in seconds.
    t_start : float, optional
        Start time. Defaults to min(spike_times).
    t_stop : float, optional
        Stop time. Defaults to max(spike_times).

    Returns
    -------
    counts : np.ndarray
        Spike counts per bin.
    edges : np.ndarray
        Bin edges.
    """
    spike_times = np.asarray(spike_times)

    if spike_times.size == 0:
        raise ValueError("spike_times cannot be empty")
    if bin_size <= 0:
        raise ValueError("bin_size must be positive")

    if t_start is None:
        t_start = float(spike_times.min())
    if t_stop is None:
        t_stop = float(spike_times.max())

    edges = np.arange(t_start, t_stop + bin_size, bin_size)
    counts, _ = np.histogram(spike_times, bins=edges)
    return counts, edges
