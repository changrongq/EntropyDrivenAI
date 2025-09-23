import torch
import numpy as np
import json
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from sklearn.feature_extraction.text import TfidfVectorizer
from m4_thought_tracker.variance_analyzer import compute_attention_jump

class MemoryTracker:
    """跨轮对话记忆映射追踪，输出raw/summary attention_paths和TF-IDF关键词"""
    
    def __init__(self, config_dict):
        """
        初始化
        参数:
            config_dict (dict): {'model_name': 'gpt2', 'output_paths_raw': 'long_term_attention_paths_raw.json', 
                                'output_paths_summary': 'long_term_attention_summary.json', 
                                'output_matrix_file': 'attention_jump_matrix.npy', 'top_k': 3}
        """
        self.model_name = config_dict.get('model_name', 'gpt2')
        self.output_paths_raw = config_dict.get('output_paths_raw', 'long_term_attention_paths_raw.json')
        self.output_paths_summary = config_dict.get('output_paths_summary', 'long_term_attention_summary.json')
        self.output_matrix_file = config_dict.get('output_matrix_file', 'attention_jump_matrix.npy')
        self.top_k = config_dict.get('top_k', 3)
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name, output_attentions=True)
        self.model.eval()

    def track_memory_paths(self, dialogue):
        """
        追踪attention路径、token共现、TF-IDF关键词
        返回:
            dict: {'long_term_attention_paths', 'attention_jump_matrix', 'token_keyframe_map', 'tfidf_keywords'}
        """
        long_term_paths = {}
        paths_summary = []
        token_counts = {}
        jump_matrix = []
        num_heads = 12

        # TF-IDF初始化
        vectorizer = TfidfVectorizer(tokenizer=lambda x: self.tokenizer.tokenize(x), max_features=self.top_k)
        tfidf_matrix = vectorizer.fit_transform(dialogue)
        feature_names = vectorizer.get_feature_names_out()
        
        for i, utterance in enumerate(dialogue):
            inputs = self.tokenizer(utterance, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
                last_layer_attn = outputs.attentions[-1][0]
                last_token_attn = last_layer_attn[:, -1, :]
                
                # Raw paths
                long_term_paths[f"turn_{i}"] = {f"head_{h}": last_token_attn[h].numpy().tolist() for h in range(num_heads)}
                
                # Summary: 提取跳跃head
                if i > 0:
                    prev_attn = np.array([long_term_paths[f"turn_{i-1}"][f"head_{h}"] for h in range(num_heads)])
                    curr_attn = last_token_attn.numpy()
                    jumps = [compute_attention_jump(prev_attn[h], curr_attn[h]) for h in range(num_heads)]
                    jump_matrix.append(jumps)
                    mean_jump = np.mean(jumps)
                    std_jump = np.std(jumps)
                    jump_heads = [h for h, j in enumerate(jumps) if j > mean_jump + 1.5 * std_jump]
                    attn_entropy = -np.sum(last_token_attn.numpy() * np.log(last_token_attn.numpy() + 1e-12), axis=1).mean()
                    paths_summary.append({
                        'turn': i,
                        'jump_heads': jump_heads,
                        'max_jump_score': float(max(jumps)) if jumps else 0.0,
                        'attention_entropy': float(attn_entropy)
                    })
                else:
                    jump_matrix.append([0.0] * num_heads)
                    paths_summary.append({
                        'turn': i,
                        'jump_heads': [],
                        'max_jump_score': 0.0,
                        'attention_entropy': 0.0
                    })

                # Token共现
                tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
                for token in tokens:
                    token_counts[token] = token_counts.get(token, 0) + 1

            # TF-IDF关键词
            tfidf_scores = tfidf_matrix[i].toarray()[0]
            top_indices = tfidf_scores.argsort()[-self.top_k:][::-1]
            tfidf_keywords = {f"turn_{i}": {
                'keywords': [feature_names[idx] for idx in top_indices],
                'top_score': float(tfidf_scores[top_indices[0]])
            }}

        # 保存输出
        np.save(self.output_matrix_file, np.array(jump_matrix))
        with open(self.output_paths_raw, 'w', encoding='utf-8') as f:
            json.dump(long_term_paths, f, ensure_ascii=False, indent=2)
        with open(self.output_paths_summary, 'w', encoding='utf-8') as f:
            json.dump(paths_summary, f, ensure_ascii=False, indent=2)
        with open('token_keyframe_map.json', 'w', encoding='utf-8') as f:
            json.dump({token: count for token, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True)[:self.top_k]}, f, ensure_ascii=False, indent=2)
        with open('tfidf_keywords.json', 'w', encoding='utf-8') as f:
            json.dump(tfidf_keywords, f, ensure_ascii=False, indent=2)

        return {
            'long_term_attention_paths': long_term_paths,
            'attention_jump_matrix': np.array(jump_matrix),
            'token_keyframe_map': token_counts,
            'tfidf_keywords': tfidf_keywords
        }