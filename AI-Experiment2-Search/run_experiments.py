"""对照实验：启发函数、访问顺序、搜索深度，并导出图表与 JSON。"""

from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from astar import AStarStats
from problem1_maze import SAMPLE_END, SAMPLE_GRID, SAMPLE_START, solve_maze
from problem2_weighted import SAMPLE_END as W_END
from problem2_weighted import SAMPLE_GRID as W_GRID
from problem2_weighted import SAMPLE_START as W_START
from problem2_weighted import solve_weighted
from problem3_alphabeta import (
    TreeNode,
    alphabeta,
    build_sample_tree,
    build_sample_tree_independent,
    leaf_max,
    leaf_min,
    minimax,
    reorder_tree,
    solve_tree,
)
from problem4_treasure import (
    VALUES,
    apply_move,
    distance_matrix,
    first_move_gains,
    print_matrix,
    solve,
)

OUT = Path(__file__).resolve().parent / "outputs"
FIG = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

# 中文字体（在 Linux 盒子上可能没有，生成时再尝试；Mac 上重跑）
def setup_font():
    candidates = [
        "PingFang SC",
        "PingFang HK",
        "Heiti SC",
        "Songti SC",
        "Hiragino Sans GB",
        "Noto Sans CJK SC",
        "Noto Sans CJK SC Regular",
        "Source Han Sans SC",
        "WenQuanYi Micro Hei",
        "SimHei",
        "Arial Unicode MS",
    ]
    matplotlib.rcParams["font.sans-serif"] = candidates + matplotlib.rcParams["font.sans-serif"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def larger_maze(n=21, seed=0, wall_prob=0.28):
    rng = random.Random(seed)
    grid = [["." for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if rng.random() < wall_prob:
                grid[i][j] = "X"
    grid[0][0] = "S"
    grid[n - 1][n - 1] = "E"
    # 保证连通：如果无路则降低障碍重试
    return grid


def exp_problem1():
    rows = []
    for h in ("zero", "manhattan"):
        path, st = solve_maze(SAMPLE_START, SAMPLE_END, SAMPLE_GRID, heuristic=h, return_stats=True)
        rows.append({
            "case": "official",
            "heuristic": h,
            "path_len": len(path) - 1,
            "expanded": st.expanded,
            "generated": st.generated,
            "pushed": st.pushed,
            "path": path,
        })
    # 自设更大迷宫
    for n, seed, wp in ((15, 1, 0.25), (21, 2, 0.28), (31, 3, 0.30)):
        grid = None
        for s in range(seed, seed + 30):
            g = larger_maze(n, s, wp)
            path, st = solve_maze((0, 0), (n - 1, n - 1), g, heuristic="manhattan", return_stats=True)
            if path:
                grid = g
                break
        if not grid:
            continue
        for h in ("zero", "manhattan"):
            path, st = solve_maze((0, 0), (n - 1, n - 1), grid, heuristic=h, return_stats=True)
            rows.append({
                "case": f"maze_{n}_seed_ok",
                "n": n,
                "heuristic": h,
                "path_len": len(path) - 1 if path else None,
                "expanded": st.expanded,
                "generated": st.generated,
                "pushed": st.pushed,
            })
    return rows


def exp_problem2():
    rows = []
    for h in ("zero", "manhattan", "manhattan_minus_one"):
        cost, path, st = solve_weighted(
            W_START, W_END, W_GRID, heuristic=h, return_stats=True, return_path=True
        )
        rows.append({
            "heuristic": h,
            "cost": cost,
            "path": path,
            "expanded": st.expanded,
            "generated": st.generated,
            "pushed": st.pushed,
        })
    return rows


def random_tree(depth, branch, rng, lo=0, hi=20) -> TreeNode:
    if depth == 0:
        return TreeNode(value=rng.randint(lo, hi))
    return TreeNode(children=[random_tree(depth - 1, branch, rng, lo, hi) for _ in range(branch)])


def exp_problem3():
    root = build_sample_tree_independent()
    rows = []
    for method in ("minimax", "alphabeta"):
        val, st = solve_tree(root, method, return_stats=True)
        rows.append({
            "tree": "official",
            "order": "left_to_right",
            "method": method,
            "value": val,
            "nodes": st.nodes,
            "leaves": st.leaves,
            "prunes": st.prunes,
        })

    # 不同访问顺序：按叶最大值 / 最小值排序
    orders = {
        "left_to_right": root,
        "leafmax_desc": reorder_tree(root, leaf_max, reverse=True),
        "leafmax_asc": reorder_tree(root, leaf_max, reverse=False),
        "leafmin_desc": reorder_tree(root, leaf_min, reverse=True),
        "leafmin_asc": reorder_tree(root, leaf_min, reverse=False),
    }
    for name, t in orders.items():
        val, st = solve_tree(t, "alphabeta", return_stats=True)
        rows.append({
            "tree": "official",
            "order": name,
            "method": "alphabeta",
            "value": val,
            "nodes": st.nodes,
            "leaves": st.leaves,
            "prunes": st.prunes,
        })

    # 自设更大随机树
    rng = random.Random(42)
    big = random_tree(depth=6, branch=3, rng=rng)  # 3^6 = 729 leaves if full; depth 6 from root is 6 plies, 3**6 leaves
    # depth=6 means 6 levels below? My fn: depth 0 is leaf. depth=5 -> 3^5=243 leaves. Let's use depth=5 branch=3.
    rng = random.Random(42)
    big = random_tree(depth=5, branch=3, rng=rng)
    val_m, sm = solve_tree(big, "minimax", return_stats=True)
    val_a, sa = solve_tree(big, "alphabeta", return_stats=True)
    assert val_m == val_a
    rows.append({
        "tree": "random_d5_b3",
        "order": "left_to_right",
        "method": "minimax",
        "value": val_m,
        "nodes": sm.nodes,
        "leaves": sm.leaves,
        "prunes": 0,
    })
    rows.append({
        "tree": "random_d5_b3",
        "order": "left_to_right",
        "method": "alphabeta",
        "value": val_a,
        "nodes": sa.nodes,
        "leaves": sa.leaves,
        "prunes": sa.prunes,
    })
    # 好顺序 vs 坏顺序
    big_good = reorder_tree(big, leaf_max, reverse=True)
    big_bad = reorder_tree(big, leaf_max, reverse=False)
    for name, t in (("leafmax_desc", big_good), ("leafmax_asc", big_bad)):
        val, st = solve_tree(t, "alphabeta", return_stats=True)
        assert val == val_m
        rows.append({
            "tree": "random_d5_b3",
            "order": name,
            "method": "alphabeta",
            "value": val,
            "nodes": st.nodes,
            "leaves": st.leaves,
            "prunes": st.prunes,
        })
    return rows


def enumerate_first_moves(dist, H, method="minimax"):
    """固定 A 的首步，再搜索剩余深度，得到各首步对应的 U。"""
    from problem4_treasure import GameState, GameStats, search

    root = GameState("A", "B", frozenset(VALUES), 0, 0, "A")
    out = []
    for t in sorted(VALUES):
        nxt = apply_move(root, t, dist)
        stats = GameStats()
        val, reply = search(nxt, H - 1, dist, method, "natural", stats)
        out.append({
            "first": t,
            "U": val,
            "B_reply": reply,
            "gain_A": VALUES[t] - dist["A"][t],
            "nodes": stats.nodes,
        })
    return out


def reconstruct_pv(dist, H, first=None):
    """重建一条主变例（双方按最优走）。"""
    from problem4_treasure import GameState, GameStats, search

    st = GameState("A", "B", frozenset(VALUES), 0, 0, "A")
    moves = []
    depth = H
    if first is not None:
        nxt = apply_move(st, first, dist)
        gain = VALUES[first] - dist[st.pos_a][first]
        moves.append({"player": "A", "target": first, "gain": gain, "U_after": nxt.utility()})
        st = nxt
        depth -= 1
    while depth > 0 and st.remaining:
        stats = GameStats()
        val, mv = search(st, depth, dist, "minimax", "natural", stats)
        if mv is None:
            break
        src = st.pos_a if st.player == "A" else st.pos_b
        gain = VALUES[mv] - dist[src][mv]
        nxt = apply_move(st, mv, dist)
        moves.append({
            "player": st.player,
            "target": mv,
            "gain": gain,
            "U_after": nxt.utility(),
            "backed_value": val,
        })
        st = nxt
        depth -= 1
    return {"final_U": st.utility(), "score_a": st.score_a, "score_b": st.score_b, "moves": moves}


def exp_problem4():
    dist = distance_matrix()
    rows = []
    for H in (2, 4):
        for method in ("minimax", "alphabeta"):
            for order in ("natural", "reverse", "gain_desc", "gain_asc"):
                r = solve(H, method=method, order=order, dist=dist)
                rows.append(r)
    first_h2 = enumerate_first_moves(dist, 2)
    first_h4 = enumerate_first_moves(dist, 4)
    pvs = {
        "H2_best": reconstruct_pv(dist, 2),
        "H4_best": reconstruct_pv(dist, 4),
        "H4_if_T2": reconstruct_pv(dist, 4, first="T2"),
        "H2_if_T3": reconstruct_pv(dist, 2, first="T3"),
    }
    return {
        "matrix": {a: dist[a] for a in dist},
        "matrix_text": print_matrix(dist),
        "first_gains": first_move_gains(dist),
        "search_rows": rows,
        "first_moves_H2": first_h2,
        "first_moves_H4": first_h4,
        "principal_variations": pvs,
    }


def make_figures(p1, p2, p3, p4):
    setup_font()

    # 图1：题目一 启发函数节点数（官方 + 自设）
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    official = [r for r in p1 if r["case"] == "official"]
    # group larger mazes
    labels, zero, manh = [], [], []
    labels.append("官方迷宫")
    z = next(r for r in official if r["heuristic"] == "zero")
    m = next(r for r in official if r["heuristic"] == "manhattan")
    zero.append(z["expanded"])
    manh.append(m["expanded"])
    seen = set()
    for r in p1:
        if r["case"].startswith("maze_") and r["heuristic"] == "zero":
            key = r["case"] + str(r.get("n"))
            if key in seen:
                continue
            seen.add(key)
            n = r["n"]
            zz = r["expanded"]
            mm = next(
                x["expanded"]
                for x in p1
                if x.get("n") == n and x["heuristic"] == "manhattan" and x["case"] == r["case"]
            )
            labels.append(f"{n}×{n} 迷宫")
            zero.append(zz)
            manh.append(mm)
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, zero, w, label="h=0（Dijkstra）", color="#7BA3C9")
    ax.bar(x + w / 2, manh, w, label="曼哈顿距离", color="#2B6CB0")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("扩展节点数")
    ax.set_title("题目一：不同启发函数的搜索节点数")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "p1_heuristic_nodes.png", dpi=160)
    plt.close()

    # 图2：题目二启发函数
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    names = {"zero": "h=0", "manhattan": "曼哈顿", "manhattan_minus_one": "曼哈顿-1（可采纳）"}
    xs = [names[r["heuristic"]] for r in p2]
    ys = [r["expanded"] for r in p2]
    colors = ["#7BA3C9", "#E07A5F", "#2B6CB0"]
    bars = ax.bar(xs, ys, color=colors)
    for b, r in zip(bars, p2):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15, f"代价={r['cost']}", ha="center", fontsize=8)
    ax.set_ylabel("扩展节点数")
    ax.set_title("题目二：启发函数对节点数与最优性的影响")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "p2_heuristic_nodes.png", dpi=160)
    plt.close()

    # 图3：题目三 官方树 minimax vs ab + 顺序
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    official_ab = [r for r in p3 if r["tree"] == "official" and r["method"] == "alphabeta"]
    # unique orders
    order_label = {
        "left_to_right": "从左到右",
        "leafmax_desc": "叶最大值降序",
        "leafmax_asc": "叶最大值升序",
        "leafmin_desc": "叶最小值降序",
        "leafmin_asc": "叶最小值升序",
    }
    # include minimax as reference
    mm = next(r for r in p3 if r["tree"] == "official" and r["method"] == "minimax")
    labels = ["Minimax"]
    vals = [mm["nodes"]]
    for r in official_ab:
        if r["order"] == "left_to_right" and "Minimax" in labels:
            labels.append("AB 从左到右")
            vals.append(r["nodes"])
        elif r["order"] != "left_to_right":
            labels.append("AB " + order_label.get(r["order"], r["order"]))
            vals.append(r["nodes"])
    ax.bar(range(len(labels)), vals, color=["#9AA8B5"] + ["#2B6CB0"] * (len(labels) - 1))
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("访问节点数")
    ax.set_title("题目三：访问顺序对 Alpha-Beta 剪枝开销的影响（官方树）")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "p3_order_nodes.png", dpi=160)
    plt.close()

    # 图3b 随机大树
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    big = [r for r in p3 if r["tree"] == "random_d5_b3"]
    lab_map = {
        ("minimax", "left_to_right"): "Minimax",
        ("alphabeta", "left_to_right"): "AB 原顺序",
        ("alphabeta", "leafmax_desc"): "AB 好顺序",
        ("alphabeta", "leafmax_asc"): "AB 坏顺序",
    }
    labels, vals = [], []
    for r in big:
        k = (r["method"], r["order"])
        if k in lab_map:
            labels.append(lab_map[k])
            vals.append(r["nodes"])
    ax.bar(labels, vals, color=["#9AA8B5", "#7BA3C9", "#2B6CB0", "#E07A5F"])
    ax.set_ylabel("访问节点数")
    ax.set_title("自设实验：随机树（深度5、分支3）上的剪枝效率")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "p3_random_tree.png", dpi=160)
    plt.close()

    # 图4：题目四 各首步在 H=2/H=4 的 U
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ts = [r["first"] for r in p4["first_moves_H2"]]
    u2 = [r["U"] for r in p4["first_moves_H2"]]
    u4 = [r["U"] for r in p4["first_moves_H4"]]
    x = np.arange(len(ts))
    w = 0.35
    ax.bar(x - w / 2, u2, w, label="H=2", color="#7BA3C9")
    ax.bar(x + w / 2, u4, w, label="H=4（完整对局）", color="#2B6CB0")
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(ts)
    ax.set_ylabel("收益差 U = Score_A − Score_B")
    ax.set_title("题目四：A 各首步在不同搜索深度下的最优收益差")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "p4_first_moves.png", dpi=160)
    plt.close()

    # 图5：H=4 不同方法/顺序节点数
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    rows = [r for r in p4["search_rows"] if r["H"] == 4]
    # grouped
    orders = ["natural", "reverse", "gain_desc", "gain_asc"]
    ol = {"natural": "自然顺序", "reverse": "逆序", "gain_desc": "即时收益降序", "gain_asc": "即时收益升序"}
    mm = [next(r["nodes"] for r in rows if r["method"] == "minimax" and r["order"] == o) for o in orders]
    ab = [next(r["nodes"] for r in rows if r["method"] == "alphabeta" and r["order"] == o) for o in orders]
    x = np.arange(len(orders))
    ax.bar(x - w / 2, mm, w, label="Minimax", color="#9AA8B5")
    ax.bar(x + w / 2, ab, w, label="Alpha-Beta", color="#2B6CB0")
    ax.set_xticks(x)
    ax.set_xticklabels([ol[o] for o in orders])
    ax.set_ylabel("访问节点数")
    ax.set_title("题目四（H=4）：搜索方法与访问顺序对节点数的影响")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "p4_search_nodes.png", dpi=160)
    plt.close()

    # 图6：距离矩阵热力图
    labels = ["A", "B", "T1", "T2", "T3", "T4"]
    mat = np.array([[p4["matrix"][a][b] for b in labels] for a in labels], dtype=float)
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    im = ax.imshow(mat, cmap="Blues")
    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, int(mat[i, j]), ha="center", va="center",
                    color="white" if mat[i, j] > mat.max() / 2 else "black", fontsize=8)
    ax.set_title("A、B 与四座宝藏两两最短代价")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(FIG / "p4_distance_matrix.png", dpi=160)
    plt.close()


def main():
    p1 = exp_problem1()
    p2 = exp_problem2()
    p3 = exp_problem3()
    p4 = exp_problem4()
    summary = {"problem1": p1, "problem2": p2, "problem3": p3, "problem4": p4}
    with open(OUT / "experiment_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    make_figures(p1, p2, p3, p4)
    print(json.dumps({
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "p4_first_H2": p4["first_moves_H2"],
        "p4_first_H4": p4["first_moves_H4"],
        "p4_pv": p4["principal_variations"],
        "p4_rows": p4["search_rows"],
        "matrix": p4["matrix_text"],
    }, ensure_ascii=False, indent=2, default=str))
    print("figures:", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()
