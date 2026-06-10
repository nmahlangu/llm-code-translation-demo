"""Cross-language parity tests: the strongest evidence in this repo.

../original-javascript/test_vectors.json was produced by EXECUTING the
original JavaScript library with Node.js (see generate_vectors.js). Every
recorded case is replayed here against the Python port:

- if the JavaScript returned a value, Python must return the same value
  (within a tight floating point tolerance, rel=1e-9);
- if the JavaScript threw an error, Python must raise one too.

The point of this layer: the definition of "correct" comes from running the
original program, not from a human's or a model's belief about what the
program does.
"""

import json
from pathlib import Path

import pytest

import mathlib

VECTORS_PATH = (
    Path(__file__).resolve().parent.parent / "original-javascript" / "test_vectors.json"
)
VECTORS = json.loads(VECTORS_PATH.read_text())
CASES = VECTORS["cases"]

# The port is idiomatic Python, so two functions changed name.
NAME_MAP = {
    "standardDeviation": "standard_deviation",
    "linearRegression": "linear_regression",
}

CASE_IDS = [f"{i:03d}-{case['function']}" for i, case in enumerate(CASES)]


def split_args(raw_args):
    """A trailing JS options object like {"sample": false} becomes kwargs."""
    if raw_args and isinstance(raw_args[-1], dict):
        return raw_args[:-1], raw_args[-1]
    return raw_args, {}


def test_vector_file_provenance():
    assert "EXECUTING the original JavaScript" in VECTORS["description"]
    assert VECTORS["count"] == len(CASES) == 86


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_parity(case):
    fn = getattr(mathlib, NAME_MAP.get(case["function"], case["function"]))
    args, kwargs = split_args(case["args"])

    if case.get("throws"):
        # Error parity: both implementations must reject this input. The
        # exact exception type is Python's own idiom (ValueError,
        # ZeroDivisionError, ...) and is pinned in test_mathlib.py.
        with pytest.raises(Exception):
            fn(*args, **kwargs)
        return

    result = fn(*args, **kwargs)
    expected = case["result"]
    if isinstance(expected, dict):
        # linearRegression returns an object; the port returns a NamedTuple.
        for key, value in expected.items():
            assert getattr(result, key) == pytest.approx(value, rel=1e-9, abs=1e-12)
    else:
        assert result == pytest.approx(expected, rel=1e-9, abs=1e-12)
