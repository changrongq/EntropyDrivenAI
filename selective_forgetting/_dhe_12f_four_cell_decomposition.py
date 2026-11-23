# -*- coding: utf-8 -*-
"""
DHE 12F FOUR-CONDITION-CELL DECOMPOSITION  (凌翼 §六 + §七, 睫 §四)

AUTHORIZED: zero new forward. Data already sealed in DHE_12F_PER_ITEM.v1.1.json.

WHAT THIS IS
    POST-HOC DESCRIPTIVE RE-EXPRESSION OF ALREADY OPENED DATA.

WHAT THIS IS NOT
    It is NOT a gate. It does NOT change result_class. It does NOT prove an
    interior maximum. 凌翼 §七: four points obtained near two DIFFERENT base
    points (E_A, E_B) along a parallel direction do not lie on a proven common
    coordinate line, so they may not be spliced into a one-dimensional f(x) and
    mined for an extremum. They show shore-specific finite-dose response
    pattern only.

REQUIRED MARKS (凌翼 §六 / 睫 §四)
    - POST-HOC
    - DESCRIPTIVE
    - HYPOTHESIS-GENERATING
    - four cells reported in full, never only the significant one
    - if any single cell value is ever cited, it must travel together with
      C_raw, fraction_positive, and both arm means

MECHANICAL IDENTITY CHECKS (凌翼 §六)
    B_raw_plus_armA  - B_raw_minus_armA == C_raw_armA
    B_raw_plus_armB  - B_raw_minus_armB == C_raw_armB
    same for signed.
    This is where the shore reversal is taken apart: is the +lambda arm moving,
    the -lambda arm moving, or both?

ZERO FORWARD. Read-only w.r.t. the sealed artifact.
"""

import hashlib
import json
import os
import statistics as st

REPORTS = r"D:\qcr\EntropyDrivenAI\selective_forgetting\reports"
PER_ITEM = os.path.join(REPORTS, "DHE_12F_PER_ITEM.v1.1.json")
CONFIRM = os.path.join(REPORTS, "DHE_12F_CAUSAL_CONFIRM.v1.1.json")

PER_ITEM_EXPECTED_CONTENT_HASH = "abfae9dc3f706127c66d121dafc5d1567a4cc19d13fda43764d687ae9ac77a0a"


