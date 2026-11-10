"""通用 A* 搜索（四方向），同时统计扩展/入队节点数。"""

from __future__ import annotations

import heapq
from typing import Callable, Hashable, Iterable, Optional


class AStarStats:
    def __init__(self):
        self.expanded = 0  # 从优先队列中弹出并真正扩展的节点数
        self.generated = 0  # 产生的后继（入堆）次数
        self.pushed = 0


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    start: Hashable,
    is_goal: Callable[[Hashable], bool],
    neighbors: Callable[[Hashable], Iterable[tuple[Hashable, float]]],
    heuristic: Callable[[Hashable], float],
    *,
    stats: Optional[AStarStats] = None,
) -> tuple[list[Hashable], float] | tuple[None, float]:
    """
    返回 (path, cost)。无解时 path 为 None，cost 为 inf。
    neighbors(node) 产出 (next_node, step_cost)。
    """
    if stats is None:
        stats = AStarStats()

    g = {start: 0.0}
    parent = {start: None}
    # (f, tie, g, node)  — tie 保证比较稳定
    tie = 0
    heap = [(heuristic(start), tie, 0.0, start)]
    stats.pushed += 1
    closed = set()

    while heap:
        f, _, g_cur, node = heapq.heappop(heap)
        if node in closed:
            continue
        # 过时条目
        if g_cur > g.get(node, float("inf")):
            continue
        closed.add(node)
        stats.expanded += 1

        if is_goal(node):
            path = []
            cur = node
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path, g[node]

        for nxt, step in neighbors(node):
            stats.generated += 1
            ng = g[node] + step
            if ng < g.get(nxt, float("inf")):
                g[nxt] = ng
                parent[nxt] = node
                tie += 1
                heapq.heappush(heap, (ng + heuristic(nxt), tie, ng, nxt))
                stats.pushed += 1

    return None, float("inf")


def grid_neighbors_4(
    grid_cost: list[list[Optional[float]]],
    pos: tuple[int, int],
    *,
    goal: tuple[int, int] | None = None,
    goal_cost_override: float | None = None,
):
    """进入格子的代价取 grid_cost[r][c]；None 表示障碍。
    若指定 goal_cost_override，进入终点时使用该代价（题目二中 E 视为 0）。
    """
    rows, cols = len(grid_cost), len(grid_cost[0])
    r, c = pos
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid_cost[nr][nc] is not None:
            cost = grid_cost[nr][nc]
            if goal is not None and goal_cost_override is not None and (nr, nc) == goal:
                cost = goal_cost_override
            yield (nr, nc), float(cost)
