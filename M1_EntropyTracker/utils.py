import torch
import numpy as np

def softmax(logits):
    """
    通用softmax函数，用于probs计算（备用）
    参数:
        logits (np.ndarray or torch.Tensor): 输入logits
    返回:
        probs (np.ndarray): 概率分布
    """
    if isinstance(logits, torch.Tensor):
        return torch.softmax(logits, dim=-1).cpu().numpy()
    else:
        logits = np.array(logits)
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / exp_logits.sum()

def visualize_heatmap(data, title="Heatmap"):
    """
    通用热图可视化（未来扩展激活追踪）
    参数:
        data (2D np.ndarray): 数据矩阵
        title (str): 图标题
    """
    import matplotlib.pyplot as plt
    plt.imshow(data, cmap='viridis')
    plt.title(title)
    plt.colorbar()
    plt.show()