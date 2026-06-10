/**
 * generate_vectors.js
 *
 * Executes the ORIGINAL JavaScript library across a battery of inputs and
 * records exactly what it returned (or what it threw) in test_vectors.json.
 *
 * This file is the heart of the demo's trust model: the recorded outputs
 * come from running the original program, not from anyone's (or any
 * model's) opinion of what the outputs should be. The Python port is then
 * required to reproduce every recorded case (see
 * ../translated-python/test_parity.py).
 *
 * Run with:  node generate_vectors.js
 */

'use strict';

const fs = require('fs');
const path = require('path');
const lib = require('./mathlib.js');

// Shorthand: c('fn', arg1, arg2, ...) builds one test case.
function c(fn, ...args) {
  return { function: fn, args };
}

const cases = [
  // add: typical, negatives, classic floating point (0.1 + 0.2)
  c('add', 2, 3),
  c('add', -2.5, 0.5),
  c('add', 0.1, 0.2),
  c('add', 1e15, 1),
  c('add', 0, 0),

  // subtract
  c('subtract', 10, 4),
  c('subtract', 0.3, 0.1),
  c('subtract', -5, -5),
  c('subtract', 1, 1e-10),

  // multiply
  c('multiply', 6, 7),
  c('multiply', 0.1, 0.3),
  c('multiply', -4, 2.5),
  c('multiply', 1e8, 1e8),

  // divide, including the division-by-zero contract
  c('divide', 10, 4),
  c('divide', 1, 3),
  c('divide', -7, 2),
  c('divide', 0, 5),
  c('divide', 5, 0),

  // power, including cases where JavaScript and Python disagree by default:
  // 0 ** -1 is Infinity in JS; (-8) ** 0.5 is NaN in JS but a complex
  // number in Python. The library treats both as errors.
  c('power', 2, 10),
  c('power', 2, -2),
  c('power', 9, 0.5),
  c('power', 10, 0),
  c('power', -8, 2),
  c('power', -8, 0.5),
  c('power', 0, -1),

  // sqrt
  c('sqrt', 16),
  c('sqrt', 2),
  c('sqrt', 0),
  c('sqrt', -4),

  // factorial (kept <= 20 so the value is exact in a 64-bit float; see
  // the README section on judgment calls for the n > 170 overflow story)
  c('factorial', 0),
  c('factorial', 1),
  c('factorial', 5),
  c('factorial', 10),
  c('factorial', 20),
  c('factorial', -3),
  c('factorial', 2.5),

  // combinations
  c('combinations', 10, 3),
  c('combinations', 52, 5),
  c('combinations', 5, 0),
  c('combinations', 5, 5),
  c('combinations', 0, 0),
  c('combinations', 6, 7),
  c('combinations', -1, 0),
  c('combinations', 5, 2.5),

  // mean
  c('mean', [1, 2, 3, 4]),
  c('mean', [2.5]),
  c('mean', [-1, 1]),
  c('mean', [0.1, 0.2, 0.3]),
  c('mean', []),

  // median: odd and even lengths, unsorted input, values that would be
  // mis-sorted by JavaScript's default lexicographic sort
  c('median', [1, 3, 2]),
  c('median', [4, 1, 3, 2]),
  c('median', [10, 9, 100, 1]),
  c('median', [7]),
  c('median', [5, 5, 5, 5]),

  // variance: sample (default) vs population
  c('variance', [1, 2, 3, 4, 5]),
  c('variance', [1, 2, 3, 4, 5], { sample: false }),
  c('variance', [2, 4, 4, 4, 5, 5, 7, 9], { sample: false }),
  c('variance', [2, 4, 4, 4, 5, 5, 7, 9]),
  c('variance', [5], { sample: false }),
  c('variance', [5]),

  // standardDeviation
  c('standardDeviation', [1, 2, 3, 4, 5]),
  c('standardDeviation', [2, 4, 4, 4, 5, 5, 7, 9], { sample: false }),
  c('standardDeviation', [3, 3, 3]),

  // quantile (R type 7 interpolation)
  c('quantile', [1, 2, 3, 4, 5], 0),
  c('quantile', [1, 2, 3, 4, 5], 0.25),
  c('quantile', [1, 2, 3, 4, 5], 0.5),
  c('quantile', [1, 2, 3, 4, 5], 1),
  c('quantile', [15, 20, 35, 40, 50], 0.4),
  c('quantile', [3, 1, 2], 0.5),
  c('quantile', [1, 2, 3], 1.5),
  c('quantile', [1, 2, 3], -0.1),

  // percentile
  c('percentile', [15, 20, 35, 40, 50], 40),
  c('percentile', [1, 2, 3, 4], 75),
  c('percentile', [1, 2, 3, 4], 101),

  // covariance
  c('covariance', [1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
  c('covariance', [1, 2, 3, 4, 5], [2, 4, 6, 8, 10], { sample: false }),
  c('covariance', [1, 2, 3], [4, 5]),
  c('covariance', [1, 2, 3], [7, 7, 7]),

  // correlation
  c('correlation', [1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
  c('correlation', [1, 2, 3, 4, 5], [10, 8, 6, 4, 2]),
  c('correlation', [1, 2, 3, 4, 5], [2, 1, 4, 3, 5]),
  c('correlation', [1, 2, 3], [7, 7, 7]),

  // linearRegression
  c('linearRegression', [1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
  c('linearRegression', [1, 2, 3, 4, 5], [5, 4, 6, 5, 7]),
  c('linearRegression', [1, 2, 3], [5, 5, 5]),
  c('linearRegression', [2, 2, 2], [1, 2, 3]),
];

const results = cases.map(({ function: fn, args }) => {
  try {
    const result = lib[fn](...args);
    return { function: fn, args, result };
  } catch (err) {
    return { function: fn, args, throws: true, error: String(err.message) };
  }
});

const payload = {
  description:
    'Golden test vectors produced by EXECUTING the original JavaScript ' +
    'library (mathlib.js). Each case records the inputs passed to a ' +
    'function and the exact value it returned, or the fact that it threw. ' +
    'The Python port must reproduce every case; see test_parity.py.',
  generator: 'generate_vectors.js, run with Node.js ' + process.version,
  count: results.length,
  cases: results,
};

const outPath = path.join(__dirname, 'test_vectors.json');
fs.writeFileSync(outPath, JSON.stringify(payload, null, 2) + '\n');
console.log('Wrote ' + results.length + ' cases to ' + outPath);
