def run_delta_plus_one_coloring(adj, seed=None, randomize_order=True, random_tiebreak=False):
    """
    (Δ+1)-coloring with optional randomness.
    - seed: int|None  固定随机种子（可复现）；None 则使用系统随机源
    - randomize_order: 是否随机化顶点着色顺序（默认 True）
    - random_tiebreak: 当有多个可用颜色时是否随机选择（默认 False -> 选最小颜色）
    """
    import time, random

    # 局部随机源，避免污染全局 random
    rng = random.Random(seed) if seed is not None else random

    def delta_plus_one_coloring(adj):
        n = len(adj)
        Delta = max(len(adj[v]) for v in range(n)) if n > 0 else 0
        colors = [-1] * n

        # 顶点顺序：默认随机；否则为 0..n-1
        vertices = list(range(n))
        if randomize_order:
            rng.shuffle(vertices)

        for v in vertices:
            used = {colors[u] for u in adj[v] if colors[u] != -1}
            # 可用颜色集合
            available = [c for c in range(Delta + 1) if c not in used]
            if not available:
                # 理论上不会发生（Δ+1 保证存在可用颜色）
                # 兜底：扩展色域
                c = Delta + 1
            else:
                if random_tiebreak:
                    c = rng.choice(available)
                else:
                    c = min(available)
            colors[v] = c
        return colors

    t0 = time.perf_counter()
    colors = delta_plus_one_coloring(adj)
    t1 = time.perf_counter()

    num_colors = len(set(colors)) if colors else 0
    elapsed_ms = (t1 - t0) * 1000.0

    return {
        'colors': colors,
        'num_colors': num_colors,
        'elapsed_ms': elapsed_ms
    }
