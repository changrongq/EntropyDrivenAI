# -*- coding: utf-8 -*-
"""_dhe_12f_s0_sign_manifest.py —— S0+S1: material-only sign function + sign manifest

凌翼 §⑪ S0/S1:
  S0 freeze material-only sign function
  S1 seal sign manifest for all items

sign rule (只依赖冻结材料 canonical place order):
    s_i = +1 if index(p_A) < index(p_B)
    s_i = -1 if index(p_A) > index(p_B)
  (p_A == p_B 不出现; item 已机械排除)

要求:
    activation dependency = 0
    R_g dependency        = 0
    behavior dependency   = 0
    confirmation dependency = 0

零 forward。
"""
import sys, os, json, hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
RD = 'reports'

TRUTHMAPS = f'{RD}/BB4c_BBS5_SCC24_D1_truthmaps.json'
PROJ = f'{RD}/DHE_D2_EPISODE_PROJECTION_v1.json'
SPLIT = f'{RD}/DHE_D2_SPLIT_MANIFEST_v1.json'
OUT = f'{RD}/DHE_D2_SIGN_ORIENTATION_v0.2.json'

SIGN_TAG = 'DHE-D2-SIGN-ORIENTATION-v0.2'


def jcs(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, default=str)
                          .encode('utf-8')).hexdigest()


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


print('=' * 76)
print('  S0/S1: MATERIAL-ONLY SIGN FUNCTION + SIGN MANIFEST')
print('=' * 76)
print()

src = json.load(open(TRUTHMAPS, encoding='utf-8'))
proj = json.load(open(PROJ, encoding='utf-8'))
split = json.load(open(SPLIT, encoding='utf-8'))

# canonical place order per block (from frozen lexical order; NOT re-sorted)
PLACE_ORDER = {b['block_id']: list(b['places']) for b in src['blocks']}
ROLE_ORDER = {b['block_id']: list(b['roles']) for b in src['blocks']}

SIGN_FN_SRC = (
    "def sign_of_item(block_id, p_A, p_B, PLACE_ORDER):\n"
    "    idx = {p: i for i, p in enumerate(PLACE_ORDER[block_id])}\n"
    "    ia, ib = idx[p_A], idx[p_B]\n"
    "    assert ia != ib, 'p_A == p_B not allowed'\n"
    "    return 1 if ia < ib else -1\n"
)
SIGN_FN_HASH = sha256_str(SIGN_FN_SRC)
print('--- S0 sign function (material-only) ---')
print('    ' + SIGN_FN_SRC.replace('\n', '\n    ').rstrip())
print(f'    sign function sha256 = {SIGN_FN_HASH}')
print()

# dependencies declaration
DEPS = {'activation_dependency': 0, 'R_g_dependency': 0,
        'behavior_dependency': 0, 'confirmation_dependency': 0}
print(f'    dependencies = {DEPS}')
print()


def sign_of_item(block_id, p_A, p_B, PLACE_ORDER):
    idx = {p: i for i, p in enumerate(PLACE_ORDER[block_id])}
    ia, ib = idx[p_A], idx[p_B]
    assert ia != ib, 'p_A == p_B not allowed'
    return 1 if ia < ib else -1


# ── build manifest for ALL 96 items (48 derive + 48 confirm) ──────────
der_ids = set(split['TRACE_DERIVE']['pair_ids'])
con_ids = set(split['CAUSAL_CONFIRM']['pair_ids'])
rows = []
n_der = n_con = 0
for p in proj['pairs']:
    pid = p['pair_id']
    bid = p['block_id']
    in_der = pid in der_ids
    in_con = pid in con_ids
    assert in_der ^ in_con, pid
    for it in p['items']:
        s = sign_of_item(bid, it['p_A'], it['p_B'], PLACE_ORDER)
        idx = {q: i for i, q in enumerate(PLACE_ORDER[bid])}
        rows.append({
            'episode_id': it['episode_id'],
            'block': bid,
            'role': it['role_id'],
            'p_A': it['p_A'], 'p_B': it['p_B'],
            'canonical_place_index_A': idx[it['p_A']],
            'canonical_place_index_B': idx[it['p_B']],
            'sign': s,
            'reason': (f'index(p_A)={idx[it["p_A"]]} '
                       f'{"<" if s > 0 else ">"} index(p_B)={idx[it["p_B"]]} '
                       f'=> s={s:+d}'),
            'split': 'TRACE_DERIVE' if in_der else 'CAUSAL_CONFIRM',
        })
        if in_der:
            n_der += 1
        else:
            n_con += 1

