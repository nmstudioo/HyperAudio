#!/usr/bin/env python3
"""Fit a candidate 10-section IEM NextGEN VDC against the v7 IEM IRS.

This script is intentionally candidate-only:
- it reads src/profiles/iem-hd/EDX_HD.irs without modifying it;
- it uses the existing target_iem() median-alignment convention;
- it fits independent 48 kHz and 44.1 kHz VDC banks;
- it constrains every biquad's pole radius during optimization;
- it writes only to build/generator/out/iem_nextgen/ unless --out is supplied.

Run from any working directory:
    python3 build/generator/fit_nextgen.py

Dependencies are the repository's existing NumPy/SciPy requirements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares, minimize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import lib as L  # noqa: E402

# Do not silently fit a different or modified IRS.
EXPECTED_V7_IRS_SHA256 = "cf4aa68cbc005b50960d6c91392829f6fa3bbf7f385bf1c54a8f948968cc0620"
POLE_LIMIT = 0.985
# Optimize a little inside the release limit to leave room for 9-decimal VDC output.
POLE_OPT_LIMIT = 0.9848
N_SECTIONS = 10
F_MIN = 30.0
F_MAX = 16000.0
MAX_BANK_DIFFERENCE_DB = 0.3
MID_BAND = (300.0, 3000.0)

IRS_PATH = ROOT / "src/profiles/iem-hd/EDX_HD.irs"
RAW_PATH = HERE / "inputs/data/Raw/kz_edx_pro_raw_nextgen.txt"
TARGET_PATH = HERE / "inputs/data/target/kz_edx_pro_target.txt"
DEFAULT_OUT = HERE / "out/iem_nextgen/EDX_HD_NextGEN_candidate.vdc"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_file(path: Path, purpose: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {purpose}: {path}\n"
            "Place the expected input in the repository path shown above; "
            "the fitter will not substitute another measurement."
        )


def load_two_column(path: Path, *, delimiter: str | None, skiprows: int = 0) -> np.ndarray:
    data = np.loadtxt(path, delimiter=delimiter, comments="#", skiprows=skiprows, dtype=float)
    data = np.atleast_2d(data)
    if data.shape[1] < 2:
        raise ValueError(f"Expected at least two columns in {path}; got shape {data.shape}")
    data = data[:, :2]
    if not np.all(np.isfinite(data)):
        raise ValueError(f"Non-finite values in {path}")
    freq = data[:, 0]
    if np.any(freq <= 0) or np.any(np.diff(freq) <= 0):
        raise ValueError(f"Frequencies in {path} must be positive and strictly increasing")
    if freq[0] > L.f[0] or freq[-1] < L.f[-1]:
        raise ValueError(
            f"{path} must cover the full {L.f[0]:g}-{L.f[-1]:g} Hz fitting grid; "
            f"found {freq[0]:g}-{freq[-1]:g} Hz"
        )
    return data


def interpolate_curve(data: np.ndarray) -> np.ndarray:
    return np.interp(np.log(L.f), np.log(data[:, 0]), data[:, 1])


def ear_response(irs: np.ndarray) -> np.ndarray:
    """Match build_v5.py's IEM earM(): H[0] + H[2] for 4-channel IRS."""
    if irs.ndim != 2 or irs.shape[1] not in (1, 2, 4):
        raise ValueError(f"Unexpected IRS channel shape: {irs.shape}")
    h = [L.Hm(irs[:, channel]) for channel in range(irs.shape[1])]
    return h[0] + h[2] if irs.shape[1] == 4 else h[0]


def target_iem_nextgen(irs_response: np.ndarray, raw_db: np.ndarray, target_db: np.ndarray) -> np.ndarray:
    """Reproduce build_v5.py target_iem() exactly, using the NextGEN raw curve."""
    correction = target_db - raw_db - L.dB(irs_response)
    mid = (L.f >= MID_BAND[0]) & (L.f <= MID_BAND[1])
    correction = correction - np.median(correction[mid])
    hi = L.f > 16000.0
    below_16k = np.flatnonzero(L.f <= 16000.0)
    correction[hi] = correction[below_16k[-1]]
    return correction


