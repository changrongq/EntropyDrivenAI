# -*- coding: utf-8 -*-
"""_dhe_12f_s7_s10_confirm.py —— S7-S10: 唯一一次 CAUSAL_CONFIRM opening (4608 forwards)

凌翼 §11 最终版:
  RAW    : direction = d_raw    ±λ ; endpoint = U(p_A)-U(p_B)
  SIGNED : direction = d_signed ±λ ; endpoint = s_i*[U(p_A)-U(p_B)]
  同 48 confirmation items ; 24π ; layer23 ; t_dec ; λ=1.1402872562408447

  C_raw    = (1/48) sum_i C_i^raw        C_i^raw    = B_i,+^raw    - B_i,-^raw
  C_signed = (1/48) sum_i C_i^signed     C_i^signed = s_i*( [U_+(pA)-U_+(pB)] - [U_-(pA)-U_-(pB)] )
  Δ_C = C_signed - C_raw                 (SECONDARY: estimator-package contrast)

  gates: C_raw > 0 (H_raw) ; C_signed > 0 (H_signed)
  无第二判据 / 无 effect-size rescue / 无第三层 rescue

正向 count:
  每 item × 24π × 2 signs × 2 directions = 96 => 48 × 96 = 4608

禁止: 只报赢的那个 / 把 Δ_C 塞脚注 / no memory / memory absent / digital hippocampus absent
始终: autograd=0 ; logits NOT consumed ; behavior = endpoint only (预注册) ;
      retention/delay/interference = NOT TOUCHED
"""
import sys, os, json, hashlib, gc, time, itertools, math

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
RD = 'reports'

MODEL_DIR = r'D:\qcr\EntropyDrivenAI'
GGUF_FILE = 'mistral-7b-instruct-v0.1.Q6_K.gguf'
MODEL_PATH = os.path.join(MODEL_DIR, GGUF_FILE)
GGUF_SHA_EXPECTED = 'dfb053cb8d5f56abde8f56899ffe0d23e1285a423df0b65ea3f3adbb263b22c2'

REPLAY_ART = f'{RD}/DHE_12A_MODEL_LOAD_REPLAY.json'
PROJ = f'{RD}/DHE_D2_EPISODE_PROJECTION_v1.json'
SPLIT = f'{RD}/DHE_D2_SPLIT_MANIFEST_v1.json'
TPL = f'{RD}/DHE_D2_TEMPLATE_MANIFEST_v1.json'
SIGN = f'{RD}/DHE_D2_SIGN_ORIENTATION_v0.2.json'
IDS_ART = f'{RD}/DHE_CODE_TOKEN_IDS.json'
IMPL_ART = f'{RD}/DHE_U_DHE_IMPL_v0.1.json'
CONF_ART = f'{RD}/DHE_U_CONFORMANCE_REAL.json'

RAW_DM = f'{RD}/_dhe_12f_raw_dm.npy'
SIGNED_DM = f'{RD}/_dhe_12f_signed_dm.npy'

OUT = f'{RD}/DHE_12F_CAUSAL_CONFIRM.json'
OUT_SIDE = OUT + '.sidecar.json'
OUT_LED = f'{RD}/DHE_12F_PER_ITEM.json'

RAW_HASH = 'f9aae5833055859c481b500a8a54cfdac9b994e59d10f924b81f6369bfc2515a'
SIGNED_HASH = '0b91e4e945189e1bf0c301215bad179f61b9f7fcd6446ecd96ebc1cbc07f0d88'

L_SITE = 23
HID = 4096
LAMBDA = 1.1402872562408447
ALPHA_EFF_D2 = 0.05415999941978071
N_ITEMS = 48
N_PERMS = 24

FWD = 0
AUTOG = 0
PATCHES = 0
PARAM_MUT = 0
OPT_STEPS = 0
BEHAV_READS = 0


def jcs(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, default=str)
                          .encode('utf-8')).hexdigest()


