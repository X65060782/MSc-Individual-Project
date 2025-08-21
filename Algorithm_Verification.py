import snap
from Δ_list_coloring_Algorithm import run_delta_list_coloring


# ------------------------------------------------------------
# ① 用 SNAP 构建 6个节点的路径图 P6
#    结构： 0 - 1 - 2 - 3 - 4 - 5
# ------------------------------------------------------------
G = snap.TUNGraph.New()

N = 6
for i in range(N):
    G.AddNode(i)

for i in range(N - 1):
    G.AddEdge(i, i + 1)

print(f"P6 Graph loaded → {G.GetNodes()} nodes, {G.GetEdges()} edges")

# ------------------------------------------------------------
# ② 转为邻接表供算法使用
# ------------------------------------------------------------
adj_list = [[] for _ in range(G.GetNodes())]
for EI in G.Edges():
    u, v = EI.GetSrcNId(), EI.GetDstNId()
    adj_list[u].append(v)
    adj_list[v].append(u)

Delta = max(len(neis) for neis in adj_list)
print(f"Max degree Δ = {Delta}")

# ------------------------------------------------------------
# ③ 使用封装好的 Δ-list-coloring 算法
# ------------------------------------------------------------
result_dl = run_delta_list_coloring(adj_list)

# ------------------------------------------------------------
# ④ 输出结果验证
# ------------------------------------------------------------
print("\n=== P6 Path Graph Coloring Result ===")
print(f"Δ-list-coloring → {result_dl['num_colors']} colors, time {result_dl['elapsed_ms']:.3f} ms")
print(f"Coloring Result (per node): {result_dl['colors']}")

# ------------------------------------------------------------
# ⑤ 验证结果是否正确
# ------------------------------------------------------------
def is_valid(adj, colors):
    for u in range(len(adj)):
        for v in adj[u]:
            if colors[u] == colors[v]:
                return False
    return True


print("Coloring valid?", is_valid(adj_list, result_dl['colors']))




# ------------------------------------------------------------

def build_almost_complete_graph(n):
    """返回 SNAP 图对象，n 节点，缺一条边的完全图"""
    G = snap.TUNGraph.New()
    for i in range(n):
        G.AddNode(i)
    for i in range(n):
        for j in range(i + 1, n):
            # 故意漏掉最后一条边 (0, n-1)
            if not (i == 0 and j == n - 1):
                G.AddEdge(i, j)
    return G


def convert_to_adj_list(G):
    N = G.GetNodes()
    adj_list = [[] for _ in range(N)]
    for EI in G.Edges():
        u, v = EI.GetSrcNId(), EI.GetDstNId()
        adj_list[u].append(v)
        adj_list[v].append(u)
    return adj_list


# ----------------- 测试 4-10 偶数节点，缺一条边的完全图 ------------------
print("\n=== Almost Complete Graphs (Even n, Missing One Edge, Brooks case, Δ = n-1) ===")
for n in [4, 6, 8, 10]:
    G = build_almost_complete_graph(n)
    adj_list = convert_to_adj_list(G)
    Delta = max(len(neis) for neis in adj_list)
    result_dl = run_delta_list_coloring(adj_list)
    print(f"n = {n}, missing 1 edge, Δ = {Delta} → Δ-list-coloring 用色 {result_dl['num_colors']}, time {result_dl['elapsed_ms']:.3f} ms")
