from __future__ import annotations

import numpy as np

from .models import BranchingRatioEstimate, DCCResult, SufficiencyReport


def _autoregressive_slopes(activity: np.ndarray, k_max: int) -> np.ndarray:
    """Return the regression slopes ``r(k) = Cov(A_t, A_{t+k}) / Var(A_t)``.

    Slopes are computed for lags ``k = 1 .. k_max`` from the biased
    autocovariance via the FFT, which is ``O(n log n)`` rather than
    ``O(n * k_max)``.
    """
    centered = activity - activity.mean()
    n = centered.size
    size = int(2 ** np.ceil(np.log2(2 * n)))
    spectrum = np.fft.rfft(centered, n=size)
    autocov = np.fft.irfft(spectrum * np.conjugate(spectrum), n=size)[: k_max + 1]
    autocov = autocov / n
    return autocov[1:] / autocov[0]


def _estimate_sigma(slopes: np.ndarray) -> tuple[float, float]:
    """Estimate sigma and the fit R-squared from autoregressive slopes.

    For a branching process ``r(k) = b * sigma**k``, so successive slopes obey
    ``r(k+1) = sigma * r(k)`` regardless of the offset ``b``. Sigma is the
    least-squares slope of ``r(k+1)`` on ``r(k)`` through the origin; weighting
    by ``r(k)`` lets the high-amplitude low lags dominate and suppresses the
    noise floor at high lags (so an uncorrelated series yields sigma near 0).
    """
    current = slopes[:-1]
    following = slopes[1:]
    denom = float(np.dot(current, current))
    sigma = float(np.dot(current, following) / denom)

    predicted = sigma * current
    ss_res = float(np.sum((following - predicted) ** 2))
    ss_tot = float(np.sum((following - following.mean()) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else 0.0
    r_squared = float(np.clip(r_squared, 0.0, 1.0))
    return sigma, r_squared


def branching_ratio(
    counts: np.ndarray,
    *,
    k_max: int = 150,
    method: str = "mr",
) -> BranchingRatioEstimate:
    """Estimate the branching ratio sigma from binned population activity.

    Implements the multistep-regression (MR) estimator of Wilting &
    Priesemann (2018). The autoregressive slopes ``r(k) = Cov(A_t, A_{t+k}) /
    Var(A_t)`` decay as ``r(k) = b * sigma**k`` for a branching process; sigma
    is recovered from the geometric decay rate and is invariant to the offset
    ``b`` that spatial subsampling introduces, which is why the MR estimator is
    robust to MEA-style subsampling.

    Parameters
    ----------
    counts : np.ndarray
        Binned population spike counts, one value per time bin.
    k_max : int, optional
        Largest lag (in bins) used to fit the slope decay. Reduced internally
        when the series is too short to support it. Default ``150``.
    method : str, optional
        Estimator variant. Only ``"mr"`` (multistep regression) is supported.
        Default ``"mr"``.

    Returns
    -------
    BranchingRatioEstimate
        The estimated sigma with its autocorrelation time, fit quality, and
        the slopes used.

    Raises
    ------
    ValueError
        If ``method`` is not ``"mr"``, the series has fewer than three bins,
        ``k_max`` is not positive, or the activity has zero variance.
    """
    if method != "mr":
        raise ValueError(f"Unknown method {method!r}; only 'mr' is supported")
    if k_max < 1:
        raise ValueError(f"k_max must be positive, got {k_max}")

    activity = np.asarray(counts, dtype=float)
    n = activity.size
    if n < 3:
        raise ValueError(
            f"counts must have at least 3 bins to estimate sigma, got {n}"
        )
    if activity.var() == 0.0:
        raise ValueError("population activity has zero variance")

    k_max_eff = min(k_max, n - 2)
    slopes = _autoregressive_slopes(activity, k_max_eff)
    k_used = np.arange(1, k_max_eff + 1)

    sigma, r_squared = _estimate_sigma(slopes)
    tau_bins = -1.0 / np.log(sigma) if 0.0 < sigma < 1.0 else float("inf")

    return BranchingRatioEstimate(
        sigma=sigma,
        tau_bins=tau_bins,
        r_squared=r_squared,
        k_used=k_used,
        r_values=slopes,
    )


def _block_bootstrap_indices(
    n: int, block_size: int, rng: np.random.Generator
) -> np.ndarray:
    """Build resample indices from contiguous blocks covering ``n`` samples."""
    n_blocks = int(np.ceil(n / block_size))
    starts = rng.integers(0, n - block_size + 1, size=n_blocks)
    offsets = np.arange(block_size)
    indices = (starts[:, None] + offsets[None, :]).ravel()
    return indices[:n]


def distance_to_criticality(
    counts: np.ndarray,
    *,
    n_bootstrap: int = 1000,
    sufficiency: SufficiencyReport | None = None,
    k_max: int = 150,
    block_size: int | None = None,
    seed: int | None = None,
) -> DCCResult:
    """Compute the distance-to-criticality coefficient ``DCC = 1 - sigma``.

    The branching ratio sigma is estimated with the MR estimator and a
    confidence interval on ``DCC`` is obtained by a moving-block bootstrap that
    preserves the temporal correlation the estimator depends on. When a
    :class:`SufficiencyReport` is supplied and does not pass, no point estimate
    is computed and all estimate fields are returned as ``None``.

    Parameters
    ----------
    counts : np.ndarray
        Binned population spike counts, one value per time bin.
    n_bootstrap : int, optional
        Number of bootstrap resamples. Default ``1000``.
    sufficiency : SufficiencyReport or None, optional
        If provided and ``sufficiency.passes`` is ``False``, the function
        refuses to return a point estimate. Default ``None``.
    k_max : int, optional
        Largest lag passed to :func:`branching_ratio`. Default ``150``.
    block_size : int or None, optional
        Block length (in bins) for the moving-block bootstrap. Defaults to
        ``k_max`` so each block preserves the lag structure the estimator uses.
    seed : int or None, optional
        Seed for the bootstrap resampling, for reproducibility. Default
        ``None``.

    Returns
    -------
    DCCResult
        The DCC point estimate, bootstrap confidence interval, and the
        underlying branching-ratio estimate; estimate fields are ``None`` when
        sufficiency fails.

    Raises
    ------
    ValueError
        Propagated from :func:`branching_ratio` for invalid input when a point
        estimate is computed.
    """
    if sufficiency is not None and not sufficiency.passes:
        return DCCResult(
            dcc=None,
            ci_lower=None,
            ci_upper=None,
            branching=None,
            sufficiency=sufficiency,
            bootstrap_n=n_bootstrap,
        )

    activity = np.asarray(counts, dtype=float)
    branching = branching_ratio(activity, k_max=k_max)
    dcc = 1.0 - branching.sigma

    effective_block = block_size if block_size is not None else k_max
    effective_block = min(effective_block, activity.size - 2)
    rng = np.random.default_rng(seed)

    dcc_samples = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        indices = _block_bootstrap_indices(activity.size, effective_block, rng)
        resampled = activity[indices]
        sample = branching_ratio(resampled, k_max=k_max)
        dcc_samples[i] = 1.0 - sample.sigma

    ci_lower = float(np.percentile(dcc_samples, 2.5))
    ci_upper = float(np.percentile(dcc_samples, 97.5))

    return DCCResult(
        dcc=dcc,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        branching=branching,
        sufficiency=sufficiency,
        bootstrap_n=n_bootstrap,
    )
