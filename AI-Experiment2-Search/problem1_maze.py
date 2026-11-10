"""题目一：迷宫寻路（单位代价 A*）。"""

from __future__ import annotations

from astar import AStarStats, astar, grid_neighbors_4, manhattan


def parse_maze(grid: list[list[str]]) -> tuple[list[list[float | None]], tuple[int, int], tuple[int, int]]:
    costs = []
    start = end = None
    for i, row in enumerate(grid):
        crow = []
        for j, cell in enumerate(row):
            if cell == "X":
                crow.append(None)
            else:
                crow.append(1.0)
                if cell == "S":
                    start = (i, j)
                elif cell == "E":
                    end = (i, j)
        costs.append(crow)
    if start is None or end is None:
        raise ValueError("地图中需要包含 S 和 E")
    return costs, start, end


def solve_maze(
    start: tuple[int, int],
    end: tuple[int, int],
    grid: list[list[str]],
    *,
    heuristic: str = "manhattan",
    return_stats: bool = False,
):
    """
    返回从 start 到 end 的最短路径坐标列表；无解返回 []。
    heuristic: "manhattan" | "zero"
    """
    costs, s0, e0 = parse_maze(grid)
    # 允许调用方显式传入起终点（与测试用例格式一致）
    start = start or s0
    end = end or e0

    def h(n):
        if heuristic == "zero":
            return 0.0
        return float(manhattan(n, end))

    stats = AStarStats()
    path, _ = astar(
        start,
        lambda n: n == end,
        lambda n: grid_neighbors_4(costs, n),
        h,
        stats=stats,
    )
    result = path if path is not None else []
    if return_stats:
        return result, stats
    return result


SAMPLE_GRID = [
    ["S", ".", ".", "X", "."],
    [".", "X", ".", ".", "."],
    [".", "X", ".", "X", "."],
    [".", ".", ".", "X", "E"],
    ["X", "X", ".", ".", "."],
]

SAMPLE_START = (0, 0)
SAMPLE_END = (3, 4)
SAMPLE_PATH = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)]


if __name__ == "__main__":
    path, st = solve_maze(SAMPLE_START, SAMPLE_END, SAMPLE_GRID, return_stats=True)
    print("path:", path)
    print("len:", len(path) - 1 if path else None, "expanded:", st.expanded)
    assert path == SAMPLE_PATH or (path and len(path) == len(SAMPLE_PATH)), path
    # 允许其他等长最短路，但官方样例这条应当可被找到或至少等长
    assert path and len(path) == len(SAMPLE_PATH)
    print("题目一样例通过")
