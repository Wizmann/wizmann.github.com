Date: 2025-06-12
Title: 线段树入门：一种基于不变式的理解方式
Tags: 算法, 线段树, algorithm, segment-tree
Slug: segment-tree-by-invariant

## 前言

线段树是一种在算法中频繁出现的数据结构，既实用又略带挑战性。它之所以常见，是因为在涉及**区间查询与修改**的问题中，线段树常常能提供高效解法；而之所以“高阶”，则是因为在实现过程中需要细致处理边界和递归逻辑，否则容易出现**运行时错误（RE）**，因此也被戏称为“RE 树”（只有我）。

市面上已有不少教程通过图解、动画等方式帮助初学者建立对线段树的直观印象。建议读者在阅读本文前，可先参考这些资料（见文末参考链接），以获得对线段树结构的整体感知。

本文将尝试采用一种更为抽象的方式，从**数据结构不变式**的角度，系统分析线段树的设计逻辑，并通过若干经典例题，展示如何在实践中运用这些思想来构建高效且可扩展的线段树变体。

---

## 基本原理：从递归到不变式

线段树的核心思想是：**通过递归划分区间，使每个节点维护一个子区间的信息**，进而高效支持查询和修改操作。

### 示例：求区间最大值

以求解一个长度为 $n$ 的静态数组的区间最大值为例：

设数组为 $\text{array}[1 \dots n]$，我们定义 $\text{maxi}_{i,j}$ 表示区间 $[i,j]$ 的最大值。

当 $i = j$ 时，显然有：

$$
\text{maxi}_{i,i} = \text{array}[i]
$$

若 $i < j$，我们可以将其一分为二，划分为 $[i,m]$ 与 $[m+1,j]$，其中 $m = \left\lfloor \frac{i+j}{2} \right\rfloor$，进而递推：

$$
\text{maxi}_{i,j} = \max(\text{maxi}_{i,m}, \text{maxi}_{m+1,j})
$$

这就是线段树的**核心不变式**：

> 每个区间的信息完全由其左右子区间决定。

基于这个不变式，我们可以自底向上构建整棵线段树，或在查询和修改过程中维护其正确性。

## 查询操作

当我们查询一个区间 $[l,r]$ 的最大值时，可以递归地访问其子区间，并合并结果。

最终，查询过程会遍历一组**恰好覆盖区间 $[l,r]$** 的子区间，它们的最大值即为所求。


## 修改操作

### 点修改

若数组中某个元素发生变动（如将 $\text{array}[k]$ 修改为 $v$），只需从对应的叶子节点出发，沿路径向上传播更新信息，确保不变式在修改后依旧成立。该操作的时间复杂度为 $O(log n)$。

### 区间修改与懒标记

对于支持区间修改的线段树，其核心操作可以抽象为：

* **区间更新**：对 $[l, r]$ 中的所有元素执行某种操作，如加上一个常数 $c$，即：

  $$
  \forall i \in [l, r],\quad A[i] := A[i] + c
  $$
* **区间查询**：查询某一子区间 $[l, r]$ 的某个聚合函数，如最小值、和、最大值等。

若直接递归修改所有受影响的节点，则时间复杂度最坏为 $O(n)$。为避免这一问题，引入\*\*懒标记（Lazy Propagation）\*\*机制，通过“延迟计算”优化操作效率。

#### 不变式定义

设线段树的每个节点表示区间 $[L, R]$，维护的信息为 $S_{L,R}$。我们希望维护以下**结构不变式**：

* 对于区间加法操作：

  $$
  S_{L,R} = \sum_{i=L}^R A[i]
  $$

* 且满足：

  $$
  S_{L,R} = \text{Merge}(S_{L,M},\; S_{M+1,R})
  $$

#### 懒标记设计

为保持整体结构在多次操作下仍可高效工作，引入**延迟标记变量** $\text{lazy}_{L,R}$，用于记录尚未传播的修改信息。更新操作流程如下：

1. **打标记**（Apply）：

   * 当整个区间 $[L, R]$ 被完全覆盖时，不递归更新子区间；
   * 只需：

     $$
     S_{L,R} \leftarrow S_{L,R} + (R - L + 1) \cdot c
     $$

     $$
     \text{lazy}_{L,R} \leftarrow \text{lazy}_{L,R} + c
     $$

2. **下推标记**（PushDown）：

   * 当访问某节点的子节点时，将标记下传至左右子区间：

     $$
     \text{lazy}_{L,M} \leftarrow \text{lazy}_{L,M} + \text{lazy}_{L,R}
     $$

     $$
     S_{L,M} \leftarrow S_{L,M} + (M - L + 1) \cdot \text{lazy}_{L,R}
     $$

     同理处理 $[M+1, R]$，然后清除父节点标记：

     $$
     \text{lazy}_{L,R} \leftarrow 0
     $$

