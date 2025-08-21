from collections import deque
import itertools


def is_brooks_graph(adj):
    n = len(adj)

    # 1. 判断连通性（BFS）
    visited = [False] * n
    def bfs(start):
        queue = deque([start])
        visited[start] = True
        while queue:
            v = queue.popleft()
            for u in adj[v]:
                if not visited[u]:
                    visited[u] = True
                    queue.append(u)

    bfs(0)
    if not all(visited):
        return False, "图不连通"

    # 2. 判断是否是完全图（每个顶点度数为 n-1）
    if all(len(adj[v]) == n - 1 for v in range(n)):
        return False, "图是完全图"

    # 3. 判断是否是奇圈（即长度为奇数的简单环图）
    if all(len(adj[v]) == 2 for v in range(n)):
        # 每个点度数为2，可能是环图
        # 用 BFS 检查是否有奇数个点 + 环
        def is_cycle():
            count = 0
            v = 0
            prev = -1
            visited_cycle = set()
            while v not in visited_cycle:
                visited_cycle.add(v)
                count += 1
                neighbors = [u for u in adj[v] if u != prev]
                if not neighbors:
                    return False
                prev, v = v, neighbors[0]
            return count == len(adj) and count % 2 == 1

        if is_cycle():
            return False, "图是奇圈"

    # 都通过则为 Brooks 图
    return True, "图是 Brooks 图"
