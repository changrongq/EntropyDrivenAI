# -*- coding: utf-8 -*-
"""_dhe_12f_v1_1_reporting_semantics_correction.py

凌翼 §8 REPORTING SEMANTICS CORRECTION (12F-v1.1).

问题字段:
    logits_consumed_by_behavior_read = false

语义不准确原因:
    12F 的 scientific endpoint U(p) 本身就是从 raw code logits 计算出来的。
    所以模型 logits **确实被实验代码消费了** —— 只不过消费方式被预注册为
    "registered endpoint", 而不是 "choice read"。

拆成 5 个互不重叠的字段:
    logits_consumed_for_registered_endpoint = TRUE
    forbidden_choice_read                   = FALSE
    argmax_read                             = FALSE
    accuracy_read                           = FALSE
    unregistered_behavior_read              = FALSE

性质: REPORTING SEMANTICS CORRECTION
      - 不影响结果
      - 不需要重跑
      - 不修改已 seal 的 DHE_12F_CAUSAL_CONFIRM.v1.1.json
      - 只追加一份 correction artifact, 由 supersedes 字段指向原字段
"""
import sys, os, json, hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.abspath(__file__)))
RD = 'reports'

TARGET = f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1.1.json'
OUT = f'{RD}/DHE_12F_REPORTING_SEMANTICS_CORRECTION.json'


def jcs(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, default=str)
                          .encode('utf-8')).hexdigest()


def _pyclean(o):
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


def safe_dump(path, obj):
    txt = json.dumps(obj, indent=2, ensure_ascii=False)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    return txt


with open(TARGET, encoding='utf-8') as f:
    conf = json.load(f)

old_field = conf['guards']['logits_consumed_by_behavior_read']
old_hash = conf['CONTENT_HASH']

print('=' * 76)
print('  12F-v1.1 REPORTING SEMANTICS CORRECTION (凌翼 §8)')
print('=' * 76)
print()
print(f'    target artifact      : {TARGET}')
print(f'    target CONTENT_HASH  : {old_hash[:16]}')
print(f'    legacy field         : logits_consumed_by_behavior_read = {old_field}')
print(f'    legacy field verdict : SEMANTICALLY INCORRECT (not false as an outcome,')
print(f'                           but false as a description of what happened)')
print()