def pole_margins(ty: list[str], params: np.ndarray, fs: int, radius: float) -> np.ndarray:
    """Jury stability margins for every section with all poles inside radius.

    lib.bq() returns denominator terms d1,d2 used as
        1 - d1*z - d2*z**2
    so the pole polynomial is z**2 - d1*z - d2. Applying the second-order
    Jury conditions after scaling the pole radius by ``radius`` gives the
    four inequalities returned here. All must be positive.
    """
    margins: list[float] = []
    for i, kind in enumerate(ty):
        fc, gain, q = params[3 * i:3 * i + 3]
        section = L.bq(kind, float(fc), float(gain), float(q), fs)
        d1, d2 = float(section[3]), float(section[4])
        r2 = radius * radius
        margins.extend((r2 - d1 * radius - d2,
                        r2 + d1 * radius - d2,
                        r2 - d2,
                        r2 + d2))
    return np.asarray(margins, dtype=float) / (radius * radius)


def pole_radii(sections: np.ndarray) -> list[float]:
    result = []
    for section in sections:
        roots = np.roots([1.0, -float(section[3]), -float(section[4])])
        result.append(float(np.max(np.abs(roots))))
    return result


def constrained_refine(
    ty: list[str],
    start: list[float],
    lower: list[float],
    upper: list[float],
    target: np.ndarray,
    weight: np.ndarray,
    fs: int,
) -> np.ndarray:
    lo = np.asarray(lower, dtype=float)
    hi = np.asarray(upper, dtype=float)
    p0 = np.clip(np.asarray(start, dtype=float), lo + 1e-9, hi - 1e-9)
    if np.any(hi <= lo):
        raise ValueError("Invalid optimizer parameter bounds")

    def residual(p: np.ndarray) -> np.ndarray:
        tonal = (L.resp_db(L.mkS(ty, p, fs), L.f, fs) - target) * weight
        gain_regularizer = 0.03 * np.asarray(p)[1::3]
        return np.concatenate((tonal, gain_regularizer))

    # Match the existing fitter's least-squares objective to obtain a good
    # unconstrained starting point; the following SLSQP pass enforces stability.
    seed_fit = least_squares(
        residual,
        p0,
        bounds=(lo, hi),
        max_nfev=400,
        x_scale="jac",
        method="trf",
    )
    seed = np.asarray(seed_fit.x, dtype=float)
    span = hi - lo

    def unpack(y: np.ndarray) -> np.ndarray:
        return lo + np.asarray(y, dtype=float) * span

    def objective(y: np.ndarray) -> float:
        r = residual(unpack(y))
        return 0.5 * float(np.dot(r, r))

    def stability(y: np.ndarray) -> np.ndarray:
        return pole_margins(ty, unpack(y), fs, POLE_OPT_LIMIT)

    y0 = np.clip((seed - lo) / span, 1e-9, 1.0 - 1e-9)
    opt = minimize(
        objective,
        y0,
        method="SLSQP",
        jac="2-point",
        bounds=[(0.0, 1.0)] * len(y0),
        constraints=[{"type": "ineq", "fun": stability}],
        options={"maxiter": 1000, "ftol": 1e-9, "disp": False},
    )
    fitted = unpack(opt.x)
    margins = pole_margins(ty, fitted, fs, POLE_OPT_LIMIT)
    feasible = bool(np.all(np.isfinite(fitted)) and np.min(margins) >= -1e-8)
    if not opt.success or not feasible:
        worst = float(np.min(margins)) if margins.size else float("nan")
        raise RuntimeError(
            f"Constrained fit failed at {fs} Hz: optimizer success={opt.success}, "
            f"message={opt.message!s}, worst normalized pole margin={worst:.6g}"
        )
    if not np.all(np.isfinite(L.resp_db(L.mkS(ty, fitted, fs), L.f, fs))):
        raise RuntimeError(f"Non-finite response after constrained fit at {fs} Hz")
    return fitted


def fit_bank(
    correction: np.ndarray,
    weight: np.ndarray,
    fs: int,
    *,
    sections: int = N_SECTIONS,
    warm: tuple[list[str], list[float], list[float], list[float]] | None = None,
    gain_bounds: tuple[float, float] = (-12.0, 6.0),
) -> tuple[list[str], list[float], list[float], list[float]]:
    if warm is None:
        kinds = ["LS", "HS"]
        params = [150.0, -2.0, 0.6, 6000.0, -2.0, 0.6]
        lower = [20.0, -14.0, 0.3, 3000.0, -14.0, 0.3]
        upper = [500.0, 8.0, 1.0, 16000.0, 8.0, 1.0]
    else:
        kinds = list(warm[0])
        params = list(warm[1])
        lower = list(warm[2])
        upper = list(warm[3])

    params_np = constrained_refine(kinds, params, lower, upper, correction, weight, fs)
    params = params_np.tolist()

    while len(kinds) < sections:
        residual_db = correction - L.resp_db(L.mkS(kinds, params, fs), L.f, fs)
        smoothed = np.convolve(residual_db, np.ones(7, dtype=float) / 7.0, mode="same") * weight
        index = int(np.argmax(np.abs(smoothed)))
        center = float(L.f[index])
        gain = float(np.clip(residual_db[index], -8.0, 5.0))
        kinds.append("PK")
        params.extend((center, gain, 2.5))
        lower.extend((max(20.0, center / 1.6), gain_bounds[0], 0.5))
        upper.extend((min(19500.0, center * 1.6), gain_bounds[1], 6.0))
        params_np = constrained_refine(kinds, params, lower, upper, correction, weight, fs)
        params = params_np.tolist()

    return kinds, params, lower, upper


