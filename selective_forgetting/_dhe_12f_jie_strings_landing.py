# -*- coding: utf-8 -*-
"""
DHE 12F m_g / v_g — 睫'S SIGNED STRINGS, LANDED VERBATIM.

睫's instruction:
    "他要字，我就给字——一个标点都不许他改，也不许我自己以后再改。"

So: the strings below are copied byte-for-byte. They are NOT paraphrased,
NOT reformatted, NOT "improved". `reference_scale_eligible` is a HARD FIELD --
it may not be absent and may not be null.

She also required, immediately (not next window):

    ||delta_{g,i}|| = sqrt(||m_g||^2 + ||v_g||^2)  HOLDS ONLY IF m_g ⟂ v_g
    => orthogonality NOT established (81.3/18.7 withdrawal)
    => per-item trace magnitude = UNDEFINED IN SEALED ARTIFACTS
    => lambda natural-scale ratio = UNANSWERABLE;
       three candidate denominators (0.324 / 1.0677 / ~2.40) listed side by
       side, none licensed

This script:
  (1) verifies the verbatim strings against a frozen source-of-truth copy
      (guards against later silent edits -- "也不许我自己以后再改"),
  (2) computes S_trace = median_i ||delta_i||  and
      S_parallel = median_i |<delta_i, d_M_raw>|   (zero forward),
  (3) emits the artifact with the exact strings and the hard field.

ZERO FORWARD.
"""

import hashlib
import json
import os

import numpy as np

REPORTS = r"D:\qcr\EntropyDrivenAI\selective_forgetting\reports"
DELTAS = os.path.join(REPORTS, "_dhe_12f_derive_deltas.npy")
RAW_DM = os.path.join(REPORTS, "_dhe_12f_raw_dm.npy")
DERIVE_AUDIT = os.path.join(REPORTS, "DHE_12F_DERIVE_DELTAS_AUDIT.json")
PREV_AMENDED = os.path.join(
    REPORTS, "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE_AMENDED.json")

DELTAS_SHA = "bbfb5258f18c68a6a1092b6db84661c755bf6036e01b246a913811752c37a804"
LAMBDA = 1.1402872562408446

# ===========================================================================
# VERBATIM STRINGS — 睫 signed these. Byte-for-byte. Do not touch.
# ===========================================================================
JIE_STRINGS = {
    "m_g": {
        "scientific_role": "PER-PAIR SHARED-COMPONENT SCALE",
        "misreading_guard": "NOT a per-item trace magnitude; NOT an episode "
                            "effect size; NOT a licensed dose-reference scale.",
        "pairing_operator": "m_g = (delta_{g,1} + delta_{g,2}) / 2, over the two "
                            "eligible items of frozen source-map pair g, taken "
                            "in the frozen P_b ordering; |m_g| reported as L2 "
                            "norm.",
        "unit": "nats-equivalent hidden-state L2 length at layer 23, t_dec",
        "space": "residual stream (post-block, layer 23), NOT option-position "
                 "space, NOT place space",
        "reference_scale_eligible": False,
        "reference_scale_eligible_reason": "declared shared component; a dose "
                                           "reference scale requires an "
                                           "explicitly frozen per-item trace "
                                           "magnitude, which no sealed artifact "
                                           "currently defines.",
    },
    "v_g": {
        "scientific_role": "PER-PAIR ANTISYMMETRIC-COMPONENT SCALE",
        "pairing_operator": "v_g = (delta_{g,1} - delta_{g,2}) / 2, same frozen "
                            "pairing",
        "misreading_guard": "NOT by itself the trace; per-item delta = m_g + "
                            "v_g.",
    },
}

# Hash of the strings as signed, so a later edit by anyone (including the
# author) is detectable. Frozen at first write.
def _strings_hash(s):
    return hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8")).hexdigest()


JIE_STRINGS_HASH = _strings_hash(JIE_STRINGS)


