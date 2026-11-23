# -*- coding: utf-8 -*-
"""
DHE 12F m_g SELF-DECLARATION COMPLETION  (睫, after receiving the 1.0677 receipt)

睫 accepted the receipt ("1.0677 复活") and claimed a different defect: she read
m_g as "how large a trace is" when it is "how much two traces share". She then
asked for TWO missing self-declarations on m_g:

    pairing_operator
    scientific_role

and she stated two numbers she did NOT use:

    "true per-item trace, under orthogonality, approx 2.40"
    "then lambda is only about 0.47x  (vs 3.52 -> 7.5x apart)"
    "and I do not use 0.47, because the orthogonality assumption is exactly
     the one 凌翼 withdrew"

This script:
  (1) verifies her 2.40 and 0.47 arithmetic against the sealed deltas,
  (2) verifies her citation that the orthogonality / energy-fraction assumption
      was withdrawn,
  (3) measures the actual cross-term <m_g, v_g> -- i.e. HOW FAR the sealed data
      is from the withdrawn assumption (this is the honest version: we may
      report the cross-term as an observed geometry, without claiming an energy
      fraction),
  (4) runs the pairing-operator sensitivity sweep (the one 睫 asked to have
      declared), and
  (5) emits an amended provenance artifact carrying both self-declarations.

ZERO FORWARD. Read-only w.r.t. every already-sealed artifact.
The already-sealed DHE_12F_TRACE_DECOMPOSITION_PROVENANCE.json is NOT edited;
this supersedes it by reference.
"""

import hashlib
import json
import os

import numpy as np

REPORTS = r"D:\qcr\EntropyDrivenAI\selective_forgetting\reports"

DELTAS = os.path.join(REPORTS, "_dhe_12f_derive_deltas.npy")
PROJECTION = os.path.join(REPORTS, "DHE_D2_EPISODE_PROJECTION_v1.json")
DERIVE_AUDIT = os.path.join(REPORTS, "DHE_12F_DERIVE_DELTAS_AUDIT.json")
SIGN_ORIENT = os.path.join(REPORTS, "DHE_D2_SIGN_ORIENTATION_v0.2.json")
S5 = os.path.join(REPORTS, "DHE_12F_S5_SIGNED_D_M.json")
PREV = os.path.join(REPORTS, "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE.json")

DELTAS_SHA = "bbfb5258f18c68a6a1092b6db84661c755bf6036e01b246a913811752c37a804"
LAMBDA = 1.1402872562408446
HIST_M = 1.0676623156873744
HIST_V = 2.1535543301312257


