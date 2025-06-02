Date: 2025-06-02
Title: Abel 求和公式在算法竞赛中的应用
Tags: math, leetcode, codeforces, algorithm, dp
Slug: abel-sum-dp-optimization

## Leetcode 3500. Minimum Cost to Divide Array Into Subarrays

链接：[英文][1] | [中文][2]

### 题目大意

给定两个等长数组 `nums` 和 `cost`，以及一个整数 `k`，你可以将 `nums` 分割成若干个**非空连续子数组**。第 `i` 段子数组（编号从 1 开始）为 `nums[l..r]`，其代价计算方式如下：

$$
f(l, r, i) = \left( \sum_{j=0}^r \text{nums}[j] + k \cdot i \right) \cdot \left( \sum_{j=l}^r \text{cost}[j] \right)
$$

目标是通过某种划分方式，使得总代价最小。

### 约束条件

* $1 \leq n \leq 1000$
* $1 \leq nums[i], cost[i], k \leq 1000$

## 直观的解法：三重循环暴力 DP

我们定义状态：

* `dp[i][j]` 表示前 `j` 个元素分成 `i` 段的最小总代价。

转移方程为：

$$
dp[i][r] = \min_{l < r} \left\{ dp[i-1][l] + f(l+1, r, i) \right\}
$$

即使使用前缀和将单次 $f(l+1, r, i)$ 的计算复杂度优化到 $O(1)$，每次仍需枚举 $n$ 次转移，总体时间复杂度仍为 $O(n^3)$，无法通过本题。

## Abel 求和公式优化

### Abel 求和公式简介

Abel 求和公式是一种优化形如 $\sum a_i b_i$ 的乘积和的技巧，适用于以下场景：

* $a_i$ 可以预处理为前缀和
* $b_i$ 是单调或线性变化

公式如下：

$$
\sum_{i=1}^n a_i b_i = B_n a_n - \sum_{k=1}^{n-1}B_k(a_{k + 1} - a_{k})
$$

其中：

* $B_i = \sum_{j=1}^i a_j$，是从 $b_1$ 开始的前缀和；
* $B_{0} = 0$。

### 几何意义与解释

可以将 $\sum a_i b_i$ 理解为“宽度为 $a_i$，高度为 $b_i$ 的矩形”所构成的总面积。Abel 求和的思想，相当于用一套更容易累加的方式来表达这些面积之和。

![abel](https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/Abel.png)
（图源：[Easymath-wiki][3]）

### 加法形式变体（对称结构）

还有一种对称的加法表达：

$$
\sum_{i=1}^n a_i b_i = \sum_{i=1}^{n} (B_{n - i} - B_{i}) \cdot (a_{i} - a_{i - 1})
$$

此时，有$a_0 = 0$和$B_0 = 0$。

## 在 Leetcode 3500 中的应用

我们再看代价函数：

$$
f(l, r, i) = \left( \sum_{j=0}^r \text{nums}[j] + k \cdot i \right) \cdot \left( \sum_{j=l}^r \text{cost}[j] \right)
$$

将其拆为两部分：

### 与数组值相关的部分：

$$
g(l, r) = \left( \sum_{j=0}^r \text{nums}[j] \right) \cdot \left( \sum_{j=l}^r \text{cost}[j] \right)
$$

用前缀和：

* `psum_nums[r] = nums[0] + ... + nums[r]`
* `psum_cost[r] - psum_cost[l-1] = cost[l..r]`

即可在 $O(1)$ 时间内得到 $g(l, r)$。

### 与子数组编号 $i$ 相关的部分：

$$
h(l, r, i) = k \cdot i \cdot \left( \sum_{j=l}^r \text{cost}[j] \right)
$$

这类“线性编号 × 区间和”的结构，正是 Abel 求和思想的典型应用场景。我们可以通过Abel求和将其转化为如下形式：

