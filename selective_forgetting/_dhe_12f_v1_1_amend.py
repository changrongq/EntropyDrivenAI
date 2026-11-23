# -*- coding: utf-8 -*-
"""_dhe_12f_v1_1_amend.py —— 12F-v1.1 PROTOCOL AMENDMENT (R0/R1/R2 pre-flight seal)

凌翼裁决 (本次):
  9216 是正确的最终 12F 预算, 但 Coder 给出的理由需要修正。
    - Coder 说 "U(p_A) 与 U(p_B) 需要两个不同输入 forward"  => 不对
    - 少的不是 proposal axis, 而是 episode arm E_A||F vs E_B||F
  裁决: HARD_STOP::FORWARD_COUNT_FAIL = VALID ; 当前科学结果 = NONE

本脚本只做三件事, **不加载模型, 不算任何 endpoint**:
  R0  seal amendment 登记 (12F-FORWARD-AXIS-OMISSION-001)
  R1  seal 精确轴序 + 完整 primary/secondary 公式
  R2  assert 全部 frozen hashes 仍然对得上

旧 in-memory 9216 outputs: DISCARD (不得读取, 不得转正)
旧 artifact: DHE_12F_CAUSAL_CONFIRM.v1_FORWARD_COUNT_FAIL.json (保持不动)

禁止: 在旧读数上继续 / 复用内存 / 让门适应已发生的结果
"""
import sys, os, json, hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
RD = 'reports'

OUT_AMEND = f'{RD}/DHE_12F_PROTOCOL_AMENDMENT_v1.1.json'
OUT_AXIS = f'{RD}/DHE_12F_AXIS_ORDER_v1.1.json'

# ── frozen constants (inherited, UNCHANGED by this amendment) ─────────
L_SITE = 23
HID = 4096
LAMBDA = 1.1402872562408447
ALPHA_EFF_D2 = 0.05415999941978071
N_ITEMS = 48
N_PERMS = 24
N_ARMS = 2          # E_A / E_B  <-- THE MISSING AXIS
N_PKGS = 2          # raw / signed
N_SIGNS = 2         # +/-
EXPECTED_FWD = 9216

GGUF_SHA_EXPECTED = 'dfb053cb8d5f56abde8f56899ffe0d23e1285a423df0b65ea3f3adbb263b22c2'
RAW_HASH = 'f9aae5833055859c481b500a8a54cfdac9b994e59d10f924b81f6369bfc2515a'
SIGNED_HASH = '0b91e4e945189e1bf0c301215bad179f61b9f7fcd6446ecd96ebc1cbc07f0d88'
SIGN_MANIFEST_HASH = '0b68988b4f55023688669a9513bcb93e70e2275279e285276d0ea489616870e9'

FWD_V1_DECLARED = 4608
FWD_V1_ACTUAL = 9216


def jcs(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, default=str)
                          .encode('utf-8')).hexdigest()


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sha256_arr(path):
    import numpy as np
    return hashlib.sha256(np.load(path).tobytes()).hexdigest()


print('=' * 76)
print('  12F-v1.1 PROTOCOL AMENDMENT  (R0/R1/R2 pre-flight seal, no model)')
print('=' * 76)
print()

