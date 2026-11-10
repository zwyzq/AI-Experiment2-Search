"""题目四：竞争环境下的宝藏分配（A* 距离 + Minimax / Alpha-Beta）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from astar import AStarStats, astar, grid_neighbors_4, manhattan

# ---------- 地图与宝藏（与讲义一致）----------
MAP_RAW = [
    ["A", 1, 1, "X", 2, 1, "T1"],
    [1, "X", 6, "X", 1, "X", 1],
    [1, 1, "T2", 1, 1, 1, 1],
    ["X", 1, "X", 8, "X", 1, "X"],
    [1, 1, 1, 1, "T3", 1, 1],
    [1, "X", 9, "X", 1, "X", 1],
    ["T4", 1, 1, "X", 1, 1, "B"],
]

POINTS = {
    "A": (0, 0),
    "B": (6, 6),
    "T1": (0, 6),
    "T2": (2, 2),
    "T3": (4, 4),
    "T4": (6, 0),
}
VALUES = {"T1": 9, "T2": 6, "T3": 7, "T4": 7}
LABELS = ["A", "B", "T1", "T2", "T3", "T4"]


def parse_map(raw=MAP_RAW):
    costs = []
    for row in raw:
        crow = []
        for cell in row:
            if cell == "X":
                crow.append(None)
            elif isinstance(cell, str):
                crow.append(1.0)  # A / B / Ti 所在格代价为 1
            else:
                crow.append(float(cell))
        costs.append(crow)
    return costs


def point_distance(costs, src: tuple[int, int], dst: tuple[int, int], heuristic="manhattan"):
    """从 src 到 dst 的最小进入代价之和（起点不付费，进入 dst 付费）。"""
    if src == dst:
        return 0, [], AStarStats()

    def h(n):
        if heuristic == "zero":
            return 0.0
        # 每格最小代价为 1，标准曼哈顿可采纳
        return float(manhattan(n, dst))

    stats = AStarStats()
    path, cost = astar(
        src,
        lambda n: n == dst,
        lambda n: grid_neighbors_4(costs, n),
        h,
        stats=stats,
    )
    if path is None:
        return None, None, stats
    return int(cost) if cost == int(cost) else cost, path, stats


def distance_matrix(costs=None, heuristic="manhattan"):
    if costs is None:
        costs = parse_map()
    mat = {}
    stats_sum = AStarStats()
    for a in LABELS:
        mat[a] = {}
        for b in LABELS:
            d, path, st = point_distance(costs, POINTS[a], POINTS[b], heuristic)
            mat[a][b] = d
            stats_sum.expanded += st.expanded
    return mat


def print_matrix(mat):
    header = "     " + " ".join(f"{k:>4}" for k in LABELS)
    lines = [header]
    for a in LABELS:
        row = f"{a:>4} " + " ".join(f"{mat[a][b]:>4}" for b in LABELS)
        lines.append(row)
    return "\n".join(lines)


# ---------- 博弈搜索 ----------
@dataclass
class GameState:
    pos_a: str
    pos_b: str
    remaining: frozenset
    score_a: int
    score_b: int
    player: Literal["A", "B"]  # 当前行动方

    def utility(self) -> int:
        return self.score_a - self.score_b


@dataclass
class GameStats:
    nodes: int = 0
    leaves: int = 0
    prunes: int = 0


def apply_move(state: GameState, treasure: str, dist: dict) -> GameState:
    if state.player == "A":
        src = state.pos_a
        d = dist[src][treasure]
        gain = VALUES[treasure] - d
        return GameState(
            pos_a=treasure,
            pos_b=state.pos_b,
            remaining=state.remaining - {treasure},
            score_a=state.score_a + gain,
            score_b=state.score_b,
            player="B",
        )
    src = state.pos_b
    d = dist[src][treasure]
    gain = VALUES[treasure] - d
    return GameState(
        pos_a=state.pos_a,
        pos_b=treasure,
        remaining=state.remaining - {treasure},
        score_a=state.score_a,
        score_b=state.score_b + gain,
        player="A",
    )


def ordered_treasures(state: GameState, dist: dict, order: str) -> list[str]:
    items = list(state.remaining)
    if order == "natural":
        items.sort()  # T1, T2, T3, T4
    elif order == "reverse":
        items.sort(reverse=True)
    elif order == "gain_desc":
        # 按当前玩家即时收益从大到小（常能更早剪枝）
        src = state.pos_a if state.player == "A" else state.pos_b
        items.sort(key=lambda t: VALUES[t] - dist[src][t], reverse=True)
    elif order == "gain_asc":
        src = state.pos_a if state.player == "A" else state.pos_b
        items.sort(key=lambda t: VALUES[t] - dist[src][t])
    else:
        raise ValueError(order)
    return items


def search(
    state: GameState,
    depth: int,
    dist: dict,
    method: str,
    order: str,
    stats: GameStats,
    alpha=float("-inf"),
    beta=float("inf"),
) -> tuple[int, str | None]:
    """返回 (best_value, best_first_move)。best_first_move 仅对当前层有意义。"""
    stats.nodes += 1
    if depth == 0 or not state.remaining:
        stats.leaves += 1
        return state.utility(), None

    moves = ordered_treasures(state, dist, order)
    best_move = None

    if state.player == "A":
        best_val = float("-inf")
        for i, t in enumerate(moves):
            nxt = apply_move(state, t, dist)
            val, _ = search(nxt, depth - 1, dist, method, order, stats, alpha, beta)
            if val > best_val:
                best_val = val
                best_move = t
            if method == "alphabeta":
                if best_val >= beta:
                    stats.prunes += 1
                    break
                alpha = max(alpha, best_val)
        return int(best_val), best_move

    best_val = float("inf")
    for i, t in enumerate(moves):
        nxt = apply_move(state, t, dist)
        val, _ = search(nxt, depth - 1, dist, method, order, stats, alpha, beta)
        if val < best_val:
            best_val = val
            best_move = t
        if method == "alphabeta":
            if best_val <= alpha:
                stats.prunes += 1
                break
            beta = min(beta, best_val)
    return int(best_val), best_move


def solve(
    H: int,
    method: str = "alphabeta",
    order: str = "natural",
    dist: dict | None = None,
) -> dict:
    if dist is None:
        dist = distance_matrix()
    root = GameState(
        pos_a="A",
        pos_b="B",
        remaining=frozenset(VALUES),
        score_a=0,
        score_b=0,
        player="A",
    )
    stats = GameStats()
    value, move = search(root, H, dist, method, order, stats)
    return {
        "best_target": move,
        "best_value": value,
        "nodes": stats.nodes,
        "leaves": stats.leaves,
        "prunes": stats.prunes,
        "method": method,
        "order": order,
        "H": H,
    }


def first_move_gains(dist: dict) -> dict:
    """A 各首步的即时收益，以及 B 可能的应对（便于报告解释）。"""
    out = {}
    for t in VALUES:
        d = dist["A"][t]
        out[t] = {"dist": d, "gain_A": VALUES[t] - d}
    return out


if __name__ == "__main__":
    costs = parse_map()
    mat = distance_matrix(costs)
    print("距离矩阵：")
    print(print_matrix(mat))
    print("A 首步即时收益：", first_move_gains(mat))

    for H, expect_t, expect_v in ((2, "T2", -1), (4, "T3", 3)):
        for method in ("minimax", "alphabeta"):
            r = solve(H, method=method, order="natural", dist=mat)
            print(r)
            assert r["best_target"] == expect_t and r["best_value"] == expect_v, r
    print("题目四样例通过")
