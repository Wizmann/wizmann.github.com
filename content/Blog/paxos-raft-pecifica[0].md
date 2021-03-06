Date: 2018-11-25
Title: 白话一致性协议 - Paxos、Raft和PacificA[0]
Tags: paxos, basic paxos, 数据库, 分布式系统, 一致性
Slug: paxos-raft-pecifaca[0]

## 一致性协议 - Paxos

在分布式系统当中，我们往往需要保持节点之间的一致性。在绝大多数情况下，我们需要让系统中的节点相互协调通力合作，有可能的让系统正确的工作。但是，由于分布式系统本身的特性，需要我们在不可靠的硬件上尽可能的构建可靠的系统。所以，看似简单的一致性问题成为了分布式系统领域的一个重要的课题。

Paxos算法是Leslie Lamport于1990年提出的一种一致性算法。也是目前公认解决分布式一致性问题最有效的算法之一。

Paxos算法的目标是在一个不可靠的分布式系统内，只通过网络通信，能够快速且正确地在集群内部对某个数据的值达成一致。并且保证不论发生任何异常，都不会破坏系统的一致性。

## Paxos算法

### 另一种（简化了的）形象的问题描述 - 买车位

某小区的一些居民在抢车位，而车位只有一个。居民们达成协议，只要一个报价获得半数以上居民认可，那么提出这个出价的居民则获得了车位的所有权。

居民之间非常友善，如果知道了车位已经有了买家，就不会继续出价购买，并且会帮忙传播这个信息。

居民们都是遵纪守法的好公民，在整个过程中都只会如实的与其它用户分享信息。信息的分享是在网上，通过一对一的私密聊天进行。但是小区的手机信号非常差，我们不能保证通信的质量，一些信息可能会丢失。但是居民不会掉线。也不会失去记忆，并且通信的内容是完整的，不会被篡改的。

划重点：

1. 需要半数以上居民的认可，才能声称拥有车位。这个居民被称为车位的“公认拥有者”
2. 车位有且只有一个，所以一个车位不能同时有两个“公认拥有者”
3. 车位可以暂时没有拥有者，但是需要尽快选出一个
4. 通信是不可靠的(not-reliable)，但是正确性(integrity)和可持久性（durability）是可以保证的
5. 整个流程的目标是确定车位的拥有者。流程的参与者不会以自己拥有车位为最终目标

### 如何选出最终的买家

由于通信是一对一的，对于所有参与者来说，他们对整个系统的了解都是片面的、过时的。但是参与者会通过与其它参与者进行通信，不断获得更及时的信息，从而最终达成一致。

对于普通居民，会记录“已知最高报价”和“已确认报价”两个状态。会处理两种请求：

1. 询价：如果居民已确认了某个报价，则返回这个报价。否则会尝试更新已知最高报价，并报告买家当前的最高报价
2. 报价：居民会将请求中的报价与自己已知的最高报价进行比较，如果高于或等于本地已经报价，无论是否已经有已确认报价，都会确认这个报价

而对于买家，会发出两种不同的信息：

1. 询价：以某一个报价问询多数居民，如果有已确认的报价，则放弃自己的报价。如果这个报价低于居民已知的报价，则提高报价。
2. 报价：如果询价过程中收到了已确认的报价，则帮忙转发这个报价。否则发送自己的报价，如果报价获得了多数居民的认可，即可以认为所有权已经更新

### 一致性的直观证明

报价阶段，除了保证正确性之外，对于居民和买家并没有任何约束。其本质参与者之间同步信息的过程。

而一致性在报价阶段可以被很好的保证

* 如果车位还没有主人，那么大家就拼一拼运气和手速，直到有一个买家获得了半数居民的认可。
* 如果用户A已经声明以价格P买入车位（记为`(P, A)`），此时必有多数居民已经认可`(P, A)`。如果用户B想要声明以价格Q(Q >= P)买入车位，首先需要向多数居民询价，在询价的过程中，一定会收到用户A已经拥有车位的信息，此时B只会帮A扩散信息，而不会去争夺拥有权。系统最终会达到一个稳定的状态。

### 失忆 - 放松可持久性要求

