from collections import deque
import time


def run_delta_list_coloring(adj):
    t0 = time.perf_counter()
    colors = delta_list_coloring(adj)
    t1 = time.perf_counter()
    num_colors = len(set(colors))
    elapsed_ms = (t1 - t0) * 1000
    return {
        'colors': colors,
        'num_colors': num_colors,
        'elapsed_ms': elapsed_ms
    }


def delta_list_coloring(adj):
    n = len(adj)
    degrees = [len(neigh) for neigh in adj]
    Delta = max(degrees)

    if any(degree < Delta for degree in degrees):
        return greedy_coloring_nonregular(adj, Delta)

    biconn = dfs_biconnected(adj)
    colors = [-1] * n

    cycle = find_even_cycle(biconn, adj)
    if cycle:
        color_cycle(cycle, colors)
    else:
        whel = find_whel(biconn, adj)
        if whel:
            hub, rim = whel
            color_whel(hub, rim, colors)
        else:
            theta = find_theta(biconn, adj)
            if theta:
                u, v, paths = theta
                color_theta(u, v, paths, colors)
            else:
                raise RuntimeError("未找到可行子结构，理论不应发生")

    return complete_coloring(adj, colors, Delta)


def greedy_coloring_nonregular(adj, Delta):
    n = len(adj)
    visited = [False] * n
    order = []
    start = next(i for i in range(n) if len(adj[i]) < Delta)
    q = deque([start])
    visited[start] = True
    while q:
        v = q.popleft()
        order.append(v)
        for u in adj[v]:
            if not visited[u]:
                visited[u] = True
                q.append(u)
    colors = [-1] * n
    for v in reversed(order):
        used = {colors[u] for u in adj[v] if colors[u] != -1}
        for c in range(Delta):
            if c not in used:
                colors[v] = c
                break
    return colors


def complete_coloring(adj, colors, Delta):
    n = len(adj)
    visited = [c != -1 for c in colors]
    q = deque([v for v in range(n) if visited[v]])
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for u in adj[v]:
            if not visited[u]:
                visited[u] = True
                q.append(u)
    for v in reversed(order):
        if colors[v] != -1:
            continue
        used = {colors[u] for u in adj[v] if colors[u] != -1}
        for c in range(Delta):
            if c not in used:
                colors[v] = c
                break
    return colors


def dfs_biconnected(adj):
    n = len(adj)
    index = [None] * n
    lowlink = [None] * n
    stack = []
    result = []
    idx = [0]

    def dfs(v, parent):
        index[v] = lowlink[v] = idx[0]
        idx[0] += 1
        for w in adj[v]:
            if index[w] is None:
                stack.append((v, w))
                dfs(w, v)
                lowlink[v] = min(lowlink[v], lowlink[w])
                if lowlink[w] >= index[v]:
                    block = set()
                    while stack:
                        x, y = stack.pop()
                        block.update([x, y])
                        if (x, y) == (v, w) or (x, y) == (w, v):
                            break
                    if len(block) >= 3:
                        result.append(block)
            elif w != parent and index[w] < index[v]:
                lowlink[v] = min(lowlink[v], index[w])
                stack.append((v, w))
    for v in range(n):
        if index[v] is None:
            dfs(v, -1)
    return result[0] if result else set(range(n))


def find_even_cycle(biconn, adj):
    n = len(adj)
    parent = [-1] * n
    depth = [0] * n
    visited = [False] * n

    def dfs(v):
        visited[v] = True
        for u in adj[v]:
            if u not in biconn:
                continue
            if not visited[u]:
                parent[u] = v
                depth[u] = depth[v] + 1
                dfs(u)
            elif depth[u] < depth[v] - 1 and (depth[v] - depth[u] + 1) % 2 == 0:
                cycle = []
                x = v
                while x != u:
                    cycle.append(x)
                    x = parent[x]
                cycle.append(u)
                return cycle[::-1]
        return None

    for v in biconn:
        if not visited[v]:
            res = dfs(v)
            if res:
                return res
    return None


def find_whel(biconn, adj):
    n = len(adj)
    for hub in biconn:
        neighbors = [u for u in adj[hub] if u in biconn]
        if len(neighbors) < 2:
            continue
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                u, v = neighbors[i], neighbors[j]
                visited = [False] * n
                q = deque([(u, [u])])
                visited[hub] = True
                visited[u] = True
                found = None
                while q:
                    x, path = q.popleft()
                    if x == v:
                        found = path
                        break
                    for w in adj[x]:
                        if w in biconn and not visited[w] and w != hub:
                            visited[w] = True
                            q.append((w, path + [w]))
                if found:
                    return (hub, found)
    return None


def find_theta(biconn, adj):
    n = len(adj)
    for u in biconn:
        for v in biconn:
            if u >= v:
                continue
            paths = []

            def dfs(x, target, path, visited):
                if x == target:
                    paths.append(path)
                    return
                for w in adj[x]:
                    if w in biconn and w not in visited:
                        dfs(w, target, path + [w], visited | {w})

            dfs(u, v, [u], {u})
            if len(paths) >= 3:
                return (u, v, paths[:3])
    return None


def color_cycle(cycle, colors):
    for i, v in enumerate(cycle):
        colors[v] = i % 2


def color_whel(hub, rim_path, colors):
    colors[hub] = 0
    color_cycle(rim_path, colors)


def color_theta(u, v, paths, colors):
    colors[u] = 0
    colors[v] = 1
    for path in paths:
        for idx, node in enumerate(path):
            if node != u and node != v and colors[node] == -1:
                colors[node] = (idx % 2) + 2
