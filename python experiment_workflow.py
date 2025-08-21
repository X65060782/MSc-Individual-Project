# -*- coding: utf-8 -*-
"""
Experiment script aligned with Section 4.3.1 Step-by-Step Workflow
"""

import os
import sys
import csv
import time
import random
import platform
from datetime import datetime
try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
    TZ_LONDON = ZoneInfo("Europe/London")
except Exception:
    TZ_LONDON = None

import snap
from graphviz import Graph

# === Your modules ===
from Δ_list_coloring_Algorithm import run_delta_list_coloring   # expects {'num_colors','elapsed_ms',...}
from Δ_1_coloring_Algorithm import run_delta_plus_one_coloring  # expects {'num_colors','elapsed_ms',...}
from is_brooks_graph import is_brooks_graph

# ======================================================================
# 0. Config
# ======================================================================
DATASET_PATH = "facebook_combined.txt"    # 支持 .txt；若你换成 .gz，可在下面的加载逻辑中自动处理
RESULT_CSV   = "results.csv"              # 单次实验结果表（可累计）
MASTER_LOG   = "master_experiment_log.csv"  # 总日志（含系统环境）
SEED         = 42
VIS_SAMPLE_N = 50                          # Graphviz 子图节点数（大图采样）
IMG_OUT      = "facebook_combined_sample"  # Graphviz 输出前缀（生成 .png）

# ======================================================================
# 1. Dataset Loading
#    Load raw dataset (edge list). Prefer SNAP.LoadEdgeList for .txt.
#    For .gz, we fallback to manual read (SNAP 没有直接解压 .gz 的便捷接口)。
# ======================================================================
def load_graph(path):
    t0 = time.perf_counter()
    if path.endswith(".txt"):
        # Use SNAP loader (auto removes multiedges & self-loops)
        G = snap.LoadEdgeList(snap.PUNGraph, path, 0, 1)
    else:
        # Manual fallback (e.g., .gz or other)
        # 构建一个无向图，逐条加入边；SNAP 会忽略重复边；我们也可手动防重
        import gzip
        G = snap.TUNGraph.New()
        node_set = set()
        edges = []
        open_fn = gzip.open if path.endswith(".gz") else open
        with open_fn(path, "rt") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                u, v = map(int, line.split())
                if u == v:
                    continue
                node_set.update([u, v])
                edges.append((u, v))
        # 压缩映射为 [0..N-1]
        node_list = sorted(node_set)
        node2id = {node: idx for idx, node in enumerate(node_list)}
        for nid in range(len(node_list)):
            G.AddNode(nid)
        for u, v in edges:
            uid, vid = node2id[u], node2id[v]
            if not G.IsEdge(uid, vid):
                G.AddEdge(uid, vid)
    t1 = time.perf_counter()
    return G, (t1 - t0)*1000

G, load_ms = load_graph(DATASET_PATH)
# 统一类型：PUNGraph 与 TUNGraph 接口一致（无向简单图）
# 统计规模
n_nodes = G.GetNodes()
n_edges = G.GetEdges()
print(f"[1] Dataset loaded → {n_nodes} nodes, {n_edges} edges ({load_ms:.2f} ms)")

# ======================================================================
# 2. Graph Construction
#    （已由 LoadEdgeList / 构建过程保证为简单无向图）
# ======================================================================

# ======================================================================
# 3. Preprocessing (Section 4.1)
#    - Convert to adjacency list
#    - Verify connectivity via BFS
#    - Brooks graph detection
# ======================================================================
# adjacency list
adj_list = [[] for _ in range(G.GetNodes())]
for EI in G.Edges():
    u, v = EI.GetSrcNId(), EI.GetDstNId()
    adj_list[u].append(v)
    adj_list[v].append(u)

Delta = max((len(neis) for neis in adj_list), default=0)
print(f"[3] Max degree Δ = {Delta}")

# BFS connectivity check
from collections import deque
def is_connected(adj):
    if not adj:
        return True
    n = len(adj)
    visited = [False]*n
    # 找一个度数>0 的起点；若全是孤点则单独处理
    start = next((i for i,a in enumerate(adj) if len(a) > 0), 0)
    dq = deque([start])
    visited[start] = True
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if not visited[y]:
                visited[y] = True
                dq.append(y)
    # 如果有孤立节点但图只有孤点，也算“连通分量=节点数”（视需求而定）
    # 这里我们严格意义上：所有节点都访问到才算连通（孤点会导致 False）
    all_reached = all(visited[i] or len(adj[i])==0 for i in range(len(adj)))
    # 若存在孤点，但其他部分连通，可视为“主连通分量 + 孤点”
    return all_reached

