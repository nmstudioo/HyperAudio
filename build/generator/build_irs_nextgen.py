import os
import struct
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

SRC_IRS = ROOT / "src/profiles/iem-hd/EDX_HD.irs"
OUT_DIR = HERE / "out/iem_nextgen"
OUT_IRS = OUT_DIR / "EDX_HD_NextGEN_candidate.irs"
OUT_JSON = OUT_DIR / "EDX_HD_NextGEN_candidate_irs.json"

EXPECTED_SHA = "cf4aa68cbc005b50960d6c91392829f6fa3bbf7f385bf1c54a8f948968cc0620"

KEEP_FRAMES = 1357
TAIL_THRESHOLD_DB = -80.0

PEAK_LIMIT = 0.95
L1_LIMIT = 1.25

RESPONSE_RMS_LIMIT = 0.1
RESPONSE_MAX_LIMIT = 0.25

CROSSFEED_MAG_LIMIT_DB = 0.5
CROSSFEED_PHASE_LIMIT_DEG = 0.1

SYMMETRY_LIMIT = 1e-7

NULL_THRESHOLD_REL = 1e-6
MAX_EXCLUDED_BINS = 12

SAMPLE_RATE = 48000
CHANNELS = 4
BITS = 32
BLOCK_ALIGN = 16

FREQUENCIES = np.logspace(
    np.log10(20.0),
    np.log10(20000.0),
    1200
)

