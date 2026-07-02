Date: 2026-07-02
Title: DRAM 没有风水，SRAM 有一点：从超算内存故障看系统分析方法论
Tags: 论文阅读, 可靠性, 超算, DRAM, SRAM, 数据中心, 方法论
Slug: feng-shui-of-supercomputer-memory

有一篇论文，标题很有意思：

**Feng Shui of Supercomputer Memory: Positional Effects in DRAM and SRAM Faults**

直译是：**超算内存的风水：DRAM 和 SRAM 故障中的位置效应**。

标题像玩笑。  
但问题很严肃：

> 在大型生产系统里，内存故障到底和什么有关？  
> 是芯片供应商？是老化？是机房位置？是海拔？还是纯随机？

这篇论文研究了两个美国 DOE 体系里的大型超算系统：

- **Cielo**：约 8,500 个节点，位于 Los Alamos，高海拔，DDR3 内存，15 个月观测数据，约 **230 亿 DRAM device-hours**
- **Jaguar**：18,688 个节点，位于 Oak Ridge，低海拔，DDR2 内存，11 个月观测数据，约 **171 亿 DRAM device-hours**

这不是实验室小样本。  
这是生产环境里的真实故障数据。

论文表面研究的是内存可靠性。  
但我觉得它最有价值的部分不是某个具体故障率，而是方法论：

> 大规模数据不会自动产生真相。  
> 如果指标选错、分母选错、混杂变量没控制，大数据只会大规模地产生幻觉。

---

## 1. 先分清 fault 和 error

论文第一件重要的事，是区分两个词：

- **fault**：故障原因
- **error**：故障导致的错误状态

这不是文字游戏。

比如一个 DRAM bit 坏了。程序频繁访问它。每访问一次，ECC 都可能记录一次 corrected error。日志里可能出现几百条 error message。

但底层原因只有一个：

> 一个 fault，很多 errors。

如果直接统计 error count，你统计到的其实是：

```text
fault rate × workload access pattern × logging behavior
```

这很脏。

一个地址报错多，可能不是那里更容易坏，而是那里被访问得更多。

所以这篇论文选择研究 **fault rate**，而不是 error rate。  
作者把每个 DRAM device 上第一次观察到的 error message 视为该 device 的 fault occurrence time。后续 error 用来判断故障类型和模式。

这就是第一性原理：

> 别数症状。数病因。

---

## 2. 故障类型：transient vs permanent

论文把故障分成两大类：

### Transient fault：瞬态故障

随机发生，不代表器件永久损坏。  
典型例子是高能粒子击中存储单元，导致 bit flip。

写入正确数据或 scrubber 修正后，问题消失。

### Permanent fault：永久故障

包括 hard fault 和 intermittent fault。  
也就是持续或反复出现的问题，通常说明器件损伤、不稳定或存在制造缺陷。

严格来说，hard fault 和 intermittent fault 不一样。  
但在真实生产系统里，很难知道每一次内存访问是否都返回错误。作者没有完整访问轨迹，只有日志。

所以他们做了一个工程上合理的合并：

```text
permanent = hard + intermittent
```

不是完美。  
但可测。

他们靠硬件 scrubber 区分 transient 和 permanent：

- 如果错误只出现在一个 scrub interval 内，判为 transient
- 如果错误跨多个 scrub interval 反复出现，判为 permanent

Cielo 的 scrub interval 是：

- DRAM：24 小时
- L2 SRAM：10 秒
- L3 SRAM：129 秒

这是整篇论文的方法论地基。

---

## 3. DRAM 的第一个结论：早期从永久故障转向瞬态故障

Cielo 的整体 DRAM fault rate 是：

- **0.038% DRAM devices** 出现 fault
- **1.32% DIMMs** 出现 fault
- **40.33 FIT/device**
- 换算到整个 Cielo 系统，大约每 **11 小时** 出现一个 DRAM fault

单个芯片看起来很可靠。  
但系统太大了。规模会放大一切。

更重要的是时间趋势。

作者发现，DRAM fault rate 随时间下降，但这个下降不是所有故障一起下降。

真正发生的是：

```text
permanent fault rate 快速下降
transient fault rate 基本稳定
```

在 Cielo 上，两者的交叉点约在系统运行第 **14 个月**。  
在 Jaguar 上，约在第 **17 个月**。

这说明 DRAM 早期主要受到 permanent faults 影响。那些制造缺陷、弱器件、早期失效会在系统前期暴露出来。经过一段时间后，永久故障下降，瞬态故障成为主要组成。

这像 bathtub curve 的前段。

所以不能简单说：