如果我们放松可持久性的限制。即居民可以掉线，或者清空自己的记忆。那此时最差情况是多数已经确认报价的居民不再承认报价，那么系统就有可能退化到“仍没有人拥有车位”的状态。此时我们只需要再进行一轮选举，选出车位新的主人即可。这并不会破坏整个系统的一致性。

### 旁观者视角

假如我们做为旁观者，想要观察是谁最终拥有了车位。可以有以下两种方法：

1. “推”模型      

当新的买家被选举出来时，新买家会通知所有旁观者车位的拥有者发生了变化。这样观察者们可以实时的获得状态的变化，但是由于通信是不可靠的，旁观者可能会错过状态变化的信息。如果这种情况出现，观察者只能等待下次状态变化，才能更新自己的状态。

2. “拉”模型

旁观者可以假装自己是一个买家，向多数居民进行询价。如果最终买家已经确定，那么询价的响应中一定包含着最新的拥有者信息。

### Paxos如何解决活锁问题

假设居民里有买家A、B，同时向其它居民提出询价/报价。如果他们的询价/报价顺序排列如下，会出现什么状况呢？

```
A: 询价，1块
众居民：好的，最高价为1块
B：加钱，2块
众居民：收到，最高价为2块
（此时A仍旧认为1块是最高报价）
A：最终报价，1块
众居民：不行不行，B已经加到两块钱了
A：（内心mmp）询价，3块
（B对A提高了报价也毫无准备）
B：最终报价，2块
众居民：滚粗，A已经报价3块了
B：我加钱
A：我再加
B：我加钱
A：我再加
众居民：。。。（你们玩个球啊）
```

震惊，这帮无聊的人居然为了这几块钱可以玩一天！

以这样的流程进行下去，系统会陷入活锁，几乎不能达成一致了。想要解决这个问题，可以将A和B的询价重试时间加入随机化因子，这样可以帮助更快的让居民们达成一致。

### Paxos如何解决投票分裂问题

![][5]

如图所示，居民们的投票可能会发生分裂，即没有一个值达到了半数。这里的解决方案是让买家重新进行询价，同时加入随机化因子，使得投票达成半数以上的概率更大。

## 说正经的

对于Paxos算法的官方描述和正确性的详细证明可以参考[原论文][4]。这里就不搬运了，只是把我的例子和官方通用术语进行一下讲解，避免把大家带跑偏了。

在上面的例子中，“车位”的通用术语被称为“共识”，整个系统中最多有一个共识。而“询价请求”被称为“prepare请求”，“报价请求”被称为“accept请求”。

每个请求的价格被称为“编号”，编号大的请求可以覆盖编号小的请求，和“价高者得”是一个道理。请求中所带的信息被称为“value”，在我们的例子中，代表着购买者的身份信息。

## Basic Paxos和Multi Paxos

上面我们描述的Paxos算法又被称为Basic Paxos，因为每一轮流程执行完，所有的参与者都会（且只会）达成一个共识。而在实际的应用中，我们需要连续不断的对多个值达成共识。这时Basic Paxos算法就力不能及了，一来每一个值的共识都至少需要两次广播网络请求，性能太低，二来同时存在的多个提案会互相竞争，使得通信的效率下降。

所以为了解决这个问题，Multi Paxos算法应运而生，即一种可以高效的、连续不断的对多个值达成共识的算法。

下一篇文章中，我们会介绍一种被普遍认可，以及已经被工业界应用的Multi Paxos的实现 —— Raft算法。

## 参考链接

* [Paxos Made Simple][4]
* [从Paxos到Zookeeper][2]
* [知乎：Paxos算法详解][1]

[1]: https://zhuanlan.zhihu.com/p/31780743
[2]: https://book.douban.com/subject/26292004/
[3]: https://raw.githubusercontent.com/Wizmann/assets/master/wizmann-pic/18-11-24/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20181124152719.png
[4]: https://lamport.azurewebsites.net/pubs/paxos-simple.pdf
[5]: https://raw.githubusercontent.com/Wizmann/assets/master/wizmann-pic/18-11-25/split-vots.png
