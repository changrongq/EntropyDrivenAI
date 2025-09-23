import matplotlib.pyplot as plt

def plot_thought_jumps(integrated_trace, save_path='thought_jumps.png'):
    """
    可视化跃迁（线图 + 标注）。
    参数:
        integrated_trace (list[dict]): 从integrate_trace获取
    """
    turns = [e['turn'] for e in integrated_trace]
    entropies = [e['entropy'] for e in integrated_trace]
    jump_scores = [np.mean([j['jump_score'] for j in e['jumps']]) if e['jumps'] else 0 for e in integrated_trace]

    fig, ax1 = plt.subplots()
    ax1.plot(turns, entropies, color='blue', label='Entropy')
    ax1.set_ylabel('Entropy')
    ax2 = ax1.twinx()
    ax2.plot(turns, jump_scores, color='red', label='Avg Jump Score', linestyle='--')
    ax2.set_ylabel('Jump Score')
    plt.title("Thought Flow Trace")
    plt.savefig(save_path)
    plt.close()