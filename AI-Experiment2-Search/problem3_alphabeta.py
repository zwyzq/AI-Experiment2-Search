"""题目三：极大极小博弈树与 Alpha-Beta 剪枝。根节点为 MAX。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TreeNode:
    value: int | None = None
    children: list["TreeNode"] = field(default_factory=list)

    def is_leaf(self) -> bool:
        return not self.children


@dataclass
class SearchStats:
    nodes: int = 0          # 访问的节点数（含叶子）
    leaves: int = 0
    prunes: int = 0         # 发生剪枝的次数（切断的兄弟分支批次数）
    pruned_children: int = 0


def minimax(node: TreeNode, maximizing: bool, stats: SearchStats | None = None) -> int:
    if stats is None:
        stats = SearchStats()
    stats.nodes += 1
    if node.is_leaf():
        stats.leaves += 1
        return int(node.value)
    if maximizing:
        return max(minimax(ch, False, stats) for ch in node.children)
    return min(minimax(ch, True, stats) for ch in node.children)


def alphabeta(
    node: TreeNode,
    maximizing: bool,
    alpha: float = float("-inf"),
    beta: float = float("inf"),
    stats: SearchStats | None = None,
) -> int:
    if stats is None:
        stats = SearchStats()
    stats.nodes += 1
    if node.is_leaf():
        stats.leaves += 1
        return int(node.value)
    if maximizing:
        value = float("-inf")
        for i, ch in enumerate(node.children):
            value = max(value, alphabeta(ch, False, alpha, beta, stats))
            if value >= beta:
                stats.prunes += 1
                stats.pruned_children += len(node.children) - i - 1
                break
            alpha = max(alpha, value)
        return int(value)
    value = float("inf")
    for i, ch in enumerate(node.children):
        value = min(value, alphabeta(ch, True, alpha, beta, stats))
        if value <= alpha:
            stats.prunes += 1
            stats.pruned_children += len(node.children) - i - 1
            break
        beta = min(beta, value)
    return int(value)


def solve_tree(root: TreeNode, method: str = "alphabeta", return_stats: bool = False):
    stats = SearchStats()
    if method == "minimax":
        val = minimax(root, True, stats)
    elif method == "alphabeta":
        val = alphabeta(root, True, stats=stats)
    else:
        raise ValueError(method)
    return (val, stats) if return_stats else val


def reorder_tree(node: TreeNode, key, reverse=False) -> TreeNode:
    """按叶子静态估值的某种聚合，重排子节点访问顺序（用于对照实验）。"""
    if node.is_leaf():
        return TreeNode(value=node.value)
    new_children = [reorder_tree(ch, key, reverse) for ch in node.children]
    new_children.sort(key=key, reverse=reverse)
    return TreeNode(children=new_children)


def leaf_max(node: TreeNode) -> int:
    if node.is_leaf():
        return int(node.value)
    return max(leaf_max(ch) for ch in node.children)


def leaf_min(node: TreeNode) -> int:
    if node.is_leaf():
        return int(node.value)
    return min(leaf_min(ch) for ch in node.children)


def build_sample_tree() -> TreeNode:
    """官方构建示例：min2 与 min1 共享 max2（6,9）。"""
    leaf1 = TreeNode(value=3)
    leaf2 = TreeNode(value=5)
    leaf3 = TreeNode(value=6)
    leaf4 = TreeNode(value=9)
    leaf5 = TreeNode(value=1)
    leaf6 = TreeNode(value=2)
    max1 = TreeNode(children=[leaf1, leaf2])
    max2 = TreeNode(children=[leaf3, leaf4])
    max3 = TreeNode(children=[leaf5, leaf6])
    min1 = TreeNode(children=[max1, max2])
    min2 = TreeNode(children=[max2, max3])
    return TreeNode(children=[min1, min2])


def build_sample_tree_independent() -> TreeNode:
    """若按示意图把 (6,9) 复制成两份独立子树（不共享节点）。结果应相同。"""
    def leaves(a, b):
        return TreeNode(children=[TreeNode(value=a), TreeNode(value=b)])

    max1 = leaves(3, 5)
    max2a = leaves(6, 9)
    max2b = leaves(6, 9)
    max3 = leaves(1, 2)
    min1 = TreeNode(children=[max1, max2a])
    min2 = TreeNode(children=[max2b, max3])
    return TreeNode(children=[min1, min2])


if __name__ == "__main__":
    root = build_sample_tree()
    v1, s1 = solve_tree(root, "minimax", return_stats=True)
    v2, s2 = solve_tree(root, "alphabeta", return_stats=True)
    print("minimax", v1, "nodes", s1.nodes, "leaves", s1.leaves)
    print("alphabeta", v2, "nodes", s2.nodes, "leaves", s2.leaves, "prunes", s2.prunes)
    assert v1 == 5 and v2 == 5
    root2 = build_sample_tree_independent()
    assert solve_tree(root2, "alphabeta") == 5
    print("题目三样例通过")
