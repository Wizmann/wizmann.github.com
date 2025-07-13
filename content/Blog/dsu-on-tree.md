Title: 树上启发式合并（DSU on Tree）
Date: 2025-07-13
Tags: 数据结构, 树形DP, 启发式合并, 树链剖分, DSU on Tree, Leetcode
Slug: dsu-on-tree

## 什么是 DSU on Tree？

**DSU on Tree（Disjoint Set Union on Tree）**，中文称为“树上启发式合并”，是一种用于高效处理**树上子树统计类问题**的算法技巧。尽管其名称中含有 “DSU（并查集）”，但本质上与并查集并无直接关联。

该方法广泛应用于以下场景：

* 统计每个节点子树中的某类属性（如颜色种类、频次、权重等）；
* 在递归过程中合并不同子树的统计信息，显著提升效率；
* 避免大量冗余的 insert/delete 操作所造成的性能浪费。

其核心策略结合了**启发式合并**（小的合并到大的）与**重儿子优先保留**的思想，与树链剖分中的轻重边划分具有一致性。

近年 LeetCode 也多次考察相关题目，说明该技巧即将成为面试中的高频考点（误

## 问题背景与动机

### 示例题目：树上统计颜色种类数

[题目链接][1]

> 给定一棵以 1 为根的树，每个节点有一个颜色。
> 多次询问：以某个节点为根的子树中，有多少种不同的颜色？

输出：对于每个查询，输出对应子树中的颜色种类数。

> ⚠️ 注意：原题中颜色 c\[i] 可能为 0，代码中需进行特殊处理。

### 为什么不能直接使用树形 DP？

树形 DP 的典型做法是：递归处理每个子节点，将其统计结果合并到父节点。但这种策略在本问题中存在效率问题：

* 每次合并都需要对 map 或数组进行 insert/delete；
* 若对子树数据进行暴力合并，可能会产生大量重复操作；
* 最坏情况下，时间复杂度可能达到 O(n²)。

为解决这些问题，我们引入 **DSU on Tree**。通过对重儿子保留、轻儿子清除的启发式策略，可以将时间复杂度优化至 **O(n log n)**。

## DSU on Tree 的算法流程

1. 预处理每个节点的子树大小，确定其重儿子（子树最大的孩子）；
2. 以 DFS 遍历整棵树，处理流程如下：

   * 首先递归处理所有轻儿子，并在处理后清除其统计结构；
   * 然后递归处理重儿子，保留其统计结果；
   * 接着将所有轻儿子的统计信息合并到当前维护的结构中；
   * 将当前节点自身的信息加入统计；
   * 更新该节点的答案。

该策略确保：**每个节点的信息最多被合并 log n 次**，大幅降低了总体复杂度。

## 算法原理与复杂度分析

### 正确性说明

DSU on Tree 在整体结构上与树形 DP 一致，都是自底向上合并子树信息。不同之处在于合并顺序与数据结构管理策略更具启发性，从而降低了时间复杂度。其正确性自然继承于递归式的子树遍历结构。

### 重/轻儿子与边的定义

对于每个节点 $u$：

* **重儿子**：其所有子节点中，子树大小最大的一个；
* **轻儿子**：其余所有子节点；
* **重边**：$u$ 与其重儿子之间的边；
* **轻边**：$u$ 与轻儿子之间的边。

这一划分方式与树链剖分中的定义完全一致，旨在最大程度复用统计结构，减少数据迁移成本。

### 为什么每个节点最多被合并 $\log n$ 次？

设某节点从根开始向下，在 DFS 过程中每经过一条轻边，子树规模至多减半：

$$
\frac{n}{2^x} \geq 1 \Rightarrow x \leq \log_2 n
$$

因此，一个节点作为被合并对象，最多经历 $\log n$ 次合并操作，从而将总体复杂度限制在 $O(n \log n)$ 范围内。

### 重边的作用

重边连接的是子树最大的孩子。在合并过程中，我们选择保留重儿子的统计结构，不清空、不重建，从而实现结构的复用和效率提升。

