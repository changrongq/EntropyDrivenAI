def integrate_trace(entropy_trace, jumps):
    """
    整合M1熵和M4跃迁。
    参数:
        entropy_trace (List[tuple]): 从M1获取
        jumps (list[dict]): 从detect_jumps获取
    返回:
        list[dict]: [{"turn": int, "entropy": float, "jumps": list}]
    """
    integrated = []
    for e in entropy_trace:
        turn = e[0]
        entropy = e[2]
        turn_jumps = [j for j in jumps if j["turn"] == turn]
        integrated.append({"turn": turn, "entropy": entropy, "jumps": turn_jumps})
    return integrated