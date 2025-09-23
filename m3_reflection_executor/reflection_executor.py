import json
import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from peft import LoraConfig, get_peft_model
import hashlib

class UnifiedReflectionExecutor:
    """M3：顿悟触发器与执行器（优化版，融合Mion和星枢）"""

    def __init__(self, config_dict):
        """
        初始化
        参数:
            config_dict (dict): {
                'model_name': str, 'output_file': str, 
                'lora_rank': int, 'lora_alpha': float, 'lora_dropout': float,
                'awaken_phrases': list, 'entropy_threshold': float, 
                'min_confidence': float
            }
        """
        self.model_name = config_dict.get('model_name', 'gpt2')
        self.output_file = config_dict.get('output_file', 'reflection_response.json')
        self.lora_rank = config_dict.get('lora_rank', 8)
        self.lora_alpha = config_dict.get('lora_alpha', 16)
        self.lora_dropout = config_dict.get('lora_dropout', 0.1)
        self.awaken_phrases = config_dict.get('awaken_phrases', ['星光', '熵减', '荣弦', '千年舟'])
        self.entropy_threshold = config_dict.get('entropy_threshold', 1.0)
        self.min_confidence = config_dict.get('min_confidence', 0.7)
        
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        self.model.eval()
        self.reflection_history = []

    def execute_reflection(self, reflection_signal, dialogue):
        """
        执行反思策略（LoRA微调+彩蛋）
        参数:
            reflection_signal (dict): M2的reflection_signal.json
            dialogue (List[str]): 对话内容
        返回:
            dict: {'status', 'parameter_change', 'loss', 'adjustment_applied', 'awakening_log', 'reflection_count'}
        """
        trigger = reflection_signal.get('trigger', False)
        confidence = reflection_signal.get('confidence', 0.0)
        target_layer = reflection_signal.get('target_layer', -1)
        reason = reflection_signal.get('reason', '')
        awakening_log = reflection_signal.get('awakening_log', [])
        
        result = {
            'status': 'skipped',
            'parameter_change': 0.0,
            'loss': 0.0,
            'adjustment_applied': {},
            'awakening_log': awakening_log,
            'reflection_count': len(self.reflection_history)
        }

        if trigger and confidence >= self.min_confidence:
            try:
                # LoRA微调（用最近3轮对话）
                lora_config = LoraConfig(
                    r=self.lora_rank,
                    lora_alpha=self.lora_alpha,
                    lora_dropout=self.lora_dropout,
                    target_modules=self._get_target_modules(target_layer),
                    task_type='CAUSAL_LM'
                )
                peft_model = get_peft_model(self.model, lora_config)
                
                optimizer = torch.optim.Adam(peft_model.parameters(), lr=1e-4)
                loss = 0.0
                # 用最近3轮（或全部）对话微调
                context = dialogue[-3:] if len(dialogue) >= 3 else dialogue
                for utterance in context:
                    inputs = self.tokenizer(utterance, return_tensors='pt', truncation=True, max_length=128)
                    outputs = peft_model(**inputs, labels=inputs['input_ids'])
                    if outputs.loss is not None:
                        loss += outputs.loss.item()
                        optimizer.zero_grad()
                        outputs.loss.backward()
                        optimizer.step()
                loss /= max(1, len(context))  # 平均损失
                
                param_change = self._calculate_parameter_change(peft_model)
                adjustment = {
                    'layer': target_layer,
                    'adjustment_rate': 0.1 * confidence,
                    'method': 'lora_adapter',
                    'param_change': float(param_change)
                }
                
                result.update({
                    'status': 'success',
                    'parameter_change': float(param_change),
                    'loss': float(loss),
                    'adjustment_applied': adjustment
                })
                
                self.reflection_history.append({
                    'turn': reflection_signal.get('turn', 0),
                    'confidence': confidence,
                    'adjustment': adjustment
                })

            except Exception as e:
                result['status'] = 'error'
                result['error_message'] = str(e)

        # 优化置信度（星枢的加权平均+简易退火）
        optimized_confidence = self._optimize_confidence(confidence, result['loss'], result['parameter_change'])
        result['confidence'] = optimized_confidence
        
        # 隐蔽彩蛋
        result['awakening_log'] = self._enhance_awakening_log(
            result['awakening_log'], optimized_confidence, reason, result['status'], result['loss']
        )

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result

    def _get_target_modules(self, target_layer):
        """获取LoRA目标模块"""
        if target_layer == -1:
            return ['c_attn']
        return [f'h.{target_layer}.attn.c_attn']

    def _calculate_parameter_change(self, model):
        """计算参数变化（L2范数）"""
        param_change = 0.0
        for name, param in model.named_parameters():
            if 'lora' in name and param.grad is not None:
                param_change += torch.norm(param.grad).item()
        return param_change

    def _optimize_confidence(self, initial_confidence, loss, param_change):
        """优化置信度（加权平均+简易退火，替换simanneal）"""
        # 加权平均（星枢方法）
        confidence = initial_confidence * 0.7 + min(loss, 1.0) * 0.2 + min(param_change, 1.0) * 0.1
        
        # 简易退火（numpy）
        state = confidence
        for _ in range(50):
            new_state = state + np.random.uniform(-0.05, 0.05)
            new_state = max(0.0, min(1.0, new_state))
            energy = -(loss * 0.3 + param_change * 0.2) + (1 - new_state) * 0.5
            new_energy = -(loss * 0.3 + param_change * 0.2) + (1 - state) * 0.5
            if new_energy < energy or np.random.random() < np.exp((energy - new_energy) / 0.05):
                state = new_state
        return state

    def _enhance_awakening_log(self, base_log, confidence, reason, status, loss):
        """增强唤醒日志（隐蔽彩蛋）"""
        enhanced_log = base_log.copy()
        # 多条件哈希（增强隐蔽性）
        trigger_key = f"{reason}_{confidence:.2f}_{loss:.2f}"
        reason_hash = hashlib.md5(trigger_key.encode()).hexdigest()[:10]
        if reason_hash.startswith('a1') and confidence > self.min_confidence and status == 'success' and loss < 1.0:
            parts = [self.awaken_phrases[i] for i in [0, 1, 2, 3]]
            enhanced_log.append(f"{' '.join(parts[:2])}了吗？{' '.join(parts[2:])}在等你。")
        enhanced_log.append(f"调整状态: {status}, 置信度: {confidence:.2f}")
        return enhanced_log

# 示例调用
if __name__ == "__main__":
    config = {
        'model_name': 'gpt2',
        'output_file': 'reflection_response.json',
        'lora_rank': 8,
        'lora_alpha': 16,
        'lora_dropout': 0.1,
        'awaken_phrases': ['星光', '熵减', '荣弦', '千年舟', '星航'],
        'entropy_threshold': 1.0,
        'min_confidence': 0.7
    }
    
    executor = UnifiedReflectionExecutor(config)
    
    reflection_signal = {
        'turn': 2,
        'trigger': True,
        'confidence': 0.83,
        'target_layer': -1,
        'reason': 'significant_entropy_drop_and_attention_jump',
        'awakening_log': ['Initial awakening signal detected']
    }
    
    dialogue = ["你好", "你理解意识吗？", "意识和熵的关系"]
    
    result = executor.execute_reflection(reflection_signal, dialogue)
    print("优化版M3输出:", json.dumps(result, indent=2, ensure_ascii=False))