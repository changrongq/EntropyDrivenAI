import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import pandas as pd
import json
import os

def generate_entropy_curve(entropy_trace_path):
    """
    生成熵曲线图 (Matplotlib)，返回图片路径
    """
    with open(entropy_trace_path, 'r', encoding='utf-8') as f:
        trace = json.load(f)
    # 支持两种格式：list[dict] 或 list[tuple]
    if isinstance(trace[0], dict):
        turns = [item.get('turn', idx) for idx, item in enumerate(trace)]
        entropies = [item['entropy'] for item in trace]
    else:
        turns = [item[0] for item in trace]
        entropies = [item[2] for item in trace]

    plt.figure(figsize=(10, 6))
    sns.lineplot(x=turns, y=entropies, marker='o')
    plt.title('Entropy Trend Over Dialogue Turns')
    plt.xlabel('Turn')
    plt.ylabel('Entropy (nats)')
    plt.grid(True)
    out_path = 'entropy_curve.png'
    plt.savefig(out_path)
    plt.close()
    return out_path

def generate_attention_jump_map(matrix_path, summary_path, tfidf_path):
    """
    生成注意力跳跃热图 (Seaborn静态+Plotly交互)，返回图片路径和html路径
    """
    matrix = np.load(matrix_path)
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    with open(tfidf_path, 'r', encoding='utf-8') as f:
        tfidf = json.load(f)

    # 静态热图
    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix, cmap='viridis', annot=True)
    plt.title('Attention Jump Matrix (Turns x Heads)')
    plt.xlabel('Head Index')
    plt.ylabel('Dialogue Turn')
    static_path = 'attention_jump_map.png'
    plt.savefig(static_path)
    plt.close()

    # 交互热图（Plotly，hover显示TF-IDF关键词）
    df = pd.DataFrame(matrix)
    hover_text = []
    for i in range(df.shape[0]):
        row = []
        for j in range(df.shape[1]):
            # 取summary/TF-IDF关键词作为hover内容
            turn = str(i)
            head = str(j)
            keywords = tfidf.get(turn, [""])
            row.append(f"Turn {turn}, Head {head}<br>Keywords: {', '.join(keywords)}")
        hover_text.append(row)
    fig = px.imshow(
        df.values,
        labels=dict(x="Head Index", y="Dialogue Turn", color="Jump Score"),
        x=[f"Head {i}" for i in range(df.shape[1])],
        y=[f"Turn {i}" for i in range(df.shape[0])],
        text_auto=True,
        aspect="auto"
    )
    fig.update_traces(hovertemplate="%{customdata}")
    fig.update_layout(title="Interactive Attention Jump Map")
    fig.update_traces(customdata=hover_text)
    html_path = 'attention_jump_map.html'
    fig.write_html(html_path)

    return static_path, html_path
    
    

def load_encouragement():
    try:
        with open('m7_encouragement_stack/encouragement_response.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_encouragement_md():
    try:
        with open('m7_encouragement_stack/encouragement_log.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""    