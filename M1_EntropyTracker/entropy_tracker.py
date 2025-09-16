import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import matplotlib.pyplot as plt

def compute_token_entropy(token_probs):
    """
    计算给定token概率分布的熵值
    参数:
        token_probs (List[float] or np.ndarray): 每个token的预测概率
    返回:
        entropy (float): 信息熵（nats）
    """
    token_probs = np.array(token_probs)  # 确保为numpy数组
    token_probs = np.clip(token_probs, 1e-12, 1.0)
    entropy = -np.sum(token_probs * np.log(token_probs))
    return entropy

def track_entropy_over_dialogue(dialogue):
    """
    追踪多轮对话的熵变化，使用GPT-2计算每轮utterance的最后一个token的probs熵。
    参数:
        dialogue (List[str]): 多轮对话列表
    返回:
        entropy_trace (List[tuple]): [(turn_index, utterance, entropy)]
    """
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2", output_attentions=True)
    model.eval()

    entropy_trace = []

    for i, utterance in enumerate(dialogue):
        inputs = tokenizer(utterance, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0]  # [seq_len - 1, vocab_size] (忽略第一个token的预测)
            probs = torch.softmax(logits[-1], dim=-1).numpy()  # 最后一个token的probs
            entropy = compute_token_entropy(probs)
            entropy_trace.append((i, utterance, entropy))

    return entropy_trace

def plot_entropy(entropy_trace):
    """
    可视化熵趋势图谱
    参数:
        entropy_trace (List[tuple]): 从track_entropy_over_dialogue获取
    """
    rounds = [e[0] for e in entropy_trace]
    entropies = [e[2] for e in entropy_trace]
    plt.plot(rounds, entropies, marker='o', linestyle='-', color='blue')
    plt.title("Entropy Trace Across Dialogue")
    plt.xlabel("Dialogue Turn")
    plt.ylabel("Entropy (nats)")
    plt.grid(True)
    plt.savefig('entropy_trace.png')  # 保存为文件，便于集成
    plt.close()  # 关闭以防REPL显示问题
    print("Entropy plot saved as 'entropy_trace.png'.")

# 示例使用（if __name__ == "__main__" 可用于测试）
if __name__ == "__main__":
    dialogue = [
        "你好，今天的天气如何？",
        "今天天气晴朗，气温适宜。",
        "你知道宇宙膨胀的速度吗？",
        "让我查查哈勃常数的最新估计……"
    ]
    trace = track_entropy_over_dialogue(dialogue)
    print("Entropy Trace:", trace)
    plot_entropy(trace)