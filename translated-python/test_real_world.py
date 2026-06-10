"""End-to-end tests: many functions composed to solve real problems.

The unit and parity tests check functions one at a time. These tests run
the same kind of multi-step calculation a person would actually do (the
analysis in example_analysis.py) and pin the final numbers.

The pinned values were computed independently with Python's statistics
module before being hardcoded here, so they do not descend from either
the JavaScript library or its port.
"""

import statistics

import pytest

import mathlib

HOURS = [1, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 6.5, 7, 8]
SCORES = [52, 55, 60, 58, 64, 67, 70, 71, 78, 76, 84, 89]


class TestExamScoreAnalysis:
    def test_score_summary(self):
        assert mathlib.mean(SCORES) == pytest.approx(68.66666666666667)
        assert mathlib.median(SCORES) == pytest.approx(68.5)
        assert mathlib.standard_deviation(SCORES) == pytest.approx(11.57845438996959)

    def test_quartiles(self):
        assert mathlib.quantile(SCORES, 0.25) == pytest.approx(59.5)
        assert mathlib.quantile(SCORES, 0.50) == pytest.approx(68.5)
        assert mathlib.quantile(SCORES, 0.75) == pytest.approx(76.5)

    def test_correlation(self):
        assert mathlib.correlation(HOURS, SCORES) == pytest.approx(0.9877746142715493)

    def test_regression_fit(self):
        fit = mathlib.linear_regression(HOURS, SCORES)
        assert fit.slope == pytest.approx(5.315875613747955)
        assert fit.intercept == pytest.approx(45.188216039279865)
        assert fit.r2 == pytest.approx(0.9756986885993081)

    def test_prediction_at_7_5_hours(self):
        fit = mathlib.linear_regression(HOURS, SCORES)
        predicted = mathlib.add(fit.intercept, mathlib.multiply(fit.slope, 7.5))
        assert predicted == pytest.approx(85.05728314238954)

    def test_whole_pipeline_agrees_with_statistics_module(self):
        # The same pipeline, recomputed with the standard library.
        ours = mathlib.linear_regression(HOURS, SCORES)
        theirs = statistics.linear_regression(HOURS, SCORES)
        assert ours.slope == pytest.approx(theirs.slope)
        assert ours.intercept == pytest.approx(theirs.intercept)
        assert mathlib.correlation(HOURS, SCORES) == pytest.approx(
            statistics.correlation(HOURS, SCORES)
        )


class TestCompoundInterest:
    def test_composed_arithmetic(self):
        # $1,000 at 5% APR compounded monthly for 10 years, built from
        # add/divide/multiply/power rather than one formula.
        principal, rate, periods, years = 1000, 0.05, 12, 10
        growth = mathlib.power(
            mathlib.add(1, mathlib.divide(rate, periods)),
            mathlib.multiply(periods, years),
        )
        balance = mathlib.multiply(principal, growth)
        assert balance == pytest.approx(1647.00949769028)
        assert balance == pytest.approx(principal * (1 + rate / periods) ** (periods * years))
