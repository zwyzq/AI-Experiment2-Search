"""题目二：加权地形 A*。进入格子的代价等于该格权值；终点 E 进入代价为 0。"""

from __future__ import annotations

from astar import AStarStats, astar, grid_neighbors_4, manhattan


def parse_weighted(grid) -> tuple[list[list[float | None]], tuple[int, int], tuple[int, int], float]:
    costs = []
    start = end = None
    positive = []
    for i, row in enumerate(grid):
        crow = []
        for j, cell in enumerate(row):
            if cell in ("X", "x"):
                crow.append(None)
                continue
            if cell == "S":
                start = (i, j)
                crow.append(0.0)  # 起点已在其上，不付进入代价
                continue
            if cell == "E":
                end = (i, j)
                crow.append(0.0)  # 题目规定 E 视为 0
                continue
            v = float(cell)
            crow.append(v)
            if v > 0:
                positive.append(v)
        costs.append(crow)
    min_pos = min(positive) if positive else 1.0
    return costs, start, end, min_pos


def heuristic_fn(kind: str, end: tuple[int, int], min_pos: float):
    def h(n):
        d = manhattan(n, end)
        if kind == "zero":
            return 0.0
        if kind == "manhattan":
            # 每步至少 1？但最后一步进入 E 代价为 0，可能高估
            return float(d)
        if kind == "manhattan_minus_one":
            # 可采纳：到达 E 前最多 d-1 步需付正代价
            return float(max(0, d - 1) * min_pos)
        raise ValueError(kind)
    return h


def solve_weighted(
    start: tuple[int, int],
    end: tuple[int, int],
    grid,
    *,
    heuristic: str = "manhattan_minus_one",
    return_stats: bool = False,
    return_path: bool = False,
):
    """返回最小总代价；无解返回 -1。"""
    costs, s0, e0, min_pos = parse_weighted(grid)
    start = start or s0
    end = end or e0
    stats = AStarStats()
    path, cost = astar(
        start,
        lambda n: n == end,
        lambda n: grid_neighbors_4(costs, n, goal=end, goal_cost_override=0.0),
        heuristic_fn(heuristic, end, min_pos),
        stats=stats,
    )
    result = -1 if path is None else int(cost) if cost == int(cost) else cost
    if return_stats and return_path:
        return result, path, stats
    if return_stats:
        return result, stats
    if return_path:
        return result, path
    return result


SAMPLE_GRID = [
    ["S", 1, 1, 8, 1],
    [1, 8, 3, 1, 1],
    [1, 8, 1, 8, 1],
    [1, 1, 1, 8, 1],
    [8, 8, 1, 1, "E"],
]
SAMPLE_START = (0, 0)
SAMPLE_END = (4, 4)
SAMPLE_COST = 7
SAMPLE_PATH = [
    (0, 0),
    (1, 0),
    (2, 0),
    (3, 0),
    (3, 1),
    (3, 2),
    (4, 2),
    (4, 3),
    (4, 4),
]


if __name__ == "__main__":
    cost, path, st = solve_weighted(
        SAMPLE_START, SAMPLE_END, SAMPLE_GRID, return_stats=True, return_path=True
    )
    print("cost:", cost, "path:", path, "expanded:", st.expanded)
    assert cost == SAMPLE_COST, cost
    # 等长/等价代价路径即可
    print("题目二样例通过")
