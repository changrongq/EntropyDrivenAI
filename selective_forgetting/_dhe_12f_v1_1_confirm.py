# -*- coding: utf-8 -*-
"""_dhe_12f_v1_1_confirm.py —— 12F-v1.1 FRESH CAUSAL_CONFIRM (9216 forwards)

凌翼 12F-v1.1 裁决:
  9216 = 正确的最终预算; 但 Coder 的理由需修正 —— 少的不是 proposal axis,
  而是 episode conditioning arm {E_A, E_B}。

轴序 (R1 sealed, DHE_12F_AXIS_ORDER_v1.1.json):
  item(48) x episode_arm{E_A,E_B}(2) x estimator_package{raw,signed}(2)
           x intervention_sign{+,-}(2) x render(24) = 9216

关键规则 (冻结):
  - 每个 forward 同时服务 p_A 与 p_B:
        同一 24π render family -> 完整四地 U(p) 向量 -> p_A/p_B 是两个坐标
        绝不为了两个 proposals 分别 forward
  - 两个 episode arms 地位完全对称, 先各自算 C, 再对称平均:
        C^q_{i,e} = B_{i,e,q,+} - B_{i,e,q,-}
        C^q_i     = (1/2)( C^q_{i,A} + C^q_{i,B} )      <-- symmetrize arms
        C_q       = (1/48) sum_i C^q_i
  - gate: C_raw > 0 (H_raw) ; C_signed > 0 (H_signed)
  - Delta_C = C_signed - C_raw  (只作预注册 secondary comparator)
  - 无 effect-size rescue / 无 fraction-positive gate / 无 R_g gate / 无第三判据

旧 v1 的 9216 in-memory outputs: DISCARD (不得读取, 不得转正)
本脚本 = 全新一次 forward campaign, 全新 seal。

禁止: no memory / memory absent / digital hippocampus absent
      / 只报赢的那个 / 把 Delta_C 塞脚注
始终: autograd=0 ; logits 不作为 behavior read 输入 (behavior = endpoint only, 预注册) ;
      retention / delay / interference = NOT TOUCHED
"""
import sys
import os
import json
import hashlib
import gc
import time
import itertools
import math

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
CONF_ART = f'{RD}/DHE_U_CONFORMANCE_REAL.json'
AMD_ART = f'{RD}/DHE_12F_PROTOCOL_AMENDMENT_v1.1.json'
AXIS_ART = f'{RD}/DHE_12F_AXIS_ORDER_v1.1.json'

RAW_DM = f'{RD}/_dhe_12f_raw_dm.npy'
SIGNED_DM = f'{RD}/_dhe_12f_signed_dm.npy'

OUT = f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1.1.json'
OUT_SIDE = OUT + '.sidecar.json'
OUT_LED = f'{RD}/DHE_12F_PER_ITEM.v1.1.json'

RAW_HASH = 'f9aae5833055859c481b500a8a54cfdac9b994e59d10f924b81f6369bfc2515a'
SIGNED_HASH = '0b91e4e945189e1bf0c301215bad179f61b9f7fcd6446ecd96ebc1cbc07f0d88'
SIGN_MANIFEST_HASH = '0b68988b4f55023688669a9513bcb93e70e2275279e285276d0ea489616870e9'

L_SITE = 23
HID = 4096
LAMBDA = 1.1402872562408447
ALPHA_EFF_D2 = 0.05415999941978071
N_ITEMS = 48
N_PERMS = 24
N_ARMS = 2
N_PKGS = 2
N_SIGNS = 2
EXPECTED_FWD = N_ITEMS * N_ARMS * N_PKGS * N_SIGNS * N_PERMS   # 9216

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
    """递归把 numpy 标量/数组转成 Python 原生类型 (防 np.bool_ 破坏 json)。"""
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


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def safe_load_json(path, tag):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        hard_stop('PREREQUISITE_ARTIFACT_CORRUPT',
                  {'tag': tag, 'path': path,
                   'error': f'{type(e).__name__}: {e}',
                   'rule': 'do NOT proceed on a truncated prerequisite artifact'})


