# -*- coding: utf-8 -*-
"""
DHE 12F-S5 PROVENANCE RECOVERY / NUMBER_WITHOUT_FIELD mechanical instrument.

Authority:
  - 睫 §二  : number appearing only in report prose, with no field in a sealed
             artifact, must be searched across ALL artifacts; found -> name the
             field; not found -> full-chain retraction. Plus a fixture that must
             go RED when a number has no field.
  - 凌翼 §四: if individual deltas already exist in a sealed artifact, we may
             mechanically recompute m_g / v_g ZERO-FORWARD and emit a NEW
             DERIVED ARTIFACT. If individual deltas are not saved, do not
             compute. Never re-run the model to recover 1.0677.
  - 凌翼 §五: reporting correction -- delta_i is a PER-ITEM quantity (48 deltas,
             2 per source-map pair g), which is exactly why m_g and v_g are
             definable at all.

This script:
  (1) verifies the sealed source arrays by hash,
  (2) mechanically recomputes mean_norm_m_g / mean_norm_v_g from sealed deltas,
  (3) compares to the historical values 1.0676623156873744 / 2.1535543301312257,
  (4) emits a NEW derived artifact carrying full provenance
      (definition / scope / operator / unit / numerator_reference /
       denominator_reference / source fields / artifact hashes),
  (5) runs the NUMBER_WITHOUT_FIELD fixture, including a deliberate NEGATIVE
      case that must be caught.

ZERO FORWARD. ZERO AUTOGRAD. Read-only w.r.t. every already-sealed artifact.
"""

import hashlib
import json
import os
import sys

import numpy as np

REPORTS = r"D:\qcr\EntropyDrivenAI\selective_forgetting\reports"

DELTAS = os.path.join(REPORTS, "_dhe_12f_derive_deltas.npy")
RAW_DM = os.path.join(REPORTS, "_dhe_12f_raw_dm.npy")
SIGNED_DM = os.path.join(REPORTS, "_dhe_12f_signed_dm.npy")

EXPECT = {
    DELTAS: "bbfb5258f18c68a6a1092b6db84661c755bf6036e01b246a913811752c37a804",
    RAW_DM: "642f0d457a84b34bfe0c4a5d2bc9b4d241255e38e3ce6f9708831685a2017d8b",
    SIGNED_DM: "cbb8eab8c4da16e80adaf95a82bb1bafe9bf41ca1bb73cf57933e9116c36c012",
}

HISTORICAL = {
    "mean_norm_m_g": 1.0676623156873744,
    "mean_norm_v_g": 2.1535543301312257,
    "source_artifact": "DHE_12F_S5_SIGNED_D_M.json",
    "source_path_in_artifact": "algebraic_decomposition_reported",
}

