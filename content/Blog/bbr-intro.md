Date: 2021-08-17
Title: 浅淡TCP BBR
Tags: tcp, networking, bbr
Slug: bbr-intro

## 背景

在一对跨地域的机器（美国<->香港），使用TCP（Cubic拥塞控制算法）通信throughput最高2MB/s，丢包率0.02%。使用UDP通信throughput最高能达到140MB/s。

这是一个非常典型的长肥管道（LFN），并且丢包率比较高。尝试使用BBR算法后，throughput可达50MB/s+（Windows系统，通信协议使用用户态MsQuic）。

## Loss-based Congestion Control Algorithm

Reno和Cubic是比较经典的，用于TCP的拥塞控制算法。这一类算法使用的是基于丢包反馈的思想，即一旦产生了丢包，就认为链路上产生了拥塞。先将拥塞窗口减半，再进入快速恢复模式。

在快速恢复完成后中，就又会重新进入拥塞避免阶段。

![TCP-Reno-Cubic][1]

Reno当收到一个ACK包时，会将拥塞窗口增大一个MSS，窗口大小线性增长。而Cubic使用的是一个基于上次拥塞事件产生时间的三次函数，所以拥塞窗口能更快速的恢复到拥塞事件发生之前的大小。

但无论是Reno还是Cubic，在遭遇高丢包率的时候，其拥塞控制窗口的大小会一直处于一个非常小的状态。

在RTT较大时，拥塞窗口的大小增长速度更加缓慢，使得带宽利用率长时间维持在一个较低的状态。

下图为Cubic在有丢包（0.002%, 0.02%, 0.2%, 1%, 2%），高延时（200ms RTT）的网络条件下throughput数据。

![cubic-bandwidth][2]

## BBR - Congestion-based Congestion Control

不同于Reno和Cubic，BBR并没有使用“丢包”做为拥塞产生的信号，而是构建了一个反馈系统，通过时延的变化来确定链路上是否发生了拥塞。

### 拥塞产生的三个阶段

![BBR-3-stages][3]

* App Limited 应用限制阶段    
在此阶段，数据传输速率由用户程序决定。用户程序并没有利用所有的带宽，RTT维持稳定

* Bandwidth Limited 带宽限制阶段              
在此阶段，数据传输速率由链路带宽所决定，有效吞吐量等于链路带宽。但由于链路缓存的存在，发送端的发送速率可以略大于链路带宽。此时数据开始在链路缓存上堆积，RTT增加

* Buffer Limited 缓冲区限制阶段             
当链路缓存无法容纳所有的数据包时，就会产生丢包

Loss-based拥塞控制算法会在阶段3的时候产生“拥塞”信号，但是此时大概率为时已晚。因为链路缓存堆积的数据已经开始影响RTT，并且各个节点之间的缓存大小差异，还会导致短时间内的持续丢包，使得拥塞窗口大小急剧减小。

而BBR会将拥塞控制在阶段1和阶段2的交界处，这样可以最大化利用带宽，并且使得链路时延最小。

### 确定拥塞窗口的大小

从理论上分析，要使一条连接同时保持最高throughput和最小的延迟，那么其发送速率一定等于网络带宽。此时，在途的数据大小BDP = BtlBw × RTprop，就可以用满链路的带宽而不产生拥塞。

BDP意为“带宽时延乘积”。而BtlBw意为“瓶颈带宽”，即为整条链路中，带宽最小的部分。RTprop意为“链路固有传输延迟”。

> RTT（往返时延）与RTprop（链路固有传输延迟）的区别是：RTT包括了收发两端应用层的时延，而RTprop只包含网络传播的时延

不凑巧的是，在通信中我们几乎无法直接确定BtlBw和RTprop。BBR建立了一个模型来对其进行估计。公式如下：

![rtprop-hat][4]

η代表的是网络队列的抖动、接收方ACK时延等等。

![btlbw-hat][5]

但是，时延与带宽无法同时探测。因为探测时延时，我们必然要减慢发包速度，排空队列避免拥塞；而探测带宽时，我们需要尽量占满带宽，以检测ACK速率是否发生变化。所以时延与带宽的探测需要交替进行。

#### ProbeRTT - 时延探测

BBR每10秒钟会进入时延探测状态。在此状态下，BBR会限制拥塞窗口的大小到4个MSS（[为什么？][6]）。当收到ACK包后，会更新MinRTT的取样值。

#### ProbeBW - 带宽探测

BBR大部分时间都会处于ProbeBW状态。

BBR通过计算包的发送时间与收到ACK时间的差来确定带宽，使用“送达速度”来拟合带宽。

![bw-probe-pacing][7]

同时，BBR会采用gain cycle来随机微调（+25%, -25%, 不变）发送速率，以实时检测链路上带宽的变化。（图中的绿线看起来像心电图的部分）

### 性能比较

这里是Cubic与BBR在有丢包（0.002%, 0.02%, 0.2%, 1%, 2%），高延时（200ms RTT）的网络条件下的throughput对比。

![perf-bbr-cubic][8]

## 杂项

在Linux系统下，可以使用tc命令模拟不同的网络状态。

例如100ms延迟（RTT=2*延迟），1%丢包率：

```bash
sudo tc qdisc add dev lo root handle 1:0 netem delay 100msec loss 1%
```

在Windows下可以使用[Clumsy][13]进行模拟，但是有怀疑其会严重影响网络性能，效果有待进一步测试。

在Linux系统下，可以使用以下命令替换系统congestion control算法。

```bash
sudo sysctl -w net.ipv4.tcp_congestion_control=cubic
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr
```

## References

* [浅谈TCP/IP传输层TCP BBR算法][9]
* [CUBIC TCP][10]
* [BBR: Congestion-Based Congestion Control][11]
* [facebookincubator/mvfst][12]
* [使用TCP时序图解释BBR拥塞控制算法的几个细节][14]

  [1]: https://raw.githubusercontent.com/Wizmann/assets/master/wizmann-pic/21-08-16/2021-08-16_23-07-29.png
  [2]: https://raw.githubusercontent.com/Wizmann/assets/master/wizmann-pic/21-08-17/2021-08-17_00-18-45.png
  [3]: https://raw.githubusercontent.com/Wizmann/assets/master/wizmann-pic/21-08-17/2021-08-17_00-58-34.png
  [4]: https://raw.githubusercontent.com/Wizmann/assets/master/wizmann-pic/21-08-17/2021-08-17_10-02-28.png
  [5]: https://raw.githubusercontent.com/Wizmann/assets/master/wizmann-pic/21-08-17/2021-08-17_10-04-06.png
  [6]: https://blog.csdn.net/dog250/article/details/72042516
  [7]: https://raw.githubusercontent.com/Wizmann/assets/6b0dcc0d2f7b2446ea0c3ca6faec29da6f28dc7e/wizmann-pic/21-08-17/image.png
  [8]: https://raw.githubusercontent.com/Wizmann/assets/8a78e8e7c7193f4bf5d6de01997f21491f3794ab/wizmann-pic/21-08-17/Snipaste_2021-08-17_14-54-21.png
  [9]: https://juejin.cn/post/6844904065759969287
  [10]: https://en.wikipedia.org/wiki/CUBIC_TCP
  [11]: https://queue.acm.org/detail.cfm?id=3022184
  [12]: https://github.com/facebookincubator/mvfst
  [13]: http://jagt.github.io/clumsy/
  [14]: https://blog.csdn.net/dog250/article/details/72042516