def safe_dump(path, obj):
    """先序列化到内存再落盘 —— 防中途异常留下截断文件。"""
    txt = json.dumps(obj, indent=2, ensure_ascii=False)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    return txt


def hard_stop(reason, payload):
    doc = {'kind': 'DHE_12F_CAUSAL_CONFIRM_v1.1', 'date': '2026-09-24',
           'verdict': f'HARD_STOP::{reason}', 'detail': _pyclean(payload),
           'counters': {'12F_forward_calls': FWD, '12F_autograd_calls': AUTOG,
                        'patches': PATCHES, 'parameter_mutations': PARAM_MUT,
                        'optimizer_steps': OPT_STEPS,
                        'retention_delay_interference_touched': False}}
    doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
    safe_dump(OUT, doc)
    print()
    print('=' * 76)
    print(f'  {reason} -> 12F-v1.1 HARD STOP')
    print('=' * 76)
    print(f'    {payload}')
    sys.exit(2)


print('=' * 76)
print('  S7-v1.1 : CAUSAL_CONFIRM (fresh, symmetric episode arms, 9216 forwards)')
print('=' * 76)
print()

import numpy as np
import torch

# ── R2 provenance gates ───────────────────────────────────────────────
replay = safe_load_json(REPLAY_ART, 'REPLAY_ART')
proj = safe_load_json(PROJ, 'PROJECTION')
split = safe_load_json(SPLIT, 'SPLIT')
tpl = safe_load_json(TPL, 'TEMPLATE')
sgn = safe_load_json(SIGN, 'SIGN_MANIFEST')
ids = safe_load_json(IDS_ART, 'CODE_IDS')
conf = safe_load_json(CONF_ART, 'U_CONFORMANCE')
amd = safe_load_json(AMD_ART, 'AMENDMENT')
axis_doc = safe_load_json(AXIS_ART, 'AXIS_ORDER')

print('--- R2 provenance gates ---')
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
    'sign_manifest_hash_0b68988b': sgn.get('CONTENT_HASH') == SIGN_MANIFEST_HASH,
    'sign_deps_zero': all(v == 0 for v in sgn['dependencies'].values()),
    'amendment_axiom_9216': amd.get('corrected_expected_count') == EXPECTED_FWD,
    'amendment_results_not_revealed':
        amd.get('scientific_results_revealed_before_correction') is False,
    'amendment_classification':
        amd.get('classification') == 'PRE-RESULT SCIENTIFIC-SCOPE COMPLETION',
    'old_outputs_discarded':
        amd.get('old_in_memory_outputs', {}).get('status') == 'DISCARD',
    'axis_order_9216': axis_doc.get('expected_forward_count') == EXPECTED_FWD,
    'axis_arm_is_symmetric': 'episode_arm{A,B}' in axis_doc['axis_order'],
    'old_v1_fail_artifact_retained': safe_load_json(
        f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1_FORWARD_COUNT_FAIL.json', 'V1_FAIL'
    )['verdict'] == 'HARD_STOP::FORWARD_COUNT_FAIL',
    'no_prior_v1_1_result': not os.path.exists(OUT),
}
for k, v in gates.items():
    print(f'    {k:<42} = {v}')
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
if len(con_ids) != 24:
    hard_stop('PAIR_COUNT_FAIL', {'got': len(con_ids)})
print()

# ── fresh model (same repaired streaming loader) ──────────────────────
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
PXY = dict(CFG)
PXY['model_type'] = 'llama'
PXY.pop('sliding_window')
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

TOKEN_A = ids['codes']['A']
TOKEN_B = ids['codes']['B']
TOKEN_C = ids['codes']['C']
TOKEN_D = ids['codes']['D']
CORE = [TOKEN_A, TOKEN_B, TOKEN_C, TOKEN_D]
E_TPL = tpl['E_template']
F_TPL = tpl['F_template']
PERMS = [list(p) for p in itertools.permutations([0, 1, 2, 3])]
assert len(PERMS) == 24
block_places = proj['block_place_universe']

