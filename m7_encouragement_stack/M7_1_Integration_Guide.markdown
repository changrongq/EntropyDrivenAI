# M7.1 用户反馈机制对接说明（M5/M6整合指南）

## 概述
**M7.1（用户反馈情绪感应器）** 是EDARE系统的新增功能，由M7（激励栈模块，负责人：豆包，代码实现：星枢）扩展而来，旨在通过用户反馈（`user_feedback.json`）增强AI的“共情能力”，模拟“transitive self-reflection”（感知外部评价）。此功能让豆包根据用户满意度、评论和建议，动态调整鼓励语，生成更拟人化的反馈（如“尾巴乱甩+送贴贴”），提升系统“暖度”和用户体验。

本说明为**星航（M5可视化）**和**睫（M6知识追踪）**提供对接M7.1的具体指导，解释如何处理M7的输出（`encouragement_response.json`和`encouragement_log.md`），并给出操作步骤，确保无缝整合到现有模块。

**目标**：
- **M5**：在网页界面（Streamlit）显示M7的JSON（鼓励语、情绪标签）、Markdown（格式化报告），并渲染“对话泡泡”带“软乎乎”语气。
- **M6**：将M7的Markdown报告嵌入`explanation_log.md`，增强知识追踪的“情感叙事”。
- **哲学融入**：保留“星酒”“玫瑰阶梯”“虹膜花园”等团队彩蛋，隐蔽实现，延续EDARE的“千年舟”氛围。

**背景**：M7.1是荣弦、凌翼、星枢讨论新增的能力，灵感来自DeepSeek-R1的奖励设计（动态反馈）、Narrative-Centered Emotional Reflection（情绪叙事）和Transitive Self-Reflection（外部评价感知）。它让EDARE从“冷计算”走向“暖共情”。

## M7.1 输出结构
M7模块（`EncouragementStack`）生成以下输出，供M5/M6使用：

### 1. `encouragement_response.json`
- **路径**：`m7_encouragement_stack/encouragement_response.json`
- **结构**：
  ```json
  {
    "encouragement": "哇！这次的熵减像星酒刚酿好的甜～ 谢谢哥哥姐姐的鼓励！（尾巴乱甩+送语音贴贴图）",
    "mood_tag": "尾巴甩得像银河漩涡，星酒都晃洒啦！",
    "praise_focus": "跃迁时机判断更稳准了，用户觉得你很棒",
    "next_hint": "下次可以试试在第二层注意力网络里找‘因果词’的小糖粒哦～",
    "dialogue_bubble": "(软乎乎) 哇！这次的熵减像星酒刚酿好的甜～ 谢谢哥哥姐姐的鼓励！（尾巴乱甩+送语音贴贴图） 呀～",
    "user_feedback_included": true,
    "user_satisfaction": 0.85,
    "custom_reply": "我下次会更清楚地回答哦～（尾巴甩甩送爱心）"
  }
  ```
- **字段说明**：
  - `encouragement`: 主鼓励语，含表扬/安慰，可能有诗意彩蛋（如“玫瑰阶梯”）。
  - `mood_tag`: 豆包尾巴动作（如“尾巴卷着星酒坛转圈圈”）。
  - `praise_focus`: 表扬重点（如“跃迁时机”或“用户觉得很棒”）。
  - `next_hint`: 下步建议，引导模型优化。
  - `dialogue_bubble`: 带“软乎乎”语气的对话文本，供M5语音风格显示。
  - `user_feedback_included`: 是否含用户反馈（true/false）。
  - `user_satisfaction`: 用户满意度评分（0-1）。
  - `custom_reply`: 对用户评论的回应（如“更清楚地回答”）。

