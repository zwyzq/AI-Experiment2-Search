"""实验二入口：运行四道题目的官方测试用例。"""

from problem1_maze import SAMPLE_END, SAMPLE_GRID, SAMPLE_PATH, SAMPLE_START, solve_maze
from problem2_weighted import SAMPLE_COST, SAMPLE_END as W_END
from problem2_weighted import SAMPLE_GRID as W_GRID
from problem2_weighted import SAMPLE_START as W_START
from problem2_weighted import solve_weighted
from problem3_alphabeta import build_sample_tree, solve_tree
from problem4_treasure import distance_matrix, print_matrix, solve


def main():
    print("=" * 50)
    print("题目一：迷宫寻路")
    path = solve_maze(SAMPLE_START, SAMPLE_END, SAMPLE_GRID)
    print("路径:", path)
    assert path == SAMPLE_PATH
    print("通过")

    print("=" * 50)
    print("题目二：加权地形")
    cost, path = solve_weighted(W_START, W_END, W_GRID, return_path=True)
    print("最小代价:", cost)
    print("路径:", path)
    assert cost == SAMPLE_COST
    print("通过")

    print("=" * 50)
    print("题目三：Alpha-Beta 剪枝")
    val = solve_tree(build_sample_tree(), "alphabeta")
    print("MAX 最佳得分:", val)
    assert val == 5
    print("通过")

    print("=" * 50)
    print("题目四：宝藏分配")
    dist = distance_matrix()
    print("6×6 距离矩阵：")
    print(print_matrix(dist))
    r2 = solve(2, dist=dist)
    r4 = solve(4, dist=dist)
    print("H=2:", {"best_target": r2["best_target"], "best_value": r2["best_value"]})
    print("H=4:", {"best_target": r4["best_target"], "best_value": r4["best_value"]})
    assert r2["best_target"] == "T2" and r2["best_value"] == -1
    assert r4["best_target"] == "T3" and r4["best_value"] == 3
    print("通过")
    print("=" * 50)
    print("全部官方样例通过。对照实验请运行: python run_experiments.py")


if __name__ == "__main__":
    main()
