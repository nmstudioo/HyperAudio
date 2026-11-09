#!/usr/bin/env python3
'Regression test: there is exactly one limiter gate policy and it is the strict one.'
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from limiter_tests import gate_limits

assert gate_limits("release") == (0.5, 0.5)

for bad in ("unknown", "stable-v5", "candidate-v7"):
    try:
        gate_limits(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"limiter gate {bad!r} must fail closed")

print("limiter gate policy: PASS")
