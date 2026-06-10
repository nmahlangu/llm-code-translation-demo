"""mathlib.py

Python port of ../original-javascript/mathlib.js, produced by an LLM coding
agent (Claude Code). The port is idiomatic Python rather than a line-by-line
transliteration:

- snake_case names (standardDeviation -> standard_deviation)
- type hints and docstrings
- standard Python exceptions (TypeError, ValueError, ZeroDivisionError)
- a NamedTuple result for linear_regression instead of a plain object
- {sample: false} options objects become a sample=False keyword argument

Numerical behavior is required to match the original exactly. That claim is
enforced, not assumed: test_parity.py replays 86 recorded input/output pairs
produced by executing the original JavaScript, and test_mathlib.py
cross-checks against Python's statistics module. See the README.

Deliberate semantic notes, mirrored from the original:

- Invalid input raises. Functions never return NaN or Infinity. JavaScript
  natively returns Infinity for 1/0 and NaN for sqrt(-1); the original
  library treats both as errors, so this port does too.
- power() uses math.pow rather than the ** operator: in Python,
  (-8) ** 0.5 silently returns a complex number, while the original
  JavaScript treats a non-real result as an error.
- factorial() delegates to math.factorial, which is exact for any n because
  Python integers do not overflow. JavaScript's 64-bit floats overflow above
  170!. The shared, tested domain is n <= 170; behavior above that is
  documented here as an intentional difference (Python keeps working).
- variance/standard_deviation/covariance default to the SAMPLE statistic
  (n - 1 denominator), matching R. Pass sample=False for population.
- quantile uses linear interpolation between order statistics (R type 7,
  NumPy default, statistics.quantiles(method="inclusive")).
"""

from __future__ import annotations

import math
from typing import NamedTuple, Sequence

__all__ = [
    "add",
    "subtract",
    "multiply",
    "divide",
    "power",
    "sqrt",
    "factorial",
    "combinations",
    "mean",
    "median",
    "variance",
    "standard_deviation",
    "quantile",
    "percentile",
    "covariance",
    "correlation",
    "linear_regression",
    "LinearRegressionResult",
]

Number = float | int


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------