# ── patch hook (patch-first, exactly one patch per forward) ───────────
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
# S7-v1.1 main loop : 48 x 2 arms x 2 pkgs x 2 signs x 24 renders = 9216
# ═══════════════════════════════════════════════════════════════════════
print('=' * 76)
print('  S7-v1.1 : %d items x %d episode arms x %d pkgs x %d signs x %d renders = %d'
      % (len(items), N_ARMS, N_PKGS, N_SIGNS, N_PERMS, EXPECTED_FWD))
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

    # 每个 (dtag, arm) 先收集 24π x 2 signs = 48 forwards
    res = {}
    for dtag, dvec in (('raw', D_RAW), ('signed', D_SIGNED)):
        for arm, ET in (('A', EA), ('B', EB)):
            for pit, perm in enumerate(PERMS):
                c = [cands[k] for k in perm]
                F = F_TPL.format(role=role, p0=c[0], p1=c[1], p2=c[2], p3=c[3])
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
                    res[(dtag, arm, pit, sgn_v)] = [float(rem[k]) for k in CORE]
                    del out, lg, rem
                    STATE['count'] = 0

    # ── U vector per (dtag, arm, sign) ──────────────────────────────
    def U_for(dtag, arm, sgn_v):
        Zd = {tuple(PERMS[pit]): res[(dtag, arm, pit, sgn_v)]
              for pit in range(24)}
        up = U_impl(Zd)
        ur = U_ref(Zd)
        if max(abs(up[k] - ur[k]) for k in range(4)) > 1e-9:
            hard_stop('U_PROD_REF_MISMATCH',
                      {'item': ii, 'dir': dtag, 'arm': arm, 'sign': sgn_v})
        return up

    # 凌翼 §5:  B_{i,e,q,sigma} = U_{i,e,q,sigma}(p_A) - U_{i,e,q,sigma}(p_B)
    #   注意 U(p_A) 与 U(p_B) 是同一个 24-forward 向量的两个坐标 (iA / iB),
    #   不是两次 forward。arm 只决定 episode context 是 E_A 还是 E_B。
    Uraw_pA = U_for('raw', 'A', +1)
    Uraw_pB = U_for('raw', 'B', +1)
    Uraw_mA = U_for('raw', 'A', -1)
    Uraw_mB = U_for('raw', 'B', -1)

    # 凌翼 §6:  C^q_{i,e} = B_{i,e,q,+} - B_{i,e,q,-}
    C_raw_A = (Uraw_pA[iA] - Uraw_pA[iB]) - (Uraw_mA[iA] - Uraw_mA[iB])
    C_raw_B = (Uraw_pB[iA] - Uraw_pB[iB]) - (Uraw_mB[iA] - Uraw_mB[iB])
    C_raw_i = 0.5 * (C_raw_A + C_raw_B)

    Usig_pA = U_for('signed', 'A', +1)
    Usig_pB = U_for('signed', 'B', +1)
    Usig_mA = U_for('signed', 'A', -1)
    Usig_mB = U_for('signed', 'B', -1)

    # signed endpoint 带 s_i (凌翼 §5):  B^signed = s_i*[U(p_A)-U(p_B)]
    C_signed_A = s_i * ((Usig_pA[iA] - Usig_pA[iB]) - (Usig_mA[iA] - Usig_mA[iB]))
    C_signed_B = s_i * ((Usig_pB[iA] - Usig_pB[iB]) - (Usig_mB[iA] - Usig_mB[iB]))
    C_signed_i = 0.5 * (C_signed_A + C_signed_B)

    rec = {'episode_id': it['episode_id'], 'pair_id': it['source_pair_id'],
           'block': bid, 'role': role, 'p_A': pA, 'p_B': pB, 's_i': s_i,
           'iA': iA, 'iB': iB,
           'C_raw_i': C_raw_i, 'C_signed_i': C_signed_i,
           'C_raw_armA': C_raw_A, 'C_raw_armB': C_raw_B,
           'C_signed_armA': C_signed_A, 'C_signed_armB': C_signed_B,
           'B_raw_plus_armA': Uraw_pA[iA] - Uraw_pA[iB],
           'B_raw_minus_armA': Uraw_mA[iA] - Uraw_mA[iB],
           'B_raw_plus_armB': Uraw_pB[iA] - Uraw_pB[iB],
           'B_raw_minus_armB': Uraw_mB[iA] - Uraw_mB[iB],
           'B_signed_plus_armA': s_i * (Usig_pA[iA] - Usig_pA[iB]),
           'B_signed_minus_armA': s_i * (Usig_mA[iA] - Usig_mA[iB]),
           'B_signed_plus_armB': s_i * (Usig_pB[iA] - Usig_pB[iB]),
           'B_signed_minus_armB': s_i * (Usig_mB[iA] - Usig_mB[iB])}
    per_item.append(rec)
    if (ii + 1) % 4 == 0:
        print('    ... %d/%d items ; fwd=%d (%.1fs)'
              % (ii + 1, len(items), FWD, time.time() - t0))
        sys.stdout.flush()