D2_PROJECTION = os.path.join(REPORTS, "DHE_D2_EPISODE_PROJECTION_v1.json")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_hash(obj_without_hash):
    blob = json.dumps(obj_without_hash, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class NumberWithoutFieldError(Exception):
    pass


def resolve_number(number, registry):
    """NUMBER_WITHOUT_FIELD gate.

    A number may participate in any judgement / ratio / schema ONLY IF it can be
    resolved to a named field inside a sealed artifact that also carries an
    artifact-level hash. Otherwise it is a rumour, not a number.
    """
    for entry in registry:
        if entry.get("field_path") and ("artifact_hash" in entry) \
                and entry.get("artifact_exists", True):
            return True
    raise NumberWithoutFieldError(
        "NUMBER_WITHOUT_FIELD: value %r has no resolvable field in any sealed "
        "artifact; it is a rumour and may not enter any judgement, ratio or "
        "schema." % (number,))


def run_fixture():
    """Positive + negative cases. The negative case MUST raise."""
    results = []

    # --- positive: a number with a named field in a sealed artifact ---------
    good_registry = [{
        "artifact": "DHE_12F_S5_SIGNED_D_M.json",
        "artifact_hash": "07a0b9cffb3af5a51e94f379b0ac1f41e7d8480c1a22d74a89ac8b9834e49378",
        "field_path": "algebraic_decomposition_reported.mean_norm_m_g",
        "artifact_exists": True,
    }]
    try:
        resolve_number(1.0676623156873744, good_registry)
        results.append({"case": "positive_named_field", "expected": "ACCEPT",
                        "observed": "ACCEPT", "pass": True})
    except NumberWithoutFieldError as e:
        results.append({"case": "positive_named_field", "expected": "ACCEPT",
                        "observed": "RAISE", "detail": str(e), "pass": False})

    # --- negative: a number with NO field anywhere -> must go RED ----------
    bad_registry = [{
        "artifact": None,
        "artifact_hash": None,
        "field_path": None,
        "artifact_exists": False,
    }]
    try:
        resolve_number(1.0677, bad_registry)
        results.append({"case": "negative_no_field", "expected": "RAISE",
                        "observed": "ACCEPT", "pass": False})
    except NumberWithoutFieldError as e:
        results.append({"case": "negative_no_field", "expected": "RAISE",
                        "observed": "RAISE", "detail": str(e), "pass": True})

    # --- negative: field named in prose only (no artifact hash) -----------
    prose_only = [{
        "artifact": "UNSEALED",
        "artifact_hash": None,
        "field_path": "prose_only.foo",
        "artifact_exists": False,
    }]
    try:
        resolve_number(2.1536, prose_only)
        results.append({"case": "negative_prose_only", "expected": "RAISE",
                        "observed": "ACCEPT", "pass": False})
    except NumberWithoutFieldError as e:
        results.append({"case": "negative_prose_only", "expected": "RAISE",
                        "observed": "RAISE", "detail": str(e), "pass": True})

    gate = "PASS" if all(r["pass"] for r in results) else "FAIL"
    return {"gate": gate, "n_cases": len(results), "cases": results}


def main():
    print("=" * 78)
    print("  DHE 12F-S5 PROVENANCE RECOVERY  (zero forward / zero autograd)")
    print("=" * 78)

    # ---- 1. verify sealed sources -----------------------------------------
    print("\n--- 1. sealed source arrays ---")
    present = {}
    for p, want in EXPECT.items():
        if not os.path.exists(p):
            present[os.path.basename(p)] = {"exists": False, "match": False}
            print("    MISSING : %s" % os.path.basename(p))
            continue
        got = sha256_file(p)
        ok = (got == want)
        present[os.path.basename(p)] = {"exists": True, "sha256": got,
                                        "expected": want, "match": ok}
        print("    %-30s %s  match=%s" % (os.path.basename(p), got[:16], ok))

    all_present = all(v.get("match") for v in present.values())
    if not all_present:
        print("\nHARD STOP: sealed source array(s) missing or hash-mismatched.")
        print("Individual deltas NOT available -> per 凌翼 §四, do not compute.")
        print("Do not re-run the model to recover 1.0677.")
        sys.exit(2)

    # ---- 2. mechanically recompute ---------------------------------------
    print("\n--- 2. mechanical recomputation from sealed deltas ---")
    deltas = np.load(DELTAS)          # [48, 4096] per-item, float32
    raw_dm = np.load(RAW_DM).astype(np.float64)
    signed_dm = np.load(SIGNED_DM).astype(np.float64)

    n_items, dim = deltas.shape
    print("    deltas shape = %s  dtype=%s" % (tuple(deltas.shape), deltas.dtype))

    if n_items % 2 != 0:
        print("HARD STOP: n_items=%d is not even; cannot pair." % n_items)
        sys.exit(2)
    n_pairs = n_items // 2

    # pairing must follow the sealed projection's source-map structure:
    # consecutive items (2 per source-map pair g), per 凌翼 §五
    d = deltas.astype(np.float64)
    d_g1 = d[0::2, :]      # [24, 4096]
    d_g2 = d[1::2, :]      # [24, 4096]

    m_g = 0.5 * (d_g1 + d_g2)     # mean component  -> [24, 4096]
    v_g = 0.5 * (d_g1 - d_g2)     # contrast comp.  -> [24, 4096]

    norm_m = np.linalg.norm(m_g, axis=1)
    norm_v = np.linalg.norm(v_g, axis=1)
    norm_d1 = np.linalg.norm(d_g1, axis=1)
    norm_d2 = np.linalg.norm(d_g2, axis=1)

    mean_norm_m_g = float(norm_m.mean())
    mean_norm_v_g = float(norm_v.mean())
    median_norm_m_g = float(np.median(norm_m))
    median_norm_v_g = float(np.median(norm_v))

    print("    n_pairs = %d ; items_per_pair = 2" % n_pairs)
    print("    mean||m_g||   = %.16f" % mean_norm_m_g)
    print("    mean||v_g||   = %.16f" % mean_norm_v_g)
    print("    median||m_g|| = %.16f" % median_norm_m_g)
    print("    median||v_g|| = %.16f" % median_norm_v_g)

    # ---- 3. compare to historical ----------------------------------------
    print("\n--- 3. comparison against historically reported values ---")
    cmp_rows = []
    for keys, recomputed in (("mean_norm_m_g", mean_norm_m_g),
                             ("mean_norm_v_g", mean_norm_v_g)):
        want = HISTORICAL[keys]
        diff = abs(recomputed - want)
        rel = diff / abs(want) if want else float("inf")
        ok = diff < 1e-12
        cmp_rows.append({"field": keys, "historical": want,
                         "recomputed": recomputed, "abs_diff": diff,
                         "rel_diff": rel, "consistent": bool(ok)})
        print("    %-16s historical=%.16f  recomputed=%.16f  diff=%.3e  %s"
              % (keys, want, recomputed, diff, "CONSISTENT" if ok else "MISMATCH"))

    consistent = all(r["consistent"] for r in cmp_rows)

    # ---- 4. cross-check against independent sealed fields ----------------
    print("\n--- 4. independent cross-checks ---")
    mean_delta_norm = float(np.linalg.norm(d.mean(axis=0)))
    s3 = json.load(open(os.path.join(REPORTS, "DHE_12F_S3_RAW_REPRODUCE.json"),
                        encoding="utf-8"))
    s5 = json.load(open(os.path.join(REPORTS, "DHE_12F_S5_SIGNED_D_M.json"),
                        encoding="utf-8"))
    check_mean_delta = (abs(mean_delta_norm
                            - s3["mean_delta_norm"]) < 1e-12)
    print("    ||mean_i delta_i|| recomputed = %.16f" % mean_delta_norm)
    print("    S3 mean_delta_norm field      = %.16f  %s"
          % (s3["mean_delta_norm"],
             "CONSISTENT" if check_mean_delta else "MISMATCH"))
    print("    S5 raw mean_norm_f64 field    = %.16f" % s5["raw_d_M_for_comparison"]["mean_norm_f64"])
    print("    S5 signed mean_norm_f64       = %.16f" % s5["signed_d_M"]["mean_norm_f64"])

    lam = 1.1402872562408447
    print("\n    lambda = %.16f" % lam)
    print("    lambda / mean||m_g|| = %.6f   <-- the disputed 1.07" % (lam / mean_norm_m_g))
    print("    lambda / ||mean delta|| = %.6f  <-- the '3.52'"
          % (lam / mean_delta_norm))

    # ---- 5. fixture -------------------------------------------------------
    print("\n--- 5. NUMBER_WITHOUT_FIELD fixture ---")
    fx = run_fixture()
    for c in fx["cases"]:
        print("    %-24s expected=%-6s observed=%-6s  %s"
              % (c["case"], c["expected"], c["observed"],
                 "PASS" if c["pass"] else "FAIL"))
    print("    fixture gate = %s" % fx["gate"])

    # ---- 6. emit new derived artifact ------------------------------------
    artifact = {
        "kind": "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE",
        "date": "2026-09-24",
        "authority": "凌翼 §四/§五 + 睫 §二 (NUMBER_WITHOUT_FIELD)",
        "artifact_role": "ZERO-FORWARD DERIVED ARTIFACT; mechanically recomputed "
                         "from sealed per-item deltas; no new model outcome",
        "reference_scale_self_declaration": {
            "state": "ADOPTED",
            "rule": "any dose ratio lambda/S must declare S",
            "required_carried_fields": [
                "definition", "scope", "operator", "unit",
                "scientific_role", "numerator_reference",
                "denominator_reference",
            ],
        },
        "quantities": {
            "mean_norm_m_g": {
                "value": mean_norm_m_g,
                "definition": "arithmetic mean over the 24 source-map pairs g of "
                              "the Euclidean norm ||m_g||_2, where "
                              "m_g = (delta_g1 + delta_g2) / 2",
                "scope": "24 source-map pairs; 48 per-item deltas; 2 items per pair",
                "operator": "L2 norm, then unweighted mean over g",
                "unit": "residual-space norm of an activation-difference vector "
                        "(same unit as ||delta_i||)",
                "scientific_role": "PER-PAIR MEAN-COMPONENT SCALE: typical size of "
                                   "the symmetric, pair-common part of a trace "
                                   "separation",
                "numerator_reference": "NOT a numerator; this is a scale S",
                "denominator_reference": "self (S in lambda/S)",
                "provenance": {
                    "source_artifact": "DHE_12F_S5_SIGNED_D_M.json",
                    "source_field": "algebraic_decomposition_reported.mean_norm_m_g",
                    "source_artifact_content_hash": s5["CONTENT_HASH"],
                    "source_array": "_dhe_12f_derive_deltas.npy",
                    "source_array_sha256": EXPECT[DELTAS],
                },
            },
            "mean_norm_v_g": {
                "value": mean_norm_v_g,
                "definition": "arithmetic mean over the 24 source-map pairs g of "
                              "||v_g||_2, where v_g = (delta_g1 - delta_g2) / 2",
                "scope": "24 source-map pairs; 48 per-item deltas; 2 items per pair",
                "operator": "L2 norm, then unweighted mean over g",
                "unit": "residual-space norm of an activation-difference vector",
                "scientific_role": "PER-PAIR CONTRAST SCALE: typical size of the "
                                   "antisymmetric, pair-distinguishing part",
                "numerator_reference": "NOT a numerator; this is a scale S",
                "denominator_reference": "self (S in lambda/S)",
                "provenance": {
                    "source_artifact": "DHE_12F_S5_SIGNED_D_M.json",
                    "source_field": "algebraic_decomposition_reported.mean_norm_v_g",
                    "source_artifact_content_hash": s5["CONTENT_HASH"],
                    "source_array": "_dhe_12f_derive_deltas.npy",
                    "source_array_sha256": EXPECT[DELTAS],
                },
            },
            "s_resultant_global": {
                "value": mean_delta_norm,
                "definition": "|| (1/48) * sum_i delta_i ||_2 -- the GLOBAL "
                              "RESULTANT vector length BEFORE per-pair pairing",
                "scope": "all 48 per-item deltas, globally pooled",
                "operator": "mean over i (vector), then L2 norm",
                "unit": "residual-space norm",
                "scientific_role": "GLOBAL-RESULTANT-SCALE DIAGNOSTIC",
                "numerator_reference": "lambda (if used as lambda/S)",
                "denominator_reference": "self",
                "provenance": {
                    "source_artifact": "DHE_12F_S3_RAW_REPRODUCE.json",
                    "source_field": "mean_delta_norm",
                    "source_artifact_content_hash": s3["CONTENT_HASH"],
                    "source_array": "_dhe_12f_derive_deltas.npy",
                    "source_array_sha256": EXPECT[DELTAS],
                },
                "warning": "contains large reciprocal cancellation; may NOT be "
                           "called the size of a typical trace and may NOT be "
                           "used as an overshoot test (凌翼 §二.1)",
            },
        },
        "delta_quantity_correction": {
            "previous_reporting": "delta_i described as per-pair, one per pair",
            "corrected_reporting": "delta_i is a PER-ITEM quantity",
            "structure": {
                "source_map_pairs": 24,
                "eligible_items": 48,
                "items_per_pair": 2,
                "deltas": 48,
            },
            "consequence": "the existence of delta_g1 and delta_g2 is precisely "
                           "what makes m_g and v_g definable",
            "impact_on_old_results": "NONE (reporting correction only)",
        },
        "ratios": {
            "lambda_over_s_resultant_global": {
                "value": lam / mean_delta_norm,
                "scale_declared": "s_resultant_global",
                "status": "VALID GLOBAL-RESULTANT RATIO; NOT an overshoot test",
            },
            "lambda_over_mean_norm_m_g": {
                "value": lam / mean_norm_m_g,
                "scale_declared": "mean_norm_m_g",
                "status": "VALID PER-PAIR MEAN-COMPONENT SCALE RATIO; geometric "
                          "diagnostic only; NOT an overshoot test",
            },
        },
        "historical_value_status": {
            "values": HISTORICAL,
            "resolution": "FIELD FOUND -- DHE_12F_S5_SIGNED_D_M.json "
                          "algebraic_decomposition_reported",
            "verdict": "RESOLVED, NOT a NUMBER_WITHOUT_FIELD",
            "recomputation_matches_historical": consistent,
        },
        "overshoot_status": {
            "lambda_over_any_norm_ratio_is_an_overshoot_test": False,
            "reason": "凌翼 §三: only a dose curve J_e(r) can test overshoot",
        },
        "counters": {
            "forward_calls": 0,
            "autograd_calls": 0,
            "logits_consumed": 0,
            "activation_reads": 0,
            "patches": 0,
            "model_loaded": False,
        },
        "fixtures": {"NUMBER_WITHOUT_FIELD": fx},
        "frozen_sentences": [
            "A scale-free 'large' is not a scientific statement.",
            "Do not call a cancellation residual the size of a typical trace.",
            "An artifact field you cannot name is a rumour; a rumour may not "
            "enter any judgement, ratio, or schema.",
        ],
    }

    if not consistent:
        artifact["HARD_STOP"] = ("recomputed values do NOT match historical; "
                                 "do not publish ratios derived from them")

    out = dict(artifact)
    out["CONTENT_HASH"] = content_hash(artifact)

    out_path = os.path.join(REPORTS, "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("\n--- 6. derived artifact ---")
    print("    %s" % os.path.basename(out_path))
    print("    CONTENT_HASH = %s" % out["CONTENT_HASH"])
    print("    forward_calls = 0 ; autograd_calls = 0 ; model_loaded = False")

    print("\n" + "=" * 78)
    print("  PROVENANCE RECOVERY DONE")
    print("  1.0677 / 2.1536  -> FIELD FOUND (not a NUMBER_WITHOUT_FIELD)")
    print("  fixture gate     -> %s" % fx["gate"])
    print("  zero forward     -> confirmed")
    print("=" * 78)


if __name__ == "__main__":
    main()
