Date: 2025-05-28
Title: 可控扩容与扩展中国剩余定理 ：NoSQL 分区实践
Tags: nosql, hash, partitioning, repartitioning, crt, excrt
Slug: controlled-partition-scaling-with-excrt

在现代分布式数据库中，**Hash 分区（Hash-based Partitioning）** 是最常用的数据分布策略之一。系统通过对 key 取 hash，再对分区数 `N` 取模，将数据路由到对应分区。

当业务增长带来存储与吞吐瓶颈时，系统需要 **扩容** —— 将原来的 `N` 个分区扩展为更多的 `M` 个分区。但这个过程并非总是轻松，特别是当 `N` 与 `M` 无明显倍数关系时，数据迁移可能代价巨大。

本文提出一种数学结构驱动的新思路：**通过构造满足一定约束的 N→M 映射，并借助扩展中国剩余定理（Extended Chinese Remainder Theorem, ExCRT），实现更可控的数据迁移方案**。

## 常规扩容：N → 2N 或 3N 的便利与局限

在实际工程中，最常见的扩容方式是将分区数从 `N` 扩展为 `2N`、`3N` 等倍数。这种方式之所以流行，是因为它具备天然的结构优势：

* **映射关系明确**：每个原始分区的数据可以均匀地映射到固定数量的新分区；
* **实现简洁**：只需在 hash 值的基础上调整模数，或者通过位移和除法即可建立新旧分区的映射；
* **迁移可控**：通常只需部分数据迁移，许多 key 会继续留在原本映射到的区域附近。

例如，从 `N = 8` 扩容到 `M = 16` 时，典型映射如下：

```python
new_partition = hash(key) % 16
old_partition = new_partition // 2
```

原分区 `0` 中的数据只会被重新分布到新分区 `0` 和 `1` 中，迁移边界明确。

### 然而，倍数扩容也存在明显问题：

当 `N` 本身已经非常大（如数百或数千分区）时，倍数扩容意味着将系统容量翻倍甚至三倍，这往往会带来 **资源浪费** 和 **分布不均衡** 的风险。与此同时，**维护成本和状态空间也会成倍上升**。

这引出一个更具挑战性的问题：

> 是否有办法将 `N` 扩展为一个比 `2N` 更小、但又能满足容量需求的`M`，同时**避免无序重分布带来的高迁移成本**？

## 一个新思路：ExCRT 限定映射构造

如果我们将分区扩容问题抽象为一个模运算系统：

```text
原始分区: x ≡ a₁ (mod N)
目标分区: x ≡ a₂ (mod M)
```

我们的目标是：给定原始分区编号 `a₁`，找出所有可能的目标分区编号 `a₂`。

### 利用扩展中国剩余定理（ExCRT）

将上述两个同余方程组成一个系统：

```text
x ≡ a₁ (mod N)
x ≡ a₂ (mod M)
```

根据 ExCRT 的结论，这个系统有解当且仅当：

```text
a₁ ≡ a₂ (mod d)，其中 d = gcd(N, M)
```

换句话说，**只有满足 `a₂ ≡ a₁ mod d` 的目标分区编号是合法的。**

因此，**对于每一个原始分区 `a₁`，其可映射的目标分区 `a₂` 并不是全部 M 个，而是受限于这个模 d 的条件**。

### 举例说明：有限映射如何形成

假设我们要将分区数从 `N = 12` 扩容到 `M = 20`，由于：

```
gcd(12, 20) = 4
```

我们知道，每个原始分区 `a₁ ∈ [0, 11]` 映射到的新分区 `a₂ ∈ [0, 19]` 必须满足同余关系：

```
a₂ ≡ a₁ mod 4
```

例如，对于原始分区 `a₁ = 5`，符合条件的目标分区为：

```
a₂ ∈ {5, 9, 13, 17}
```

这意味着：

> 每个原始分区最多只会映射到 `M / gcd(N, M) = 5` 个目标分区，而不是全部 `M` 个，极大地压缩了数据迁移空间。

下面是完整的映射关系示例：

| 原分区 `a₁` | 合法目标分区 `a₂ ∈ [0, 20)` 满足 `a₂ ≡ a₁ mod 4` |
| -------- | ---------------------------------------- |
| 0        | {0, 4, 8, 12, 16}                        |
| 1        | {1, 5, 9, 13, 17}                        |
| 2        | {2, 6, 10, 14, 18}                       |
| 3        | {3, 7, 11, 15, 19}                       |
| 4        | {0, 4, 8, 12, 16}                        |
| 5        | {1, 5, 9, 13, 17}                        |

以此类推，每个原始分区只会映射到与自身模 `d` 同余的一组目标分区，构成了一个**模 d 分类的稀疏映射结构**。

这就是扩展中国剩余定理在扩容中的价值所在：

> 不仅使映射可解，而且使映射**受限、有结构、可控**，从而有效避免全连接映射带来的大规模数据迁移。

## 映射空间的压缩优势

更进一步地，我们可以对比两种映射方式的边数量：

| 映射方式       | 映射边数量                 | 是否全连接 |
| ---------- | --------------------- | ----- |
| 传统全连接      | `N × M`               | 是     |
| 本方法（ExCRT） | `N × (M / gcd(N, M))` | 否     |

换句话说，我们将可能的连接数**压缩了一个因子 `gcd(N, M)`**，极大减小了数据重分布带来的迁移成本。

## 总结与展望

本文提出了一种结合扩展中国剩余定理的 NoSQL 分区扩容方法：

* 通过控制扩容目标 `M` 与原始分区数 `N` 的公约数；
* 使用 ExCRT 构造原分区号与目标分区号之间的合法映射；
* 从数学上限定了数据迁移路径，避免无序重分布；
* 显著减少了迁移成本和系统不稳定性。