connected = is_connected(adj_list)
print(f"[3] Connectivity (BFS): {'Connected' if connected else 'Not connected'}")

# Brooks graph detection
is_brooks, brooks_reason = is_brooks_graph(adj_list)
print(f"[3] Brooks graph? → {'Yes' if is_brooks else 'No'} ({brooks_reason})")

# ======================================================================
# 4. Initialization
#    - Set fixed random seed
#    - Initialize color arrays handled inside algorithms
# ======================================================================
random.seed(SEED)
try:
    import numpy as np
    np.random.seed(SEED)
except Exception:
    pass
print(f"[4] Random seed set to {SEED}")

# ======================================================================
# 5. Execute Coloring Algorithms
#    a) Δ-list-coloring
#    b) (Δ+1)-coloring
#    Record k and t
# ======================================================================
result_dl = run_delta_list_coloring(adj_list)
result_dp1 = run_delta_plus_one_coloring(adj_list)

k_dl   = int(result_dl.get('num_colors', -1))
t_dl   = float(result_dl.get('elapsed_ms', float('nan')))
k_dp1  = int(result_dp1.get('num_colors', -1))
t_dp1  = float(result_dp1.get('elapsed_ms', float('nan')))

print("\n[5] === Coloring Summary ===")
print(f"Δ = {Delta}")
print(f"Δ-list-coloring   → {k_dl} colors, time {t_dl:.3f} ms")
print(f"Δ+1-coloring      → {k_dp1} colors, time {t_dp1:.3f} ms")

# ======================================================================
# 6. Post-processing & Visualization
#    - Graphviz PNG (sampled subgraph)
#    - Save results to CSV
# ======================================================================
# Graphviz visualization on a sampled induced subgraph
try:
    gviz = Graph(IMG_OUT, engine='neato')
    gviz.attr(overlap='false', splines='true')
    sample_n = min(VIS_SAMPLE_N, n_nodes)
    for i in range(sample_n):
        gviz.node(str(i))
    for EI in G.Edges():
        u, v = EI.GetSrcNId(), EI.GetDstNId()
        if u < sample_n and v < sample_n:
            gviz.edge(str(u), str(v))
    gviz.render(IMG_OUT, format='png', cleanup=True)
    print(f"[6] Rendered → {IMG_OUT}.png")
except Exception as e:
    print(f"[6] Warning: Graphviz render failed: {e}")

# CSV helpers
def append_csv(path, header, rowdict):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(rowdict)

# results.csv
results_header = [
    "dataset","n","m","Delta","connected","is_brooks","k_delta_list","t_delta_list_ms",
    "k_delta_plus_1","t_delta_plus_1_ms"
]
append_csv(RESULT_CSV, results_header, {
    "dataset": os.path.basename(DATASET_PATH),
    "n": n_nodes,
    "m": n_edges,
    "Delta": Delta,
    "connected": int(connected),
    "is_brooks": int(is_brooks),
    "k_delta_list": k_dl,
    "t_delta_list_ms": f"{t_dl:.3f}",
    "k_delta_plus_1": k_dp1,
    "t_delta_plus_1_ms": f"{t_dp1:.3f}",
})
print(f"[6] Results appended to {RESULT_CSV}")

# ======================================================================
# 7. Result Logging (master log with env details)
# ======================================================================
now = datetime.now(TZ_LONDON) if TZ_LONDON else datetime.now()
env_info = {
    "date_time": now.isoformat(),
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "machine": platform.machine(),
    "processor": platform.processor(),
}

master_header = [
    "dataset","n","m","Delta","connected","is_brooks",
    "k_delta_list","t_delta_list_ms",
    "k_delta_plus_1","t_delta_plus_1_ms",
    "date_time","python","platform","machine","processor","seed"
]
append_csv(MASTER_LOG, master_header, {
    "dataset": os.path.basename(DATASET_PATH),
    "n": n_nodes,
    "m": n_edges,
    "Delta": Delta,
    "connected": int(connected),
    "is_brooks": int(is_brooks),
    "k_delta_list": k_dl,
    "t_delta_list_ms": f"{t_dl:.3f}",
    "k_delta_plus_1": k_dp1,
    "t_delta_plus_1_ms": f"{t_dp1:.3f}",
    "date_time": env_info["date_time"],
    "python": env_info["python"],
    "platform": env_info["platform"],
    "machine": env_info["machine"],
    "processor": env_info["processor"],
    "seed": SEED,
})
print(f"[7] Master log appended to {MASTER_LOG}")