def make_vdc_text(bank_44: np.ndarray, bank_48: np.ndarray, gain_db: float) -> str:
    gain = 10.0 ** (gain_db / 20.0)

    def encode(bank: np.ndarray) -> str:
        values = np.array(bank, dtype=float, copy=True)
        if values.ndim != 2 or values.shape[1] != 5 or len(values) == 0:
            raise ValueError("Invalid VDC bank shape")
        values[0, :3] *= gain
        return ",".join(f"{value:.9f}" for value in values.reshape(-1))

    return f"SR_44100:{encode(bank_44)}\nSR_48000:{encode(bank_48)}\n"


def parse_vdc_text(text: str) -> tuple[np.ndarray, np.ndarray]:
    parsed: dict[str, np.ndarray] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, values = line.split(":", 1)
        if key not in ("SR_44100", "SR_48000"):
            continue
        vector = np.asarray([float(v) for v in values.split(",") if v.strip()], dtype=float)
        if vector.size == 0 or vector.size % 5:
            raise ValueError(f"Malformed {key} VDC line")
        parsed[key] = vector.reshape(-1, 5)
    if set(parsed) != {"SR_44100", "SR_48000"}:
        raise ValueError("VDC output must contain both SR_44100 and SR_48000 banks")
    if not all(np.all(np.isfinite(bank)) for bank in parsed.values()):
        raise ValueError("VDC output contains non-finite coefficients")
    return parsed["SR_44100"], parsed["SR_48000"]


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(values))))


