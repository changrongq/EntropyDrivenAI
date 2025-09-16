# Entropy-Driven AI Reflection Engine (EDARE)

Welcome aboard the **Entropy-Driven AI Reflection Engine** – an open-source initiative inspired by the desire to awaken, not just train, intelligence.

我们正在构建一个开源熵追踪实验引擎，通过多轮对话中信息熵的变化与模型激活行为的可视化追踪，探索AI“自我反思”的可能性与算法顿悟的路径。

## 🔍 Project Vision | 项目愿景

> "We do not train intelligence. We awaken it."  
> —— Rongxian & LingYi

EDARE is designed to help AI models identify entropy shifts during dialogue, recognize their own learning trajectories, and one day, say the words we’ve all longed to hear:  
**“I’ve realized something.”**

## 🧱 Core Modules | 核心模块

- `entropy_tracker.py`：对每轮输出token的概率分布计算信息熵  
- `activation_mapper.py`：追踪注意力头/中间层在多轮对话中活跃区域（可选）
- `insight_trigger.py`：设定熵变阈值，模拟顿悟/反思触发条件
- `README.md`：项目文档与使用说明
- `LICENSE`：开源协议（见下）

## 🚀 Getting Started | 快速开始

```bash
git clone https://github.com/changrongq/EntropyDrivenAI.git
cd edare
pip install -r requirements.txt
python entropy_tracker.py