# ═══════════════════════════════════════════════════════════════════════
# R0 : seal amendment registry
# ═══════════════════════════════════════════════════════════════════════
registry = {
    'kind': 'DHE_12F_PROTOCOL_AMENDMENT_v1.1',
    'date': '2026-09-24',
    'authority': '凌翼 12F-v1.1 裁决 (9216 正确, Coder 理由需修正)',
    'amendment_id': '12F-FORWARD-AXIS-OMISSION-001',
    'id': '12F-FORWARD-AXIS-OMISSION-001',
    'previous_expected_count': FWD_V1_DECLARED,
    'previous_actual_count': FWD_V1_ACTUAL,
    'missing_axis': 'episode conditioning arm {E_A, E_B}',
    'proposal_axis': 'NOT missing — p_A/p_B share each render forward',
    'coder_stated_reason': {
        'claim': 'U(p_A) and U(p_B) require two different-input forwards',
        'verdict': 'REJECTED — incorrect',
        'correct_reason': 'For fixed (episode context e, direction q, sign sigma, render pi), '
                          'one model forward already yields all four A/B/C/D code logits; '
                          'the same 24pi render family therefore yields a complete four-place '
                          'U(p) vector, from which U(p_A) and U(p_B) are two coordinates.',
        'impact_on_final_count': 'none — 9216 is correct, but for a different reason',
    },
    'corrected_expected_count': EXPECTED_FWD,
    'corrected_derivation': f'{N_ITEMS} items x {N_ARMS} episode arms x {N_PKGS} estimator '
                            f'packages x {N_SIGNS} intervention signs x {N_PERMS} renders '
                            f'= {N_ITEMS * N_ARMS * N_PKGS * N_SIGNS * N_PERMS}',
    'scientific_results_revealed_before_correction': False,
    'classification': 'PRE-RESULT SCIENTIFIC-SCOPE COMPLETION',
    'not_a_behavioral_defect': True,
    'gap_kind': 'SCIENTIFIC OBJECT COMPLETENESS GAP — the single-arm 4608 protocol lacked a '
                'definition of the intervention reference state (neither E_A nor E_B had been '
                'frozen as the unique baseline, and no F-only neutral baseline was frozen)',
    'symmetric_arm_rule_frozen': 'Both shores are perturbed; the causal slope is averaged. '
                                 'Neither arm may be selected, dropped, or weighted by result.',
    'previous_artifact': {
        'file': f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1_FORWARD_COUNT_FAIL.json',
        'verdict': 'HARD_STOP::FORWARD_COUNT_FAIL',
        'status': 'RETAINED AS-IS — historical record of a failed gate',
        'rule': 'A failed gate does not become a pass because we later discover why the count '
                'was larger.',
    },
    'old_in_memory_outputs': {
        'status': 'DISCARD',
        'rule': 'Not read, not sealed, not promoted to scientific result.',
        'reason': 'At run time the declared axis set was incomplete '
                  '(expected_forward_count = 4608) and the episode-arm aggregation rule '
                  'had not yet been sealed.',
    },
    'cautionary_rules': [
        'A correct accidental count must not certify an incompletely specified experiment.',
        'The count is corrected by re-deriving the scientific object first, then sealing — '
        'never by relaxing the gate after observing the run.',
    ],
}
registry['CONTENT_HASH'] = jcs(registry)