> 内存越老越坏。

更准确的说法是：

> 在生命周期早期，故障构成会变化；永久故障下降，瞬态故障稳定。

这对运维策略很重要。

早期应该更关注 DIMM replacement 和 weak device screening。  
后期则更关注 ECC、scrubbing、checkpoint、retry 这类 transient mitigation。

---

## 4. DRAM 的第二个结论：供应商差异巨大

这是全文最有杀伤力的发现之一。

Cielo 使用了三个匿名 DRAM vendor：

- Vendor A
- Vendor B
- Vendor C

它们的 fault rate 差异非常大：

| Vendor | Fault Rate |
|---|---:|
| A | 73.6 FIT/device |
| B | 41.2 FIT/device |
| C | 18.8 FIT/device |

Vendor A 和 Vendor C 差了约：

```text
73.6 / 18.8 ≈ 3.9x
```

接近 **4 倍**。

更细看：

- permanent fault rate 差约 **2.3x**
- transient fault rate 差超过 **6x**

这不是小差异。  
这是一级变量。

如果一个数据中心只看采购单价，不看可靠性成本，就会犯局部优化错误。

正确成本函数不是：

```text
DIMM purchase price
```

而是：

```text
purchase price
+ expected faults
+ replacement labor
+ downtime
+ job reruns
+ checkpoint overhead
+ uncorrected error risk
```

便宜内存可能是最贵的内存。

这篇论文最重要的方法论提醒是：

> 如果你研究 DRAM 可靠性，但不控制 vendor/device mix，你的结论可能是错的。

后面会看到一个非常漂亮的例子。

---

## 5. DRAM 内部有没有“风水”？

论文接着问：

> DRAM 芯片内部某些位置是不是更容易发生 fault？

他们看了：

- row
- column
- bank

这里的 **bank** 不是内存条上肉眼看到的黑色芯片。  
黑色芯片是 DRAM device。  
bank 是每个 DRAM device 内部的分区。

结构大概是：

```text
DIMM
 └── DRAM device
      ├── bank 0
      ├── bank 1
      ├── ...
      └── bank 7
```

每个 bank 里面又有 row 和 column。  
所以一个 DRAM 位置可以用：

```text
bank + row + column
```

定位。

作者发现，大多数情况下，DRAM faults 在 row、column、bank 上近似均匀分布。

也就是说：

> DRAM 内部没有明显风水。

只有一个例外：

Vendor A 在 **column 0** 出现 transient fault spike。

但继续拆之后发现，这不是所有 DRAM 的普遍现象，而是：

```text
Vendor A-specific transient fault mode
```

所以结论不是“column 0 天生危险”。  
结论是“某个 vendor 的某种故障模式集中在 column 0”。

这就是控制变量的价值。

如果不按 vendor 拆，你会讲一个错误故事。

---

## 6. 数据中心位置有没有“风水”？

更有意思的是机房位置。

作者一开始看到一个现象：

> Cielo 中低编号 racks 的 DRAM fault rate 明显更高。

这太诱人了。

普通报告可能会马上解释：

- 那边温度更高
- 冷却不好
- 电源质量差
- 地板风道有问题
- 机房布局有缺陷

但作者没有停在相关性上。

他们继续看每个 rack 的 vendor mix。  
结果发现：

> 低编号 racks 装了更多 Vendor A。  
> 高编号 racks 装了更多 Vendor C。

而前面已经知道：

```text
Vendor A fault rate 高
Vendor C fault rate 低
```

所以低编号 rack 故障率高，根本不一定是位置原因。  
可能只是那里装了更多糟糕的 DRAM vendor。

作者按 vendor 重新拆分 rack fault rate 后，原来的 rack 趋势基本消失。

这就是全文最漂亮的因果拆解：

```text
表面现象：低编号 racks 故障率高
初步故事：机房位置效应
控制变量：vendor mix
真实解释：供应商分布效应
```

一句话：

> DRAM 的机房风水，大多是供应商幻觉。

---

## 7. SRAM 不一样：它真的有位置和海拔效应

论文最后研究 SRAM，也就是 CPU cache 里的内存，包括 L2 和 L3 cache。

这里结论不同。

SRAM faults 超过 **98%** 是 transient。  
这符合物理直觉。

SRAM soft error 很大程度上来自高能粒子。粒子穿过硅，产生电荷扰动，如果超过 cell 的 critical charge，就会导致 bit flip。ECC 修正后，器件本身并没有坏。

所以 SRAM 的模型更接近：

```text
particle strike
→ bit flip
→ ECC correction
→ transient fault
```

