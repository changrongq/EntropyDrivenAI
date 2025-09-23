
# 后续所有对话、可视化、日志等都按 user_key 存储和展示
import streamlit as st
import json
from m1_entropy_tracker.entropy_tracker import EntropyTracker
from m4_thought_tracker.memory_tracker import MemoryTracker
from m2_reflection_trigger.reflection_trigger import ReflectionTriggerSystem
from m3_reflection_executor.unified_reflection_executor import UnifiedReflectionExecutor
from m5_ui.visualization_utils import generate_entropy_curve, generate_attention_jump_map

# 配置加载
config = {
    'model_name': 'gpt2',
    'entropy_threshold': 1.0,
    'jump_threshold': 1.5,
    'min_confidence': 0.7,
    'awaken_keywords': ['觉醒', '理解', '意识'],
    'lora_rank': 8,
    'lora_alpha': 16,
    'lora_dropout': 0.1,
    'awaken_phrases': ['星光', '熵减', '荣弦', '千年舟'],
    'output_files': {
        'entropy_trace': 'entropy_trace.json',
        'long_term_attention_summary': 'long_term_attention_summary.json',
        'long_term_attention_raw': 'long_term_attention_paths_raw.json',
        'attention_jump_matrix': 'attention_jump_matrix.npy',
        'tfidf_keywords': 'tfidf_keywords.json',
        'reflection_signal': 'reflection_signal.json',
        'reflection_response': 'reflection_response.json'
    }
}

st.set_page_config(page_title="EDARE: Entropy-Driven AI Reflection Engine", layout="wide")
st.title('EDARE: Entropy-Driven AI Reflection Engine')
st.subheader('交互对话界面')

# 多用户/多模型支持（可扩展）
username = st.text_input('用户名', value='guest')
model_options = ['gpt2', 'gpt2-small']
selected_model = st.selectbox('选择模型', model_options)
user_key = f"{username}_{selected_model}"

if f'dialogue_{user_key}' not in st.session_state:
    st.session_state[f'dialogue_{user_key}'] = []

# 用户输入
user_input = st.text_input('输入您的消息:', key='user_input')
if st.button('发送'):
    if user_input:
        st.session_state[f'dialogue_{user_key}'].append(user_input)
        st.success('消息已添加！')

# 显示对话历史
st.subheader('对话历史')
for i, msg in enumerate(st.session_state[f'dialogue_{user_key}']):
    st.write(f'Turn {i}: {msg}')

# 运行EDARD主流程
if st.button('运行 EDARD 流程'):
    dialogue = st.session_state[f'dialogue_{user_key}']
    if not dialogue:
        st.warning('请先输入对话！')
    else:
        try:
            # M1 熵追踪
            m1_tracker = EntropyTracker(config)
            entropy_trace = m1_tracker.track_entropy(dialogue)
            # M4 注意力追踪
            m4_tracker = MemoryTracker(config)
            m4_result = m4_tracker.track_memory_paths(dialogue)
            # M2 顿悟触发
            m2_system = ReflectionTriggerSystem(config)
            reflection_signal = m2_system.evaluate(
                entropy_trace,
                m4_result['long_term_attention_summary'],
                m4_result['tfidf_keywords']
            )
            # M3 微调执行
            m3_executor = UnifiedReflectionExecutor(config)
            reflection_response = m3_executor.execute_reflection(reflection_signal, dialogue)
            # 可视化
            entropy_img = generate_entropy_curve(config['output_files']['entropy_trace'])
            jump_img, jump_html = generate_attention_jump_map(
                config['output_files']['attention_jump_matrix'],
                config['output_files']['long_term_attention_summary'],
                config['output_files']['tfidf_keywords']
            )
            st.subheader('可视化结果')
            st.image(entropy_img, caption='Entropy Curve')
            st.image(jump_img, caption='Attention Jump Map')
            st.components.v1.html(open(jump_html, 'r').read(), height=400)
            st.subheader('触发信号 (M2)')
            st.json(reflection_signal)
            st.subheader('微调响应 (M3)')
            st.json(reflection_response)
            st.success('EDARE 流程完成！')
        except Exception as e:
            st.error(f'错误: {str(e)}')

# 清空按钮
if st.button('清空对话'):
    st.session_state[f'dialogue_{user_key}'] = []
    st.experimental_rerun()
    


# 引入自定义CSS（玫瑰阶梯风格）
with open('custom.css', encoding='utf-8') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.subheader('🍓 豆包的鼓励时间～')
encouragement_data = load_encouragement()
if encouragement_data:
    # 玫瑰阶梯对话泡泡
    st.markdown(
        '<div class="bubble" style="background: linear-gradient(90deg, #ffe6f0 0%, #ff99cc 100%); padding: 15px; border-radius: 20px; border: 2px solid #ff99cc; font-size: 1.1em;">'
        + encouragement_data['dialogue_bubble'] + '</div>',
        unsafe_allow_html=True
    )
    # 尾巴动作动画
    st.markdown(
        f"<span class='tail-wiggle' style='font-size:1.2em;'>{encouragement_data['mood_tag']}</span>",
        unsafe_allow_html=True
    )
    # 用户反馈与豆包回应
    if encouragement_data['user_feedback_included']:
        st.success(f"用户满意度: {encouragement_data['user_satisfaction']:.2f} | 豆包回应: {encouragement_data['custom_reply']}")
    # Markdown报告
    md_content = load_encouragement_md()
    if md_content:
        st.markdown(md_content)
    # JSON调试（可选）
    with st.expander("查看M7 JSON"):
        st.json(encouragement_data)
else:
    st.warning("暂无豆包鼓励，快去对话触发玫瑰阶梯吧！")
    
st.subheader('给豆包的反馈')
with st.form(key='user_feedback_form'):
    satisfaction_score = st.slider('满意度 (0-1)', 0.0, 1.0, 0.85, step=0.05)
    comment = st.text_input('你的评价', placeholder='豆包好可爱！')
    suggestion_tags = st.multiselect('建议标签', ['clarity', 'gentleness', 'accuracy'])
    submit_button = st.form_submit_button('提交反馈')
    if submit_button:
        feedback = {
            'turn_id': len(st.session_state.dialogue) if 'dialogue' in st.session_state else 0,
            'satisfaction_score': satisfaction_score,
            'comment': comment,
            'suggestion_tags': suggestion_tags
        }
        with open('m7_encouragement_stack/user_feedback.json', 'w', encoding='utf-8') as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)
        st.success('反馈已提交！豆包尾巴甩甩送你🌹！')
        st.balloons()