def _check_number(value: Number, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite number")
    if not math.isfinite(value):
        raise TypeError(f"{name} must be a finite number")


def _check_number_sequence(values: Sequence[Number], name: str, min_length: int) -> None:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of numbers")
    if len(values) < min_length:
        raise ValueError(f"{name} must contain at least {min_length} element(s)")
    for v in values:
        _check_number(v, f"every element of {name}")


def _check_same_length(xs: Sequence[Number], ys: Sequence[Number]) -> None:
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")


# ---------------------------------------------------------------------------
# Basic arithmetic
# ---------------------------------------------------------------------------


def add(a: Number, b: Number) -> float:
    """Return a + b."""
    _check_number(a, "a")
    _check_number(b, "b")
    return a + b


def subtract(a: Number, b: Number) -> float:
    """Return a - b."""
    _check_number(a, "a")
    _check_number(b, "b")
    return a - b


def multiply(a: Number, b: Number) -> float:
    """Return a * b."""
    _check_number(a, "a")
    _check_number(b, "b")
    return a * b


def divide(a: Number, b: Number) -> float:
    """Return a / b. Raises ZeroDivisionError when b is 0."""
    _check_number(a, "a")
    _check_number(b, "b")
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


def power(base: Number, exponent: Number) -> float:
    """Return base raised to exponent.

    Raises ValueError when the result is not a finite real number, e.g.
    power(0, -1) or power(-8, 0.5). math.pow is used instead of ** so that
    a negative base with a fractional exponent is an error, as in the
    original, rather than a complex number.
    """
    _check_number(base, "base")
    _check_number(exponent, "exponent")
    try:
        result = math.pow(base, exponent)
    except (ValueError, OverflowError) as exc:
        raise ValueError("power: result is not a finite real number") from exc
    if not math.isfinite(result):
        raise ValueError("power: result is not a finite real number")
    return result


def sqrt(x: Number) -> float:
    """Return the square root of x. Raises ValueError for negative x."""
    _check_number(x, "x")
    if x < 0:
        raise ValueError("sqrt: x must be non-negative")
    return math.sqrt(x)


def factorial(n: Number) -> int:
    """Return n! for a non-negative integer n.

    Raises ValueError for negative or non-integer n. Unlike the JavaScript
    original, the result is an exact integer for any n (Python integers do
    not overflow); the original overflows above n = 170.
    """
    _check_number(n, "n")
    if isinstance(n, float):
        if not n.is_integer():
            raise ValueError("factorial: n must be a non-negative integer")
        n = int(n)
    if n < 0:
        raise ValueError("factorial: n must be a non-negative integer")
    return math.factorial(n)


def combinations(n: Number, k: Number) -> int:
    """Return the binomial coefficient C(n, k).

    Raises ValueError unless n and k are integers with 0 <= k <= n.
    """
    _check_number(n, "n")
    _check_number(k, "k")
    if isinstance(n, float):
        if not n.is_integer():
            raise ValueError("combinations: need integers with 0 <= k <= n")
        n = int(n)
    if isinstance(k, float):
        if not k.is_integer():
            raise ValueError("combinations: need integers with 0 <= k <= n")
        k = int(k)
    if n < 0 or k < 0 or k > n:
        raise ValueError("combinations: need integers with 0 <= k <= n")
    return math.comb(n, k)


# ---------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------


def mean(values: Sequence[Number]) -> float:
    """Return the arithmetic mean of a non-empty sequence."""
    _check_number_sequence(values, "values", 1)
    return sum(values) / len(values)


def median(values: Sequence[Number]) -> float:
    """Return the median of a non-empty sequence."""
    _check_number_sequence(values, "values", 1)
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def variance(values: Sequence[Number], *, sample: bool = True) -> float:
    """Return the variance of a sequence.

    Sample variance (n - 1 denominator) by default, matching R; pass
    sample=False for population variance. Sample variance requires at
    least 2 values.
    """
    _check_number_sequence(values, "values", 2 if sample else 1)
    m = mean(values)
    sum_sq = 0.0
    for v in values:
        sum_sq += (v - m) * (v - m)
    return sum_sq / (len(values) - (1 if sample else 0))


def standard_deviation(values: Sequence[Number], *, sample: bool = True) -> float:
    """Return the standard deviation: the square root of variance()."""
    return math.sqrt(variance(values, sample=sample))


def quantile(values: Sequence[Number], q: Number) -> float:
    """Return the q-th quantile (0 <= q <= 1) of a non-empty sequence.

    Uses linear interpolation between order statistics (R type 7, the
    NumPy default). Raises ValueError when q is outside [0, 1].
    """
    _check_number_sequence(values, "values", 1)
    _check_number(q, "q")
    if q < 0 or q > 1:
        raise ValueError("quantile: q must be between 0 and 1")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def percentile(values: Sequence[Number], p: Number) -> float:
    """Return the p-th percentile (0 <= p <= 100): quantile(values, p / 100)."""
    _check_number(p, "p")
    if p < 0 or p > 100:
        raise ValueError("percentile: p must be between 0 and 100")
    return quantile(values, p / 100)


# ---------------------------------------------------------------------------
# Bivariate statistics
# ---------------------------------------------------------------------------


def covariance(
    xs: Sequence[Number], ys: Sequence[Number], *, sample: bool = True
) -> float:
    """Return the covariance of two equal-length sequences.

    Sample covariance (n - 1 denominator) by default; pass sample=False
    for the population statistic.
    """
    min_length = 2 if sample else 1
    _check_number_sequence(xs, "xs", min_length)
    _check_number_sequence(ys, "ys", min_length)
    _check_same_length(xs, ys)
    mx = mean(xs)
    my = mean(ys)
    total = 0.0
    for x, y in zip(xs, ys):
        total += (x - mx) * (y - my)
    return total / (len(xs) - (1 if sample else 0))


def correlation(xs: Sequence[Number], ys: Sequence[Number]) -> float:
    """Return the Pearson correlation coefficient of two sequences.

    Raises ValueError when either sequence is constant (undefined).
    """
    cov = covariance(xs, ys, sample=True)
    sx = standard_deviation(xs, sample=True)
    sy = standard_deviation(ys, sample=True)
    if sx == 0 or sy == 0:
        raise ValueError("correlation: undefined for constant input")
    return cov / (sx * sy)


class LinearRegressionResult(NamedTuple):
    """Ordinary least squares fit: y = intercept + slope * x."""

    slope: float
    intercept: float
    r2: float


def linear_regression(
    xs: Sequence[Number], ys: Sequence[Number]
) -> LinearRegressionResult:
    """Fit ordinary least squares y = intercept + slope * x.

    Raises ValueError when xs is constant. When ys is constant the fit is
    exact and r2 is defined as 1.
    """
    var_x = variance(xs, sample=True)
    if var_x == 0:
        raise ValueError("linear_regression: xs must not be constant")
    slope = covariance(xs, ys, sample=True) / var_x
    intercept = mean(ys) - slope * mean(xs)
    my = mean(ys)
    ss_res = 0.0
    ss_tot = 0.0
    for x, y in zip(xs, ys):
        fitted = intercept + slope * x
        ss_res += (y - fitted) * (y - fitted)
        ss_tot += (y - my) * (y - my)
    r2 = 1.0 if ss_tot == 0 else 1 - ss_res / ss_tot
    return LinearRegressionResult(slope=slope, intercept=intercept, r2=r2)
