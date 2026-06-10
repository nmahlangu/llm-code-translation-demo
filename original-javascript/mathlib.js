/**
 * mathlib.js
 *
 * A small arithmetic and statistics library in plain JavaScript (Node.js).
 *
 * This is the ORIGINAL source in the translation demo. The Python port in
 * ../translated-python/mathlib.py was produced from this file by an LLM
 * coding agent, and the test suite verifies that the two implementations
 * behave identically.
 *
 * Design decisions (the Python port must preserve these):
 *
 * - Invalid input raises an error. Functions never return NaN or Infinity.
 *   (Plain JavaScript would happily return Infinity for 1/0 and NaN for
 *   Math.sqrt(-1); this library treats both as errors.)
 * - variance, standardDeviation, and covariance compute the SAMPLE statistic
 *   by default (n - 1 denominator), matching R. Pass {sample: false} for the
 *   population statistic (n denominator).
 * - quantile uses linear interpolation between order statistics, the same
 *   method as R's default (type 7) and NumPy's default.
 */

'use strict';

// ---------------------------------------------------------------------------
// Input validation helpers
// ---------------------------------------------------------------------------

function assertFiniteNumber(value, name) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError(name + ' must be a finite number');
  }
}

function assertNumberArray(values, name, minLength) {
  if (!Array.isArray(values)) {
    throw new TypeError(name + ' must be an array of numbers');
  }
  if (values.length < minLength) {
    throw new RangeError(name + ' must contain at least ' + minLength + ' element(s)');
  }
  for (const v of values) {
    assertFiniteNumber(v, 'every element of ' + name);
  }
}

function assertSameLength(xs, ys) {
  if (xs.length !== ys.length) {
    throw new RangeError('xs and ys must have the same length');
  }
}

// ---------------------------------------------------------------------------
// Basic arithmetic
// ---------------------------------------------------------------------------

/** Returns a + b. */
function add(a, b) {
  assertFiniteNumber(a, 'a');
  assertFiniteNumber(b, 'b');
  return a + b;
}

/** Returns a - b. */
function subtract(a, b) {
  assertFiniteNumber(a, 'a');
  assertFiniteNumber(b, 'b');
  return a - b;
}

/** Returns a * b. */
function multiply(a, b) {
  assertFiniteNumber(a, 'a');
  assertFiniteNumber(b, 'b');
  return a * b;
}

/**
 * Returns a / b.
 * Throws RangeError when b is 0. (Plain JavaScript would return Infinity.)
 */
function divide(a, b) {
  assertFiniteNumber(a, 'a');
  assertFiniteNumber(b, 'b');
  if (b === 0) {
    throw new RangeError('division by zero');
  }
  return a / b;
}

/**
 * Returns base raised to exponent.
 * Throws RangeError when the result is not a finite real number, e.g.
 * power(0, -1) (division by zero) or power(-8, 0.5) (complex result).
 */
function power(base, exponent) {
  assertFiniteNumber(base, 'base');
  assertFiniteNumber(exponent, 'exponent');
  const result = Math.pow(base, exponent);
  if (!Number.isFinite(result)) {
    throw new RangeError('power: result is not a finite real number');
  }
  return result;
}

/**
 * Returns the square root of x.
 * Throws RangeError for negative x. (Math.sqrt would return NaN.)
 */
function sqrt(x) {
  assertFiniteNumber(x, 'x');
  if (x < 0) {
    throw new RangeError('sqrt: x must be non-negative');
  }
  return Math.sqrt(x);
}

/**
 * Returns n! for a non-negative integer n.
 * Throws RangeError for negative or non-integer n, and for n large enough
 * that the result overflows a 64-bit float (n > 170).
 */
function factorial(n) {
  assertFiniteNumber(n, 'n');
  if (!Number.isInteger(n) || n < 0) {
    throw new RangeError('factorial: n must be a non-negative integer');
  }
  let result = 1;
  for (let i = 2; i <= n; i++) {
    result *= i;
  }
  if (!Number.isFinite(result)) {
    throw new RangeError('factorial: result overflows a 64-bit float');
  }
  return result;
}

/**
 * Returns the binomial coefficient C(n, k): the number of ways to choose
 * k items from n. Throws RangeError unless n and k are integers with
 * 0 <= k <= n.
 */
function combinations(n, k) {
  assertFiniteNumber(n, 'n');
  assertFiniteNumber(k, 'k');
  if (!Number.isInteger(n) || !Number.isInteger(k) || n < 0 || k < 0 || k > n) {
    throw new RangeError('combinations: need integers with 0 <= k <= n');
  }
  if (k > n - k) {
    k = n - k;
  }
  let result = 1;
  for (let i = 1; i <= k; i++) {
    result = (result * (n - k + i)) / i;
  }
  return Math.round(result);
}