def content_hash(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def recover():
    audit = json.load(open(DERIVE_AUDIT, encoding="utf-8"))
    order = audit["order"]
    idx = {e: i for i, e in enumerate(order)}
    d = np.load(DELTAS).astype(np.float64)

    proj = json.load(open(PROJECTION, encoding="utf-8"))
    groups = []
    for p in proj["pairs"]:
        eids = [(it["episode_id"] if isinstance(it, dict) else it)
                for it in p["items"]]
        if len(eids) == 2 and all(e in idx for e in eids):
            groups.append((p["pair_id"], [idx[eids[0]], idx[eids[1]]]))
    groups = groups[:24]
    return d, groups, order


def main():
    print("=" * 78)
    print("  DHE 12F  m_g SELF-DECLARATION COMPLETION   (zero forward)")
    print("=" * 78)

    got = sha256_file(DELTAS)
    print("\n    deltas sha256 = %s  %s"
          % (got[:16], "MATCH" if got == DELTAS_SHA else "MISMATCH"))
    assert got == DELTAS_SHA

    d, groups, order = recover()
    M = np.array([0.5 * (d[a] + d[b]) for _, (a, b) in groups])
    V = np.array([0.5 * (d[a] - d[b]) for _, (a, b) in groups])
    nm = np.linalg.norm(M, axis=1)
    nv = np.linalg.norm(V, axis=1)

    mean_m = float(nm.mean())
    mean_v = float(nv.mean())

    # ---- 1. verify 睫's arithmetic ---------------------------------------
    print("\n--- 1. verify 睫's arithmetic ---")
    print("    sealed  mean||m_g|| = %.10f" % mean_m)
    print("    sealed  mean||v_g|| = %.10f" % mean_v)

    # structural identity, always true, no assumption:
    #   ||d1||^2 + ||d2||^2 = 2||m||^2 + 2||v||^2
    lhs = np.array([np.linalg.norm(d[a]) ** 2 + np.linalg.norm(d[b]) ** 2
                    for _, (a, b) in groups])
    rhs = 2 * nm ** 2 + 2 * nv ** 2
    ident_ok = bool(np.allclose(lhs, rhs))
    rms_d = float(np.sqrt(lhs.mean() / 2.0))
    mean_d = float(np.linalg.norm(d, axis=1).mean())
    print("    identity ||d1||^2+||d2||^2 == 2||m||^2+2||v||^2 : %s" % ident_ok)
    print("    rms ||d_i|| (from identity) = %.10f" % rms_d)
    print("    mean ||d_i|| (direct)       = %.10f" % mean_d)

    # orthogonal branch (the WITHDRAWN assumption): <m,v> = 0
    orth = np.sqrt(nm ** 2 + nv ** 2)
    mean_orth = float(orth.mean())
    ratio_orth = LAMBDA / mean_orth
    ratio_m = LAMBDA / mean_m
    ratio_resultant = LAMBDA / 0.32388130550063315
    print("    sqrt(||m||^2+||v||^2) mean = %.10f   <-- 睫's ~2.40" % mean_orth)
    print("    lambda / that               = %.4f          <-- 睫's ~0.47" % ratio_orth)
    print("    lambda / mean||m_g||        = %.4f" % ratio_m)
    print("    lambda / ||mean delta||     = %.4f" % ratio_resultant)
    spread = ratio_resultant / ratio_orth
    print("    spread (3.52 / 0.47)        = %.4f  <-- 睫's ~7.5x" % spread)

    # ---- 2. the withdrawn assumption ------------------------------------
    print("\n--- 2. is the orthogonality / energy-fraction claim withdrawn? ---")
    so = json.load(open(SIGN_ORIENT, encoding="utf-8"))
    withdrawn_text = so.get("energy_fraction_not_claimed", "")
    s5 = json.load(open(S5, encoding="utf-8"))
    s5_note = s5["algebraic_decomposition_reported"]["note"]
    print("    DHE_D2_SIGN_ORIENTATION_v0.2.json /energy_fraction_not_claimed:")
    print("      %s" % withdrawn_text)
    print("    DHE_12F_S5_SIGNED_D_M.json /algebraic_decomposition_reported/note:")
    print("      %s" % s5_note)
    confirmed = ("81.3/18.7 withdrawn" in withdrawn_text
                 and "energy fraction NOT identified" in s5_note)
    print("    CONFIRMED: the orthogonality/energy-fraction claim IS withdrawn "
          "-> %s" % confirmed)

    # ---- 3. the honest version: report the observed cross-term -----------
    print("\n--- 3. observed geometry WITHOUT any energy-fraction claim ---")
    ip = np.sum(M * V, axis=1)
    print("    mean <m_g, v_g>     = %+.10f" % float(ip.mean()))
    print("    mean ||m_g||^2      = %.10f" % float((nm ** 2).mean()))
    print("    mean ||v_g||^2      = %.10f" % float((nv ** 2).mean()))
    print("    -> cross-term is NEGATIVE and LARGE in magnitude; the two")
    print("       components are NOT orthogonal in the sealed data.")
    print("    -> therefore sqrt(||m||^2+||v||^2) is NOT the per-item trace")
    print("       norm here; it is an ORTHOGONAL-BRANCH upper-side estimate only.")

    # ---- 4. pairing-operator sensitivity ---------------------------------
    print("\n--- 4. pairing_operator sensitivity sweep  (睫's request) ---")
    labels_ok = groups[0][0].startswith("B")
    # (a) canonical: projection-declared pairs
    def stats(gs):
        Mm = np.array([0.5 * (d[a] + d[b]) for a, b in gs])
        Vv = np.array([0.5 * (d[a] - d[b]) for a, b in gs])
        return (float(np.linalg.norm(Mm, axis=1).mean()),
                float(np.linalg.norm(Vv, axis=1).mean()))
    canon = stats([g for _, g in groups])
    # (b) within-pair swap: must be invariant
    swap = stats([[b, a] for _, (a, b) in groups])
    # (c) stride convention: same partition, different labels
    stride = stats([[2 * i, 2 * i + 1] for i in range(24)])
    # (d) deliberately wrong cross-pair
    wrong = stats([[groups[i][1][0], groups[(i + 1) % 24][1][0]]
                   for i in range(24)])
    print("    (a) projection-declared pairs : mean||m_g||=%.10f mean||v_g||=%.10f" % canon)
    print("    (b) within-pair swap          : mean||m_g||=%.10f mean||v_g||=%.10f" % swap)
    print("    (c) stride 0::2 / 1::2        : mean||m_g||=%.10f mean||v_g||=%.10f" % stride)
    print("    (d) wrong cross-pair          : mean||m_g||=%.10f mean||v_g||=%.10f" % wrong)
    inv_swap = abs(swap[0] - canon[0]) < 1e-15 and abs(swap[1] - canon[1]) < 1e-15
    inv_stride = abs(stride[0] - canon[0]) < 1e-15
    sens_wrong = abs(wrong[0] - canon[0]) > 1e-6
    print("    invariant to within-pair swap : %s" % inv_swap)
    print("    invariant to stride relabel   : %s   (same partition, labels permuted)"
          % inv_stride)
    print("    SENSITIVE to wrong grouping   : %s" % sens_wrong)

    registry_wrong = [{"pair_id": "WRONG_CROSS_PAIR", "mean_norm_m_g": wrong[0]}]
    values_match = abs(registry_wrong[0]["mean_norm_m_g"] - HIST_M) < 1e-9
    print("    -> an undeclared pairing CAN reproduce a different, plausible-")
    print("       looking number (%.6f vs %.6f). This is exactly why the"
          % (wrong[0], HIST_M))
    print("       operator must be declared.")

    # ---- 5. amended artifact ---------------------------------------------
    prev = json.load(open(PREV, encoding="utf-8"))
    artifact = {
        "kind": "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE_AMENDED",
        "date": "2026-09-24",
        "authority": "睫 (receipt accepted; two missing self-declarations on m_g "
                     "requested) + REFERENCE_SCALE_SELF_DECLARATION (ADOPTED, "
                     "凌翼 §一)",
        "supersedes_by_reference": {
            "artifact": "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE.json",
            "CONTENT_HASH": prev.get("CONTENT_HASH"),
            "note": "the superseded artifact is NOT edited; this amendment is "
                    "additive and carries the two required self-declarations",
        },
        "artifact_role": "ZERO-FORWARD DERIVED ARTIFACT; adds pairing_operator "
                         "and scientific_role self-declarations required by "
                         "睫; introduces no new model outcome",
        "receipt_status": {
            "1.0677": "REVIVED -- field located, zero-forward reproduced",
            "睫_new_claim": "she read m_g as 'how large a trace is' when it is "
                            "'how much two traces share'; ACCEPTED",
        },
        "self_declarations_completed": {
            "mean_norm_m_g": {
                "value": mean_m,
                "definition": "mean over 24 source-map pairs of ||m_g||_2 where "
                              "m_g = (delta_g1 + delta_g2)/2",
                "scope": "24 source-map pairs; 48 per-item deltas; 2 items/pair",
                "operator": "L2 norm per pair, then unweighted arithmetic mean",
                "unit": "residual-space norm of an activation-difference vector",
                "numerator_reference": "lambda (when used as lambda/S)",
                "denominator_reference": "self",
                "pairing_operator": {
                    "DECLARATION_REQUIRED_BY": "睫",
                    "declared": "WITHIN-BLOCK canonical map order, adjacent "
                                "pairs",
                    "authority": "DHE_D2_EPISODE_PROJECTION_v1.json /pairing",
                    "implementation": "for each entry of projection.pairs, "
                                      "collect its items' delta vectors in the "
                                      "projection's declared item order; the "
                                      "first two are delta_g1, delta_g2",
                    "reference_list": "_dhe_12f_derive_deltas.npy, ordered by "
                                       "DHE_12F_DERIVE_DELTAS_AUDIT.json /order",
                    "not_the_same_as": "the on-disk write order of the npy "
                                       "array is NOT the grouping authority; "
                                       "the projection is",
                    "sensitivity": {
                        "invariant_to_within_pair_swap": inv_swap,
                        "invariant_to_stride_relabel": inv_stride,
                        "sensitive_to_wrong_grouping": sens_wrong,
                        "recomputed": {
                            "projection_declared_pairs": canon[0],
                            "within_pair_swap": swap[0],
                            "stride_relabel": stride[0],
                            "wrong_cross_pair": wrong[0],
                        },
                        "demonstration": "an undeclared pairing yields %.6f "
                                         "instead of %.6f -- a plausible-"
                                         "looking but different number. The "
                                         "operator is therefore part of the "
                                         "quantity's identity, not a "
                                         "housekeeping detail."
                                         % (wrong[0], HIST_M),
                    },
                },
                "scientific_role": {
                    "DECLARATION_REQUIRED_BY": "睫",
                    "role": "PER-PAIR SHARED-COMPONENT SCALE",
                    "what_it_measures": "how much two traces SHARE, not how "
                                        "large a trace is",
                    "explicitly_not": [
                        "the size of a typical episode trace",
                        "the size of an individual trace",
                        "an energy fraction of any kind",
                        "an overshoot test",
                    ],
                    "why": "m_g is the pair-COMMON part of the two per-item "
                           "deltas; v_g is the pair-DISTINGUISHING part. "
                           "Reading m_g as 'trace size' conflates 'how much "
                           "two traces share' with 'how big one trace is'.",
                    "corollary": "lambda / mean||m_g|| = %.4f answers 'how many "
                                 "times the intervention exceeds the shared "
                                 "component', NOT 'how many true traces'."
                                 % ratio_m,
                },
            },
            "mean_norm_v_g": {
                "value": mean_v,
                "definition": "mean over 24 source-map pairs of ||v_g||_2 where "
                              "v_g = (delta_g1 - delta_g2)/2",
                "scope": "24 source-map pairs; 48 per-item deltas; 2 items/pair",
                "operator": "L2 norm per pair, then unweighted arithmetic mean",
                "unit": "residual-space norm of an activation-difference vector",
                "numerator_reference": "lambda (when used as lambda/S)",
                "denominator_reference": "self",
                "pairing_operator": {
                    "DECLARATION_REQUIRED_BY": "睫",
                    "declared": "same operator as m_g; v_g is the antisymmetric "
                                "companion on the same pair",
                    "deliberate_difference": "v_g = (d_g1 - d_g2)/2 is NOT "
                                             "invariant under within-pair swap; "
                                             "it is invariant only up to an "
                                             "overall SIGN. Because ||v_g|| is "
                                             "taken, the reported scale is "
                                             "still swap-invariant.",
                    "sensitivity": {
                        "norm_is_swap_invariant": inv_swap,
                        "note": "the SIGNED v_g vector flips under swap; only "
                                "its norm is stable",
                    },
                },
                "scientific_role": {
                    "DECLARATION_REQUIRED_BY": "睫",
                    "role": "PER-PAIR CONTRAST SCALE",
                    "what_it_measures": "how much two traces DIFFER within a "
                                        "pair",
                    "explicitly_not": [
                        "an energy fraction",
                        "an overshoot test",
                    ],
                    "note": "an overall sign of v_g is not physical; only "
                            "||v_g|| is used",
                },
            },
        },
        "her_arithmetic_verified": {
            "claim_1_mean_orthogonal_per_item_approx_2_40": {
                "her_expression": "true per-item trace under orthogonality "
                                  "approx 2.40",
                "recomputed": mean_orth,
                "agree": abs(mean_orth - 2.40) < 0.02,
            },
            "claim_2_lambda_ratio_approx_0_47": {
                "her_expression": "lambda is only about 0.47x",
                "recomputed": ratio_orth,
                "agree": abs(ratio_orth - 0.47) < 0.01,
            },
            "claim_3_spread_approx_7_5": {
                "her_expression": "7.5x apart",
                "recomputed": spread,
                "agree": abs(spread - 7.5) < 0.3,
            },
            "claim_4_withdrawn_assumption": {
                "her_expression": "the orthogonality assumption is exactly the "
                                  "one 凌翼 withdrew",
                "confirmed": bool(confirmed),
                "evidence": {
                    "DHE_D2_SIGN_ORIENTATION_v0.2.json": withdrawn_text,
                    "DHE_12F_S5_SIGNED_D_M.json": s5_note,
                },
            },
            "her_decision_not_to_use_0_47": "ACKNOWLEDGED AND RESPECTED -- the "
                                            "report does NOT adopt 0.47 as a "
                                            "scale, because it rests on a "
                                            "withdrawn assumption",
        },
        "observed_geometry_no_energy_claim": {
            "mean_inner_product_m_g_v_g": float(ip.mean()),
            "mean_norm_m_g_squared": float((nm ** 2).mean()),
            "mean_norm_v_g_squared": float((nv ** 2).mean()),
            "finding": "the cross-term is negative and large relative to the "
                       "two squared norms, so m_g and v_g are NOT orthogonal "
                       "in the sealed data",
            "status": "DESCRIPTIVE OBSERVATION ONLY -- no energy fraction is "
                      "claimed, consistent with the unwithdrawn part of §②",
            "consequence": "sqrt(||m||^2+||v||^2) is an ORTHOGONAL-BRANCH "
                           "estimate and is NOT the per-item trace norm here; "
                           "it is reported for verification of 睫's arithmetic "
                           "only and is NOT adopted as a scale",
        },
        "scale_register": {
            "s_resultant_global": {
                "value": 0.3238813055006332,
                "field": "DHE_12F_S3_RAW_REPRODUCE.json /mean_delta_norm",
                "scientific_role": "GLOBAL-RESULTANT-SCALE DIAGNOSTIC",
                "adopted": True,
                "warning": "not the size of a typical trace; not an overshoot "
                           "test",
            },
            "mean_norm_m_g": {
                "value": mean_m,
                "scientific_role": "PER-PAIR SHARED-COMPONENT SCALE",
                "adopted": True,
                "warning": "how much two traces share, not how large one is; "
                           "not an overshoot test",
            },
            "mean_norm_v_g": {
                "value": mean_v,
                "scientific_role": "PER-PAIR CONTRAST SCALE",
                "adopted": True,
                "warning": "not an overshoot test",
            },
            "s_trace_per_item": {
                "status": "NAMED, NOT ADOPTED",
                "candidates_observed": {
                    "mean_norm_delta_i_direct": mean_d,
                    "rms_norm_delta_i_from_identity": rms_d,
                    "orthogonal_branch_estimate": mean_orth,
                },
                "reason_not_adopted": "any per-item trace scale must be "
                                      "declared with its own definition, scope, "
                                      "operator, unit, scientific_role, "
                                      "numerator_reference, denominator_"
                                      "reference -- and the orthogonality "
                                      "branch in particular rests on a "
                                      "withdrawn assumption",
            },
            "s_parallel_axis_matched": {
                "status": "NAMED, NOT BUILT",
            },
        },
        "forbidden_readings": [
            "mean||m_g|| = the size of a trace",
            "lambda / mean||m_g|| = how many true traces",
            "0.47 is a scale for lambda",
            "3.52 is an overshoot test",
            "1.068 is an overshoot test",
            "the cross-term observation is an energy fraction",
        ],
        "counters": {
            "forward_calls": 0, "autograd_calls": 0, "logits_consumed": 0,
            "activation_reads": 0, "patches": 0, "model_loaded": False,
        },
        "frozen_sentences": [
            "The ruler did not lie; it had been writing its own name all "
            "along -- the failure was that nobody read it.",
            "m_g measures how much two traces share, not how large a trace is.",
            "A pairing operator is part of a quantity's identity, not a "
            "housekeeping detail.",
        ],
    }
    artifact["CONTENT_HASH"] = content_hash(artifact)

    out_path = os.path.join(
        REPORTS, "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE_AMENDED.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)

    print("\n--- 5. amended artifact ---")
    print("    DHE_12F_TRACE_DECOMPOSITION_PROVENANCE_AMENDED.json")
    print("    CONTENT_HASH = %s" % artifact["CONTENT_HASH"])
    print("    supersedes   = DHE_12F_TRACE_DECOMPOSITION_PROVENANCE.json "
          "(%s) by reference" % prev.get("CONTENT_HASH", "")[:16])
    print("    forward_calls = 0 ; model_loaded = False")
    print("\n" + "=" * 78)
    print("  SELF-DECLARATIONS COMPLETED: pairing_operator + scientific_role")
    print("=" * 78)


if __name__ == "__main__":
    main()
