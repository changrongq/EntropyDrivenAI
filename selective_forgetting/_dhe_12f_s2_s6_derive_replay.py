# -*- coding: utf-8 -*-
"""_dhe_12f_s2_s6_derive_replay.py —— S2-S6: replay TRACE_DERIVE, rebuild raw, build signed

凌翼 §⑬:
  S2 replay TRACE_DERIVE (48 items x 24 perms x 2 arms = 2304 forwards)
  S3 reconstruct raw d_M ; ASSERT hash == f9aae5833055859c481b500a8a54cfdac9b994e59d10f924b81f6369bfc2515a
  S4 construct signed d_M
  S5 seal signed d_M
  S6 STOP / verify both directions frozen

§⑫ 批准: 落盘 48 个 delta_i 作为 audit artifact; 并算 m_g / v_g 代数分解
        (但不允许据这些新数值再改 signed rule — sign manifest 已 seal)

始终: intervention = NONE ; gradient = NONE ; logits consumed = 0 ; behavior read = FALSE
      CAUSAL_CONFIRM model data 不触碰
"""
import sys, os, json, hashlib, gc, time, itertools

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

OUT_RAW = f'{RD}/DHE_12F_S3_RAW_REPRODUCE.json'
OUT_SIGNED = f'{RD}/DHE_12F_S5_SIGNED_D_M.json'
OUT_DELTA = f'{RD}/DHE_12F_DERIVE_DELTAS_AUDIT.json'

RAW_HASH_EXPECTED = 'f9aae5833055859c481b500a8a54cfdac9b994e59d10f924b81f6369bfc2515a'
L_SITE = 23
HID = 4096
N_ITEMS = 48
N_PERMS = 24

FWD = 0
AUTOG = 0
LOGIts = 0
ACT_READS = 0
PATCHES = 0
D2_BEHAV = 0