Cielo 位于 Los Alamos，海拔约 7,300 feet。  
Jaguar 位于 Oak Ridge，海拔约 875 feet。

高海拔意味着大气层屏蔽更少，宇宙射线诱发的中子通量更高。论文估计 LANL 和 ORNL 的中子通量比约 **4.39x**。

实际观测：

- Cielo 的 L2 SRAM transient fault rate 比 Jaguar 高约 **2.3x**
- Cielo 的 L3 SRAM transient fault rate 比 Jaguar 高约 **3.4x**

方向一致，但小于 4.39x。  
这说明除了 cosmic-ray neutrons，可能还有 alpha particles 等其他 fault sources。

更有意思的是 rack 内部高度。

Cielo 和 Jaguar 都显示：

> top-of-rack SRAM fault rate 比 bottom-of-rack 高约 20%。

可能原因有两个：

### 第一，温度

冷空气从机房地板进入，先经过底部 chassis，再经过中部，最后到顶部。顶部更热。作者现场测量到从底部到顶部温度可增加约 **16°C**。

温度会影响 SRAM soft error susceptibility。

### 第二，中子遮蔽和散射

宇宙射线诱发中子从上方来。顶部 chassis 先被打到。中子穿过上层硬件时可能发生散射，导致下层接收到的有效中子通量略低。

也就是说：

```text
top chassis 更暴露
bottom chassis 被一定程度遮蔽
```

作者没有强行定因，只说需要 heat studies 和 beam studies。

这是正确态度。

所以：

> DRAM 的风水大多是假的。  
> SRAM 的风水更接近真实物理。

---

## 8. 超算和普通数据中心有什么关系？

这篇论文研究的是超算，不是普通互联网数据中心。

Cielo 和 Jaguar 是大型 HPC systems。  
它们运行在数据中心机房里，但目标和普通云数据中心不同。

超算的特点是：

```text
大量节点
高速互连
紧耦合作业
长时间运行
MPI 通信
checkpoint/restart 敏感
```

普通云数据中心更像：

```text
大量相对独立服务
负载均衡
副本机制
请求级重试
节点可替换
```

区别很大。

在云数据中心，一台服务器出问题，可以迁移 VM、重启实例、流量切走。  
在超算里，一个节点出错，可能导致一个占用几千节点、运行数天的作业失败或回滚。

但这篇论文的方法论可以迁移。

不要直接搬数值。  
要搬方法。

可以迁移的是：

```text
fault ≠ error
用 device-hours 做分母
控制 vendor/device mix
区分 transient/permanent
不要把 rack correlation 直接当因果
把日志映射到具体硬件实体
```

这些适用于 GPU 集群、SSD 故障、网络丢包、云实例可靠性、甚至 AI inference error 分析。

---

## 9. 这篇论文真正教的不是内存，而是分析方法

我认为这篇论文最值得学的是这套流程：

```text
1. 定义对象
   研究 fault，不研究 error count

2. 建立映射
   console log → physical address → DIMM/device → vendor → rack/chassis

3. 归一化分母
   faults / device-hours

4. 拆故障类型
   transient vs permanent

5. 拆故障模式
   bit / word / row / column / bank / rank

6. 控制混杂变量
   vendor, device, operational hours

7. 再判断位置效应
   DRAM: mostly no
   SRAM: yes

8. 用物理机制解释
   DRAM: vendor, aging, manufacturing
   SRAM: altitude, neutrons, temperature
```

这套方法比结论更重要。

因为很多系统分析失败，不是因为数据不够，而是因为问题定义错了。

常见错误是：

```text
看到 error 多 → 以为那里更容易坏
看到 rack 故障高 → 以为机房位置有问题
看到时间趋势 → 以为老化单调变化
看到供应商便宜 → 以为总成本更低
```

错。

先问：

```text
我数的是原因，还是症状？
分母对吗？
混杂变量控制了吗？
异常是不是某个 subgroup 造成的？
有没有物理机制支持？
```

---

## 10. 总结

这篇论文可以压成三句话：

第一：

> DRAM 故障在生命周期早期会从永久故障为主，转向瞬态故障为主。

第二：

> DRAM vendor 是巨大变量，不控制 vendor，就会把供应商问题误判成位置或环境问题。

第三：

> SRAM 故障主要是瞬态，并且真的受海拔和 rack 高度影响。

再压缩一点：

> DRAM 没有明显风水，SRAM 有一点。  
> 但真正重要的是：先控制混杂变量，再讲故事。

就这样。


<div class="alert alert-warning" role="alert">
  ⚠️ 本文使用 GPT5.5 生成
</div>
