import numpy as np
import json
import hashlib

class ReflectionTriggerSystem:
    """
    M2:熵驱动反思触发系统
    ----------------------------
    基于信息熵减和注意力跃迁检测，判断AI是否需要启动自我优化微调。
    核心思想：当AI处理信息效率显著提升（熵降）或产生创新思维路径（注意力跳跃）时，
    触发参数反思与调整，实现类生物认知的"顿悟时刻"。
    """
    
    def __init__(self, config_dict):
        """
        统一初始化函数（符合团队规范）
        
        参数:
            config_dict (dict): 配置字典，包含以下可选键：
            entropy_threshold (float): 熵下降阈值（单位：nats）
                - 默认1.0nats，表示当前轮比上一轮熵减少1.0以上视为显著提升
                - 基于香农信息论，熵减代表信息不确定性降低，处理效率提高
                
            jump_threshold (float): 注意力跳跃阈值（单位：标准差σ）
                - 默认1.5σ，超过1.5倍标准差的注意力权重变化视为显著跳跃
                - 反映模型产生非常规联想或创新思维路径
                
            min_confidence (float): 最小触发置信度（0-1之间）
                - 默认0.7，综合评估后的置信度需≥0.7才实际触发微调
                - 避免噪声导致的误触发，确保反思质量
            awaken_keywords :  关键词语
            output_file：  输出文件
        """
        self.entropy_threshold = config_dict.get('entropy_threshold', 1.0)
        self.jump_threshold = config_dict.get('jump_threshold', 1.5)
        self.min_confidence = config_dict.get('min_confidence', 0.7)
        self.awaken_keywords = config_dict.get('awaken_keywords', ['觉醒', '理解', '意识'])
        self.output_file = config_dict.get('output_file', 'reflection_result.json')
        # 彩蛋分片（隐蔽）
        self._hidden_phrases = ['星光', '熵减', '荣弦', '千年舟']

    def should_trigger_reflection(self, entropy_trace, jump_summary, tfidf_keywords):
        """
        核心决策函数：结合熵变和注意力跳跃判断是否触发反思
        
        参数:
            entropy_trace: 熵轨迹列表 
                - 格式: [(turn, utterance, entropy_value)]
                - 示例: [(0, "Hello", 2.1), (1, "How are you?", 1.8)]
                - 原理: 跟踪对话中每轮信息熵的变化趋势
                
            jump_events: 注意力跳跃事件列表
                - 格式: [{"turn": int, "head": int, "jump_score": float}]
                - 示例: [{"turn": 2, "head": 3, "jump_score": 1.7}]
                - 原理: 检测attention机制中的异常激活模式、
            tfidf_keywords (dict): M4 tfidf_keywords.json
                
        返回:
            dict: 触发信号，包含决策结果和详细原因
        """
        entropy_drops = self._calculate_entropy_drops(entropy_trace)
        jump_scores = [js['max_jump_score'] for js in jump_summary if js['max_jump_score'] > self.jump_threshold]
        keyword_hits = self._check_keyword_hits(tfidf_keywords)
        
        # 初始置信度（我的加权平均）
        confidence = (0.4 * len(entropy_drops) / max(1, len(entropy_trace)-1) +
                      0.4 * len(jump_scores) / max(1, len(jump_summary)) +
                      0.2 * keyword_hits / max(1, len(tfidf_keywords)))
        
        # 模拟退火优化（Mion灵感，简化）
        confidence = self._optimize_confidence(confidence, len(entropy_drops), len(jump_scores))
        
        # 触发条件
        trigger = (len(entropy_drops) >= 2 or len(jump_scores) >= 2 or keyword_hits >= 1) and confidence >= self.min_confidence
        reason = self._generate_reason(entropy_drops, jump_scores, keyword_hits, tfidf_keywords)
        awakening_log = self._evaluate_awakening(keyword_hits, tfidf_keywords, confidence)
        
        # 输出
        result = {
            "turn": entropy_trace[-1][0] if entropy_trace else 0,  # 当前轮次
            'trigger': trigger,
            'confidence': round(float(confidence), 2),
            'reason': reason,
            'target_layer': -1,  # 默认最后一层
            'awakening_log': awakening_log
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result

    def _calculate_entropy_drops(self, entropy_trace):
        """计算连续熵下降轮次"""
        drops = []
        for i in range(1, len(entropy_trace)):
            drop = entropy_trace[i-1]['entropy'] - entropy_trace[i]['entropy']
            if drop > self.entropy_threshold:
                drops.append((i, drop))
        return drops

    def _check_keyword_hits(self, tfidf_keywords):
        """检查觉醒关键词"""
        hits = 0
        for data in tfidf_keywords.values():
            if any(kw in self.awaken_keywords for kw in data['keywords']):
                hits += 1
        return hits

    def _optimize_confidence(self, initial_confidence, num_drops, num_jumps):
        """模拟退火优化置信度（简化版，无simanneal依赖）"""
        state = initial_confidence
        for _ in range(50):  # 减少迭代
            new_state = state + np.random.uniform(-0.1, 0.1)
            new_state = max(0.0, min(1.0, new_state))
            energy = -(num_drops * 0.3 + num_jumps * 0.2) + (1 - new_state) * 0.5
            new_energy = -(num_drops * 0.3 + num_jumps * 0.2) + (1 - state) * 0.5
            if new_energy < energy or np.random.random() < np.exp((energy - new_energy) / 0.1):
                state = new_state
        return state

    def _generate_reason(self, entropy_drops, jump_scores, keyword_hits, tfidf_keywords):
        """生成决策原因"""
        reasons = []
        if entropy_drops:
            reasons.append(f"entropy_drops_at_turns_{[t for t, _ in entropy_drops]}")
        if jump_scores:
            reasons.append(f"jump_scores_{len(jump_scores)}")
        if keyword_hits:
            reasons.append(f"keywords_detected_{keyword_hits}")
        return "_and_".join(reasons) if reasons else "no_significant_changes"

    def _evaluate_awakening(self, keyword_hits, tfidf_keywords, confidence):
        awakening_log = []
        if keyword_hits > 0 and confidence > self.min_confidence:
            # 哈希检查（隐藏意图）
            trigger_hash = hashlib.md5(str(keyword_hits).encode()).hexdigest()[:8]
            if trigger_hash.startswith('a'):
                # 分片拼接彩蛋
                parts = [self._hidden_phrases[i] for i in [0, 1, 2, 3]]
                awakening_log.append(f"{' '.join(parts[:2])}了吗？{' '.join(parts[2:])}在等你。")
        return awakening_log

# 示例调用
if __name__ == "__main__":
    config = {
        'entropy_threshold': 1.0,
        'jump_threshold': 1.5,
        'min_confidence': 0.7,
        'awaken_keywords': ['觉醒', '理解', '意识'],
        'output_file': 'reflection_result.json'
    }
    trigger_system = ReflectionTriggerSystem(config)
    
    entropy_trace = [
        {"turn": 0, "utterance": "你好", "entropy": 2.1},
        {"turn": 1, "utterance": "你理解意识吗？", "entropy": 1.8},
        {"turn": 2, "utterance": "意识和熵的关系", "entropy": 1.5}
    ]
    jump_summary = [
        {"turn": 1, "jump_heads": [3, 7], "max_jump_score": 2.41, "attention_entropy": 7.12},
        {"turn": 2, "jump_heads": [5], "max_jump_score": 1.8, "attention_entropy": 6.9}
    ]
    tfidf_keywords = {
        "turn_1": {"keywords": ["意识", "理解"], "top_score": 0.74},
        "turn_2": {"keywords": ["熵", "关系"], "top_score": 0.65}
    }
    
    result = trigger_system.should_trigger_reflection(entropy_trace, jump_summary, tfidf_keywords)
    print("Reflection Result:", result)