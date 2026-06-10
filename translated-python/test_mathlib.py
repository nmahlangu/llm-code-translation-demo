"""Hand-written unit tests for the Python port.

These tests were written from the JavaScript source as a specification,
before the port was accepted. They pin down:

- expected results for typical inputs,
- edge cases (empty input, single element, duplicates, negatives,
  non-integer factorial, constant series),
- the exact Python exception type raised for each invalid input,
- mathematical properties that must hold regardless of implementation.

Where Python's standard library implements the same statistic, it is used
as an independent cross-check. That gives a second oracle that has nothing
to do with either the original JavaScript or the model that did the
translation: two unrelated implementations agreeing on the same numbers.
"""

import math
import statistics

import pytest

import mathlib

DATA = [2.5, 3.1, 4.8, 5.0, 6.2, 7.7, 8.1, 9.4]
XS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
YS = [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]


# ---------------------------------------------------------------------------
# Basic arithmetic
# ---------------------------------------------------------------------------


class TestArithmetic:
    def test_add(self):
        assert mathlib.add(2, 3) == 5
        assert mathlib.add(-2.5, 0.5) == -2.0
        assert mathlib.add(0.1, 0.2) == pytest.approx(0.3)

    def test_subtract(self):
        assert mathlib.subtract(10, 4) == 6
        assert mathlib.subtract(-5, -5) == 0

    def test_multiply(self):
        assert mathlib.multiply(6, 7) == 42
        assert mathlib.multiply(-4, 2.5) == -10.0

    def test_divide(self):
        assert mathlib.divide(10, 4) == 2.5
        assert mathlib.divide(1, 3) == pytest.approx(1 / 3)
        assert mathlib.divide(0, 5) == 0

    def test_divide_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            mathlib.divide(5, 0)

    def test_non_numeric_input_raises(self):
        with pytest.raises(TypeError):
            mathlib.add("2", 3)
        with pytest.raises(TypeError):
            mathlib.add(math.nan, 1)
        with pytest.raises(TypeError):
            mathlib.add(math.inf, 1)


class TestPower:
    def test_basics(self):
        assert mathlib.power(2, 10) == 1024
        assert mathlib.power(2, -2) == 0.25
        assert mathlib.power(9, 0.5) == 3.0
        assert mathlib.power(10, 0) == 1
        assert mathlib.power(-8, 2) == 64

    def test_complex_result_raises(self):
        # (-8) ** 0.5 would be a complex number in plain Python; the
        # library contract says non-real results are errors.
        with pytest.raises(ValueError):
            mathlib.power(-8, 0.5)

    def test_zero_to_negative_raises(self):
        with pytest.raises(ValueError):
            mathlib.power(0, -1)

    def test_overflow_raises(self):
        with pytest.raises(ValueError):
            mathlib.power(10, 400)


class TestSqrt:
    def test_basics(self):
        assert mathlib.sqrt(16) == 4
        assert mathlib.sqrt(0) == 0
        assert mathlib.sqrt(2) == pytest.approx(math.sqrt(2))

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            mathlib.sqrt(-4)


class TestFactorialAndCombinations:
    def test_factorial(self):
        assert mathlib.factorial(0) == 1
        assert mathlib.factorial(1) == 1
        assert mathlib.factorial(5) == 120
        assert mathlib.factorial(20) == 2432902008176640000

    def test_factorial_exact_beyond_float_precision(self):
        # Python integers are exact at sizes where 64-bit floats are not.
        assert mathlib.factorial(25) == math.factorial(25)

    def test_factorial_invalid_raises(self):
        with pytest.raises(ValueError):
            mathlib.factorial(-3)
        with pytest.raises(ValueError):
            mathlib.factorial(2.5)

    def test_combinations(self):
        assert mathlib.combinations(10, 3) == 120
        assert mathlib.combinations(52, 5) == 2598960
        assert mathlib.combinations(5, 0) == 1
        assert mathlib.combinations(5, 5) == 1
        assert mathlib.combinations(0, 0) == 1

    def test_combinations_symmetry(self):
        for n in range(0, 12):
            for k in range(0, n + 1):
                assert mathlib.combinations(n, k) == mathlib.combinations(n, n - k)

    def test_combinations_invalid_raises(self):
        with pytest.raises(ValueError):
            mathlib.combinations(6, 7)
        with pytest.raises(ValueError):
            mathlib.combinations(-1, 0)
        with pytest.raises(ValueError):
            mathlib.combinations(5, 2.5)


# ---------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------


class TestMeanMedian:
    def test_mean(self):
        assert mathlib.mean([1, 2, 3, 4]) == 2.5
        assert mathlib.mean([2.5]) == 2.5
        assert mathlib.mean([-1, 1]) == 0

    def test_mean_matches_statistics_module(self):
        assert mathlib.mean(DATA) == pytest.approx(statistics.fmean(DATA))

    def test_mean_empty_raises(self):
        with pytest.raises(ValueError):
            mathlib.mean([])

    def test_median_odd_and_even(self):
        assert mathlib.median([1, 3, 2]) == 2
        assert mathlib.median([4, 1, 3, 2]) == 2.5
        assert mathlib.median([7]) == 7

    def test_median_values_that_break_lexicographic_sort(self):
        # JavaScript's default sort orders [10, 9, 100, 1] as
        # [1, 10, 100, 9]. The original library sorts numerically; the
        # port must too.
        assert mathlib.median([10, 9, 100, 1]) == 9.5

    def test_median_matches_statistics_module(self):
        assert mathlib.median(DATA) == pytest.approx(statistics.median(DATA))