print('--- S1 sign manifest ---')
print(f'    total items = {len(rows)}  (TRACE_DERIVE {n_der} / CAUSAL_CONFIRM {n_con})')
pos = sum(1 for r in rows if r['sign'] > 0)
neg = sum(1 for r in rows if r['sign'] < 0)
print(f'    sign distribution: +1 = {pos} ; -1 = {neg}')
print()
print('    --- first 6 rows ---')
for r in rows[:6]:
    print(f"    {r['split'][:5]:<6} {r['block']} {r['role'][:13]:<13} "
          f"{r['p_A'][:11]:<11}->{r['p_B'][:11]:<11} s={r['sign']:+d}")
print()

# per-block sign balance
blk = {}
for r in rows:
    b = blk.setdefault(r['block'], {'+1': 0, '-1': 0})
    b['+1' if r['sign'] > 0 else '-1'] += 1
print('    --- per block sign balance ---')
for b in sorted(blk):
    print(f"    {b}: +1={blk[b]['+1']}  -1={blk[b]['-1']}")
print()

doc = {
    'kind': 'DHE_D2_SIGN_ORIENTATION_v0.2',
    'artifact_role': 'DERIVE-INFORMED, PROSPECTIVELY FROZEN ALTERNATIVE ESTIMATOR — '
                     'sign orientation manifest',
    'date': '2026-09-23',
    'authority': '凌翼 §⑪ S0/S1',
    'sign_tag': SIGN_TAG,
    'rule': ('s_i = +1 if canonical_index(p_A) < canonical_index(p_B) else -1; '
             'canonical place order comes from frozen lexical material'),
    'sign_function_source': SIGN_FN_SRC,
    'sign_function_sha256': SIGN_FN_HASH,
    'canonical_place_order': PLACE_ORDER,
    'canonical_role_order': ROLE_ORDER,
    'dependencies': DEPS,
    'n_items': len(rows),
    'n_derive': n_der, 'n_confirm': n_con,
    'sign_distribution': {'plus': pos, 'minus': neg},
    'per_block_sign_balance': blk,
    'items': rows,
    'frozen_before_activations_reappear': True,
    'historical_identity_note': ('signed estimator is DERIVE-INFORMED: motivated after '
                                 'observing systematic R_g<0; it may NOT be rewritten as '
                                 '"the definition we should always have used"'),
    'energy_fraction_not_claimed': ('systematic reciprocal component exists; its energy '
                                    'fraction is NOT identified (81.3/18.7 withdrawn)'),
    'model_forward': 0, 'activation_read': 0, 'behavior_read': 0,
    'frozen_sentences': [
        'A null from the wrong axis cannot establish absence of the underlying signal.',
        'A derive-informed axis can still receive a fair confirmation if the confirmation '
        'set is still dark when the axis is frozen.',
    ],
}
doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
json.dump(doc, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

print('=' * 76)
print('  S0/S1 SEALED')
print('=' * 76)
print()
print(f'    sign function sha256 = {SIGN_FN_HASH[:16]}')
print(f'    n_items = {len(rows)} ; +1={pos} -1={neg}')
print(f'    dependencies: {DEPS}')
print()
print('--- 产物 ---')
print('    %-44s %8d B  %s' % (os.path.basename(OUT), os.path.getsize(OUT),
                               sha256_file(OUT)[:16]))
print(f'    CONTENT_HASH = {doc["CONTENT_HASH"][:32]}...')
print()
print(f'    model_forward = 0 ; activation_read = 0 ; behavior_read = 0')
