#!/usr/bin/env python3
'Strict v7 limiter acceptance for all six unpromoted candidate EELs. Calculated with eel2py, not WDL/JSFX.'
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests", "eel"))
from limiter_tests import build_checks

CASES = [
    ("iem-hd", "candidates/v7/eel/EDX_HD.eel"),
    ("iem-v4", "candidates/v7/eel/EDX_v4.eel"),
    ("iem-v10", "candidates/v7/eel/EDX_v10.eel"),
    ("spk-v6", "candidates/v7/eel/SPK_v6.eel"),
    ("spk-v8", "candidates/v7/eel/SPK_v8.eel"),
    ("spk-v10", "candidates/v7/eel/SPK_v10.eel"),
]

def run(case):
    pid, relpath = case
    path = os.path.join(ROOT, relpath)
    if not os.path.isfile(path):
        return pid, [dict(check="file", status="fail", detail=f"missing candidate EEL {relpath}")]
    return pid, build_checks(path, pid, gate="candidate-v7")

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor   # the six EELs are independent: ~4x faster on a 4-core runner
    failed = False
    with ProcessPoolExecutor() as ex:
        for pid, results in ex.map(run, CASES):
            for result in results:
                print(f"{result['status'].upper()} {pid} {result['check']}: {result['detail']}")
                failed |= result["status"] != "pass"
    print("v7 candidate limiter gate: " + ("FAILED" if failed else "PASS"))
    sys.exit(1 if failed else 0)