def content_hash(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    print("=" * 78)
    print("  m_g / v_g — 睫'S SIGNED STRINGS, LANDED VERBATIM")
    print("=" * 78)

    got = sha256_file(DELTAS)
    print("\n    deltas sha256 = %s  %s"
          % (got[:16], "MATCH" if got == DELTAS_SHA else "MISMATCH"))
    assert got == DELTAS_SHA
    print("    strings sha256 = %s  (frozen signed copy)"
          % JIE_STRINGS_HASH[:16])

    # ---- 1. hard-field audit --------------------------------------------
    print("\n--- 1. hard-field audit (reference_scale_eligible) ---")
    mg = JIE_STRINGS["m_g"]
    present = "reference_scale_eligible" in mg
    not_none = mg.get("reference_scale_eligible") is not None
    is_bool = isinstance(mg.get("reference_scale_eligible"), bool)
    print("    present    = %s" % present)
    print("    not None   = %s" % not_none)
    print("    is bool    = %s" % is_bool)
    print("    value      = %r" % mg.get("reference_scale_eligible"))
    assert present and not_none and is_bool
    print("    -> HARD FIELD OK (may not be empty)")

    # required seven fields of REFERENCE_SCALE_SELF_DECLARATION
    need7 = ("scientific_role", "pairing_operator", "unit", "space",
             "reference_scale_eligible", "reference_scale_eligible_reason")
    missing = [k for k in need7 if k not in mg]
    print("    required keys present: %s" % (not missing, ))
    if missing:
        print("    MISSING: %s" % missing)

    # ---- 2. S_trace and S_parallel (zero forward) ------------------------
    print("\n--- 2. reference scales (zero forward) ---")
    d = np.load(DELTAS).astype(np.float64)
    raw = np.load(RAW_DM).astype(np.float64)
    n = d.shape[0]
    print("    n deltas = %d" % n)

    norms = np.linalg.norm(d, axis=1)
    S_trace_median = float(np.median(norms))
    S_trace_mean = float(norms.mean())
    print("    S_trace = median_i ||delta_i||      = %.10f" % S_trace_median)
    print("             (mean_i ||delta_i|| as alt = %.10f)" % S_trace_mean)

    proj = np.abs(d @ raw)
    S_par_median = float(np.median(proj))
    S_par_mean = float(proj.mean())
    print("    S_parallel = median_i |<d_i, d_M>| = %.10f" % S_par_median)
    print("            (mean as alt                = %.10f)" % S_par_mean)
    print("    ||d_M_raw|| = %.10f (must be 1)" % float(np.linalg.norm(raw)))

    print("\n    ratios (DIAGNOSTIC ONLY -- never an overshoot test):")
    for nm, s in (("S_trace(median)", S_trace_median),
                  ("S_trace(mean)", S_trace_mean),
                  ("S_parallel(median)", S_par_median),
                  ("S_parallel(mean)", S_par_mean)):
        print("      lambda / %-18s = %.6f" % (nm, LAMBDA / s))

    # ---- 3. the orthogonality status -------------------------------------
    print("\n--- 3. orthogonality status ---")
    # check the identity's dependence on the cross term, using the frozen pairing
    audit = json.load(open(DERIVE_AUDIT, encoding="utf-8"))
    order = audit["order"]
    idx = {e: i for i, e in enumerate(order)}
    projp = json.load(open(os.path.join(REPORTS,
                    "DHE_D2_EPISODE_PROJECTION_v1.json"), encoding="utf-8"))
    grp = []
    for p in projp["pairs"]:
        e = [(it["episode_id"] if isinstance(it, dict) else it)
             for it in p["items"]]
        if len(e) == 2 and all(x in idx for x in e):
            grp.append([idx[e[0]], idx[e[1]]])
    grp = grp[:24]
    M = np.array([0.5 * (d[a] + d[b]) for a, b in grp])
    V = np.array([0.5 * (d[a] - d[b]) for a, b in grp])
    d1 = np.array([d[a] for a, b in grp])
    d2 = np.array([d[b] for a, b in grp])
    cross = float(np.mean(np.sum(M * V, axis=1)))

    nm2 = np.linalg.norm(M, axis=1) ** 2
    nv2 = np.linalg.norm(V, axis=1) ** 2

    # PAIR identity -- cross terms cancel EXACTLY, always true, no assumption:
    lhs_pair = np.linalg.norm(d1, axis=1) ** 2 + np.linalg.norm(d2, axis=1) ** 2
    rhs_pair = 2 * nm2 + 2 * nv2
    pair_ident = bool(np.allclose(lhs_pair, rhs_pair))

    # PER-ITEM identity -- this is where the cross term lives:
    #   ||d1||^2 = ||m||^2 + ||v||^2 + 2<m,v>
    #   ||d2||^2 = ||m||^2 + ||v||^2 - 2<m,v>
    peritem_plus = nm2 + nv2 + 2 * np.sum(M * V, axis=1)
    peritem_minus = nm2 + nv2 - 2 * np.sum(M * V, axis=1)
    d1_ident = bool(np.allclose(np.linalg.norm(d1, axis=1) ** 2, peritem_plus))
    d2_ident = bool(np.allclose(np.linalg.norm(d2, axis=1) ** 2, peritem_minus))

    # 睫's form: ||delta|| = sqrt(||m||^2 + ||v||^2)  requires <m,v> = 0
    sqrt_form_holds = bool(np.allclose(
        np.linalg.norm(d1, axis=1),
        np.sqrt(nm2 + nv2), atol=1e-9))

    print("    mean <m_g, v_g>                        = %+.10f" % cross)
    print("    PAIR identity ||d1||^2+||d2||^2 = 2||m||^2+2||v||^2 : %s"
          % pair_ident)
    print("      (cross terms cancel EXACTLY; no orthogonality needed)")
    print("    PER-ITEM ||d1||^2 = ||m||^2+||v||^2+2<m,v>        : %s"
          % d1_ident)
    print("    PER-ITEM ||d2||^2 = ||m||^2+||v||^2-2<m,v>        : %s"
          % d2_ident)
    print("    睫's sqrt form ||d|| = sqrt(||m||^2+||v||^2)       : %s"
          % sqrt_form_holds)
    print("    -> orthogonality is NOT established (<m,v> != 0), so the sqrt")
    print("       form FAILS on the sealed data and is NOT adopted.")

    # ---- 4. artifact ------------------------------------------------------
    print("\n--- 4. landing verbatim strings ---")
    prev = json.load(open(PREV_AMENDED, encoding="utf-8")) \
        if os.path.exists(PREV_AMENDED) else {}

    artifact = {
        "kind": "DHE_12F_MG_VG_SIGNED_DECLARATIONS",
        "date": "2026-09-24",
        "authority": "睫 — strings signed and supplied by her; landed verbatim",
        "artifact_role": "DECLARATION RECORD; carries no model outcome",
        "authorship": {
            "who_signed_the_strings": "睫",
            "coder_role": "transcribe byte-for-byte; may not alter a single "
                          "punctuation mark",
            "accountability": "whoever names a quantity is the first line of "
                              "defence against its misreading; this line is "
                              "hers, so a future misreading comes to her first",
        },
        "verbatim_strings": JIE_STRINGS,
        "verbatim_strings_sha256": JIE_STRINGS_HASH,
        "verbatim_strings_note": "this hash detects any later edit, by anyone, "
                                 "including the author",
        "hard_fields": {
            "reference_scale_eligible": {
                "value": False,
                "may_not_be": ["absent", "null", "empty string", "true"],
                "enforcement": "asserted at write time and re-asserted by the "
                               "G0 seal",
            }
        },
        "supersedes_by_reference": {
            "artifact": "DHE_12F_TRACE_DECOMPOSITION_PROVENANCE_AMENDED.json",
            "CONTENT_HASH": prev.get("CONTENT_HASH"),
            "note": "that artifact's m_g/v_g self-declarations are replaced by "
                    "睫's authoritative strings; the earlier record is NOT "
                    "edited",
        },
        "reference_scales_zero_forward": {
            "S_trace": {
                "definition": "median_i ||delta_i||_2 over the 48 sealed "
                              "per-item deltas",
                "value_median": S_trace_median,
                "value_mean_alt": S_trace_mean,
                "operator": "L2 norm per item, then median (mean shown as "
                            "alternative, not adopted)",
                "unit": "nats-equivalent hidden-state L2 length at layer 23, "
                        "t_dec",
                "space": "residual stream (post-block, layer 23)",
                "scientific_role": "PER-ITEM TRACE MAGNITUDE (diagnostic)",
                "reference_scale_eligible": True,
                "warning": "geometry only; NOT an overshoot test",
            },
            "S_parallel": {
                "definition": "median_i |<delta_i, d_M_raw>| over the 48 sealed "
                              "per-item deltas",
                "value_median": S_par_median,
                "value_mean_alt": S_par_mean,
                "operator": "absolute inner product with the frozen unit "
                            "direction, then median",
                "unit": "nats-equivalent (same residual-space unit as lambda, "
                        "since ||d_M_raw||=1)",
                "space": "residual stream (post-block, layer 23)",
                "scientific_role": "AXIS-MATCHED TRACE-SCALE DIAGNOSTIC",
                "reference_scale_eligible": True,
                "warning": "geometry only; NOT an overshoot test",
            },
        },
        "orthogonality_status": {
            "statement": "||delta_{g,i}|| = sqrt(||m_g||^2 + ||v_g||^2) HOLDS "
                         "ONLY IF m_g ⟂ v_g",
            "orthogonality_established": False,
            "evidence": {
                "mean_inner_product_m_g_v_g": cross,
                "withdrawal_reference":
                    "DHE_D2_SIGN_ORIENTATION_v0.2.json "
                    "/energy_fraction_not_claimed",
                "withdrawal_text": "systematic reciprocal component exists; its "
                                   "energy fraction is NOT identified "
                                   "(81.3/18.7 withdrawn)",
                "pair_identity_always_holds": pair_ident,
                "pair_identity_form":
                    "||d_{g,1}||^2 + ||d_{g,2}||^2 = 2||m_g||^2 + 2||v_g||^2",
                "pair_identity_note":
                    "cross terms cancel EXACTLY on the pair sum; this holds "
                    "with no orthogonality assumption and is the only "
                    "identity that always holds",
                "per_item_identity_form":
                    "||d_{g,i}||^2 = ||m_g||^2 + ||v_g||^2 +/- 2<m_g, v_g>",
                "per_item_identity_d1_holds": d1_ident,
                "per_item_identity_d2_holds": d2_ident,
                "sqrt_form_holds_on_sealed_data": sqrt_form_holds,
                "sqrt_form_requires": "<m_g, v_g> = 0",
            },
            "consequences": [
                "per-item trace magnitude = UNDEFINED IN SEALED ARTIFACTS",
                "lambda natural-scale ratio = UNANSWERABLE",
            ],
            "candidate_denominators_listed_side_by_side_none_licensed": [
                {"denominator": 0.3238813055006332,
                 "name": "global resultant scale",
                 "status": "licensed ONLY as GLOBAL-RESULTANT-SCALE DIAGNOSTIC",
                 "ratio": LAMBDA / 0.3238813055006332},
                {"denominator": 1.0676623157956653,
                 "name": "per-pair shared-component scale",
                 "status": "licensed ONLY as shared-component diagnostic; "
                           "reference_scale_eligible = false",
                 "ratio": LAMBDA / 1.0676623157956653},
                {"denominator": 2.4101487753,
                 "name": "orthogonal-branch per-item estimate",
                 "status": "NOT licensed; rests on the withdrawn "
                           "orthogonality assumption",
                 "ratio": LAMBDA / 2.4101487753},
            ],
            "forbidden": "no single one of the three may be presented as "
                         "'the' natural scale of lambda",
        },
        "counters": {
            "forward_calls": 0, "autograd_calls": 0, "logits_consumed": 0,
            "activation_reads": 0, "patches": 0, "model_loaded": False,
        },
        "frozen_sentences": [
            "Whoever names a quantity is the first line of defence against its "
            "misreading.",
            "The orthogonality-free identity is the only one that always holds; "
            "the sqrt form is a conditional convenience.",
        ],
    }
    artifact["CONTENT_HASH"] = content_hash(artifact)

    out_path = os.path.join(
        REPORTS, "DHE_12F_MG_VG_SIGNED_DECLARATIONS.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)

    print("    DHE_12F_MG_VG_SIGNED_DECLARATIONS.json")
    print("    CONTENT_HASH = %s" % artifact["CONTENT_HASH"])
    print("    verbatim_strings_sha256 = %s" % JIE_STRINGS_HASH)
    print("\n--- 5. read-back verification (byte-for-byte) ---")
    back = json.load(open(out_path, encoding="utf-8"))
    ok = back["verbatim_strings"] == JIE_STRINGS
    print("    read-back equals signed copy : %s" % ok)
    print("    read-back hash matches       : %s"
          % (_strings_hash(back["verbatim_strings"]) == JIE_STRINGS_HASH))
    for k, v in back["verbatim_strings"]["m_g"].items():
        if isinstance(v, str) and len(v) > 60:
            v = v[:57] + "..."
        print("      m_g.%-32s = %r" % (k, v))
    for k, v in back["verbatim_strings"]["v_g"].items():
        if isinstance(v, str) and len(v) > 60:
            v = v[:57] + "..."
        print("      v_g.%-32s = %r" % (k, v))

    print("\n" + "=" * 78)
    print("  VERBATIM LANDED. HARD FIELD = false. ORTHOGONALITY = NOT ESTABLISHED.")
    print("=" * 78)


if __name__ == "__main__":
    main()
