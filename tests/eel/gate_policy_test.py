#!/usr/bin/env python3
'Regression test for the intentionally separate v5-stable and v7-candidate gates.'
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from limiter_tests import gate_limits

assert gate_limits("stable-v5") == (0.35, 2.5)
assert gate_limits("candidate-v7") == (0.5, 0.5)

try:
    gate_limits("unknown")
except ValueError:
    pass
else:
    raise AssertionError("unknown limiter gate must fail closed")

print("limiter gate policy: PASS")
