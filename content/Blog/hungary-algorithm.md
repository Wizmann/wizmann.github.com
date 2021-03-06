date: 2014-01-01 22:01
title: 匈牙利算法
tags: algorithm
slug: hungary-algorithm

## 概念

### 交错路

> 交错路：设P是图G的一条路，如果P的任意两条相邻的边一定是一条属于M而另一条不属于M，就称P是一条交错路。

通俗点来说，就是把一个图中的路径染成红黑两种。然后找出一条路，使这条路**红黑交错**。

注：交错路是无向图，图中的箭头只是为了便于观察。

例如下图中的：``(3) -> (2) -> (1)``

![图1][1]

### 从端点扩张交错路

假设我们已经有一个红黑交错路``P``，其端点为``A``和``B``，其路径被标记为``黑红``。此时，我们向``P``中的一个端点（假设为``A``）加入一条边``T``。

此时我们有``边T + 交错路P（黑红）``。当我们将边``T``标记为``黑色``时，我们就扩展了交错路``P``。
如果我们要保持红黑交错路的**性质**。则我们必须将边``T``标记为``黑色``。

于是``P（BR） => P'(BRB)``

![图2][2]

### 分割交错路

易得，分割交错路不会改变它的性质。

### 我们要红还是要黑

如果我们翻转红黑交错路的颜色，例如从``RBR => BRB``，则我们的交错路仍然**保持原来的性质**。

所以翻转颜色是安全的。

## 算法实现

### 匹配

匈牙利算法是用来求二分图最大匹配的算法。

于是我们人为标记集合中的点为``左集``和``右集``。


### 红色是种好颜色

由于``红黑交错路``可以安全的翻转颜色。所以我们保持交错路中**红色路多于黑色路**的性质也是安全的。

因为我们要求出最大匹配，所以我们设完成匹配的边为红色。

### 你可以证明你的算法吗

我们选取左集端点``T``到图中，此时图中有``k``条边与点``T``连接。这``k``条边分别为``p1...pk``。

```
选取p1...pk中的任一条边px

如果 图中没有交错路 或者 图中有交错路但px的端点不在交错路中 ：
    将px标为红色
    返回true。

如果 图中有交错路，且px的端点在交错路中：
    如果 px的另一个端点是交错路的头/尾端点。（重申，交错路是无向的）
        那么，我们可以直接扩展交错路。px标为红色
        返回true
    如果 px的另一个端点在交错路的中间。
        则我们在此端点分割交错路，将T点加入某一交错路。并且选取此交错路的一个端点执行这个扩展操作

如果 px不存在：
    则返回false， 洗洗睡了

所以我们在每一次操作之后，会得到一个返回值。如果为true，则匹配数+1。反之则不变。
```

p.s. 我觉得我的证明我自己都TMD看不懂。。。好挫败。。。

## 代码

```cpp
int n, m; //左集端点数，右集端点数
vector<int> g[SIZE]; // 边集
char inPath[SIZE]; // 是否在交错路中
int match[SIZE]; // 只存储黑色路径
int hungary()
{
    int sum = 0; // 总数标为0
    for (int i = 0; i < n; i++) {
        memset(inPath, 0, sizeof(inPath)); // 新加入的点不在任何交错路中
        sum += deal(i)? 1: 0;
    }
    return sum;
}
```

```cpp
bool deal(int x)
{
    // 遍历所有的边
    for (int i = 0; i < (int)g[x].size(); i++) {
        int next = g[x][i];
        if (inPath[next]) continue; // 如果点在交错路中，pass
        inPath[next] = 1;
        
        // 如果找到一个不在交错路中的点，将其加入交错路，此轮算法结束
        // 否则，分割交错路，从下一个点重新寻找扩展交错路的方法。
        // 方法存在则更新。如果不存在，不更新。
        if (match[next] == -1 || deal(match[next])) {
            match[next] = x;
            return true;
        }
    }
    return false;
}
```

## 参考

byvoid: [匈牙利算法][3]

Matrix67: [二分图最大匹配的König定理及其证明][4]

wikipedia: [匈牙利算法][5]

[1]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/blog-hungary-1.png
[2]: https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/blog-hungary-2.png
[3]: https://www.byvoid.com/blog/hungary
[4]: http://www.matrix67.com/blog/archives/116
[5]: http://zh.wikipedia.org/wiki/%E5%8C%88%E7%89%99%E5%88%A9%E7%AE%97%E6%B3%95
