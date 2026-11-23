# -*- coding: utf-8 -*-
"""_dhe_12f_hold_check.py —— HOLD BEFORE S7 : 零-forward 复核

凌翼 §5: sign manifest 是否覆盖全 96 items (含 CAUSAL_CONFIRM 48)?
凌翼 §2: 确认 signed endpoint 必须使用同一 orientation function s_i

只读已封产物; 零 forward。
"""
import sys, os, json, hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
RD = 'reports'

SIGN = f'{RD}/DHE_D2_SIGN_ORIENTATION_v0.2.json'
SPLIT = f'{RD}/DHE_D2_SPLIT_MANIFEST_v1.json'
PROJ = f'{RD}/DHE_D2_EPISODE_PROJECTION_v1.json'


def jcs(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, default=str)
                          .encode('utf-8')).hexdigest()


print('=' * 72)
print('  HOLD BEFORE S7 — 零-forward 复核')
print('=' * 72)
print()

sgn = json.load(open(SIGN, encoding='utf-8'))
sp = json.load(open(SPLIT, encoding='utf-8'))
proj = json.load(open(PROJ, encoding='utf-8'))

items = sgn['items']
print('--- §5 sign manifest coverage ---')
print(f"    manifest n_items          = {sgn['n_items']}")
print(f"    manifest n_derive         = {sgn['n_derive']}")
print(f"    manifest n_confirm        = {sgn['n_confirm']}")
print(f"    actual len(items)         = {len(items)}")

by_split = {}
for r in items:
    by_split.setdefault(r['split'], []).append(r)
print(f"    items by split            = "
      f"{{k: len(v) for k, v in by_split.items()}}".replace('{k: len(v) for k, v in by_split.items()}',
                                                            str({k: len(v) for k, v in by_split.items()})))
print()

# coverage assertions
der_ids = set(sp['TRACE_DERIVE']['pair_ids'])
con_ids = set(sp['CAUSAL_CONFIRM']['pair_ids'])
proj_items = {it['episode_id']: it for p in proj['pairs'] for it in p['items']}
der_items = set(it['episode_id'] for p in proj['pairs'] if p['pair_id'] in der_ids
                for it in p['items'])
con_items = set(it['episode_id'] for p in proj['pairs'] if p['pair_id'] in con_ids
                for it in p['items'])
manifest_ids = set(r['episode_id'] for r in items)

c = {
    'manifest_has_96': len(items) == 96,
    'manifest_covers_all_projection_items': manifest_ids == set(proj_items.keys()),
    'derive_48_present': len(der_items & manifest_ids) == 48,
    'confirm_48_present': len(con_items & manifest_ids) == 48,
    'no_extra_ids': not (manifest_ids - set(proj_items.keys())),
    'confirm_signs_generated_from_material_only': sgn['dependencies'] == {
        'activation_dependency': 0, 'R_g_dependency': 0,
        'behavior_dependency': 0, 'confirmation_dependency': 0},
}
for k, v in c.items():
    print(f'    {k:<46} = {v}')
COVER = all(c.values())
print(f'    ⇒ SIGN MANIFEST COVERS ALL 96 = {COVER}')
print()

# signed endpoint identity demo (structural, no model)
print('--- §2 signed endpoint orientation demo (structural) ---')
n_pos = sum(1 for r in items if r['sign'] > 0)
n_neg = sum(1 for r in items if r['sign'] < 0)
print(f"    s_i = +1 : {n_pos} items ; s_i = -1 : {n_neg} items")
print(f"    ⇒ 若 endpoint 用 A-B (旧写法), 则 {n_neg} 个 item 的 direction 与 endpoint 符号相反")
print(f"    ⇒ 修正后 endpoint = s_i*[U(p_A)-U(p_B)], 全部 {len(items)} 个 item 对齐")
print()

print('--- 两个 estimator package ---')
print('    RAW package    : direction = mean(delta_i)        ; endpoint = U(p_A)-U(p_B)')
print('    SIGNED package : direction = mean(s_i*delta_i)    ; endpoint = s_i*[U(p_A)-U(p_B)]')
print()

doc = {
    'kind': 'DHE_12F_HOLD_CHECK', 'date': '2026-09-23',
    'authority': '凌翼 §2/§5 (SCALAR SEMANTIC-IDENTITY REPAIR BEFORE REVEAL)',
    'sign_manifest_hash': sgn['CONTENT_HASH'],
    'sign_function_sha256': sgn['sign_function_sha256'],
    'manifest_n_items': len(items), 'n_derive': sgn['n_derive'],
    'n_confirm': sgn['n_confirm'],
    'coverage_checks': c, 'manifest_covers_all_96': COVER,
    'signed_endpoint_correction': {
        'old_wrong': 'B_i,± = U_i,±(p_A) - U_i,±(p_B)   (missing s_i)',
        'new_frozen': 'B_i,± = s_i * [U_i,±(p_A) - U_i,±(p_B)]',
        'C_i_signed': 's_i * ( [U_+(p_A)-U_+(p_B)] - [U_-(p_A)-U_-(p_B)] )',
        'C_signed': '(1/48) sum_i C_i_signed', 'gate': 'C_signed > 0',
        'why': 'a signed direction requires a signed measurement axis; otherwise for '
               's_i=-1 items the direction and endpoint have opposite signs and the '
               'reciprocal cancellation returns in TEST',
    },
    'delta_C_identity': 'SIGNED-vs-RAW ESTIMATOR-PACKAGE CONTRAST (SECONDARY)',
    'raw_unchanged': True,
    'CAUSAL_CONFIRM_still_dark': True,
    'model_forward': 0, 'activation_read': 0, 'behavior_read': 0,
    'frozen_sentences': [
        'A signed direction requires a signed measurement axis.',
        'Do not align the arrow and then score half the targets backwards.',
        'Orient the endpoint by the same rule that oriented the direction.',
    ],
}
doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
OUT = f'{RD}/DHE_12F_HOLD_CHECK.json'
json.dump(doc, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('--- 产物 ---')
print('    %-40s %8d B  %s' % (os.path.basename(OUT), os.path.getsize(OUT),
                               hashlib.sha256(open(OUT, 'rb').read()).hexdigest()[:16]))
print()
print(f'    model_forward = 0 ; CAUSAL_CONFIRM still dark = TRUE')