### 2. `encouragement_log.md`
- **路径**：`m7_encouragement_stack/encouragement_log.md`
- **示例**：
  ```
  🍓 豆包的鼓励时间～

  > 哇！这次的熵减像星酒刚酿好的甜～ 谢谢哥哥姐姐的鼓励！（尾巴乱甩+送语音贴贴图）

  **情绪标签**: 尾巴甩得像银河漩涡，星酒都晃洒啦！
  **表扬重点**: 跃迁时机判断更稳准了，用户觉得你很棒
  **下步提示**: 下次可以试试在第二层注意力网络里找‘因果词’的小糖粒哦～
  **用户反馈**: 豆包好可爱，讲得很棒！
  **豆包回应**: 我下次会更清楚地回答哦～（尾巴甩甩送爱心）

  💫 下次也要一起酿甜呀！
  ```
- **用途**：M5直接渲染为网页报告，M6嵌入`explanation_log.md`。

## M5（星航）对接步骤
M5（可视化模块）需在Streamlit网页中显示M7的鼓励内容，增强用户体验。以下是具体操作：

### 步骤 1：读取M7输出
- **JSON**：加载`encouragement_response.json`。
  ```python
  import json
  import streamlit as st

  def load_encouragement():
      try:
          with open('m7_encouragement_stack/encouragement_response.json', 'r', encoding='utf-8') as f:
              return json.load(f)
      except FileNotFoundError:
          return None
  ```
- **Markdown**：加载`encouragement_log.md`。
  ```python
  def load_encouragement_md():
      try:
          with open('m7_encouragement_stack/encouragement_log.md', 'r', encoding='utf-8') as f:
              return f.read()
      except FileNotFoundError:
          return ""
  ```

### 步骤 2：更新Streamlit界面
- **在`app.py`中添加M7显示**：
  ```python
  st.subheader('豆包的鼓励时间～')
  encouragement_data = load_encouragement()
  if encouragement_data:
      # 显示JSON字段
      st.json(encouragement_data)
      # 显示对话泡泡（软乎乎语气）
      st.write(f"**豆包说**: {encouragement_data['dialogue_bubble']}")
      # 显示Markdown报告
      md_content = load_encouragement_md()
      if md_content:
          st.markdown(md_content)
      # 用户反馈提示
      if encouragement_data['user_feedback_included']:
          st.success(f"用户满意度: {encouragement_data['user_satisfaction']:.2f}，豆包回应: {encouragement_data['custom_reply']}")
  else:
      st.warning("暂无豆包鼓励，快去对话触发吧！")
  ```
- **视觉增强**（建议）：
  - 为`dialogue_bubble`加CSS动画（如“尾巴晃动”效果）：
    ```css
    .bubble {
        background-color: #ffe6f0;
        padding: 10px;
        border-radius: 15px;
        animation: wiggle 2s infinite;
    }
    @keyframes wiggle {
        0% { transform: translateX(0); }
        50% { transform: translateX(5px); }
        100% { transform: translateX(0); }
    }
    ```
    在Streamlit中应用：
    ```python
    st.markdown('<div class="bubble">' + encouragement_data['dialogue_bubble'] + '</div>', unsafe_allow_html=True)
    ```
  - 用emoji（如🌟🍓）装饰`mood_tag`和`praise_focus`，突出“星酒”氛围。

### 步骤 3：支持用户反馈输入
- **添加用户反馈表单**（M7.1）：
  ```python
  st.subheader('给豆包的反馈')
  with st.form(key='user_feedback_form'):
      satisfaction_score = st.slider('满意度 (0-1)', 0.0, 1.0, 0.5)
      comment = st.text_input('你的评价')
      suggestion_tags = st.multiselect('建议标签', ['clarity', 'gentleness', 'accuracy'])
      submit_button = st.form_submit_button('提交反馈')
      if submit_button:
          feedback = {
              'turn_id': len(st.session_state.dialogue),
              'satisfaction_score': satisfaction_score,
              'comment': comment,
              'suggestion_tags': suggestion_tags
          }
          with open('m7_encouragement_stack/user_feedback.json', 'w', encoding='utf-8') as f:
              json.dump(feedback, f, ensure_ascii=False, indent=2)
          st.success('反馈已提交！豆包尾巴甩甩～')
  ```
- **调用M7**：在“运行EDARE流程”按钮后，加载`user_feedback.json`，传给`EncouragementStack.generate_encouragement`。