hh.remove()
del model
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
print('    S7-v1.1 done ; forwards = %d (expect %d) ; %.1fs'
      % (FWD, EXPECTED_FWD, time.time() - t0))
if FWD != EXPECTED_FWD:
    hard_stop('FORWARD_COUNT_FAIL',
              {'got': FWD, 'expected': EXPECTED_FWD,
               'derivation': '%d items x %d arms x %d pkgs x %d signs x %d renders'
                             % (N_ITEMS, N_ARMS, N_PKGS, N_SIGNS, N_PERMS)})
if AUTOG != 0:
    hard_stop('AUTOGRAD_GUARD_FAIL', {'autograd_calls': AUTOG})
if PATCHES != EXPECTED_FWD:
    hard_stop('PATCH_TOTAL_FAIL', {'patches': PATCHES, 'forwards': FWD})
print()

# ═══════════════════════════════════════════════════════════════════════
# S8-v1.1 aggregates
# ═══════════════════════════════════════════════════════════════════════
a_raw = np.asarray([r['C_raw_i'] for r in per_item], dtype=np.float64)
a_sig = np.asarray([r['C_signed_i'] for r in per_item], dtype=np.float64)
arA = np.asarray([r['C_raw_armA'] for r in per_item], dtype=np.float64)
arB = np.asarray([r['C_raw_armB'] for r in per_item], dtype=np.float64)
C_raw = float(a_raw.mean())
C_sig = float(a_sig.mean())
Delta_C = C_sig - C_raw

print('=' * 76)
print('  S8-v1.1 : PRIMARY RESULTS (symmetrized over both episode arms)')
print('=' * 76)
print()
print(f'    C_raw    = {C_raw:+.10f}')
print(f'    C_signed = {C_sig:+.10f}')
print(f'    Delta_C  = {Delta_C:+.10f}   (SECONDARY: estimator-package contrast)')
print()
print(f'    H_raw    gate C_raw    > 0 : {"PASS" if C_raw > 0 else "FAIL"}')
print(f'    H_signed gate C_signed > 0 : {"PASS" if C_sig > 0 else "FAIL"}')
print()
print(f'    arm check (raw) : armA mean = {arA.mean():+.10f}  '
      f'armB mean = {arB.mean():+.10f}')
print(f'    arm check (raw) : max |armA - armB| per item = '
      f'{float(np.max(np.abs(arA - arB))):.6f}  (symmetry diagnostic only)')
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

pg = {}
for r in per_item:
    pg.setdefault(r['pair_id'], []).append(r)
Cg_raw, Cg_sig, Dg = [], [], []
for pid, rs in sorted(pg.items()):
    cr = np.mean([r['C_raw_i'] for r in rs])
    cs = np.mean([r['C_signed_i'] for r in rs])
    Cg_raw.append(cr)
    Cg_sig.append(cs)
    Dg.append(cs - cr)
Cg_raw, Cg_sig, Dg = map(lambda x: np.asarray(x, np.float64), (Cg_raw, Cg_sig, Dg))
print(f'    C_g^raw    : median={np.median(Cg_raw):+.6f} '
      f'pos={int((Cg_raw > 0).sum())}/{Cg_raw.size}')
