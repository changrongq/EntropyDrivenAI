import numpy as np

def compute_attention_jump(attn_matrix_t, attn_matrix_t1):
    """
    计算相邻轮次attention分布的方差变化。
    参数:
        attn_matrix_t, attn_matrix_t1 (np.array): attn vectors
    返回:
        float: var(diff)
    """
    max_len = max(len(attn_matrix_t), len(attn_matrix_t1))
    attn_t = np.pad(attn_matrix_t, (0, max_len - len(attn_matrix_t)), mode='constant')
    attn_t1 = np.pad(attn_matrix_t1, (0, max_len - len(attn_matrix_t1)), mode='constant')
    diff = attn_t1 - attn_t
    return np.var(diff)