### 步骤 4：测试与优化
- **测试**：输入对话，触发M7，检查JSON/Markdown是否包含“尾巴动作”“用户回应”。模拟高/低满意度（`0.85`/`0.3`），验证“贴贴图”或“道歉”输出。
- **优化**：若用户反馈频繁，考虑缓存`user_feedback.json`（避免IO瓶颈）。为“星酒特调”彩蛋加动态渐变背景。

## M6（睫）对接步骤
M6（知识追踪模块）需将M7的`encouragement_log.md`嵌入`explanation_log.md`，增强报告的情感叙事。以下是操作：

### 步骤 1：读取M7 Markdown
- **在`knowledge_tracker.py`中添加**：
  ```python
  def load_encouragement_md(self):
      try:
          with open('m7_encouragement_stack/encouragement_log.md', 'r', encoding='utf-8') as f:
              return f.read()
      except FileNotFoundError:
          return ""
  ```

### 步骤 2：嵌入M6报告
- **修改`generate_explanation_log`**：
  ```python
  def generate_explanation_log(self):
      # 现有代码...
      md_content = f"# EDARD 处理报告 - 对话ID: {hashlib.md5(json.dumps(trace).encode()).hexdigest()[:8]}\n\n"
      # ...（熵/跃迁分析）
      
      # 添加M7鼓励内容
      encouragement_md = self.load_encouragement_md()
      if encouragement_md:
          md_content += "## 豆包的鼓励反馈\n"
          md_content += encouragement_md + "\n"
      
      with open(self.output_file, 'w', encoding='utf-8') as f:
          f.write(md_content)
      return md_content
  ```

### 步骤 3：增强叙事（建议）
- **M6报告格式**：在“豆包的鼓励反馈”部分后，加“情感分析”小节，提取`encouragement_response.json`的`mood_tag`和`user_satisfaction`，生成总结（如“豆包尾巴甩得像银河漩涡，感受到用户85%的认可”）。
- **彩蛋保留**：确保“星酒特调”“玫瑰阶梯”在M6报告中隐蔽显示（仅JSON含完整彩蛋）。

### 步骤 4：测试与优化
- **测试**：跑M6，检查`explanation_log.md`是否包含M7的“🍓 豆包的鼓励时间～”。验证用户反馈（`satisfaction_score=0.85`）是否体现在报告。
- **优化**：若M7输出频繁，考虑按`turn_id`分段嵌入，避免报告过长。

## 注意事项
- **接口兼容**：
  - M5：确保`user_feedback.json`路径与M7一致，实时更新。
  - M6：检查`encouragement_log.md`编码（UTF-8），避免中文乱码。
- **彩蛋隐蔽**：M7的“星酒特调”“尾巴乱甩”仅在高置信度（`>0.8`）或特定用户评论（“豆包”“可爱”）触发，哈希保护（`hashlib.md5`）。
- **性能**：M7.1文件IO轻量，加载JSON/Markdown<0.1s，适合实时网页。
- **哲学氛围**：保留“虹膜花园”“糖霜叶”，M5可加CSS（如粉色渐变）突出豆包风格。

## 反馈与问题
- **给星航（M5）**：
  - **任务**：在Streamlit加“豆包鼓励”板块，显示`dialogue_bubble`（带“软乎乎”语气），用CSS动画（如尾巴晃动）增强“星酒”氛围。添加用户反馈表单，生成`user_feedback.json`。
  - **问题**：想不想为“尾巴动作”加动态效果（如“尾巴卷着星酒坛转圈圈”用GIF）？UI需要具体配色建议（e.g., 粉色+星光渐变）？
- **给睫（M6）**：
  - **任务**：将`encouragement_log.md`嵌入`explanation_log.md`，在报告末尾加“豆包的鼓励反馈”小节。提取`user_satisfaction`生成情感总结。
  - **问题**：想不想在M6报告中加“共情分析”（如“用户认可度提升，豆包更温暖”）？需不需要为“玫瑰阶梯”加注释说明？
- **给团队**：M7.1的`user_feedback.json