doc = {
    'kind': 'DHE_12F_REPORTING_SEMANTICS_CORRECTION',
    'date': '2026-09-24',
    'authority': '凌翼 §8 REPORTING SEMANTICS CORRECTION',
    'classification': 'REPORTING SEMANTICS CORRECTION',
    'affects_scientific_result': False,
    'requires_rerun': False,
    'target': {
        'artifact': TARGET,
        'CONTENT_HASH': old_hash,
        'artifact_untouched': True,
        'rule': 'a sealed artifact is not retro-edited; the correction supersedes '
                'the field by reference',
    },
    'superseded_field': {
        'path': 'guards.logits_consumed_by_behavior_read',
        'value_as_sealed': old_field,
        'verdict': 'SEMANTICALLY INCORRECT',
        'why': 'The 12F scientific endpoint U(p) is itself computed from the raw A/B/C/D '
               'code logits. Therefore the model logits WERE consumed by the experimental '
               'code. The old field conflated "logits consumed at all" with "logits '
               'consumed as an unregistered behavior choice", which is a different and '
               'false claim.',
    },
    'replacement_fields': {
        'logits_consumed_for_registered_endpoint': True,
        'forbidden_choice_read': False,
        'argmax_read': False,
        'accuracy_read': False,
        'unregistered_behavior_read': False,
    },
    'replacement_semantics': {
        'logits_consumed_for_registered_endpoint': 'TRUE — U(p) is a deterministic '
            'function of the four pre-registered code-position logits at t_dec.',
        'forbidden_choice_read': 'FALSE — no A/B/C/D choice was ever read; p_A/p_B are '
            'truth-side roles, not model selections.',
        'argmax_read': 'FALSE — no argmax over logits was taken anywhere in 12F.',
        'accuracy_read': 'FALSE — no accuracy-like quantity is defined in this lineage.',
        'unregistered_behavior_read': 'FALSE — the endpoint was sealed before the '
            'confirmation run; nothing outside it was read.',
    },
    'retraction_notice': {
        'must_not_write_further': 'logits consumed = false',
        'must_write': 'logits_consumed_for_registered_endpoint = TRUE ; '
                      'forbidden_choice_read / argmax_read / accuracy_read / '
                      'unregistered_behavior_read = FALSE',
        'reason': 'Otherwise later provenance audits will read "logits not consumed" '
                  'and infer the model was never queried, which is false.',
    },
    'wording_rules_frozen': {
        'allowed': 'PRESPECIFIED AGGREGATE CONTEXT-DERIVED CAUSAL CONTRAST = POSITIVE '
                   '(positive net contrast after prespecified symmetric averaging)',
        'deferred': 'CAUSAL TRACE DEMONSTRATED',
        'deferral_reason': 'effect is very close to 0; median item is negative; '
                           '23/48 items positive; two shores strongly opposite-signed; '
                           'signed alternative negative. These facts show that '
                           '"a stable shared causal trace" claims strictly more than '
                           'the primary sign gate actually verified.',
        'frozen_sentence': 'A gate determines the registered decision; it does not '
                           'automatically license every stronger English sentence.',
        'required_conjunction': [
            'C_raw = +0.0006236256 => H_raw PASS',
            'fraction_positive = 0.479 (23/48) — magnitude-level fragility',
            'armA = -0.0167793954 / armB = +0.0180266466 — shores are opposite-signed',
        ],
        'citation_unit_rule': 'Any citation of C_raw = +0.0006236256 that omits '
                              'fraction_positive = 0.479 and the two-shore opposite '
                              'signs is an overstatement. The three numbers form ONE '
                              'inseparable citation unit.',
        'forbidden_phrasings': [
            'memory causal effect demonstrated',
            'raw design worked',
            'the causal effect was robust across episode states',
            'the same direction worked from both shores',
            'the effect generalized across A/B conditioning',
            'positive effect on each constituent shore',
            'most episodes showed a same-direction causal shift',
            'no memory', 'memory absent', 'digital hippocampus absent',
        ],
    },
    'open_question_elevated': {
        'question': 'Why does the same raw direction yield a negative causal slope from '
                    'the E_A shore and a positive causal slope from the E_B shore?',
        'values': {'armA_raw': -0.0167793954, 'armB_raw': 0.0180266466,
                   'net_after_symmetrization': 0.0006236256},
        'note': 'This -0.01678 vs +0.01803 is more informative than +0.000624 itself.',
        'candidate_readings': [
            'a genuine context-dependent intervention effect '
            '(injecting d_M pushes state away from A under E_A and toward A under E_B)',
            'OR an overshoot artifact — lambda = 1.1402872562408447 may be too large at '
            'this site/context, so what we measure is the rebound',
        ],
        'adjudication': 'NOT adjudicated in this window; this is the next-round design '
                        'question, not a result.',
    },
    'standing_rule_added': {
        'id': 'REFERENCE_STATE_SELF_DECLARATION',
        'rule': 'Any Δ / C / contrast must self-declare its reference state.',
        'reason': '12E\'s trace was already z_A - z_B; going into causal confirmation we '
                  'must not silently pick one shore as the baseline. A difference must '
                  'state what it is relative to.',
        'same_disease_as': 'the a0 cell (missing coordinate system). This cell was '
                           '(missing reference state).',
    },
    'history_preserved': {
        '12F_v1': 'FAILED PRE-RESULT PROTOCOL EXECUTION — must NOT be relabeled '
                  '"preliminary run"',
        '12F_v1_1': 'result-bearing run',
        'artifact': f'{RD}/DHE_12F_CAUSAL_CONFIRM.v1_FORWARD_COUNT_FAIL.json',
    },
    'frozen_sentences': [
        'The raw gate passed; the raw effect is not robust across shores.',
        'A cleaner geometric direction failed its causal test.',
        'Do not confuse a positive average with uniformly positive constituents.',
        'Symmetrization saved us from choosing which shore\'s sign to believe.',
        'A gate determines the registered decision; it does not automatically license '
        'every stronger English sentence.',
        'A difference that does not declare its reference state is not a contrast — '
        'it is two numbers talking separately.',
    ],
}
doc['CONTENT_HASH'] = jcs({k: v for k, v in doc.items() if k != 'CONTENT_HASH'})
doc = _pyclean(doc)
safe_dump(OUT, doc)
safe_dump(OUT + '.sidecar.json',
          {'kind': 'DHE_12F_REPORTING_SEMANTICS_CORRECTION_SIDECAR',
           'file': OUT,
           'artifact_file_sha256': hashlib.sha256(open(OUT, 'rb').read()).hexdigest(),
           'CONTENT_HASH': doc['CONTENT_HASH']})

print('--- replacement fields ---')
for k, v in doc['replacement_fields'].items():
    print(f'    {k:<44} = {v}')
print()
print('=' * 76)
print('  CORRECTION SEALED — sealed artifact untouched, no rerun')
print('=' * 76)
print()
print(f'    CONTENT_HASH = {doc["CONTENT_HASH"][:16]}')
print(f'    file size    = {os.path.getsize(OUT)} B')
print()
print(f'    target CONTENT_HASH unchanged = '
      f'{json.load(open(TARGET, encoding="utf-8"))["CONTENT_HASH"][:16]}')