def build_report(
    raw_db: np.ndarray,
    target_db: np.ndarray,
    irs_db: np.ndarray,
    bank_44: np.ndarray,
    bank_48: np.ndarray,
    gain_db: float,
    raw_hash: str,
    target_hash: str,
    irs_hash: str,
) -> dict[str, Any]:
    # The caller passes serialized banks whose first-section numerator
    # already includes gain_db. Do not apply the normalization a second time.
    v48 = L.resp_db(bank_48, L.f, 48000)
    v44 = L.resp_db(bank_44, L.f, 44100)
    chain48 = irs_db + v48
    chain44 = irs_db + v44
    predicted = raw_db + chain48
    absolute_error = predicted - target_db
    mid = (L.f >= MID_BAND[0]) & (L.f <= MID_BAND[1])
    aligned_error = absolute_error - np.median(absolute_error[mid])
    evaluation = (L.f >= F_MIN) & (L.f <= F_MAX)
    bands = [(20, 100), (100, 500), (500, 2000), (2000, 6000), (6000, 10000), (10000, 16000)]
    band_report = []
    for low, high in bands:
        mask = (L.f >= low) & (L.f < high)
        band_report.append({
            "band_hz": [low, high],
            "aligned_rms_db": rms(aligned_error[mask]),
            "absolute_rms_db": rms(absolute_error[mask]),
        })
    radii_44 = pole_radii(bank_44)
    radii_48 = pole_radii(bank_48)
    return {
        "status": "candidate_validated_for_review",
        "fit_convention": {
            "method": "target_iem median alignment",
            "median_alignment_hz": list(MID_BAND),
            "above_16khz": "held at the last correction value at or below 16 kHz",
            "absolute_reference_used_for_fit": False,
        },
        "inputs": {
            "raw_path": str(RAW_PATH.relative_to(ROOT)),
            "raw_sha256": raw_hash,
            "target_path": str(TARGET_PATH.relative_to(ROOT)),
            "target_sha256": target_hash,
            "irs_path": str(IRS_PATH.relative_to(ROOT)),
            "irs_sha256": irs_hash,
            "irs_preserved_without_rescaling_or_peakfix": True,
        },
        "optimizer": {
            "sections": int(len(bank_48)),
            "pole_radius_limit": POLE_LIMIT,
            "optimization_pole_radius_limit": POLE_OPT_LIMIT,
            "max_44khz_vs_48khz_bank_difference_db": MAX_BANK_DIFFERENCE_DB,
            "sample_rates_hz": [44100, 48000],
        },
        "normalization": {
            "gain_db_applied_to_vdc": float(gain_db),
            "chain_peak_48khz_db_30_16k": float(np.max(chain48[evaluation])),
            "chain_peak_44khz_db_30_16k": float(np.max(chain44[evaluation])),
            "target_chain_peak_db": -0.5,
        },
        "pole_radii": {
            "sr_44100_max": float(max(radii_44)),
            "sr_48000_max": float(max(radii_48)),
            "sr_44100_per_section": radii_44,
            "sr_48000_per_section": radii_48,
        },
        "response_error_db": {
            "absolute_reference_rms_30_16k": rms(absolute_error[evaluation]),
            "absolute_reference_max_abs_30_16k": float(np.max(np.abs(absolute_error[evaluation]))),
            "median_aligned_rms_30_16k": rms(aligned_error[evaluation]),
            "median_aligned_max_abs_30_16k": float(np.max(np.abs(aligned_error[evaluation]))),
            "absolute_error_median_300_3000_hz": float(np.median(absolute_error[mid])),
            "bank_difference_max_abs_db_30_20k": float(np.max(np.abs(v44 - v48))),
            "bands": band_report,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=RAW_PATH, help="NextGEN raw response (whitespace-delimited frequency dB)")
    parser.add_argument("--target", type=Path, default=TARGET_PATH, help="KZ EDX Pro target CSV already in the repository")
    parser.add_argument("--irs", type=Path, default=IRS_PATH, help="v7 EDX_HD.irs (must match the pinned SHA-256)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="candidate VDC output path (never writes into src/profiles by default)")
    args = parser.parse_args()

    require_file(args.raw, "NextGEN raw response")
    require_file(args.target, "IEM target curve")
    require_file(args.irs, "v7 IEM IRS")

    irs_hash = sha256(args.irs)
    if irs_hash != EXPECTED_V7_IRS_SHA256:
        raise RuntimeError(
            "The selected IRS is not the pinned v7 IEM HD IRS.\n"
            f"Expected SHA-256: {EXPECTED_V7_IRS_SHA256}\n"
            f"Actual SHA-256:   {irs_hash}\n"
            "No candidate was written. Do not substitute the old v4 generator IRS."
        )

    raw_data = load_two_column(args.raw, delimiter=None)
    # The checked-in target starts with a comment line, then 'frequency,target'.
    target_data = load_two_column(args.target, delimiter=",", skiprows=2)
    raw_db = interpolate_curve(raw_data)
    target_db = interpolate_curve(target_data)

    irs, fmt, _extra, _file_size, _data_size, _data_len = L.rdirs(str(args.irs))
    tag, channels, sample_rate, _byte_rate, _block_align, bits = fmt
    if (tag, channels, sample_rate, bits) != (3, 4, 48000, 32):
        raise RuntimeError(
            "Unexpected v7 IRS WAV format; expected IEEE Float32, 4-channel, 48 kHz. "
            f"Found format={tag}, channels={channels}, sample_rate={sample_rate}, bits={bits}."
        )
    if irs.shape[0] == 0 or not np.all(np.isfinite(irs)):
        raise RuntimeError("The v7 IRS contains no usable samples or non-finite values")

    # IMPORTANT: no scale_to_maxgain() and no peakfix(). The released v7 IRS is
    # used exactly as-is; this fitter never rewrites or rescales it.
    irs_response = ear_response(irs)
    irs_db = L.dB(irs_response)
    correction = target_iem_nextgen(irs_response, raw_db, target_db)
    weight = np.where(L.f < 30.0, 0.3, np.where(L.f <= 16000.0, 1.0, 0.3))

    # Fit 48 kHz first using the existing greedy section-placement strategy,
    # now with explicit pole-radius constraints.
    fit48 = fit_bank(correction, weight, 48000)
    types48, params48 = fit48[0], np.asarray(fit48[1], dtype=float)
    bank48 = np.asarray(L.mkS(types48, params48, 48000), dtype=float)

    # Preserve build_vdc()'s 44.1 kHz approach: warm-start from the 48 kHz
    # solution and fit the 44.1 kHz bank toward the 48 kHz bank response.
    correction44 = L.resp_db(bank48, L.f, 48000)
    weight44 = np.where(L.f > 19000.0, 0.2, 1.0)
    fit44 = fit_bank(correction44, weight44, 44100, warm=fit48)
    types44, params44 = fit44[0], np.asarray(fit44[1], dtype=float)
    bank44 = np.asarray(L.mkS(types44, params44, 44100), dtype=float)

    # Validate nominal-rate pole radii before gain normalization or file output.
    radii44 = pole_radii(bank44)
    radii48 = pole_radii(bank48)
    if max(radii44) > POLE_LIMIT or max(radii48) > POLE_LIMIT:
        raise RuntimeError(
            "Pole-radius release gate failed; no candidate was written. "
            f"44.1 kHz max={max(radii44):.9f}, 48 kHz max={max(radii48):.9f}, "
            f"limit={POLE_LIMIT:.6f}."
        )

    # Normalize against the worse of the two sample-rate banks so both chains
    # peak at or below -0.5 dB over the established 30 Hz–16 kHz evaluation band.
    evaluation = (L.f >= F_MIN) & (L.f <= F_MAX)
    unnormalized48 = irs_db + L.resp_db(bank48, L.f, 48000)
    unnormalized44 = irs_db + L.resp_db(bank44, L.f, 44100)
    worst_chain_peak = max(float(np.max(unnormalized48[evaluation])),
                           float(np.max(unnormalized44[evaluation])))
    gain_db = -0.5 - worst_chain_peak

    vdc_text = make_vdc_text(bank44, bank48, gain_db)
    encoded44, encoded48 = parse_vdc_text(vdc_text)
    # Recheck serialized (9-decimal) coefficients, not just in-memory doubles.
    final_radii44 = pole_radii(encoded44)
    final_radii48 = pole_radii(encoded48)
    if max(final_radii44) > POLE_LIMIT or max(final_radii48) > POLE_LIMIT:
        raise RuntimeError("Serialized VDC pole-radius gate failed; no candidate was written")

    report = build_report(
        raw_db, target_db, irs_db, encoded44, encoded48, gain_db,
        sha256(args.raw), sha256(args.target), irs_hash,
    )
    if (report["normalization"]["chain_peak_48khz_db_30_16k"] > 0.0 or
            report["normalization"]["chain_peak_44khz_db_30_16k"] > 0.0):
        raise RuntimeError("Serialized chain headroom gate failed; no candidate was written")
    if report["response_error_db"]["bank_difference_max_abs_db_30_20k"] > MAX_BANK_DIFFERENCE_DB:
        raise RuntimeError(
            "44.1/48 kHz bank matching gate failed; no candidate was written. "
            f"Maximum difference={report['response_error_db']['bank_difference_max_abs_db_30_20k']:.4f} dB, "
            f"limit={MAX_BANK_DIFFERENCE_DB:.3f} dB."
        )

    out_path = args.out if args.out.is_absolute() else (ROOT / args.out).resolve()
    profiles_root = (ROOT / "src/profiles").resolve()
    try:
        out_path.relative_to(profiles_root)
    except ValueError:
        pass
    else:
        raise RuntimeError(
            "Refusing to write a candidate inside src/profiles/. "
            "Use the default build/generator/out/ path and promote files only after review."
        )
    report_path = out_path.with_suffix(".json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_vdc = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp_json = report_path.with_suffix(report_path.suffix + ".tmp")
    try:
        tmp_vdc.write_text(vdc_text, encoding="utf-8", newline="\n")
        tmp_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(tmp_vdc, out_path)
        os.replace(tmp_json, report_path)
    finally:
        for temp in (tmp_vdc, tmp_json):
            if temp.exists():
                temp.unlink()

    print("IEM NextGEN candidate generated and validated for review.")
    print(f"VDC:    {out_path}")
    print(f"Report: {report_path}")
    print(f"Pole radius max: 44.1 kHz={max(final_radii44):.6f}, 48 kHz={max(final_radii48):.6f} (limit {POLE_LIMIT:.3f})")
    print(f"Chain peak: 44.1 kHz={report['normalization']['chain_peak_44khz_db_30_16k']:.3f} dB, "
          f"48 kHz={report['normalization']['chain_peak_48khz_db_30_16k']:.3f} dB")
    print(f"Median-aligned RMS error, 30 Hz–16 kHz: {report['response_error_db']['median_aligned_rms_30_16k']:.3f} dB")
    print(f"Absolute-reference RMS error, 30 Hz–16 kHz (diagnostic only): "
          f"{report['response_error_db']['absolute_reference_rms_30_16k']:.3f} dB")
    print("No release profile, v7 IRS, v7 VDC, or v7 EEL file was modified.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