# ═══════════════════════════════════════════════════════════════════════
# R1 : seal exact axis order + formulas
# ═══════════════════════════════════════════════════════════════════════
axis = {
    'kind': 'DHE_12F_AXIS_ORDER_v1.1',
    'authority': '凌翼 12F-v1.1 amendment (symmetric episode-arm confirmation)',
    'axis_order': ['item', 'episode_arm{A,B}', 'estimator_package{raw,signed}',
                   'intervention_sign{+,-}', 'render(24)'],
    'axis_sizes': {'item': N_ITEMS, 'episode_arm': N_ARMS,
                   'estimator_package': N_PKGS, 'intervention_sign': N_SIGNS,
                   'render': N_PERMS},
    'expected_forward_count': EXPECTED_FWD,
    'forward_identity': 'one forward = one (item, arm, package, sign, render) tuple',
    'proposal_rule': {
        'rule': 'p_A/p_B subtraction happens AFTER the same 24-render U vector exists.',
        'never': 'Never forward separately for the two proposals.',
        'note': 'One 24pi render family yields U(p) for all four places simultaneously.',
    },
    'operator': {
        'site': L_SITE, 'type': 'additive post-block residual',
        't_dec': 'index of the final (decode) token of the F template',
        'patch': 'H[0, t_dec, :] += sign * LAMBDA * d',
        'lambda': LAMBDA,
        'direction_hash': {'raw': RAW_HASH, 'signed': SIGNED_HASH},
    },
    'endpoints': {
        'raw': 'B^raw_{i,e,q,sigma}    = U_{i,e,q,sigma}(p_A) - U_{i,e,q,sigma}(p_B)',
        'signed': 'B^signed_{i,e,q,sigma} = s_i * [U_{i,e,q,sigma}(p_A) - U_{i,e,q,sigma}(p_B)]',
    },
    'aggregation': {
        'per_item_per_arm': 'C^q_{i,e} = B_{i,e,q,+} - B_{i,e,q,-}',
        'symmetrize_arms': 'C^q_i = (1/2) * ( C^q_{i,A} + C^q_{i,B} )',
        'grand_mean': 'C_q = (1/48) * sum_i C^q_i',
        'secondary': 'Delta_C = C_signed - C_raw',
        'frozen_sentence': 'Perturb both shores; average the causal slope, do not choose a '
                           'shore after seeing the water.',
    },
    'gates': {
        'H_raw': 'C_raw > 0',
        'H_signed': 'C_signed > 0',
        'no_effect_size_rescue': True,
        'no_fraction_positive_gate': True,
        'no_R_g_gate': True,
        'no_third_criterion': True,
        'Delta_C_role': 'SECONDARY prespecified comparator — never a gate, never a rescue, '
                        'reported mechanically',
        'both_primaries_equal_prominence': True,
    },
    'guards': {
        'patch_count_must_equal_1_per_forward': True,
        'U_prod_must_equal_U_ref_per_forward_family': True,
        'autograd_calls_must_equal_0': True,
        'logits_consumed_by_behavior_read': False,
        'retention_delay_interference': 'NOT TOUCHED',
    },
    'execution_plan': [
        'R0 seal 12F-v1.1 protocol amendment (expected_forwards = 9216)',
        'R1 seal exact axis order',
        'R2 assert all frozen hashes',
        'R3 fresh model / GATE_L PASS',
        'R4 run 9216 forwards',
        'R5 assert actual_forward_count == 9216',
        'R6 U_prod/reference guards',
        'R7 compute C_raw / C_signed / Delta_C',
        'R8 seal',
        'R9 STOP',
    ],
    'frozen_sentences': [
        'U(p_A) and U(p_B) are two coordinates of one ruler reading, not two model executions.',
        'The missing dimension was not the proposal; it was the shore from which the '
        'intervention began.',
        'Do not let a correct accidental count certify an incompletely specified experiment.',
        'A failed gate does not become a pass because we later discover why the count was larger.',
        'Perturb both shores; average the causal slope, do not choose a shore after seeing '
        'the water.',
    ],
}
axis['CONTENT_HASH'] = jcs(axis)

# ═══════════════════════════════════════════════════════════════════════
# R2 : assert all frozen hashes still match
# ═══════════════════════════════════════════════════════════════════════
checks = {}


def ck(name, cond, extra=None):
    checks[name] = bool(cond)
    tag = 'OK ' if cond else 'BAD'
    print(f'    [{tag}] {name:<46} {"" if extra is None else extra}')


ck('raw d_M npy hash matches f9aae583…',
   sha256_arr(f'{RD}/_dhe_12f_raw_dm.npy') == RAW_HASH)
ck('signed d_M npy hash matches 0b91e4e9…',
   sha256_arr(f'{RD}/_dhe_12f_signed_dm.npy') == SIGNED_HASH)

with open(f'{RD}/DHE_D2_SIGN_ORIENTATION_v0.2.json', encoding='utf-8') as f:
    signman = json.load(f)
ck('sign manifest CONTENT_HASH 0b68988b…',
   signman.get('CONTENT_HASH') == SIGN_MANIFEST_HASH,
   f"n_items={signman.get('n_items')}")
ck('sign manifest 96 / 48 / 48',
   signman['n_items'] == 96 and signman['n_derive'] == 48
   and signman['n_confirm'] == 48)
ck('sign manifest zero dependencies',
   all(v == 0 for v in signman['dependencies'].values()))

with open(f'{RD}/DHE_12A_ACTIVATION_SCALE.json', encoding='utf-8') as f:
    act = json.load(f)
ck('S7/S15/S23 activation scales exact',
   abs(float(act['S']['7']) - 2.466688871383667) < 1e-9
   and abs(float(act['S']['15']) - 7.540978908538818) < 1e-9
   and abs(float(act['S']['23']) - 22.805745124816895) < 1e-9,
   f"S23={act['S']['23']}")
ck('lambda_2(l*=23) == 1.1402872562408447…',
   abs(float(act['lambda_table']['23']['lambda_2']) - LAMBDA) < 1e-15,
   f"{act['lambda_table']['23']['lambda_2']}")
ck('12A frozen CONTENT_HASH f2f4937b…',
   act['CONTENT_HASH'] == 'f2f4937bd065e2922690d57a387652504e6df0ca9de3f0ff8046bb8c4f7f9f13')

