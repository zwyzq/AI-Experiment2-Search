# 实验二：搜索算法

当代人工智能实验课 —— A* 寻路与 Alpha-Beta 剪枝。

## 环境

Python 3.8+（本机 Anaconda 已验证）。绘图需要 matplotlib：

```bash
pip install -r requirements.txt
```

## 运行官方样例

在项目根目录执行：

```bash
python main.py
```

将依次运行四道题目并核对讲义中的预期输出。

## 对照实验与图表

```bash
python run_experiments.py
```

结果写入 `outputs/experiment_summary.json`，图表写入 `figures/`。

## 生成实验报告 PDF

```bash
python generate_report_pdf.py
```

报告开头需填写 GitHub 仓库链接。若你已推送仓库，把 `generate_report_pdf.py` 与 `report.md` 中的占位 URL 改成实际地址后再生成。

## 代码结构

- `astar.py`：通用 A*（统计扩展节点）
- `problem1_maze.py`：单位代价迷宫最短路
- `problem2_weighted.py`：加权地形最小代价（终点进入代价为 0）
- `problem3_alphabeta.py`：Minimax 与 Alpha-Beta
- `problem4_treasure.py`：距离矩阵 + 宝藏博弈
- `main.py` / `run_experiments.py`

随机种子：对照实验中的随机迷宫与随机树使用固定种子，结果可复现。