def content_hash(obj_without_hash):
    blob = json.dumps(obj_without_hash, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def med(xs):
    return st.median(xs) if xs else float("nan")


def frac_pos(xs):
    return sum(1 for x in xs if x > 0) / len(xs) if xs else float("nan")


def main():
    d = json.load(open(PER_ITEM, encoding="utf-8"))
    items = d["per_item"]
    n = len(items)

    print("=" * 78)
    print("  DHE 12F FOUR-CONDITION-CELL DECOMPOSITION")
    print("  POST-HOC / DESCRIPTIVE / HYPOTHESIS-GENERATING  (zero forward)")
    print("=" * 78)
    print("\n    artifact   : DHE_12F_PER_ITEM.v1.1.json")
    print("    n_items    : %d" % n)
    ch = d.get("CONTENT_HASH", "")
    print("    CONTENT_HASH = %s  (expected prefix %s) %s"
          % (ch[:16], PER_ITEM_EXPECTED_CONTENT_HASH[:16],
             "MATCH" if ch == PER_ITEM_EXPECTED_CONTENT_HASH else "MISMATCH"))

    # ---- extract four cells per estimator --------------------------------
    B_raw = {"A,+": [], "A,-": [], "B,+": [], "B,-": []}
    B_sig = {"A,+": [], "A,-": [], "B,+": [], "B,-": []}
    C_raw_armA, C_raw_armB, C_sig_armA, C_sig_armB = [], [], [], []

    for it in items:
        B_raw["A,+"] .append(it["B_raw_plus_armA"])
        B_raw["A,-"] .append(it["B_raw_minus_armA"])
        B_raw["B,+"] .append(it["B_raw_plus_armB"])
        B_raw["B,-"] .append(it["B_raw_minus_armB"])
        B_sig["A,+"] .append(it["B_signed_plus_armA"])
        B_sig["A,-"] .append(it["B_signed_minus_armA"])
        B_sig["B,+"] .append(it["B_signed_plus_armB"])
        B_sig["B,-"] .append(it["B_signed_minus_armB"])
        C_raw_armA.append(it["C_raw_armA"])
        C_raw_armB.append(it["C_raw_armB"])
        C_sig_armA.append(it["C_signed_armA"])
        C_sig_armB.append(it["C_signed_armB"])

    # ---- 1. mechanical identity checks -----------------------------------
    print("\n--- 1. mechanical identity checks  [凌翼 §六] ---")
    ident = []
    checks = [
        ("raw", "A", B_raw["A,+"], B_raw["A,-"], C_raw_armA),
        ("raw", "B", B_raw["B,+"], B_raw["B,-"], C_raw_armB),
        ("signed", "A", B_sig["A,+"], B_sig["A,-"], C_sig_armA),
        ("signed", "B", B_sig["B,+"], B_sig["B,-"], C_sig_armB),
    ]
    ident_all = True
    for est, arm, bp, bm, cdec in checks:
        worst = 0.0
        for i in range(n):
            worst = max(worst, abs((bp[i] - bm[i]) - cdec[i]))
        ok = worst < 1e-12
        ident_all = ident_all and ok
        ident.append({"estimator": est, "arm": arm,
                      "identity": "B_+ - B_- == C_arm",
                      "max_abs_residual": worst, "holds": bool(ok)})
        print("    %-7s arm %s : max|(B+ - B-) - C_arm| = %.3e   %s"
              % (est, arm, worst, "HOLDS" if ok else "BREACH"))
    print("    identity gate = %s" % ("PASS" if ident_all else "FAIL"))

    # ---- 2. four cells, reported IN FULL ---------------------------------
    print("\n--- 2. four cells, reported in full (raw primary) ---")
    cells = {}
    for est, B in (("raw", B_raw), ("signed", B_sig)):
        cells[est] = {}
        for k in ("A,+", "A,-", "B,+", "B,-"):
            v = B[k]
            cells[est][k] = {"mean": mean(v), "median": med(v),
                             "min": min(v), "max": max(v),
                             "sd": st.pstdev(v), "n": len(v)}
        print("\n    [%s]" % est)
        print("      %-6s %14s %14s %14s %14s" % ("cell", "mean", "median",
                                                   "min", "max"))
        for k in ("A,+", "A,-", "B,+", "B,-"):
            c = cells[est][k]
            print("      %-6s %14.7f %14.7f %14.7f %14.7f"
                  % (k, c["mean"], c["median"], c["min"], c["max"]))

    # ---- 3. where did the shore reversal come from? ----------------------
    print("\n--- 3. shore reversal taken apart  [凌翼 §六] ---")
    decomposition = {}
    for est, B, cA, cB in (("raw", B_raw, C_raw_armA, C_raw_armB),
                            ("signed", B_sig, C_sig_armA, C_sig_armB)):
        mA, mAm, mB, mBm = (mean(B["A,+"]), mean(B["A,-"]),
                            mean(B["B,+"]), mean(B["B,-"]))
        dA = mA - mAm        # = mean C_A
        dB = mB - mBm        # = mean C_B
        decomposition[est] = {
            "cell_means": {"A_plus": mA, "A_minus": mAm,
                           "B_plus": mB, "B_minus": mBm},
            "A_plus_movement":  mA - mAm,
            "A_minus_movement": mAm - mA,
            "B_plus_movement":  mB - mBm,
            "B_minus_movement": mBm - mB,
            "C_A_raw_est": dA, "C_B_est": dB, "C_est": 0.5 * (dA + dB),
            "C_arm_means_from_sealed_fields": {
                "C_raw_armA": mean(cA), "C_raw_armB": mean(cB),
                "C_est_from_arms": 0.5 * (mean(cA) + mean(cB)),
            } if est == "raw" else {
                "C_signed_armA": mean(cA), "C_signed_armB": mean(cB),
                "C_est_from_arms": 0.5 * (mean(cA) + mean(cB)),
            },
            "delta_between_cells": {
                "A_signed_shift": mAm - mA,
                "B_signed_shift": mBm - mB,
                "sign_effect_A_pro_baseline":
                    (mA - mAm) + (mB - mBm),
            },
        }
        print("\n    [%s]" % est)
        print("      Bbar_{A,+} = %+.7f    Bbar_{A,-} = %+.7f   -> C_A = %+.7f"
              % (mA, mAm, dA))
        print("      Bbar_{B,+} = %+.7f    Bbar_{B,-} = %+.7f   -> C_B = %+.7f"
              % (mB, mBm, dB))
        print("      C = (C_A + C_B)/2 = %+.10f" % (0.5 * (dA + dB)))
        # which arm moves more?
        am_mag = abs(dA)
        bm_mag = abs(dB)
        print("      |C_A| = %.7f   |C_B| = %.7f   ratio |C_A|/|C_B| = %.4f"
              % (am_mag, bm_mag, (am_mag / bm_mag) if bm_mag else float("inf")))
        # is the reversal from magnitude asymmetry or sign opposition?
        if dA * dB < 0:
            print("      -> C_A and C_B have OPPOSITE SIGNS: shore reversal is a "
                  "SIGN opposition between shores, not a mere magnitude difference")
        else:
            print("      -> C_A and C_B share sign: any cancellation is a "
                  "MAGNITUDE effect within a common sign")

    # ---- 4. always-together citation bundle ------------------------------
    print("\n--- 4. citation bundle (must travel together)  [凌翼 §六 / 睫 §四] ---")
    bundle = {}
    for est, c_arm_a, c_arm_b in (("raw", C_raw_armA, C_raw_armB),
                                   ("signed", C_sig_armA, C_sig_armB)):
        c_i = [0.5 * (a + b) for a, b in zip(c_arm_a, c_arm_b)]
        bundle[est] = {
            "C": mean(c_i),
            "fraction_positive": frac_pos(c_i),
            "n_positive": sum(1 for x in c_i if x > 0),
            "n_total": len(c_i),
            "armA_mean": mean(c_arm_a),
            "armB_mean": mean(c_arm_b),
        }
        print("    [%s] C=%+.10f  fraction_positive=%.4f (%d/%d)  "
              "armA_mean=%+.7f  armB_mean=%+.7f"
              % (est, bundle[est]["C"], bundle[est]["fraction_positive"],
                 bundle[est]["n_positive"], bundle[est]["n_total"],
                 bundle[est]["armA_mean"], bundle[est]["armB_mean"]))

    # ---- 5. cross-check against sealed CAUSAL_CONFIRM --------------------
    print("\n--- 5. cross-check against sealed CAUSAL_CONFIRM.v1.1 ---")
    cc = json.load(open(CONFIRM, encoding="utf-8"))
    xc = {"artifact": "DHE_12F_CAUSAL_CONFIRM.v1.1.json",
          "CONTENT_HASH": cc.get("CONTENT_HASH", ""), "checks": []}
    sealed_map = {
        "raw": cc["PRIMARY_RESULTS"]["C_raw"],
        "signed": cc["PRIMARY_RESULTS"]["C_signed"],
    }
    for est, recomputed in (("raw", bundle["raw"]["C"]),
                             ("signed", bundle["signed"]["C"])):
        sealed = sealed_map[est]
        diff = abs(recomputed - sealed)
        entry = {"estimator": est,
                 "key_path": "PRIMARY_RESULTS.C_%s" % est,
                 "recomputed_from_per_item": recomputed,
                 "sealed_value": sealed,
                 "abs_diff": diff,
                 "consistent": bool(diff < 1e-15)}
        xc["checks"].append(entry)
        print("    %-7s recomputed=%+.16f  sealed=%+.16f  diff=%.3e  %s"
              % (est, recomputed, sealed, diff,
                 "CONSISTENT" if entry["consistent"] else "MISMATCH"))

    # arm means cross-check
    arm_sealed = cc["descriptive"]["arm_symmetry_raw"]
    arm_diff_a = abs(bundle["raw"]["armA_mean"] - arm_sealed["armA_mean"])
    arm_diff_b = abs(bundle["raw"]["armB_mean"] - arm_sealed["armB_mean"])
    xc["arm_mean_checks"] = {
        "armA_mean": {"recomputed": bundle["raw"]["armA_mean"],
                      "sealed": arm_sealed["armA_mean"], "abs_diff": arm_diff_a},
        "armB_mean": {"recomputed": bundle["raw"]["armB_mean"],
                      "sealed": arm_sealed["armB_mean"], "abs_diff": arm_diff_b},
    }
    print("    armA_mean recomputed=%+.12f sealed=%+.12f diff=%.3e"
          % (bundle["raw"]["armA_mean"], arm_sealed["armA_mean"], arm_diff_a))
    print("    armB_mean recomputed=%+.12f sealed=%+.12f diff=%.3e"
          % (bundle["raw"]["armB_mean"], arm_sealed["armB_mean"], arm_diff_b))

    xc["all_consistent"] = bool(
        all(c["consistent"] for c in xc["checks"])
        and arm_diff_a < 1e-15 and arm_diff_b < 1e-15)
    print("    cross-check gate = %s"
          % ("PASS" if xc["all_consistent"] else "FAIL"))

    # ---- 6. forbidden inferences ----------------------------------------
    forbidden = {
        "interior_maximum_proven": False,
        "reason": "凌翼 §七: E_A and E_B are two high-dimensional reference "
                  "states; it is NOT established that they lie on a common "
                  "d_M coordinate line. Four points near two different base "
                  "points may not be spliced into one f(x).",
        "overshoot_established": False,
        "reason_2": "凌翼 §三: only a dose curve J_e(r) can test overshoot.",
        "result_class_changed": False,
        "gate_created": False,
        "single_cell_may_be_cited_alone": False,
    }

    # ---- artifact --------------------------------------------------------
    artifact = {
        "kind": "DHE_12F_FOUR_CONDITION_CELL_DECOMPOSITION",
        "date": "2026-09-24",
        "authority": "凌翼 §六 (AUTHORIZED NOW, zero new forward) + §七 "
                     "(no interior-maximum claim) + 睫 §四 (four cells all "
                     "reported, marked POST-HOC, no in-window conclusion)",
        "artifact_role": "POST-HOC DESCRIPTIVE RE-EXPRESSION OF ALREADY "
                         "OPENED DATA",
        "marks": ["POST-HOC", "DESCRIPTIVE", "HYPOTHESIS-GENERATING"],
        "not_a_gate": True,
        "does_not_change_result_class": True,
        "source": {
            "artifact": "DHE_12F_PER_ITEM.v1.1.json",
            "CONTENT_HASH": ch,
            "n_items": n,
            "cells_used": ["B_{raw,signed}_{plus,minus}_{armA,armB}"],
        },
        "four_cells": cells,
        "identity_checks": {"all_hold": bool(ident_all), "checks": ident},
        "shore_decomposition": decomposition,
        "citation_bundle_must_travel_together": bundle,
        "cross_check_vs_sealed_confirm": xc,
        "forbidden_inferences": forbidden,
        "counters": {
            "forward_calls": 0, "autograd_calls": 0, "logits_consumed": 0,
            "activation_reads": 0, "patches": 0, "model_loaded": False,
        },
        "citation_rule": "If ANY single four-cell value is ever cited, it must be "
                         "cited together with C_raw, fraction_positive, and both "
                         "arm means. Citing one cell alone is selective "
                         "reporting.",
        "next_step_note": "凌翼 §八: after this, STOP NUMERICAL EXPLORATION. The "
                          "next numerical query must come from a pre-written 12G "
                          "mechanism protocol.",
        "frozen_sentences": [
            "Do not infer a response curve from four points that do not share a "
            "proven coordinate line.",
            "Four cells may inspire curvature, overshoot, or a state-dependent "
            "Jacobian; they may not identify any of the three.",
        ],
    }
    artifact["CONTENT_HASH"] = content_hash(artifact)

    out_path = os.path.join(REPORTS, "DHE_12F_FOUR_CONDITION_CELLS.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)

    print("\n--- artifact ---")
    print("    DHE_12F_FOUR_CONDITION_CELLS.json")
    print("    CONTENT_HASH = %s" % artifact["CONTENT_HASH"])
    print("    forward_calls = 0 ; autograd = 0 ; model_loaded = False")
    print("\n" + "=" * 78)
    print("  FOUR-CELL DECOMPOSITION DONE  (descriptive only; no gate; "
          "result_class unchanged)")
    print("=" * 78)


if __name__ == "__main__":
    main()
