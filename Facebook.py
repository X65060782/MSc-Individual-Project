import snap
from graphviz import Graph
from Δ_list_coloring_Algorithm import run_delta_list_coloring
from Δ_1_coloring_Algorithm import run_delta_plus_one_coloring
from is_brooks_graph import is_brooks_graph  # ✅ 导入 Brooks 图判断函数

# ------------------------------------------------------------
# ① 读取 facebook_combined.txt，构建 SNAP 无向图
# ------------------------------------------------------------
fname = 'facebook_combined.txt'
G = snap.TUNGraph.New()

node_set = set()
edges = []

with open(fname, 'r') as f:
    for line in f:
        u, v = map(int, line.strip().split())
        node_set.update([u, v])
        edges.append((u, v))

node_list = sorted(node_set)
node2id = {node: idx for idx, node in enumerate(node_list)}
N = len(node_list)

for nid in range(N):
    G.AddNode(nid)

for u, v in edges:
    uid = node2id[u]
    vid = node2id[v]
    if not G.IsEdge(uid, vid):
        G.AddEdge(uid, vid)

print(f"Graph loaded → {G.GetNodes()} nodes, {G.GetEdges()} edges")

# ------------------------------------------------------------
# ② 转为邻接表（供算法使用）
# ------------------------------------------------------------
adj_list = [[] for _ in range(G.GetNodes())]
for EI in G.Edges():
    u, v = EI.GetSrcNId(), EI.GetDstNId()
    adj_list[u].append(v)
    adj_list[v].append(u)

Delta = max(len(neis) for neis in adj_list)
print(f"Max degree Δ = {Delta}")

# ------------------------------------------------------------
# ③ 调用两个算法（分别封装成函数了）
# ------------------------------------------------------------
result_dl = run_delta_list_coloring(adj_list)
result_dp1 = run_delta_plus_one_coloring(adj_list)

# ------------------------------------------------------------
# ④ 输出对比结果
# ------------------------------------------------------------
print("\n=== Coloring Summary ===")
print(f"Δ = {Delta}")
print(f"Δ-list-coloring   → {result_dl['num_colors']} colors, time {result_dl['elapsed_ms']:.3f} ms")
print(f"Δ+1-coloring      → {result_dp1['num_colors']} colors, time {result_dp1['elapsed_ms']:.3f} ms")

# ------------------------------------------------------------
# ⑤ 可视化子图（防止 Graphviz 报错）
# ------------------------------------------------------------
g = Graph('facebook_combined_sample', engine='neato')
g.attr(overlap='false', splines='true')

sample_n = 50
for i in range(sample_n):
    g.node(str(i))

for EI in G.Edges():
    u, v = EI.GetSrcNId(), EI.GetDstNId()
    if u < sample_n and v < sample_n:
        g.edge(str(u), str(v))

try:
    g.render('facebook_combined_sample', format='png', cleanup=True)
    print("Rendered → facebook_combined_sample.png")
except Exception as e:
    print(f"Warning: Graphviz render failed: {e}")

# ------------------------------------------------------------
# ⑥ Brooks 图检测
# ------------------------------------------------------------
is_brooks, reason = is_brooks_graph(adj_list)
print("\n=== Brooks 图检测结果 ===")
print(f"是否是 Brooks 图？ → {'是' if is_brooks else '否'}（{reason}）")
