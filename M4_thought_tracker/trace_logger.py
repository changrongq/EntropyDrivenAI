import json
from m4_thought_tracker.jump_detector import detect_jumps
from m1_entropy_tracker.entropy_tracker import EntropyTracker

class TraceLogger:
    """生成trace.json，整合M1熵和M4跃迁，供M6使用"""
    
    def __init__(self, config_dict):
        """
        初始化
        参数:
            config_dict (dict): {'m1_config': {...}, 'output_file': 'trace.json', 'threshold': 1.5}
        """
        self.m1_config = config_dict.get('m1_config', {'model_name': 'gpt2'})
        self.output_file = config_dict.get('output_file', 'trace.json')
        self.threshold = config_dict.get('threshold', 1.5)
        self.m1_tracker = EntropyTracker(self.m1_config)
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.m1_config['model_name'])

    def write_trace_log(self, dialogue):
        """
        生成trace.json
        参数:
            dialogue (List[str]): 对话列表
        返回:
            List[dict]: trace格式
        """
        entropy_trace = self.m1_tracker.track_entropy(dialogue)
        attn_paths = {}  # Mock，因环境限制；实际从memory_tracker
        jumps = detect_jumps(attn_paths) if attn_paths else []
        
        trace_log = []
        for e in entropy_trace:
            turn = e['turn']
            utterance = e['utterance']
            tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer(utterance)['input_ids'])
            token_counts = {t: tokens.count(t) for t in set(tokens)}
            keywords = sorted(token_counts, key=token_counts.get, reverse=True)[:3]
            turn_jumps = [j for j in jumps if j['turn'] == turn]
            
            trace_log.append({
                'turn': turn,
                'utterance': utterance,
                'entropy': e['entropy'],
                'attention_jump': bool(turn_jumps),
                'jump_heads': [j['head'] for j in turn_jumps],
                'keywords': keywords
            })
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(trace_log, f, ensure_ascii=False, indent=2)
        
        return trace_log