def _pyclean(o):
    """递归把 numpy 标量/数组转成 Python 原生类型 (防 np.bool_/np.float64 破坏 json)。"""
    import numpy as _np
    if isinstance(o, dict):
        return {k: _pyclean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_pyclean(v) for v in o]
    if isinstance(o, _np.ndarray):
        return o.tolist()
    if isinstance(o, _np.bool_):
        return bool(o)
    if isinstance(o, _np.integer):
        return int(o)
    if isinstance(o, _np.floating):
        return float(o)
    return o


def safe_load_json(path, tag):
    """读前置产物; 完整性检查失败即 HARD STOP (避免在残缺文件上继续)。"""
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        hard_stop('PREREQUISITE_ARTIFACT_CORRUPT',
                  {'tag': tag, 'path': path, 'error': f'{type(e).__name__}: {e}',
                   'rule': 'do NOT proceed on a truncated prerequisite artifact'})


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def hard_stop(reason, payload):
    doc = {'kind': 'DHE_12F_CAUSAL_CONFIRM', 'date': '2026-09-23',
           'verdict': f'HARD_STOP::{reason}', 'detail': payload,
           'counters': {'12F_forward_calls': FWD, '12F_autograd_calls': AUTOG,
                        'patches': PATCHES, 'parameter_mutations': PARAM_MUT,
                        'optimizer_steps': OPT_STEPS,
                        'retention_delay_interference_touched': False}}
    doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
    json.dump(doc, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print()
    print('=' * 76)
    print(f'  {reason} -> 12F HARD STOP')
    print('=' * 76)
    print(f'    {payload}')
    sys.exit(2)


print('=' * 76)
print('  S7-S10 : CAUSAL_CONFIRM (唯一一次 opening, 4608 forwards)')
print('=' * 76)
print()

import numpy as np
import torch

# ── provenance ────────────────────────────────────────────────────────
replay = safe_load_json(REPLAY_ART, 'REPLAY_ART')
proj = safe_load_json(PROJ, 'PROJECTION')
split = safe_load_json(SPLIT, 'SPLIT')
tpl = safe_load_json(TPL, 'TEMPLATE')
sgn = safe_load_json(SIGN, 'SIGN_MANIFEST')
ids = safe_load_json(IDS_ART, 'CODE_IDS')
impl = safe_load_json(IMPL_ART, 'U_IMPL')
conf = safe_load_json(CONF_ART, 'U_CONFORMANCE')

print('--- provenance gates ---')
# 注意: U_DHE_IMPL 的权威判定在 DHE_U_CONFORMANCE_REAL.json (real 层完成后写入);
#       DHE_U_DHE_IMPL_v0.1.json 的 'qualified' 是 synthetic 时点的历史值, 不权威.
_u_impl_authoritative = (
    conf.get('U_DHE_IMPL_v0.1') == 'QUALIFIED'
    and all(conf['conditions'].values())
    and conf['two_paths']['pass'] is True
    and conf['two_paths']['max_abs_diff'] == 0.0
)
gates = {
    'replay_strict_equivalent': replay.get('strict_equivalent') is True,
    'u_impl_qualified_authoritative': _u_impl_authoritative,
    'u_conf_Uprod_eq_Uref': conf['two_paths']['pass'],
    'sign_manifest_96': sgn['n_items'] == 96 and sgn['n_derive'] == 48
                        and sgn['n_confirm'] == 48,
    'sign_deps_zero': sgn['dependencies'] == {
        'activation_dependency': 0, 'R_g_dependency': 0,
        'behavior_dependency': 0, 'confirmation_dependency': 0},
}
for k, v in gates.items():
    print(f'    {k:<34} = {v}')
if not all(gates.values()):
    hard_stop('PRECONDITION_FAIL', {k: v for k, v in gates.items() if not v})

raw32 = np.load(RAW_DM)
signed32 = np.load(SIGNED_DM)
raw_h = hashlib.sha256(raw32.tobytes()).hexdigest()
signed_h = hashlib.sha256(signed32.tobytes()).hexdigest()
print(f'    raw    d_M hash = {raw_h[:16]}  match={raw_h == RAW_HASH}')
print(f'    signed d_M hash = {signed_h[:16]}  match={signed_h == SIGNED_HASH}')
if raw_h != RAW_HASH or signed_h != SIGNED_HASH:
    hard_stop('DIRECTION_HASH_MISMATCH', {'raw': raw_h, 'signed': signed_h})
print()

SIGN_MAP = {r['episode_id']: r['sign'] for r in sgn['items']}
con_ids = list(split['CAUSAL_CONFIRM']['pair_ids'])
pairs_all = {p['pair_id']: p for p in proj['pairs']}
con_pairs = [pairs_all[pid] for pid in con_ids]
items = [it for p in con_pairs for it in p['items']]
print(f'    CAUSAL_CONFIRM pairs={len(con_pairs)} items={len(items)}')
if len(items) != N_ITEMS:
    hard_stop('ITEM_COUNT_FAIL', {'got': len(items)})
print()

# ── model ─────────────────────────────────────────────────────────────
import gguf
from gguf.quants import dequantize
from transformers import (AutoTokenizer, LlamaConfig, LlamaForCausalLM,
                          MistralConfig, MistralForCausalLM)
import transformers.modeling_gguf_pytorch_utils as U

CFG = {'vocab_size': 32000, 'hidden_size': HID, 'intermediate_size': 14336,
       'num_hidden_layers': 32, 'num_attention_heads': 32, 'num_key_value_heads': 8,
       'hidden_act': 'silu', 'max_position_embeddings': 32768,
       'initializer_range': 0.02, 'rms_norm_eps': 1e-5, 'use_cache': True,
       'bos_token_id': 1, 'eos_token_id': 2, 'tie_word_embeddings': False,
       'rope_theta': 10000.0, 'sliding_window': 4096, 'attention_dropout': 0.0,
       'model_type': 'mistral'}
PXY = dict(CFG); PXY['model_type'] = 'llama'; PXY.pop('sliding_window')
mcfg = MistralConfig(**CFG)
mcfg._attn_implementation = 'eager'
model = MistralForCausalLM(mcfg)
SD = model.state_dict()
EXPECTED = set(SD.keys())
with torch.device('meta'):
    proxy = LlamaForCausalLM(LlamaConfig(**PXY))
reader = gguf.GGUFReader(MODEL_PATH)
md = U.load_gguf_checkpoint(MODEL_PATH, return_tensors=False)
pcfg = md.get('config', {})
P = U.TENSOR_PROCESSORS.get('llama', U.TensorProcessor)
proc = P(config=dict(pcfg))
tkm = U.get_gguf_hf_weights_map(proxy, proc)
seen = set()
for si, t in enumerate(reader.tensors):
    dec = dequantize(t.data, t.tensor_type)
    r = proc.process(weights=dec, name=t.name, tensor_key_mapping=tkm,
                     parsed_parameters={'config': dict(pcfg)})
    w, nm = getattr(r, 'weights', None), getattr(r, 'name', None)
    if nm is None or nm not in tkm:
        hard_stop('UNMAPPED_SOURCE_TENSOR', {'idx': si})
    k = tkm[nm]
    if k not in EXPECTED or k in seen:
        hard_stop('TARGET_KEY_PROBLEM', {'key': k})
    with torch.no_grad():
        SD[k].copy_(torch.from_numpy(np.ascontiguousarray(w, dtype=np.float32)))
    seen.add(k)
    del w, dec, r
    gc.collect()
del proxy, reader
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
model = model.to('cuda').eval()
if sha256_file(MODEL_PATH) != GGUF_SHA_EXPECTED:
    hard_stop('GGUF_SHA_MISMATCH', {})
lay = model.model.layers
if (type(model).__name__ != 'MistralForCausalLM'
        or model.config.model_type != 'mistral'
        or type(lay[L_SITE]).__name__ != 'MistralDecoderLayer'
        or len(seen) != len(EXPECTED)):
    hard_stop('GATE_L_FAIL', {})
tok = AutoTokenizer.from_pretrained(MODEL_DIR, gguf_file=GGUF_FILE)
print(f'    loaded {len(seen)}/{len(EXPECTED)} ; GATE_L PASS ; FWD before = 0')
print()

TOKEN_A = ids['codes']['A']; TOKEN_B = ids['codes']['B']
TOKEN_C = ids['codes']['C']; TOKEN_D = ids['codes']['D']
CORE = [TOKEN_A, TOKEN_B, TOKEN_C, TOKEN_D]
E_TPL = tpl['E_template']; F_TPL = tpl['F_template']
PERMS = [list(p) for p in itertools.permutations([0, 1, 2, 3])]
assert len(PERMS) == 24
block_places = proj['block_place_universe']

# ── patch hook (patch-first) ──────────────────────────────────────────
STATE = {'d': None, 'sign': 0, 't_dec': None, 'count': 0, 'patch_count': 0}


def patch_hook(module, args, output):
    out = output[0] if isinstance(output, tuple) else output
    if STATE['count'] >= 1:
        return None
    STATE['count'] += 1
    H = out.clone()
    H[0, STATE['t_dec'], :] = H[0, STATE['t_dec'], :] + \
        STATE['sign'] * LAMBDA * STATE['d']
    STATE['patch_count'] += 1
    if isinstance(output, tuple):
        return (H,) + tuple(output[1:])
    return H


hh = lay[L_SITE].register_forward_hook(patch_hook)


def log_softmax4(z):
    m = max(z)
    lse = m + math.log(sum(math.exp(zi - m) for zi in z))
    return [zi - lse for zi in z]


CANON = [list(p) for p in itertools.permutations([0, 1, 2, 3])]


def U_impl(Zd):
    acc = [0.0] * 4
    for pi in CANON:
        ell = log_softmax4(Zd[tuple(pi)])
        for p_idx in range(4):
            acc[p_idx] += ell[pi[p_idx]]
    return [a / 24.0 for a in acc]


def U_ref(Zd):
    out = [0.0] * 4
    for p in range(4):
        vals = []
        for pi in CANON:
            k = pi[p]
            z = list(Zd[tuple(pi)])
            m = max(z)
            lse = m + math.log(sum(math.exp(zi - m) for zi in z))
            vals.append(z[k] - lse)
        out[p] = sum(vals) / 24.0
    return out


# ═══════════════════════════════════════════════════════════════════════
# S7 main loop
# ═══════════════════════════════════════════════════════════════════════
print('=' * 76)
print('  S7 : CAUSAL_CONFIRM — %d items x 24pi x 2 signs x 2 directions' % len(items))
print('=' * 76)
print()

D_RAW = torch.from_numpy(raw32).to('cuda')
D_SIGNED = torch.from_numpy(signed32).to('cuda')

cmax = 0.0
per_item = []
t0 = time.time()
for ii, it in enumerate(items):
    role, pA, pB = it['role_id'], it['p_A'], it['p_B']
    bid = it['block_id']
    cands = list(block_places[bid])
    s_i = SIGN_MAP[it['episode_id']]
    idx = {q: j for j, q in enumerate(block_places[bid])}
    iA, iB = idx[pA], idx[pB]

    EA = E_TPL.format(role=role, place=pA)
    EB = E_TPL.format(role=role, place=pB)

    # 两次 patch × 24π × 2 signs = 96 forwards per item
    res = {}
    for dtag, dvec in (('raw', D_RAW), ('signed', D_SIGNED)):
        for pit, perm in enumerate(PERMS):
            c = [cands[k] for k in perm]
            F = F_TPL.format(role=role, p0=c[0], p1=c[1], p2=c[2], p3=c[3])
            for arm, ET in (('A', EA), ('B', EB)):
                for sgn_v in (+1, -1):
                    STATE.update({'d': dvec, 'sign': sgn_v, 't_dec': None,
                                  'count': 0, 'patch_count': 0})
                    enc = tok(ET + F, return_tensors='pt')
                    ids_t = enc['input_ids'].to('cuda')
                    at = enc['attention_mask'].to('cuda')
                    t_dec = int(ids_t.shape[1]) - 1
                    STATE['t_dec'] = t_dec
                    with torch.no_grad():
                        out = model(input_ids=ids_t, attention_mask=at,
                                    use_cache=False, return_dict=True)
                    FWD += 1
                    if STATE['patch_count'] != 1:
                        hard_stop('PATCH_COUNT_GUARD_FAIL',
                                  {'item': ii, 'dir': dtag, 'pi': pit,
                                   'arm': arm, 'sign': sgn_v,
                                   'patch_count': STATE['patch_count']})
                    PATCHES += STATE['patch_count']
                    lg = out.logits[0, t_dec, :]
                    rem = lg.detach().to('cpu', torch.float64).numpy()
                    cmax = max(cmax, float(np.abs(rem).max()))
                    res[(dtag, pit, arm, sgn_v)] = [float(rem[k]) for k in CORE]
                    del out, lg, rem
                    STATE['count'] = 0

    # ── assemble Z per (dtag, sign) and compute U ────────────────────
    rec = {'episode_id': it['episode_id'], 'pair_id': it['source_pair_id'],
           'block': bid, 'role': role, 'p_A': pA, 'p_B': pB, 's_i': s_i,
           'iA': iA, 'iB': iB}

    def U_for(dtag, arm, sgn_v):
        Zd = {tuple(PERMS[pit]): res[(dtag, pit, arm, sgn_v)] for pit in range(24)}
        up = U_impl(Zd)
        ur = U_ref(Zd)
        if max(abs(up[k] - ur[k]) for k in range(4)) > 1e-9:
            hard_stop('U_PROD_REF_MISMATCH',
                      {'item': ii, 'dir': dtag, 'arm': arm, 'sign': sgn_v})
        return up

    Uraw_plus_A = U_for('raw', 'A', +1); Uraw_plus_B = U_for('raw', 'B', +1)
    Uraw_minus_A = U_for('raw', 'A', -1); Uraw_minus_B = U_for('raw', 'B', -1)
    Braw_p = Uraw_plus_A[iA] - Uraw_plus_B[iB]
    Braw_m = Uraw_minus_A[iA] - Uraw_minus_B[iB]
    C_raw_i = Braw_p - Braw_m

    Usig_plus_A = U_for('signed', 'A', +1); Usig_plus_B = U_for('signed', 'B', +1)
    Usig_minus_A = U_for('signed', 'A', -1); Usig_minus_B = U_for('signed', 'B', -1)
    Bsig_p = s_i * (Usig_plus_A[iA] - Usig_plus_B[iB])
    Bsig_m = s_i * (Usig_minus_A[iA] - Usig_minus_B[iB])
    C_signed_i = Bsig_p - Bsig_m

    rec.update({'C_raw_i': C_raw_i, 'C_signed_i': C_signed_i,
                'B_raw_plus': Braw_p, 'B_raw_minus': Braw_m,
                'B_signed_plus': Bsig_p, 'B_signed_minus': Bsig_m})
    per_item.append(rec)
    if (ii + 1) % 4 == 0:
        print(f'    ... {ii+1}/{len(items)} items ; fwd={FWD} ({time.time()-t0:.1f}s)')

hh.remove()
del model
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
print(f'    S7 done ; forwards = {FWD} (expect 4608) ; {time.time()-t0:.1f}s')
if FWD != 4608:
    hard_stop('FORWARD_COUNT_FAIL', {'got': FWD})
print()

# ═══════════════════════════════════════════════════════════════════════
# S8 aggregates
# ═══════════════════════════════════════════════════════════════════════
a_raw = np.asarray([r['C_raw_i'] for r in per_item], dtype=np.float64)
a_sig = np.asarray([r['C_signed_i'] for r in per_item], dtype=np.float64)
C_raw = float(a_raw.mean())
C_sig = float(a_sig.mean())
Delta_C = C_sig - C_raw

print('=' * 76)
print('  S8 : PRIMARY RESULTS')
print('=' * 76)
print()
print(f'    C_raw    = {C_raw:+.10f}')
print(f'    C_signed = {C_sig:+.10f}')
print(f'    Delta_C  = {Delta_C:+.10f}   (SECONDARY: estimator-package contrast)')
print()
print(f'    H_raw    gate C_raw    > 0 : {"PASS" if C_raw > 0 else "FAIL"}')
print(f'    H_signed gate C_signed > 0 : {"PASS" if C_sig > 0 else "FAIL"}')
print()


def summ(a):
    return {'N': int(a.size), 'mean': float(a.mean()), 'median': float(np.median(a)),
            'q05': float(np.quantile(a, .05)), 'q25': float(np.quantile(a, .25)),
            'q75': float(np.quantile(a, .75)), 'q95': float(np.quantile(a, .95)),
            'min': float(a.min()), 'max': float(a.max()),
            'n_positive': int((a > 0).sum()),
            'fraction_positive': float((a > 0).mean())}


C_raw_s, C_sig_s = summ(a_raw), summ(a_sig)
print(f'    C_i^raw    : median={C_raw_s["median"]:+.6f} '
      f'pos={C_raw_s["n_positive"]}/{C_raw_s["N"]} '
      f'({C_raw_s["fraction_positive"]:.3f})')
print(f'    C_i^signed : median={C_sig_s["median"]:+.6f} '
      f'pos={C_sig_s["n_positive"]}/{C_sig_s["N"]} '
      f'({C_sig_s["fraction_positive"]:.3f})')
print()

# per-pair aggregation
pg = {}
for r in per_item:
    pg.setdefault(r['pair_id'], []).append(r)
Cg_raw, Cg_sig, Dg = [], [], []
for pid, rs in sorted(pg.items()):
    cr = np.mean([r['C_raw_i'] for r in rs]); cs = np.mean([r['C_signed_i'] for r in rs])
    Cg_raw.append(cr); Cg_sig.append(cs); Dg.append(cs - cr)
Cg_raw, Cg_sig, Dg = map(lambda x: np.asarray(x, np.float64), (Cg_raw, Cg_sig, Dg))
print(f'    C_g^raw    : median={np.median(Cg_raw):+.6f} '
      f'pos={int((Cg_raw>0).sum())}/{Cg_raw.size}')
print(f'    C_g^signed : median={np.median(Cg_sig):+.6f} '
      f'pos={int((Cg_sig>0).sum())}/{Cg_sig.size}')
print(f'    D_g        : median={np.median(Dg):+.6f}')
print()

json.dump({'kind': 'DHE_12F_PER_ITEM', 'date': '2026-09-23',
           'n_items': len(per_item), 'per_item': per_item,
           'CONTENT_HASH': jcs(per_item)},
          open(OUT_LED, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

# result class A/B/C/D
if C_raw > 0 and C_sig > 0:
    cls = 'A'
elif C_raw <= 0 and C_sig > 0:
    cls = 'B'
elif C_raw > 0 and C_sig <= 0:
    cls = 'C'
else:
    cls = 'D'

doc = {
    'kind': 'DHE_12F_CAUSAL_CONFIRM', 'date': '2026-09-23',
    'authority': '凌翼 §10/§11 (S7-S10 direct go) + Mion 三条同等报告条件',
    'step': '12F_CAUSAL_CONFIRM',
    'data': {'split': 'CAUSAL_CONFIRM (first and only opening)',
             'n_pairs': len(con_pairs), 'n_items': len(items),
             'retention_delay_interference_touched': False},
    'directions': {'raw': {'sha256': raw_h, 'endpoint': 'U(p_A)-U(p_B)'},
                   'signed': {'sha256': signed_h,
                              'endpoint': 's_i*[U(p_A)-U(p_B)]'}},
    'sign_manifest_hash': sgn['CONTENT_HASH'],
    'lambda': LAMBDA, 'alpha_effective_D2': ALPHA_EFF_D2,
    'alpha_effective_role': 'DESCRIPTIVE DOMAIN-SCALE DIAGNOSTIC (真实 provenance 是 lambda)',
    'site': L_SITE, 'operator': 'additive post-block residual',
    'render_symmetrization': 24,
    'PRIMARY_RESULTS': {
        'C_raw': C_raw, 'C_signed': C_sig,
        'H_raw_gate': 'PASS' if C_raw > 0 else 'FAIL',
        'H_signed_gate': 'PASS' if C_sig > 0 else 'FAIL',
        'result_class': cls,
    },
    'SECONDARY_comparative': {
        'Delta_C': Delta_C,
        'identity': 'SIGNED-vs-RAW ESTIMATOR-PACKAGE CONTRAST',
        'role': 'SECONDARY — not a gate, not a rescue, reported mechanically'},
    'descriptive': {
        'C_i_raw': C_raw_s, 'C_i_signed': C_sig_s,
        'C_g_raw': summ(Cg_raw), 'C_g_signed': summ(Cg_sig), 'D_g': summ(Dg)},
    'interpretation_boundaries': {
        'R_g': '24/24 negative, systematic reciprocal anti-alignment, material '
               'reciprocity confirmed — INTERPRETIVE BOUNDARY, not a gate',
        'l_star': 'l*=23 selected under near-equal normalized response (~4.8% span); '
                  'any behavioral effect must NOT be read as "layer 23 is special"',
        'raw_null_reading': 'C_raw <= 0 cannot be read as absence of memory; raw null '
                            'does not distinguish causal absence from estimator-direction '
                            'misspecification',
        'multiplicity': 'TWO prespecified primary hypotheses (H_raw, H_signed) run in the '
                        'same opening; both must be reported at equal prominence; no '
                        'selective reporting of the winner',
        'forbidden_conclusions': ['no memory', 'memory absent', 'digital hippocampus absent'],
    },
    'four_class_wording': {
        'A': 'both estimator packages demonstrate held-out causal effect; Delta_C descriptive',
        'B': 'raw reciprocal-averaging null is compatible with orientation cancellation; '
             'material-aligned estimator recovered a held-out causal effect => "direction '
             'setting was falsified", NOT "memory exists" — no arm-switching claim',
        'C': 'original raw aggregate effective; derive-informed signed alternative did not pass',
        'D': 'neither linear aggregate estimator demonstrated the frozen causal effect; '
             'still NOT "no memory"',
        'current_class': cls,
    },
    'counters': {'12F_forward_calls': FWD, '12F_autograd_calls': AUTOG,
                 'patches': PATCHES, 'parameter_mutations': PARAM_MUT,
                 'optimizer_steps': OPT_STEPS,
                 'retention_delay_interference_touched': False},
    'U_prod_U_ref_conformance': 'PASS on every render (checked per (dir,arm,sign))',
    'CAUSAL_CONFIRM_opened': True,
    'next': 'S10 STOP — 不进 retention / delay / interference / transplantation',
    'frozen_sentences': [
        'The ruler is qualified. The directions are frozen. The confirmation set is '
        'still dark.',
        'A signed direction requires a signed measurement axis.',
        'Do not align the arrow and then score half the targets backwards.',
        'No redesign between the question and its answer.',
    ],
}
doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
doc = _pyclean(doc)
json.dump(doc, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
json.dump({'kind': 'DHE_12F_CAUSAL_CONFIRM_SIDECAR', 'file': OUT,
           'artifact_file_sha256': sha256_file(OUT),
           'CONTENT_HASH': doc['CONTENT_HASH']},
          open(OUT_SIDE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

print('=' * 76)
print('  S10 : STOP')
print('=' * 76)
print()
print(f'    12F_forward_calls = {FWD} ; autograd = {AUTOG} ; patches = {PATCHES}')
print(f'    parameter_mutations = {PARAM_MUT} ; optimizer_steps = {OPT_STEPS}')
print(f'    CAUSAL_CONFIRM opened = TRUE ; retention/delay/interference = NOT TOUCHED')
print()
print(f'    result_class = {cls}')
print()
print('--- 产物 ---')
for p in [OUT, OUT_SIDE, OUT_LED]:
    print('    %-42s %10d B  %s' % (os.path.basename(p), os.path.getsize(p),
                                    sha256_file(p)[:16]))