## 伪代码示例

```python
# 全局变量说明：
# g[u]：邻接表表示的树结构
# sz[u]：以 u 为根的子树大小
# big[u]：u 的重儿子（子树最大的孩子）
# col[u]：每个节点的颜色
# L[u], R[u]：u 的 DFS 序区间
# Node[i]：DFS 序编号 i 对应的节点编号
# cnt[c]：颜色为 c 的节点出现次数
# totColor：当前颜色种类数
# ans[u]：以 u 为根的子树的答案

def dfs0(u, parent):
    global time
    time += 1
    L[u] = time
    Node[time] = u
    sz[u] = 1
    for v in g[u]:
        if v == parent:
            continue
        dfs0(v, u)
        sz[u] += sz[v]
        if big[u] is None or sz[v] > sz[big[u]]:
            big[u] = v
    R[u] = time

def add(u):
    color = col[u]
    if cnt[color] == 0:
        totColor += 1
    cnt[color] += 1

def remove(u):
    color = col[u]
    cnt[color] -= 1
    if cnt[color] == 0:
        totColor -= 1

def get_answer():
    return totColor

def dfs1(u, parent, keep):
    # 处理所有轻儿子并清除其贡献
    for v in g[u]:
        if v == parent or v == big[u]:
            continue
        dfs1(v, u, keep=False)

    # 处理重儿子，保留其统计数据
    if big[u] is not None:
        dfs1(big[u], u, keep=True)

    # 把所有轻儿子的 DFS 区间数据合并进来
    for v in g[u]:
        if v == parent or v == big[u]:
            continue
        for i in range(L[v], R[v] + 1):
            add(Node[i])

    # 加入当前节点自身
    add(u)

    # 保存当前节点答案
    ans[u] = get_answer()

    # 若不保留此子树信息，则清除
    if not keep:
        for i in range(L[u], R[u] + 1):
            remove(Node[i])

```

### 时间复杂度分析

* 每个节点的信息最多被合并 $\log n$ 次；
* 每次合并操作为 $O(1)$（若使用数组）或 $O(\log n)$（若使用 map）；
* 因此总复杂度为：$ O(n \log n) $

对于多数题目中，颜色值范围有限时可使用数组，使整体操作更接近线性。

## 例题：LeetCode3575 - Maximum Good Subtree Score

🔗 [题目链接](https://leetcode.com/problems/maximum-good-subtree-score/description/)

### 题意简述

给定一棵以 0 为根的树，每个节点有一个整数权值 `vals[i]`，及其父节点 `par[i]`。一个子树中，若**任意子集**中所有节点的十进制表示中每个数字最多出现一次，该子集为“合法子集”。合法子集的得分为其节点权值之和。子集可以不连通。

定义 `maxScore[u]` 表示以节点 `u` 为根的子树中，合法子集的最大得分。求所有节点的 `maxScore[u]` 之和。

### 解法思路

这是典型的 DSU on Tree 应用场景，适用于子树统计类问题：

* 每个节点 DFS 时记录子树中数字出现情况（用 bitmask）；
* 合并时保留重儿子的统计结构，将轻儿子信息逐步合并进来；
* 遇到重复数字时及时剪枝；
* 使用“重儿子保留，轻儿子清除”策略，确保总复杂度不超限。

总复杂度控制在 $O(n \log n)$，显著优于暴力枚举或者树形DP。

## 小结

**DSU on Tree 是解决树上子树信息统计类问题的高效工具**，其主要优势包括：

* 避免重复统计，提升合并效率；
* 时间复杂度优秀，达 $O(n \log n)$；
* 与树链剖分的轻重边思想互补；
* 实用性强，广泛应用于竞赛与工程题中。

## 参考资料

* [OI Wiki：树上启发式合并](https://oi-wiki.org/graph/dsu-on-tree/)
* [LeetCode3575 - Maximum Good Subtree Score](https://leetcode.com/problems/maximum-good-subtree-score/description/)
* [Luogu U41492 树上数颜色][1]

[1]: https://www.luogu.com.cn/problem/U41492