class TestVarianceAndStdDev:
    def test_sample_is_default(self):
        # Sample variance of 1..5 is 2.5; population variance is 2.0.
        assert mathlib.variance([1, 2, 3, 4, 5]) == pytest.approx(2.5)
        assert mathlib.variance([1, 2, 3, 4, 5], sample=False) == pytest.approx(2.0)

    def test_textbook_population_example(self):
        assert mathlib.variance([2, 4, 4, 4, 5, 5, 7, 9], sample=False) == pytest.approx(4.0)
        assert mathlib.standard_deviation(
            [2, 4, 4, 4, 5, 5, 7, 9], sample=False
        ) == pytest.approx(2.0)

    def test_matches_statistics_module(self):
        assert mathlib.variance(DATA) == pytest.approx(statistics.variance(DATA))
        assert mathlib.variance(DATA, sample=False) == pytest.approx(
            statistics.pvariance(DATA)
        )
        assert mathlib.standard_deviation(DATA) == pytest.approx(statistics.stdev(DATA))

    def test_stddev_squared_is_variance(self):
        assert mathlib.standard_deviation(DATA) ** 2 == pytest.approx(
            mathlib.variance(DATA)
        )

    def test_shift_invariance_and_scaling(self):
        shifted = [v + 1000 for v in DATA]
        scaled = [v * -3 for v in DATA]
        assert mathlib.variance(shifted) == pytest.approx(mathlib.variance(DATA))
        assert mathlib.standard_deviation(scaled) == pytest.approx(
            3 * mathlib.standard_deviation(DATA)
        )

    def test_single_value(self):
        assert mathlib.variance([5], sample=False) == 0
        with pytest.raises(ValueError):
            mathlib.variance([5])  # sample variance needs n >= 2


class TestQuantiles:
    def test_endpoints_and_median(self):
        data = [1, 2, 3, 4, 5]
        assert mathlib.quantile(data, 0) == min(data)
        assert mathlib.quantile(data, 1) == max(data)
        assert mathlib.quantile(data, 0.5) == mathlib.median(data)

    def test_interpolation(self):
        # Known NumPy/R type 7 result.
        assert mathlib.quantile([15, 20, 35, 40, 50], 0.4) == pytest.approx(29.0)

    def test_matches_statistics_quantiles_inclusive(self):
        # statistics.quantiles(method="inclusive") is the same type 7 method.
        q1, q2, q3 = statistics.quantiles(DATA, n=4, method="inclusive")
        assert mathlib.quantile(DATA, 0.25) == pytest.approx(q1)
        assert mathlib.quantile(DATA, 0.50) == pytest.approx(q2)
        assert mathlib.quantile(DATA, 0.75) == pytest.approx(q3)

    def test_percentile_is_quantile(self):
        assert mathlib.percentile(DATA, 40) == pytest.approx(mathlib.quantile(DATA, 0.4))

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            mathlib.quantile([1, 2, 3], 1.5)
        with pytest.raises(ValueError):
            mathlib.quantile([1, 2, 3], -0.1)
        with pytest.raises(ValueError):
            mathlib.percentile([1, 2, 3], 101)


# ---------------------------------------------------------------------------
# Bivariate statistics
# ---------------------------------------------------------------------------


class TestCovarianceCorrelation:
    def test_known_values(self):
        assert mathlib.covariance([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]) == pytest.approx(5.0)
        assert mathlib.covariance(
            [1, 2, 3, 4, 5], [2, 4, 6, 8, 10], sample=False
        ) == pytest.approx(4.0)

    def test_matches_statistics_module(self):
        assert mathlib.covariance(XS, YS) == pytest.approx(statistics.covariance(XS, YS))
        assert mathlib.correlation(XS, YS) == pytest.approx(
            statistics.correlation(XS, YS)
        )

    def test_perfect_correlation(self):
        assert mathlib.correlation([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]) == pytest.approx(1.0)
        assert mathlib.correlation([1, 2, 3, 4, 5], [10, 8, 6, 4, 2]) == pytest.approx(-1.0)

    def test_symmetry(self):
        assert mathlib.correlation(XS, YS) == pytest.approx(mathlib.correlation(YS, XS))

    def test_errors(self):
        with pytest.raises(ValueError):
            mathlib.covariance([1, 2, 3], [4, 5])  # length mismatch
        with pytest.raises(ValueError):
            mathlib.correlation([1, 2, 3], [7, 7, 7])  # constant input


class TestLinearRegression:
    def test_exact_fit(self):
        fit = mathlib.linear_regression([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
        assert fit.slope == pytest.approx(2.0)
        assert fit.intercept == pytest.approx(0.0)
        assert fit.r2 == pytest.approx(1.0)

    def test_matches_statistics_module(self):
        fit = mathlib.linear_regression(XS, YS)
        expected = statistics.linear_regression(XS, YS)
        assert fit.slope == pytest.approx(expected.slope)
        assert fit.intercept == pytest.approx(expected.intercept)
        assert fit.r2 == pytest.approx(statistics.correlation(XS, YS) ** 2)

    def test_r2_bounds(self):
        fit = mathlib.linear_regression(XS, YS)
        assert 0 <= fit.r2 <= 1

    def test_constant_y(self):
        fit = mathlib.linear_regression([1, 2, 3], [5, 5, 5])
        assert fit.slope == pytest.approx(0.0)
        assert fit.intercept == pytest.approx(5.0)
        assert fit.r2 == 1.0

    def test_constant_x_raises(self):
        with pytest.raises(ValueError):
            mathlib.linear_regression([2, 2, 2], [1, 2, 3])