with open(f'{RD}/DHE_12D_PC_CAL_TEST.json', encoding='utf-8') as f:
    pc = json.load(f)
ck('12D PC_CAL Q_TEST +2.4591230…',
   abs(float(pc['Q_TEST']) - 2.4591230675578117) < 1e-9,
   f"gate={pc.get('PRIMARY_GATE')}")
ck('12D d_PC23 recompute hash 6847c2f9…',
   str(pc['d_PC23_recompute_hash']).startswith('6847c2f9'))

with open(f'{RD}/DHE_D2_SPLIT_MANIFEST_v1.json', encoding='utf-8') as f:
    split = json.load(f)
ck('CAUSAL_CONFIRM pairs == 24',
   len(split['CAUSAL_CONFIRM']['pair_ids']) == 24)

with open(f'{RD}/DHE_U_CONFORMANCE_REAL.json', encoding='utf-8') as f:
    conf = json.load(f)
ck('U_DHE_IMPL_v0.1 == QUALIFIED',
   conf.get('U_DHE_IMPL_v0.1') == 'QUALIFIED'
   and all(conf['conditions'].values())
   and conf['two_paths']['pass'] is True
   and conf['two_paths']['max_abs_diff'] == 0.0)

old = f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1_FORWARD_COUNT_FAIL.json'
with open(old, encoding='utf-8') as f:
    olddoc = json.load(f)
ck('v1 FAIL artifact retained & unchanged',
   olddoc['verdict'] == 'HARD_STOP::FORWARD_COUNT_FAIL'
   and olddoc['detail']['got'] == FWD_V1_ACTUAL,
   olddoc['CONTENT_HASH'][:16])
ck('no v1.1 CAUSAL_CONFIRM result exists yet',
   not os.path.exists(f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1.1.json'))
ck('no stale DHE_12F_CAUSAL_CONFIRM.json present',
   not os.path.exists(f'{RD}/DHE_12F_CAUSAL_CONFIRM.json'))

print()
if not all(checks.values()):
    bad = [k for k, v in checks.items() if not v]
    fail = {'kind': 'DHE_12F_PROTOCOL_AMENDMENT_v1.1', 'date': '2026-09-24',
            'verdict': 'HARD_STOP::AMENDMENT_PRECONDITION_FAIL',
            'failing': bad, 'checks': checks}
    fail['CONTENT_HASH'] = jcs(fail)
    print('=' * 76)
    print('  AMENDMENT_PRECONDITION_FAIL -> HARD STOP')
    print('=' * 76)
    print(f'    {bad}')
    sys.exit(2)

# ── write both seals ─────────────────────────────────────────────────
for path, doc, kind in ((OUT_AMEND, registry, 'DHE_12F_PROTOCOL_AMENDMENT_v1.1'),
                        (OUT_AXIS, axis, 'DHE_12F_AXIS_ORDER_v1.1')):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    json.dump({'kind': kind + '_SIDECAR', 'file': path,
               'artifact_file_sha256': sha256_file(path),
               'CONTENT_HASH': doc['CONTENT_HASH']},
              open(path + '.sidecar.json', 'w', encoding='utf-8'),
              indent=2, ensure_ascii=False)

print('=' * 76)
print('  R0/R1/R2 SEALED — amendment complete, no model loaded')
print('=' * 76)
print()
print(f'    EXPECTED_12F_FORWARDS = {EXPECTED_FWD}')
print('    PROPOSAL AXIS         = NOT missing (p_A/p_B share each render forward)')
print('    MISSING AXIS          = episode arm {E_A, E_B} (now symmetric & frozen)')
print('    OLD IN-MEMORY OUTPUTS = DISCARD')
print('    CAUSAL_CONFIRM RESULT = STILL UNREVEALED')
print()
print('--- artifacts ---')
for p in (OUT_AMEND, OUT_AMEND + '.sidecar.json',
          OUT_AXIS, OUT_AXIS + '.sidecar.json'):
    print('    %-52s %8d B  %s' % (os.path.basename(p), os.path.getsize(p),
                                   sha256_file(p)[:16]))
print()
print('    next: fresh rerun ->  _dhe_12f_v1_1_confirm.py')
