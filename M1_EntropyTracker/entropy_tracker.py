import numpy as np
import json
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

class EntropyTracker:
    """信息熵追踪模块，计算对话中token分布熵，输出entropy_trace.json"""
    
    def __init__(self, config_dict):
        """
        初始化
        参数:
            config_dict (dict): 配置，例如{'model_name': 'gpt2', 'output_file': 'entropy_trace.json'}
        """
        self.model_name = config_dict.get('model_name', 'gpt2')
        self.output_file = config_dict.get('output_file', 'entropy_trace.json')
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name, output_attentions=True)
        self.model.eval()

    def compute_token_entropy(self, token_probs):
        """
        计算token概率分布的熵值
        参数:
            token_probs (np.ndarray): 预测概率
        返回:
            float: 熵值（nats）
        """
        token_probs = np.clip(token_probs, 1e-12, 1.0)
        entropy = -np.sum(token_probs * np.log(token_probs))
        return entropy

    def track_entropy(self, dialogue):
        """
        追踪多轮对话熵
        参数:
            dialogue (List[str]): 对话列表
        返回:
            List[dict]: entropy_trace格式
        """
        entropy_trace = []
        for i, utterance in enumerate(dialogue):
            inputs = self.tokenizer(utterance, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[0]
                probs = torch.softmax(logits[-1], dim=-1).numpy()
                entropy = self.compute_token_entropy(probs)
                entropy_trace.append({
                    'turn': i,
                    'utterance': utterance,
                    'entropy': float(entropy)  # JSON序列化要求float
                })
        
        # 写入entropy_trace.json
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(entropy_trace, f, ensure_ascii=False, indent=2)
        
        return entropy_trace

# 示例调用
if __name__ == "__main__":
    config = {'model_name': 'gpt2', 'output_file': 'entropy_trace.json'}
    tracker = EntropyTracker(config)
    dialogue = [
        "你好，我想问...",
        "这是个好问题..."
    ]
    trace = tracker.track_entropy(dialogue)
    print("Entropy Trace:", trace)