BANDS = [
    (20, 100),
    (100, 500),
    (500, 2000),
    (2000, 6000),
    (6000, 10000),
    (10000, 20000),
]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def parse_canonical_wav(data):
    if len(data) < 44:
        raise ValueError("WAV too short")

    if data[0:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("Invalid RIFF/WAVE")

    riff_size = struct.unpack_from("<I", data, 4)[0]

    if riff_size + 8 != len(data):
        raise ValueError("RIFF size mismatch")

    if data[12:16] != b"fmt ":
        raise ValueError("Missing fmt chunk")

    fmt_size = struct.unpack_from("<I", data, 16)[0]

    if fmt_size != 16:
        raise ValueError("fmt chunk not canonical")

    fmt, ch, sr, br, ba, bits = struct.unpack_from(
        "<HHIIHH", data, 20
    )

    if data[36:40] != b"data":
        raise ValueError("Missing data chunk")

    data_size = struct.unpack_from("<I", data, 40)[0]

    if fmt != 3 or ch != CHANNELS or sr != SAMPLE_RATE or bits != BITS:
        raise ValueError("Format mismatch")

    if ba != BLOCK_ALIGN or br != SAMPLE_RATE * BLOCK_ALIGN:
        raise ValueError("Alignment mismatch")

    if data_size % BLOCK_ALIGN:
        raise ValueError("Not frame-aligned")

    if data_size + 44 != len(data):
        raise ValueError("Noncanonical data size")

    return {
        "frames": data_size // BLOCK_ALIGN,
        "data_size": data_size,
    }


def make_wav_header(data_size):
    header = bytearray(44)

    struct.pack_into(
        "<4sI4s",
        header,
        0,
        b"RIFF",
        36 + data_size,
        b"WAVE",
    )

    struct.pack_into(
        "<4sIHHIIHH",
        header,
        12,
        b"fmt ",
        16,
        3,
        CHANNELS,
        SAMPLE_RATE,
        SAMPLE_RATE * BLOCK_ALIGN,
        BLOCK_ALIGN,
        BITS,
    )

    struct.pack_into(
        "<4sI",
        header,
        36,
        b"data",
        data_size,
    )

    return bytes(header)


def direct_dtft(signal, freqs, sr, chunk=32):
    sig = np.asarray(signal, dtype=np.float64)
    freqs = np.asarray(freqs, dtype=np.float64)
    n = np.arange(len(sig), dtype=np.float64)

    out = np.empty(len(freqs), dtype=np.complex128)

    for start in range(0, len(freqs), chunk):
        stop = min(start + chunk, len(freqs))

        omega = 2.0 * np.pi * freqs[start:stop] / sr
        phase = np.outer(omega, n)

        out[start:stop] = np.exp(-1j * phase) @ sig

    return out


def wrapped_phase_delta_deg(a, b):
    return float(
        np.degrees(np.angle(np.exp(1j * (b - a))))
    )


def crossfeed_metrics(orig, cand, direct_ch, cross_ch):
    f = [500.0]

    d_o = direct_dtft(
        orig[:, direct_ch], f, SAMPLE_RATE
    )[0]

    c_o = direct_dtft(
        orig[:, cross_ch], f, SAMPLE_RATE
    )[0]

    d_n = direct_dtft(
        cand[:, direct_ch], f, SAMPLE_RATE
    )[0]

    c_n = direct_dtft(
        cand[:, cross_ch], f, SAMPLE_RATE
    )[0]

    magnitudes = [abs(d_o), abs(c_o), abs(d_n), abs(c_n)]

    if not all(np.isfinite(v) for v in magnitudes):
        raise ValueError("Non-finite crossfeed DTFT")

    direct_floor = max(magnitudes) * 1e-12

    if abs(d_o) <= direct_floor or abs(d_n) <= direct_floor:
        raise ValueError(
            "500 Hz direct-path response is numerically unstable"
        )

    r_o = c_o / d_o
    r_n = c_n / d_n

    mag_o = float(20 * np.log10(abs(r_o) + 1e-30))
    mag_n = float(20 * np.log10(abs(r_n) + 1e-30))

    return {
        "original_db": mag_o,
        "candidate_db": mag_n,
        "magnitude_delta_db": abs(mag_n - mag_o),
        "phase_original_deg": float(np.degrees(np.angle(r_o))),
        "phase_candidate_deg": float(np.degrees(np.angle(r_n))),
        "phase_delta_deg": abs(
            wrapped_phase_delta_deg(
                np.angle(r_o),
                np.angle(r_n),
            )
        ),
    }


def channel_symmetry(samples):
    return {
        "direct_L_vs_R_max_abs_diff": float(
            np.max(np.abs(samples[:, 0] - samples[:, 3]))
        ),
        "cross_L_vs_R_max_abs_diff": float(
            np.max(np.abs(samples[:, 1] - samples[:, 2]))
        ),
    }


def main():
    if not SRC_IRS.is_file():
        raise FileNotFoundError(f"Missing source: {SRC_IRS}")

    source_bytes = SRC_IRS.read_bytes()

    if sha256_bytes(source_bytes) != EXPECTED_SHA:
        raise ValueError("Source SHA-256 mismatch")

    source_info = parse_canonical_wav(source_bytes)
    original_frames = source_info["frames"]

    if KEEP_FRAMES > original_frames:
        raise ValueError("Candidate exceeds source frame count")

    original_payload = source_bytes[44:]

    expected_payload = original_payload[
        :KEEP_FRAMES * BLOCK_ALIGN
    ]

    original = np.frombuffer(
        original_payload,
        dtype="<f4",
    ).reshape(original_frames, CHANNELS)

    candidate = np.frombuffer(
        expected_payload,
        dtype="<f4",
    ).reshape(KEEP_FRAMES, CHANNELS)

    # Rebuild and independently parse the candidate WAV.
    candidate_bytes = (
        make_wav_header(len(expected_payload))
        + expected_payload
    )

    candidate_info = parse_canonical_wav(candidate_bytes)

    if candidate_info["frames"] != KEEP_FRAMES:
        raise ValueError("Candidate frame count mismatch")

    if candidate_bytes[44:] != expected_payload:
        raise ValueError("Candidate payload differs from source slice")

    if not np.all(np.isfinite(original)):
        raise ValueError("Non-finite source samples")

    if not np.all(np.isfinite(candidate)):
        raise ValueError("Non-finite candidate samples")

    peak = float(np.max(np.abs(candidate)))

    l1 = float(
        np.max(np.sum(np.abs(candidate), axis=0))
    )

    if peak > PEAK_LIMIT:
        raise ValueError(f"Peak {peak:.6f} > {PEAK_LIMIT}")

    if l1 > L1_LIMIT:
        raise ValueError(f"L1 {l1:.6f} > {L1_LIMIT}")

    # Tail-energy threshold, measured against the full source.
    energy = np.sum(
        original.astype(np.float64) ** 2,
        axis=1,
    )

    total_energy = float(np.sum(energy))

    if not np.isfinite(total_energy) or total_energy <= 0:
        raise ValueError("Invalid source energy")

    remaining = np.cumsum(energy[::-1])[::-1]

    tail_db = 10.0 * np.log10(
        remaining / total_energy + 1e-30
    )

    crossings = np.flatnonzero(
        tail_db < TAIL_THRESHOLD_DB
    )

    tail_frame = (
        int(crossings[0])
        if len(crossings)
        else original_frames
    )

    if tail_frame >= KEEP_FRAMES:
        raise ValueError(
            f"Tail threshold not reached before frame {KEEP_FRAMES}"
        )

    # Composite response comparison.
    H_orig = direct_dtft(
        original[:, 0] + original[:, 2],
        FREQUENCIES,
        SAMPLE_RATE,
    )

    H_cand = direct_dtft(
        candidate[:, 0] + candidate[:, 2],
        FREQUENCIES,
        SAMPLE_RATE,
    )

    mag_orig = np.abs(H_orig)
    mag_cand = np.abs(H_cand)

    ref_peak = float(np.max(mag_orig))

    if not np.isfinite(ref_peak) or ref_peak <= 0:
        raise ValueError("Invalid reference response peak")

    null_floor = ref_peak * NULL_THRESHOLD_REL

    valid = mag_orig > null_floor
    excluded_idx = np.flatnonzero(~valid)

    if len(excluded_idx) > MAX_EXCLUDED_BINS:
        raise ValueError(
            f"Excluded {len(excluded_idx)} bins; "
            f"maximum allowed is {MAX_EXCLUDED_BINS}"
        )

    # Inspect candidate behaviour at excluded reference-null bins.
    excluded_candidate_metrics = []

    for idx in excluded_idx:
        original_mag = float(mag_orig[idx])
        candidate_mag = float(mag_cand[idx])

        if candidate_mag > null_floor * 10:
            raise ValueError(
                f"New energy at excluded reference-null bin "
                f"{FREQUENCIES[idx]:.2f} Hz"
            )

        excluded_candidate_metrics.append({
            "frequency_hz": round(float(FREQUENCIES[idx]), 2),
            "original_magnitude": original_mag,
            "candidate_magnitude": candidate_mag,
            "candidate_below_relative_floor": (
                candidate_mag <= null_floor
            ),
        })

    if not np.any(valid):
        raise ValueError("No valid response-comparison bins")

    db_diff = 20.0 * np.log10(
        mag_cand[valid] / mag_orig[valid] + 1e-30
    )

    response_rms = float(
        np.sqrt(np.mean(db_diff ** 2))
    )

    response_max = float(
        np.max(np.abs(db_diff))
    )

    if response_rms > RESPONSE_RMS_LIMIT:
        raise ValueError(
            f"Response RMS {response_rms:.6f} exceeds limit"
        )

    if response_max > RESPONSE_MAX_LIMIT:
        raise ValueError(
            f"Response max {response_max:.6f} exceeds limit"
        )

    per_band = {}

    for low, high in BANDS:
        mask = (
            (FREQUENCIES >= low)
            & (FREQUENCIES < high)
            & valid
        )

        if np.any(mask):
            band_diff = 20.0 * np.log10(
                mag_cand[mask] / mag_orig[mask] + 1e-30
            )

            per_band[f"{low}-{high}Hz"] = float(
                np.sqrt(np.mean(band_diff ** 2))
            )

    # Crossfeed magnitude and phase preservation.
    cf1 = crossfeed_metrics(original, candidate, 0, 1)
    cf2 = crossfeed_metrics(original, candidate, 3, 2)

    for label, metrics in (
        ("channel_1_over_0", cf1),
        ("channel_2_over_3", cf2),
    ):
        if metrics["magnitude_delta_db"] > CROSSFEED_MAG_LIMIT_DB:
            raise ValueError(f"{label}: crossfeed magnitude drift")

        if metrics["phase_delta_deg"] > CROSSFEED_PHASE_LIMIT_DEG:
            raise ValueError(f"{label}: crossfeed phase drift")

    # Channel symmetry.
    sym_o = channel_symmetry(original)
    sym_n = channel_symmetry(candidate)

    for label, metrics in (
        ("original", sym_o),
        ("candidate", sym_n),
    ):
        if max(metrics.values()) > SYMMETRY_LIMIT:
            raise ValueError(f"{label}: channel symmetry failed")

    gates = {
        key: "pass"
        for key in [
            "source_hash",
            "canonical_source_wav",
            "canonical_candidate_wav",
            "frame_alignment",
            "retained_payload_byte_identical",
            "finite_source_and_candidate",
            "peak",
            "l1_norm",
            "tail_threshold",
            "response_rms",
            "response_max",
            "crossfeed_1_magnitude",
            "crossfeed_1_phase",
            "crossfeed_2_magnitude",
            "crossfeed_2_phase",
            "original_channel_symmetry",
            "candidate_channel_symmetry",
            "no_new_energy_at_excluded_bins",
        ]
    }

    report = {
        "status": "candidate_validated",
        "source": {
            "path": str(SRC_IRS.relative_to(ROOT)),
            "sha256": EXPECTED_SHA,
        },
        "candidate": {
            "filename": OUT_IRS.name,
            "sha256": sha256_bytes(candidate_bytes),
            "frames": KEEP_FRAMES,
            "duration_ms": round(
                KEEP_FRAMES / SAMPLE_RATE * 1000,
                4,
            ),
            "bytes": len(candidate_bytes),
            "reduction_pct": round(
                (
                    1 - len(expected_payload) / len(original_payload)
                ) * 100,
                2,
            ),
        },
        "format": {
            "encoding": "IEEE Float32",
            "channels": CHANNELS,
            "sample_rate": SAMPLE_RATE,
            "bits": BITS,
            "block_align": BLOCK_ALIGN,
        },
        "tail": {
            "threshold_db": TAIL_THRESHOLD_DB,
            "crossing_frame": tail_frame,
            "crossing_energy_db": float(tail_db[tail_frame]),
        },
        "sample_metrics": {
            "peak": peak,
            "l1_norm": l1,
            "peak_limit": PEAK_LIMIT,
            "l1_limit": L1_LIMIT,
        },
        "response": {
            "method": "chunked direct DTFT",
            "grid": "1200 logarithmic points, 20-20000 Hz",
            "null_threshold_relative": NULL_THRESHOLD_REL,
            "null_floor": null_floor,
            "excluded_bins": len(excluded_idx),
            "excluded_frequencies_hz": [
                round(float(FREQUENCIES[i]), 2)
                for i in excluded_idx
            ],
            "excluded_bin_details": excluded_candidate_metrics,
            "maximum_excluded_bins": MAX_EXCLUDED_BINS,
            "rms_difference_db": response_rms,
            "rms_limit_db": RESPONSE_RMS_LIMIT,
            "max_absolute_difference_db": response_max,
            "max_limit_db": RESPONSE_MAX_LIMIT,
            "per_band_rms_db": per_band,
        },
        "crossfeed_500hz": {
            "channel_1_over_0": cf1,
            "channel_2_over_3": cf2,
            "magnitude_delta_limit_db": CROSSFEED_MAG_LIMIT_DB,
            "phase_delta_limit_deg": CROSSFEED_PHASE_LIMIT_DEG,
        },
        "channel_symmetry": {
            "original": sym_o,
            "candidate": sym_n,
            "tolerance": SYMMETRY_LIMIT,
        },
        "gates": gates,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tmp_irs = OUT_DIR / (OUT_IRS.name + ".tmp")
    tmp_json = OUT_DIR / (OUT_JSON.name + ".tmp")

    try:
        tmp_irs.write_bytes(candidate_bytes)
        tmp_json.write_text(
            json.dumps(report, indent=2) + "\n"
        )

        # Independently reopen and validate the written candidate.
        written = tmp_irs.read_bytes()

        if sha256_bytes(written) != report["candidate"]["sha256"]:
            raise ValueError("Written candidate SHA mismatch")

        written_info = parse_canonical_wav(written)

        if written_info["frames"] != KEEP_FRAMES:
            raise ValueError("Written candidate frame count mismatch")

        if written[44:] != expected_payload:
            raise ValueError("Written candidate payload mismatch")

        os.replace(tmp_irs, OUT_IRS)
        os.replace(tmp_json, OUT_JSON)

    finally:
        if tmp_irs.exists():
            tmp_irs.unlink()

        if tmp_json.exists():
            tmp_json.unlink()

    print(f"IRS candidate: {OUT_IRS}")
    print(f"Frames: {KEEP_FRAMES}")
    print(f"Response RMS: {response_rms:.6f} dB")
    print(f"Response max: {response_max:.6f} dB")
    print(f"Excluded bins: {len(excluded_idx)}")
    print(f"Excluded frequencies: {report['response']['excluded_frequencies_hz']}")
    print(f"Crossfeed magnitude deltas: "
          f"{cf1['magnitude_delta_db']:.6f}, "
          f"{cf2['magnitude_delta_db']:.6f} dB")


if __name__ == "__main__":
    main()
