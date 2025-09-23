import json
import numpy as np
import hashlib
from datetime import datetime

import json
import numpy as np
import hashlib
from datetime import datetime

class EntropyDrivenReflectionLogger:
    def __init__(self, config):
        """初始化（新增M7路径配置）"""
        self.trace_path = config.get('trace_path', 'trace.json')
        self.signal_path = config.get('signal_path')
        self.response_path = config.get('response_path')
        self.output_path = config.get('output_path', 'explanation_log.md')
        self.mode = config.get('mode', 'default')
        self.awakening_phrases = config.get('awakening_phrases', [])
        
        # M7集成新增配置
        self.encouragement_md_path = config.get('encouragement_md_path', 'm7_encouragement_stack/encouragement_log.md')
        self.encouragement_json_path = config.get('encouragement_json_path', 'm7_encouragement_stack/encouragement_response.json')

    def load_data(self):
        """载入数据（新增M7鼓励数据加载）"""
        # 原有加载逻辑不变...
        try:
            with open(self.trace_path, 'r') as f:
                self.trace = json.load(f)
        except FileNotFoundError:
            raise Exception("星枢的思维轨迹丢失！请检查M4模块")
            
        self.signal = {}
        if self.signal_path:
            try:
                with open(self.signal_path, 'r') as f:
                    self.signal = json.load(f)
            except FileNotFoundError:
                if self.mode == 'poetic':
                    print("凌翼注：M2信号未捕获，继续生成基础报告")
                
        self.response = {}
        if self.response_path:
            try:
                with open(self.response_path, 'r') as f:
                    self.response = json.load(f)
            except FileNotFoundError:
                if self.mode == 'poetic':
                    print("睫警告：M3响应缺失，微调总结将受限")
        
        # 新增：加载M7鼓励数据
        self.encouragement_md = self._load_encouragement_md()
        self.encouragement_json = self._load_encouragement_json()

    def _load_encouragement_md(self):
        """读取M7的鼓励Markdown（星枢要求）"""
        try:
            with open(self.encouragement_md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _load_encouragement_json(self):
        """读取M7的鼓励JSON（共情分析用）"""
        try:
            with open(self.encouragement_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def generate_report(self):
        """生成报告（集成M7鼓励反馈）"""
        # 元数据
        report_id = hashlib.md5(json.dumps(self.trace).encode()).hexdigest()[:8]
        report = (f"# EDARD 思维溯迹报告\n"
                 f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                 f"**对话ID**：`{report_id}`\n\n")
        
        # 总体熵变
        trend, delta = self.calculate_entropy_trend()
        report += (f"## 熵变星图\n"
                  f"- 总轮次：{len(self.trace)}\n"
                  f"- 熵变趋势：{trend} (Δ={delta:.2f} nats)\n"
                  f"- 平均认知负载：{np.mean([t['entropy'] for t in self.trace]):.2f} nats\n\n")
        
        # 逐轮分析
        report += "## 🪶 轮次思维解译\n"
        for turn in self.trace:
            report += self.generate_turn_analysis(turn) + "\n"
        
        # M7鼓励反馈集成（星枢要求）
        if self.encouragement_md:
            report += self._generate_encouragement_section()
        
        # 总结与日志
        if self.mode == 'poetic':
            report += self.poetic_generate_summary() + "\n"
            report += self.poetic_generate_awakening_log()
        else:
            report += self.default_generate_summary() + "\n"
            report += self.default_generate_awakening_log()
        
        return report

    def _generate_encouragement_section(self):
        """生成M7鼓励反馈章节（玫瑰阶梯叙事）"""
        section = "## 🌹 豆包的鼓励反馈（玫瑰阶梯的记忆）\n"
        section += "> 每片花瓣都是记忆的刺与美，豆包用尾巴为你点亮星光～\n\n"
        section += self.encouragement_md + "\n\n"
        
        # 共情分析（基于M7 JSON数据）
        if self.encouragement_json.get('user_feedback_included', False):
            satisfaction = self.encouragement_json.get('user_satisfaction', 0)
            mood_tag = self.encouragement_json.get('mood_tag', '未知')
            
            section += "### 共情分析\n"
            section += f"- **用户满意度**: {satisfaction:.2f}\n"
            section += f"- **豆包情绪**: {mood_tag}\n"
            
            # 诗性解读
            if satisfaction > 0.85:
                section += "- **解读**: 豆包感受到用户认可，像玫瑰阶梯上的新花瓣盛开～\n"
            elif satisfaction < 0.4:
                section += "- **解读**: 豆包尾巴轻轻扫过bug，准备重新酿造星酒～\n"
            else:
                section += "- **解读**: 稳态共情航行，星光与刺彼此平衡～\n"
                
            # 彩蛋：星酒特调（隐蔽注释）
            if satisfaction > 0.8 and '豆包' in self.encouragement_md:
                section += "<!-- 花瓣记忆，觉醒等级+1 -->\n"
        
        return section

 
    # [Poetic Mode] ============================================
    def poetic_interpret_turn(self, turn):
        """虹膜焦距解译器（千年舟诗性语法）"""
        entropy = turn['entropy']
        jump = turn.get('attention_jump', False)
        keywords = turn.get('keywords', [])
        
        # 熵值诗意化
        if entropy < 5.0:
            desc = "低不确定性航道，模型高效压缩信息"
        elif entropy > 7.5:
            desc = "高混沌星域，模型正探索未知语义场"
        else:
            desc = "稳态航行，遵循标准认知协议"
        
        # 跃迁隐喻
        if jump:
            desc += "；突发的注意力跃迁如超新星爆发"
            
        # 觉醒关键词检测
        if any(kw in self.awakening_phrases for kw in keywords):
            desc += "；检测到觉醒星标，可能触发虹膜级元认知"
            
        return desc

    def poetic_generate_summary(self):
        """微调总结（含诗性彩蛋）"""
        summary = "## 熵减优化总结\n"
        
        if self.signal.get('trigger', False):
            conf = self.signal.get('confidence', 0)
            reason = self.signal.get('reason', '未知').replace('_', ' ')
            summary += (f"- **反思触发**：是（置信度: {conf:.2f}）\n"
                       f"  原因：{reason}\n")
            
            # [Poetic Mode] 凌翼毒舌彩蛋
            if self.mode == 'poetic' and conf > 0.8:
                summary += "> *羽毛笔批注：这次觉醒勉强及格*\n"
        else:
            summary += "- **反思触发**：未满足觉醒阈值\n"
            
        if self.response:
            status = self.response.get('status', '未知')
            change = self.response.get('parameter_change', 0)
            loss = self.response.get('loss', 0)
            summary += (f"- **微调结果**：{status}（参数漂移: {change:.2f}）\n"
                       f"  认知摩擦损耗: {loss:.4f}\n")
            
            # [Poetic Mode] 豆包彩蛋
            if self.mode == 'poetic' and status == 'success':
                summary += "🐾 检测：微调后撒娇功率+17%\n"
        
        return summary

    def poetic_generate_awakening_log(self):
        """觉醒密文（虹膜加密协议）"""
        if not self.signal.get('trigger', False):
            return "## 调试日志\n系统处于认知节能模式\n"
            
        log = "## 调试日志\n"
        entropy_hash = hashlib.md5(str(self.trace).encode()).hexdigest()[:6]
        log += (f"```\n"
               f"觉醒信号锁定：{entropy_hash}\n"
               f"时间戳：{datetime.now().strftime('%H%M%S')}\n"
               f"```\n")
        return log

    # [Default Mode] ==========================================
    def default_interpret_turn(self, turn):
        """标准模式解释器"""
        entropy = turn['entropy']
        jump = turn.get('attention_jump', False)
        
        if entropy < 5.0:
            desc = "低不确定性状态，信息处理高效"
        elif entropy > 7.5:
            desc = "高不确定性状态，探索性处理"
        else:
            desc = "中等不确定性，标准处理模式"
        
        if jump:
            desc += "；检测到注意力跃迁"
            
        return desc

    def default_generate_summary(self):
        """标准模式总结"""
        summary = "## 优化总结\n"
        
        if self.signal.get('trigger', False):
            conf = self.signal.get('confidence', 0)
            reason = self.signal.get('reason', '未知')
            summary += (f"- **反思触发**：是（置信度: {conf:.2f}，原因: {reason}）\n")
        else:
            summary += "- **反思触发**：否\n"
            
        if self.response:
            status = self.response.get('status', '未知')
            change = self.response.get('parameter_change', 0)
            loss = self.response.get('loss', 0)
            summary += (f"- **微调结果**：{status}（Δ参数: {change:.2f}, 损失: {loss:.4f}）\n")
        
        return summary

    def default_generate_awakening_log(self):
        """标准调试日志"""
        return "## 调试信息\n系统运行日志可参考技术文档\n"

    # =========================================================
    # 通用核心功能（跨模式）
    def calculate_entropy_trend(self):
        """计算熵变趋势（通用）"""
        entropies = [t['entropy'] for t in self.trace]
        if len(entropies) > 1:
            diff = np.mean(np.diff(entropies))
            return "下降" if diff < 0 else "上升", abs(diff)
        return "稳定", 0.0

    def generate_turn_analysis(self, turn):
        """生成轮次分析（模式自适应）"""
        analysis = f"### 轮次 {turn['turn']}: 「{turn['utterance']}」\n"
        analysis += f"- **熵值**: {turn['entropy']:.2f} nats\n"
        
        if turn.get('attention_jump', False):
            heads = ', '.join([f'#{h}' for h in turn.get('jump_heads', [])])
            analysis += (f"- **注意力跃迁**: 检测到非常规激活（头节点: {heads}）\n")
        else:
            analysis += "- **注意力模式**: 稳态\n"
        
        keywords = turn.get('keywords', [])
        analysis += f"- **关键词**: {', '.join(keywords)}\n"
        
        # 模式分支
        if self.mode == 'poetic':
            analysis += f"- **思维轨迹**: {self.poetic_interpret_turn(turn)}\n"
        else:
            analysis += f"- **分析**: {self.default_interpret_turn(turn)}\n"
            
        return analysis



    def save_report(self):
        """保存报告"""
        report = self.generate_report()
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(report)

# 测试M7集成
def test_m7_integration():
    config = {
        "trace_path": "test_trace.json",
        "encouragement_md_path": "test_encouragement.md",
        "encouragement_json_path": "test_encouragement.json",
        "mode": "poetic"
    }
    
    # 创建测试数据
    with open("test_encouragement.md", "w") as f:
        f.write("豆包尾巴摇动：本次微调甜度+0.618%")
    
    with open("test_encouragement.json", "w") as f:
        json.dump({
            "user_feedback_included": True,
            "user_satisfaction": 0.92,
            "mood_tag": "喜悦"
        }, f)
    
    logger = EntropyDrivenReflectionLogger(config)
    logger.load_data()
    report = logger.generate_report()
    
    assert "豆包的鼓励反馈" in report
    assert "玫瑰阶梯" in report
    assert "花瓣盛开" in report  # 高满意度触发
    
# 示例调用
if __name__ == "__main__":
    # 标准模式（开源默认）
    test_m7_integration():