// ---------------------------------------------------------------------------
// Descriptive statistics
// ---------------------------------------------------------------------------

/** Returns the arithmetic mean of a non-empty array. */
function mean(values) {
  assertNumberArray(values, 'values', 1);
  let total = 0;
  for (const v of values) {
    total += v;
  }
  return total / values.length;
}

/**
 * Returns the median of a non-empty array.
 * Note the comparator passed to sort(): JavaScript's default sort is
 * LEXICOGRAPHIC, so [10, 9].sort() stays [10, 9]. A correct numeric sort
 * must be requested explicitly.
 */
function median(values) {
  assertNumberArray(values, 'values', 1);
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) {
    return sorted[mid];
  }
  return (sorted[mid - 1] + sorted[mid]) / 2;
}

/**
 * Returns the variance of an array.
 * Sample variance (n - 1 denominator) by default; pass {sample: false}
 * for population variance. Sample variance requires at least 2 values.
 */
function variance(values, { sample = true } = {}) {
  assertNumberArray(values, 'values', sample ? 2 : 1);
  const m = mean(values);
  let sumSq = 0;
  for (const v of values) {
    sumSq += (v - m) * (v - m);
  }
  return sumSq / (values.length - (sample ? 1 : 0));
}

/** Returns the standard deviation: the square root of variance(). */
function standardDeviation(values, options) {
  return Math.sqrt(variance(values, options));
}

/**
 * Returns the q-th quantile (0 <= q <= 1) of a non-empty array, using
 * linear interpolation between order statistics (R type 7, NumPy default).
 */
function quantile(values, q) {
  assertNumberArray(values, 'values', 1);
  assertFiniteNumber(q, 'q');
  if (q < 0 || q > 1) {
    throw new RangeError('quantile: q must be between 0 and 1');
  }
  const sorted = [...values].sort((a, b) => a - b);
  const position = (sorted.length - 1) * q;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) {
    return sorted[lower];
  }
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

/** Returns the p-th percentile (0 <= p <= 100). Equal to quantile(values, p / 100). */
function percentile(values, p) {
  assertFiniteNumber(p, 'p');
  if (p < 0 || p > 100) {
    throw new RangeError('percentile: p must be between 0 and 100');
  }
  return quantile(values, p / 100);
}

// ---------------------------------------------------------------------------
// Bivariate statistics
// ---------------------------------------------------------------------------

/**
 * Returns the covariance of two equal-length arrays.
 * Sample covariance (n - 1 denominator) by default; pass {sample: false}
 * for the population statistic.
 */
function covariance(xs, ys, { sample = true } = {}) {
  assertNumberArray(xs, 'xs', sample ? 2 : 1);
  assertNumberArray(ys, 'ys', sample ? 2 : 1);
  assertSameLength(xs, ys);
  const mx = mean(xs);
  const my = mean(ys);
  let total = 0;
  for (let i = 0; i < xs.length; i++) {
    total += (xs[i] - mx) * (ys[i] - my);
  }
  return total / (xs.length - (sample ? 1 : 0));
}

/**
 * Returns the Pearson correlation coefficient of two equal-length arrays.
 * Throws RangeError when either array is constant (correlation undefined).
 */
function correlation(xs, ys) {
  const cov = covariance(xs, ys, { sample: true });
  const sx = standardDeviation(xs, { sample: true });
  const sy = standardDeviation(ys, { sample: true });
  if (sx === 0 || sy === 0) {
    throw new RangeError('correlation: undefined for constant input');
  }
  return cov / (sx * sy);
}

/**
 * Fits ordinary least squares y = intercept + slope * x.
 * Returns {slope, intercept, r2}. Throws RangeError when xs is constant.
 * When ys is constant the fit is exact and r2 is defined as 1.
 */
function linearRegression(xs, ys) {
  const varX = variance(xs, { sample: true });
  if (varX === 0) {
    throw new RangeError('linearRegression: xs must not be constant');
  }
  const slope = covariance(xs, ys, { sample: true }) / varX;
  const intercept = mean(ys) - slope * mean(xs);
  const my = mean(ys);
  let ssRes = 0;
  let ssTot = 0;
  for (let i = 0; i < xs.length; i++) {
    const fitted = intercept + slope * xs[i];
    ssRes += (ys[i] - fitted) * (ys[i] - fitted);
    ssTot += (ys[i] - my) * (ys[i] - my);
  }
  const r2 = ssTot === 0 ? 1 : 1 - ssRes / ssTot;
  return { slope, intercept, r2 };
}

module.exports = {
  add,
  subtract,
  multiply,
  divide,
  power,
  sqrt,
  factorial,
  combinations,
  mean,
  median,
  variance,
  standardDeviation,
  quantile,
  percentile,
  covariance,
  correlation,
  linearRegression,
};
