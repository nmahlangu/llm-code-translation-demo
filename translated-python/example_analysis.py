"""A small end-to-end analysis built only from the translated library.

Scenario: 12 students reported how many hours they studied for an exam,
and we have their scores. Summarize the scores, measure the association
between studying and performance, fit a regression line, and predict the
score for a student who studied 7.5 hours.

Every number printed here comes from mathlib.py, the Python port of the
original JavaScript library. test_real_world.py pins these results.

Run with:  python3 example_analysis.py
"""

import mathlib

HOURS = [1, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 6.5, 7, 8]
SCORES = [52, 55, 60, 58, 64, 67, 70, 71, 78, 76, 84, 89]


def main() -> None:
    print("Study hours vs. exam scores (n = %d students)" % len(SCORES))
    print()

    print("Score summary")
    print(f"  mean               {mathlib.mean(SCORES):8.2f}")
    print(f"  median             {mathlib.median(SCORES):8.2f}")
    print(f"  sample std dev     {mathlib.standard_deviation(SCORES):8.2f}")
    print(f"  1st quartile       {mathlib.quantile(SCORES, 0.25):8.2f}")
    print(f"  3rd quartile       {mathlib.quantile(SCORES, 0.75):8.2f}")
    print(f"  90th percentile    {mathlib.percentile(SCORES, 90):8.2f}")
    print()

    r = mathlib.correlation(HOURS, SCORES)
    print(f"Correlation between hours studied and score: r = {r:.4f}")
    print()

    fit = mathlib.linear_regression(HOURS, SCORES)
    print("Least squares fit:")
    print(f"  score = {fit.intercept:.2f} + {fit.slope:.2f} * hours   (R^2 = {fit.r2:.4f})")
    predicted = mathlib.add(fit.intercept, mathlib.multiply(fit.slope, 7.5))
    print(f"  predicted score after 7.5 hours of study: {predicted:.1f}")
    print()

    # A second mini-scenario using the arithmetic primitives: compound
    # interest, $1,000 at 5% APR compounded monthly for 10 years.
    principal, rate, periods, years = 1000, 0.05, 12, 10
    growth = mathlib.power(
        mathlib.add(1, mathlib.divide(rate, periods)),
        mathlib.multiply(periods, years),
    )
    balance = mathlib.multiply(principal, growth)
    print("Compound interest check: $1,000 at 5% APR, monthly, 10 years")
    print(f"  final balance: ${balance:,.2f}")


if __name__ == "__main__":
    main()