此时，每个节点所维护的信息可能**暂不符合精确值定义**，但满足以下**宽松不变式**：

> 若未访问子区间，则本节点记录的是更新后的区间值；一旦访问子区间，将立即下推以恢复精确不变式。

#### 结构不变式对比总结

<table class="table table-bordered table-striped table-hover align-middle">
  <thead class="table-light">
    <tr>
      <th>状态</th>
      <th>不变式形式</th>
      <th>是否立即满足</th>
      <th>性质</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>普通节点</td>
      <td>\( S_{L,R} = \text{Merge}(S_{L,M}, S_{M+1,R}) \)</td>
      <td>是</td>
      <td>严格不变式</td>
    </tr>
    <tr>
      <td>有懒标记</td>
      <td>\( S_{L,R} = \text{真实值} + \delta \cdot (R - L + 1) \)</td>
      <td>暂不满足</td>
      <td>延迟不变式</td>
    </tr>
    <tr>
      <td>下推后</td>
      <td>子节点恢复准确值</td>
      <td>恢复</td>
      <td>最终仍满足整体一致性</td>
    </tr>
  </tbody>
</table>

如需支持更多操作（如区间赋值、区间最小值+修改等），只需根据操作类型调整：

* 标记类型：如记录「待加数 $c$」或「待赋值为 $v$」；
* Merge 函数：如 $\max$、$\min$、$\sum$；
* 更新函数的结合律或可交换性是否成立。

只要操作满足**结合律与分配律**，就可以稳定维护懒标记下的结构正确性。

## 例题

### Luogu P3372 【模板】线段树 1：区间加法与求和查询

本题是线段树的经典模板题，支持两种操作：

* 区间加值：对区间 $[l, r]$ 内的每个元素加上一个常数 $c$；
* 区间求和：查询 $\sum_{i=l}^r A[i]$。

**实现要点**：

* 每个节点维护当前区间 $[L, R]$ 的区间和 $S_{L,R}$；
* 引入懒标记 $\text{lazy}_{L,R}$，用于延迟传播加值操作；
* 满足如下不变式（带标记时）：

  $$
  S_{L,R} = \sum_{i=L}^R A[i] + (R - L + 1) \cdot \text{lazy}_{L,R}
  $$

结合懒标记机制，可将修改与查询操作均优化至 $O(\log n)$。

### Luogu P1816 忠诚：静态区间最小值查询

题目要求支持多次查询：

* 给定初始数组 $A[1 \dots m]$，回答若干个区间 $[a, b]$ 内的最小值 $\min_{i=a}^{b} A[i]$。

**实现要点**：

* 每个节点维护对应区间的最小值 $M_{L,R} = \min_{i=L}^{R} A[i]$；
* 不涉及任何更新操作，结构在初始化后保持不变；
* 查询过程仅需递归访问覆盖区间，合并左右子树最小值即可。

> 由于为静态查询问题，可选用 ST 表（稀疏表）进行预处理，查询时间降至 $O(1)$，此处不再展开。

### Luogu P1558 色板游戏：区间赋值与状态统计

本题是典型的“染色问题”，操作包括：

* 将区间 $[l, r]$ 染为颜色 $c$；
* 查询区间 $[l, r]$ 中**不同颜色的种类数**（颜色数 ≤ 30）。

**实现要点**：

* 每个节点维护区间颜色集合 $C_{L,R}$，使用 30 位整数位运算记录状态（例如第 $k$ 位为 1 表示颜色 $k$ 存在）；
* 支持区间赋值，需使用懒标记 $T_{L,R}$ 表示待覆盖的颜色值；
* 不变式表达为：

  $$
  C_{L,R} = 
  \begin{cases}
    \text{bitmask of color } c & \text{若整段染色为 } c \\
    C_{L,M} \,|\, C_{M+1,R} & \text{否则}
  \end{cases}
  $$
  
* 查询通过统计 $C_{L,R}$ 中二进制 1 的个数来获取颜色数。

## 小结

线段树的设计之所以高效，是因为它通过**递归划分 + 不变式维护**，使得复杂的区间操作能够以对数级别的时间完成。

本文从不变式角度出发，分析了线段树的构造与操作逻辑。与常见的图解类教程相比，这种方法更强调原理和形式化思维，适合希望进一步深入理解线段树本质的读者。


## 参考链接

* [算法通关手册（LeetCode）- 线段树知识](https://algo.itcharge.cn/07.Tree/03.Segment-Tree/01.Segment-Tree/)
* [题单 - 线段树](https://www.luogu.com.cn/training/206)