$$
\begin{align*}
h'(l, r, i) &= k * \sum_{j=1}^{r}cost[j] * ((i + 1) - i) \\
&= k * \sum_{j=1}^{r}cost[j]
\end{align*}
$$

> 注：$h'$函数中计算的是`cost`数组的后辍和，从1开始。并非$h$函数中的$(l, r)$区间和。

这样一来，$h'(l, r, i)$只与变量$r$相关，进而减少了DP的状态空间。

## 时间复杂度优化

通过将 \$f(l, r, i)\$ 拆解，并借助前缀和 + Abel 求和思想，我们将原本 \$O(n^3)\$ 的三重循环 DP 优化为：

* 单次状态转移：$O(1)$
* 空间复杂度：$O(n)$
* 总体复杂度：$O(n^2)$

可以通过本题的数据范围限制。

## 相关问题：Codeforces 1175D - Array Splitting

题目链接：[Codeforces 原题][4] | [解答代码][5] | [官方题解][6]

### 题目描述

给定数组 $a = [a_1, ..., a_n]$ 和整数 $k$，将其划分为 $k$ 个非空连续子数组，设每个子数组编号从 1 到 $k$ 递增，总代价函数为：

$$
\text{cost} = \sum_{i=1}^k Sub_{i} \cdot i
$$

$Sub_{i}$ 为第$i$个的子数组元素之和。

你需要设计一种划分方式，使得总代价最大。

### 样例：

设 
$$a = [1, -2, -3, 4, -5, 6, -7]$$

若划分为三段：$([1, -2, -3], [4, -5], [6, -7])$，代价为：

$$
(1\cdot1 -2\cdot1 -3\cdot1) + (4\cdot2 -5\cdot2) + (6\cdot3 -7\cdot3) = -9
$$

### Abel 求和视角分析

总代价可以计为：

$$
\text{cost} = \sum_{i=1}^k Sub_{i} \cdot i
$$

即每段的区间和乘以其编号 $i$：

$$
\begin{align*}
f(l, r, i) &= i \cdot  Sub_{i} \\ 
&= i \cdot \left( \sum_{j=l}^r a_j \right)
\end{align*}
$$

使用Abel求和公式，我们可以进行如下的转化：

$$
f'(l, r, i) = ((i + 1) - i) * \sum_{j = l}^{n}a_j = \sum_{j = l}^{n}a_j
$$

我们可以先将所有元素视为编号为 1 的一段：

$$
\text{base} = \sum_{j=1}^n a_j
$$

每新增一段，就意味着将某段的编号从 $i$ 提升到 $i+1$，对应的提升值就是“该段和 × 增量编号”。

因此，我们只需选择 $k-1$ 个切割点，使得**后缀和最大的 $k-1$ 段被额外计入一次**，即可达到最大化目标。

### 实现步骤：

1. 枚举每个位置的后缀和（不含第一个）；
2. 取最大的 $k-1$ 个后缀和；
3. 答案为整段和 + 它们之和。

## 小结

Abel 求和是一种处理“数列乘编号”类结构的经典技巧，虽然起源于数学，但在很多竞赛问题中都能找到它的影子。特别是在涉及“编号 × 权重”、“位置 × 值”这种结构时，它常常提供一种结构性的优化方式。

在 Leetcode 3500 中，它帮助我们把三重循环的 DP 优化为 $O(n^2)$；在 CF1175D 中，它转化为一个“最大权重选取”问题。虽然应用方式不同，但核心思想是一样的。

## 参考

* [Easymath Wiki: Abel 求和公式][3]
* [Leetcode 3500][1]
* [Codeforces 1175D][4]


[1]: https://leetcode.com/problems/minimum-cost-to-divide-array-into-subarrays/description/
[2]: https://leetcode.cn/problems/minimum-cost-to-divide-array-into-subarrays/description/
[3]: https://easymath.org/wiki/Abel_summation_formula
[4]: https://codeforces.com/contest/1175/problem/D
[5]: https://ideone.com/eMWXRL
[6]: https://codeforces.com/blog/entry/67484