def jcs(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, default=str)
                          .encode('utf-8')).hexdigest()


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def hard_stop(reason, payload):
    doc = {'kind': 'DHE_12F_DERIVE_REPLAY', 'date': '2026-09-23',
           'verdict': f'HARD_STOP::{reason}', 'detail': payload,
           'counters': {'forward_calls': FWD, 'autograd_calls': AUTOG,
                        'logits_consumed': LOGIts, 'activation_reads': ACT_READS,
                        'patches': PATCHES, 'behavior_read': False}}
    doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
    json.dump(doc, open(OUT_RAW, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print()
    print('=' * 76)
    print(f'  {reason} -> HARD STOP (before CAUSAL_CONFIRM)')
    print('=' * 76)
    print(f'    {payload}')
    sys.exit(2)


print('=' * 76)
print('  S2-S6: DERIVE REPLAY -> raw reproduce -> signed build')
print('=' * 76)
print()

import numpy as np
import torch

replay = json.load(open(REPLAY_ART, encoding='utf-8'))
proj = json.load(open(PROJ, encoding='utf-8'))
split = json.load(open(SPLIT, encoding='utf-8'))
tpl = json.load(open(TPL, encoding='utf-8'))
sgn = json.load(open(SIGN, encoding='utf-8'))
ids = json.load(open(IDS_ART, encoding='utf-8'))

print('--- provenance ---')
print(f'    replay strict_equivalent = {replay.get("strict_equivalent")}')
print(f'    projection hash  = {proj["CONTENT_HASH"][:16]}')
print(f'    split hash       = {split["CONTENT_HASH"][:16]}')
print(f'    template hash    = {tpl["CONTENT_HASH"][:16]}')
print(f'    sign manifest    = {sgn["CONTENT_HASH"][:16]}')
print(f'    code authority   = {ids["CONTENT_HASH"][:16]}')
if not replay.get('strict_equivalent'):
    hard_stop('REPLAY_NOT_QUALIFIED', {})

# sign map: episode_id -> sign
SIGN_MAP = {r['episode_id']: r['sign'] for r in sgn['items']}
assert len(SIGN_MAP) == 96, len(SIGN_MAP)

# TRACE_DERIVE items in sealed order
der_ids = list(split['TRACE_DERIVE']['pair_ids'])
pairs_all = {p['pair_id']: p for p in proj['pairs']}
der_pairs = [pairs_all[pid] for pid in der_ids]
items = [it for p in der_pairs for it in p['items']]
print(f'    TRACE_DERIVE pairs={len(der_pairs)} items={len(items)}')
if len(items) != N_ITEMS:
    hard_stop('ITEM_COUNT_FAIL', {'got': len(items)})
print()

# ── build model (verified replay) ─────────────────────────────────────
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
h_gguf = sha256_file(MODEL_PATH)
if h_gguf != GGUF_SHA_EXPECTED:
    hard_stop('GGUF_SHA_MISMATCH', {})
lay = model.model.layers
gate_l = (type(model).__name__ == 'MistralForCausalLM'
          and model.config.model_type == 'mistral'
          and type(lay[L_SITE]).__name__ == 'MistralDecoderLayer'
          and len(seen) == len(EXPECTED))
print(f'    loaded {len(seen)}/{len(EXPECTED)} ; GATE_L = {gate_l} ; forward before = {FWD}')
if not gate_l:
    hard_stop('GATE_L_FAIL', {})
tok = AutoTokenizer.from_pretrained(MODEL_DIR, gguf_file=GGUF_FILE)
print()

TOKEN_A = ids['codes']['A']
TOKEN_B = ids['codes']['B']
E_TPL = tpl['E_template']
F_TPL = tpl['F_template']
PERMS = [list(p) for p in itertools.permutations([0, 1, 2, 3])]
assert len(PERMS) == N_PERMS
block_places = proj['block_place_universe']

CAP = {}


def hk(module, args, output):
    CAP['h'] = output[0] if isinstance(output, tuple) else output
    return None


hh = lay[L_SITE].register_forward_hook(hk)

# ═══════════════════════════════════════════════════════════════════════
# S2 replay
# ═══════════════════════════════════════════════════════════════════════
print('=' * 76)
print(f'  S2 replay TRACE_DERIVE : {len(items)} items x 24 perms x 2 arms')
print('=' * 76)
print()

delta = {}
t0 = time.time()
for ii, it in enumerate(items):
    role, pA, pB = it['role_id'], it['p_A'], it['p_B']
    cands = list(block_places[it['block_id']])
    EA = E_TPL.format(role=role, place=pA)
    EB = E_TPL.format(role=role, place=pB)
    zA = np.zeros(HID, dtype=np.float64)
    zB = np.zeros(HID, dtype=np.float64)
    for perm in PERMS:
        c = [cands[k] for k in perm]
        F = F_TPL.format(role=role, p0=c[0], p1=c[1], p2=c[2], p3=c[3])
        for arm, ET in (('A', EA), ('B', EB)):
            enc = tok(ET + F, return_tensors='pt')
            ids_t = enc['input_ids'].to('cuda')
            at = enc['attention_mask'].to('cuda')
            t_dec = int(ids_t.shape[1]) - 1
            CAP.clear()
            with torch.no_grad():
                out = model(input_ids=ids_t, attention_mask=at, use_cache=False,
                            return_dict=True)
            FWD += 1
            h = CAP.get('h')
            if h is None:
                hard_stop('HOOK_NO_CAPTURE', {'item': ii, 'arm': arm})
            hv = h[0, t_dec, :]
            ACT_READS += 1
            hf = hv.detach().to('cpu', torch.float64).numpy()
            if not np.isfinite(hf).all():
                hard_stop('NONFINITE_ACTIVATION', {'item': ii})
            if arm == 'A':
                zA += hf
            else:
                zB += hf
            del out, hv, hf
    delta[it['episode_id']] = (zA / 24.0) - (zB / 24.0)
    if (ii + 1) % 8 == 0:
        print(f'    ... {ii+1}/{len(items)} items ; fwd={FWD} ({time.time()-t0:.1f}s)')

hh.remove()
print(f'    replay done ; forwards = {FWD} ; {time.time()-t0:.1f}s')
print()

# ═══════════════════════════════════════════════════════════════════════
# S3 reconstruct raw + ASSERT hash
# ═══════════════════════════════════════════════════════════════════════
print('--- S3 reconstruct raw d_M ---')
ordered = [delta[it['episode_id']] for it in items]
mean64 = np.mean(np.stack(ordered, axis=0), axis=0)
n64 = float(np.linalg.norm(mean64))
d64 = mean64 / n64
d32a = d64.astype(np.float32)
n32 = float(np.linalg.norm(d32a.astype(np.float64)))
raw32 = (d32a.astype(np.float64) / n32).astype(np.float32)
raw_hash = hashlib.sha256(raw32.tobytes()).hexdigest()
print(f'    ||mean_delta|| = {n64:.10f}')
print(f'    raw d_M sha256 = {raw_hash}')
print(f'    expected       = {RAW_HASH_EXPECTED}')
RAW_OK = (raw_hash == RAW_HASH_EXPECTED)
print(f'    ⇒ raw hash reproduces : {RAW_OK}')
if not RAW_OK:
    hard_stop('RAW_HASH_NOT_REPRODUCED',
              {'recomputed': raw_hash, 'expected': RAW_HASH_EXPECTED,
               'rule': 'S3 raw hash must reproduce f9aae583… else HARD STOP before '
                       'confirmation'})
print()

# ═══════════════════════════════════════════════════════════════════════
# S4 construct signed
# ═══════════════════════════════════════════════════════════════════════
print('--- S4 construct signed d_M (sign from sealed material manifest) ---')
signed_terms = []
for it in items:
    s = SIGN_MAP[it['episode_id']]
    signed_terms.append(s * delta[it['episode_id']])
smean64 = np.mean(np.stack(signed_terms, axis=0), axis=0)
sn64 = float(np.linalg.norm(smean64))
if not np.isfinite(sn64) or sn64 == 0.0:
    hard_stop('SIGNED_ZERO_OR_NONFINITE_NORM', {'norm': sn64})
sd64 = smean64 / sn64
sd32a = sd64.astype(np.float32)
sn32 = float(np.linalg.norm(sd32a.astype(np.float64)))
signed32 = (sd32a.astype(np.float64) / sn32).astype(np.float32)
signed_hash = hashlib.sha256(signed32.tobytes()).hexdigest()
print(f'    ||signed mean|| = {sn64:.10f}')
print(f'    raw    ||mean|| = {n64:.10f}')
print(f'    ratio signed/raw = {sn64/n64:.6f}')
print(f'    signed d_M sha256 = {signed_hash}')
print()

# ── §⑫ m_g / v_g algebraic decomposition (report only) ────────────────
pair_deltas = {}
for p in der_pairs:
    pair_deltas[p['pair_id']] = [delta[it['episode_id']] for it in p['items']]
mg_list, vg_list = [], []
for pid, ds in pair_deltas.items():
    mg_list.append(0.5 * (ds[0] + ds[1]))
    vg_list.append(0.5 * (ds[0] - ds[1]))
mg_norms = np.array([np.linalg.norm(x) for x in mg_list])
vg_norms = np.array([np.linalg.norm(x) for x in vg_list])
print('--- §⑫ m_g / v_g algebraic decomposition (report only; no rule change) ---')
print(f'    mean||m_g|| = {mg_norms.mean():.6f}   mean||v_g|| = {vg_norms.mean():.6f}')
print(f'    energy notion NOT claimed as identified fraction (per §②)')
print()

# ── seal deltas audit artifact ────────────────────────────────────────
deltas_arr = np.stack(ordered, axis=0).astype(np.float32)
np.save(f'{RD}/_dhe_12f_derive_deltas.npy', deltas_arr)
print(f'    deltas saved: shape {list(deltas_arr.shape)}')

np.save(f'{RD}/_dhe_12f_raw_dm.npy', raw32)
np.save(f'{RD}/_dhe_12f_signed_dm.npy', signed32)

raw_doc = {
    'kind': 'DHE_12F_S3_RAW_REPRODUCE', 'date': '2026-09-23',
    'authority': '凌翼 §⑬ S3',
    'recomputed_raw_hash': raw_hash, 'expected_raw_hash': RAW_HASH_EXPECTED,
    'reproduced': RAW_OK, 'mean_delta_norm': n64,
    'forward_calls': FWD, 'autograd_calls': AUTOG, 'logits_consumed': LOGIts,
    'activation_reads': ACT_READS, 'intervention': 'NONE', 'gradient': 'NONE',
    'CAUSAL_CONFIRM_touched': False,
}
raw_doc['CONTENT_HASH'] = jcs({k: v for k, v in raw_doc.items()
                               if k != 'CONTENT_HASH'})
json.dump(raw_doc, open(OUT_RAW, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

signed_doc = {
    'kind': 'DHE_12F_S5_SIGNED_D_M', 'date': '2026-09-23',
    'authority': '凌翼 §⑬ S4/S5 + §⑤ (derive-informed, prospectively frozen)',
    'artifact_role': 'DERIVE-INFORMED, PROSPECTIVELY FROZEN ALTERNATIVE ESTIMATOR',
    'sign_manifest_hash': sgn['CONTENT_HASH'],
    'sign_function_sha256': sgn['sign_function_sha256'],
    'sign_rule': sgn['rule'],
    'signed_d_M': {'shape': [HID], 'dtype': 'float32', 'norm': float(np.linalg.norm(signed32.astype(np.float64))),
                   'sha256': signed_hash, 'mean_norm_f64': sn64},
    'raw_d_M_for_comparison': {'sha256': raw_hash, 'mean_norm_f64': n64},
    'ratio_signed_over_raw': sn64 / n64,
    'npy_file': '_dhe_12f_signed_dm.npy',
    'raw_npy_file': '_dhe_12f_raw_dm.npy',
    'deltas_audit_file': '_dhe_12f_derive_deltas.npy',
    'algebraic_decomposition_reported': {
        'mean_norm_m_g': float(mg_norms.mean()),
        'mean_norm_v_g': float(vg_norms.mean()),
        'note': 'algebraic decomposition for geometry report only; energy fraction NOT '
                'identified (§②); no rule change permitted after seal'},
    'historical_identity': 'signed estimator is DERIVE-INFORMED (motivated after R_g<0); '
                           'NOT a rewrite of v0.1 raw primary',
    'counters': {'forward_calls': FWD, 'autograd_calls': AUTOG,
                 'logits_consumed': LOGIts, 'activation_reads': ACT_READS,
                 'patches': PATCHES, 'behavior_read': False},
    'CAUSAL_CONFIRM_touched': False,
    'frozen_sentences': [
        'S3 raw hash must reproduce f9aae583…',
        'function frozen before activations reappear',
    ],
}
signed_doc['CONTENT_HASH'] = jcs({k: v for k, v in signed_doc.items()
                                  if k != 'CONTENT_HASH'})
json.dump(signed_doc, open(OUT_SIGNED, 'w', encoding='utf-8'), indent=2,
          ensure_ascii=False)

json.dump({'kind': 'DHE_12F_DERIVE_DELTAS_AUDIT', 'date': '2026-09-23',
           'n_items': len(items), 'shape': list(deltas_arr.shape),
           'dtype': 'float32', 'npy_file': '_dhe_12f_derive_deltas.npy',
           'order': [it['episode_id'] for it in items],
           'sign_manifest_hash': sgn['CONTENT_HASH'],
           'role': 'audit artifact; no re-tuning permitted',
           'CONTENT_HASH': jcs({'n': len(items), 'h': hashlib.sha256(
               deltas_arr.tobytes()).hexdigest()})},
          open(OUT_DELTA, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

print()
print('=' * 76)
print('  S6: BOTH DIRECTIONS FROZEN — verify before CAUSAL_CONFIRM')
print('=' * 76)
print()
print(f'    raw    d_M : {raw_hash[:32]}…  (reproduced = {RAW_OK})')
print(f'    signed d_M : {signed_hash[:32]}…')
print(f'    ratio ||signed||/||raw|| = {sn64/n64:.6f}')
print()
print(f'    forward_calls = {FWD} (expect 2304) ; autograd = {AUTOG}')
print(f'    logits_consumed = {LOGIts} ; patches = {PATCHES}')
print(f'    behavior_read = FALSE ; CAUSAL_CONFIRM touched = FALSE')
print()
print('--- 产物 ---')
for p in [OUT_RAW, OUT_SIGNED, OUT_DELTA, f'{RD}/_dhe_12f_derive_deltas.npy',
          f'{RD}/_dhe_12f_raw_dm.npy', f'{RD}/_dhe_12f_signed_dm.npy']:
    print('    %-44s %10d B  %s' % (os.path.basename(p), os.path.getsize(p),
                                    sha256_file(p)[:16]))
