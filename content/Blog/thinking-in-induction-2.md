Date: 2014-10-01 00:05:29 
Title: 思维训练 - Thinkin' in induction 2
Tags: induction, algorithm
Slug: thinking-in-induction-2

## 最大导出子图（maximal induced graph）

> 你现在在组织一个学术会议。现在你有一份人员名单。假定名单中的每一个人都同意到达，并且有充足的时间交流意见。同时，每一个科学家都写下了他愿意与其进行交流的科学家的名字。

> 现在，问题来了：<del>挖掘机技术哪家强？</del>

> 如果要保证每一位科学家至少能与k位到场的科学家进行深入的交♂流♂。那么我们最多可以邀请多少人到会？

> 注：如果A愿意和B交流，AB一定会进行交流。反之亦然。

我们可以把问题转化成数学语言：对于一个无向图`G=(V, E)`，试求得G的最大导出子图H，使得H中所有顶点的度大于或等于k，或者证明这样的子图是不存在的。

我们继续使用归纳的思想来解决这个问题。

易得，对于顶点数为k的图，如果存在k-导出子图，则该图必为一个完全图。

假设，对于任意顶点数小于n的图，我们总可以找到图的k-最大导出子图。

对于有n个顶点的图G来说，如果有任意顶点的度小于k，那么对于图G的任意子图，此顶点的度总小于k。

所以，对于图中任意度小于k的点，必然不属于所求的子图。于是，我们每次删除一个不属于k-导出子图的点，就可以把有n个顶点的图问题化归为n-1顶点的图问题。

## 一对一映射

> 给定一个集合A和一个映射关系f。求A的一个子集S，使得f对于S是一个一对一映射。即：f把S中的一个元素映射到一个元素；S中没有两个元素映射到同一个元素。

我们仍然可以做假设：对于含有k个元素的集合，我们有方法找到所求。

基础情况的证明非常简单，对于一个点的情况，`f(A) = A`满足条件。对于两个点，找到两个点`(A, B)`，在图中有`(A -> B)`和`(B -> A)`即可。

对于任意集合，我们可以确定，当没有`f(x) = i`时，元素i必然不属于这个集合。所以，每次操作我们都删除掉必然不属于所求子集的那个点，把问题`Q(n)`化归为子问题`Q(n-1)`。

## 社会名流问题

> 社会名流都是逼格比较高的人，这体现在所有的人都认识他，但是他不认识任何人。

> 试在n个人的聚会中，找出唯一的名流。而找出的名流的方法，就是询问任意一个人：Do you know that person? 每一个人都会如实回答。而你的目标是使询问次数最少。

我们仍然使用归纳的方法，如果这个聚会只有两个人，我们很容易就知道谁**不是**名流。(Why?)

对于一般的情况，如果询问A：Do you know person B?

如果A回答YES，那么A必然不是名流。如果A回答NO，那么B不是名流。

如是，我们又可以一步一步缩小题目的数据范围。最后在排除了所有**不是**名流的人之后，对最后一个候选人再进行一轮验证。

## 总结

以上三题都是**Thinkin' in induction**的良好范例。对于有些题目，做出大胆的假设并不是纯粹的碰运气，而是一种科学的尝试。同时，在思考时，如果不能直观的找出“谁是对的“，我们不妨反向思考一下，找出“谁是不对的”。

本文参考Udi Manber的《Introduction to algorithms - A creative approach》.