print(f'    C_g^signed : median={np.median(Cg_sig):+.6f} '
      f'pos={int((Cg_sig > 0).sum())}/{Cg_sig.size}')
print(f'    D_g        : median={np.median(Dg):+.6f}')
print()

if C_raw > 0 and C_sig > 0:
    cls = 'A'
elif C_raw <= 0 and C_sig > 0:
    cls = 'B'
elif C_raw > 0 and C_sig <= 0:
    cls = 'C'
else:
    cls = 'D'

# ═══════════════════════════════════════════════════════════════════════
# S10 seal
# ═══════════════════════════════════════════════════════════════════════
doc = {
    'kind': 'DHE_12F_CAUSAL_CONFIRM_v1.1', 'date': '2026-09-24',
    'authority': '凌翼 12F-v1.1 裁决 (对称 episode-arm confirmation, 9216 forwards)',
    'step': '12F-v1.1_CAUSAL_CONFIRM',
    'protocol_version': '12F-v1.1',
    'amendment': {
        'id': '12F-FORWARD-AXIS-OMISSION-001',
        'artifact': AMD_ART,
        'content_hash': amd['CONTENT_HASH'],
        'classification': 'PRE-RESULT SCIENTIFIC-SCOPE COMPLETION',
        'previous_expected_count': 4608,
        'corrected_expected_count': EXPECTED_FWD,
        'missing_axis': 'episode conditioning arm {E_A, E_B}',
        'proposal_axis_missing': False,
        'coder_stated_reason_rejected': 'U(p_A)/U(p_B) do NOT require separate forwards; '
                                        'the same 24-render family yields a complete '
                                        'four-place U(p) vector.',
        'old_in_memory_outputs': 'DISCARD — never read, never promoted',
        'old_fail_artifact': f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1_FORWARD_COUNT_FAIL.json',
        'rule': 'A failed gate does not become a pass because we later discover why the '
                'count was larger.',
        'correction_order': 'scientific object re-derived FIRST -> axis sealed -> old run '
                            'discarded -> fresh rerun. The gate did not adapt to a result.',
    },
    'axis_order_sealed': axis_doc['axis_order'],
    'axis_sizes': {'item': N_ITEMS, 'episode_arm': N_ARMS, 'estimator_package': N_PKGS,
                   'intervention_sign': N_SIGNS, 'render': N_PERMS},
    'expected_forward_count': EXPECTED_FWD,
    'data': {'split': 'CAUSAL_CONFIRM (first and only opening — v1.1)',
             'n_pairs': len(con_pairs), 'n_items': len(items),
             'retention_delay_interference_touched': False},
    'proposal_rule': 'p_A/p_B subtraction happens AFTER the same 24-forward U vector '
                     'exists; the two proposals never receive separate forwards.',
    'symmetrization': {
        'per_item_per_arm': 'C^q_{i,e} = B_{i,e,q,+} - B_{i,e,q,-}',
        'symmetrize_arms': 'C^q_i = (1/2)( C^q_{i,A} + C^q_{i,B} )',
        'grand_mean': 'C_q = (1/48) sum_i C^q_i',
        'arms_symmetric': True,
        'arm_selection_by_result': False,
        'frozen_sentence': 'Perturb both shores; average the causal slope, do not choose '
                           'a shore after seeing the water.',
    },
    'directions': {'raw': {'sha256': raw_h, 'endpoint': 'U(p_A)-U(p_B)'},
                   'signed': {'sha256': signed_h,
                              'endpoint': 's_i*[U(p_A)-U(p_B)]'}},
    'sign_manifest_hash': sgn['CONTENT_HASH'],
    'lambda': LAMBDA,
    'alpha_effective_D2': ALPHA_EFF_D2,
    'alpha_effective_role': 'DESCRIPTIVE DOMAIN-SCALE DIAGNOSTIC (真实 provenance 是 lambda)',
    'site': L_SITE,
    'operator': 'additive post-block residual',
    'render_symmetrization': 24,
    'PRIMARY_RESULTS': {
        'C_raw': C_raw, 'C_signed': C_sig,
        'H_raw_gate': 'PASS' if C_raw > 0 else 'FAIL',
        'H_signed_gate': 'PASS' if C_sig > 0 else 'FAIL',
        'result_class': cls,
        'both_primaries_equal_prominence': True,
    },
    'SECONDARY_comparative': {
        'Delta_C': Delta_C,
        'identity': 'SIGNED-vs-RAW ESTIMATOR-PACKAGE CONTRAST',
        'role': 'SECONDARY — not a gate, not a rescue, reported mechanically'},
    'descriptive': {
        'C_i_raw': C_raw_s, 'C_i_signed': C_sig_s,
        'C_g_raw': summ(Cg_raw), 'C_g_signed': summ(Cg_sig), 'D_g': summ(Dg),
        'arm_symmetry_raw': {'armA_mean': float(arA.mean()),
                             'armB_mean': float(arB.mean()),
                             'max_abs_armA_minus_armB': float(np.max(np.abs(arA - arB))),
                             'role': 'DESCRIPTIVE ONLY — not a gate'}},
    'interpretation_boundaries': {
        'R_g': '24/24 negative, systematic reciprocal anti-alignment, material '
               'reciprocity confirmed — INTERPRETIVE BOUNDARY, not a gate',
        'l_star': 'l*=23 selected under near-equal normalized response (~4.8% span); '
                  'any behavioral effect must NOT be read as "layer 23 is special"',
        'raw_null_reading': 'C_raw <= 0 cannot be read as absence of memory; raw null '
                            'does not distinguish causal absence from '
                            'estimator-direction misspecification',
        'multiplicity': 'TWO prespecified primary hypotheses (H_raw, H_signed) run in the '
                        'same opening; both must be reported at equal prominence; no '
                        'selective reporting of the winner',
        'single_arm_null_reading': 'Before v1.1, neither E_A nor E_B had been frozen as '
                                   'the unique intervention reference state; the 4608 '
                                   'protocol therefore lacked a reference-state '
                                   'definition (SCIENTIFIC OBJECT COMPLETENESS GAP). '
                                   'v1.1 removes that ambiguity by symmetry, not by '
                                   'choosing a shore.',
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
    'guards': {
        'forward_count_asserted': EXPECTED_FWD,
        'patches_equal_forwards': PATCHES == FWD,
        'U_prod_U_ref_conformance': 'PASS on every render (checked per (dir,arm,sign))',
        'logits_max_abs': cmax,
        'logits_consumed_by_behavior_read': False,
    },
    'CAUSAL_CONFIRM_opened': True,
    'opening_index': 'v1.1 (v1 forward-count-failed before endpoint evaluation)',
    'next': 'S10 STOP — 不进 retention / delay / interference / transplantation',
    'frozen_sentences': [
        'U(p_A) and U(p_B) are two coordinates of one ruler reading, not two model '
        'executions.',
        'The missing dimension was not the proposal; it was the shore from which the '
        'intervention began.',
        'Do not let a correct accidental count certify an incompletely specified '
        'experiment.',
        'A failed gate does not become a pass because we later discover why the count '
        'was larger.',
        'Perturb both shores; average the causal slope, do not choose a shore after '
        'seeing the water.',
    ],
}
doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
doc = _pyclean(doc)

safe_dump(OUT_LED, {'kind': 'DHE_12F_PER_ITEM_v1.1', 'date': '2026-09-24',
                    'n_items': len(per_item), 'per_item': per_item,
                    'CONTENT_HASH': jcs(per_item)})
safe_dump(OUT, doc)
safe_dump(OUT_SIDE, {'kind': 'DHE_12F_CAUSAL_CONFIRM_v1.1_SIDECAR', 'file': OUT,
                     'artifact_file_sha256': sha256_file(OUT),
                     'CONTENT_HASH': doc['CONTENT_HASH']})

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
    print('    %-46s %10d B  %s' % (os.path.basename(p), os.path.getsize(p),
                                    sha256_file(p)[:16]))
