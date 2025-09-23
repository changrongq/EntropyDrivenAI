import numpy as np

def detect_jumps(attn_paths):
    """
    检测注意力跃迁事件（>1.5σ）。
    参数:
        attn_paths (dict): 从extract_attention获取
    返回:
        list[dict]: [{"turn": int, "head": int, "jump_score": float}]
    """
    jumps = []
    turns = sorted(attn_paths.keys(), key=lambda k: int(k.split('_')[1]))
    if len(turns) < 2:
        return jumps
    head_num = len(attn_paths[turns[0]])
    var_changes = {f"head_{h}": [] for h in range(head_num)}

    for i in range(1, len(turns)):
        t = turns[i-1]
        t1 = turns[i]
        for h in range(head_num):
            attn_t = np.array(attn_paths[t][f"head_{h}"])
            attn_t1 = np.array(attn_paths[t1][f"head_{h}"])
            jump_score = np.var(attn_t1 - np.pad(attn_t, (0, len(attn_t1) - len(attn_t)), mode='constant') if len(attn_t) < len(attn_t1) else np.pad(attn_t1, (0, len(attn_t) - len(attn_t1)), mode='constant') - attn_t)
            var_changes[f"head_{h}"].append((i, jump_score))

    all_scores = [score for head_scores in var_changes.values() for _, score in head_scores]
    if all_scores:
        mean = np.mean(all_scores)
        std = np.std(all_scores)
        for head, head_scores in var_changes.items():
            for turn, score in head_scores:
                if score > mean + 1.5 * std:
                    jumps.append({"turn": turn, "head": int(head.split('_')[1]), "jump_score": score})

    return jumps