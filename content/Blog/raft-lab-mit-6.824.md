Date: 2019-05-02 21:33:00
Title: 6.824 Lab 2: Raft协议实现指南 （无剧透版）
Tags: raft, 分布式系统
Slug: raft-lab-mit-6.824

## 背景

MIT6.824是一个用来学习分布式系统的非常好的资源。其中第二个课程作业就是关于[Raft算法][1]。

由于在工作中涉及到分布一致性算法的调研，接触了paxos/raft算法。然后被@neutronest安利了一发，于是开始着手实现这个作业。

本文是我对这个项目的实现总结。希望能在划出重点的同时，不涉及实现细节，避免破坏大家的写代码体验。

本文唯一参考资料：[In Search of an Understandable Consensus Algorithm][2]

## 任务分解

在官方文档里，整个项目被分成了2A、2B、2C三个部分：

* 2A - 投票与选举
* 2B - 一致性
* 2C - 可持久化

实际上，2C的工作量非常少，我们可以把2B和2C合成一个。然后单独提出几个比较重要的测试用例，划分成子项目。任务分解如下：

* 2A - 投票与选举
* 2B/2C - 一致性和可持久化
* 三个难度比较高的Case
    * Test (2B): leader backs up quickly over incorrect follower logs    
    验证协议实现的正确性
    * Test (2B): RPC counts aren't too high      
    测试协议是否产生了过多的RPC请求。验证协议的性能。
    * Test (2C): Figure 8 (unreliable)      
    测试在极端混乱的情况下，Raft协议是否能及时恢复正常工作。验证协议实现的正确性和性能。

所以推荐大家按顺序以上顺序进行实现。并且充分利用版本控制对代码进行开发和重构。

## 需要关注的知识点

以下会介绍每一个部分需要重点关注的知识点，内容包括golang基础和论文中的知识点，无剧透，请放心食用。

### 准备工作

golang是一门傲慢的语言，其标准库的缺乏实在是让人感到TMD蛋疼。但是对于一个课程作业来说，我们也没有必要引入一系列第三方库。所以我们先要扩充`util.go`文件，使其为我们的开发提供更多的便利。

#### Log模块

项目给出的`DPrintf`函数非常简单，只提供了一个`fmt.Printf`的封装。并不能打印行号和文件名。这里提供一个扩展版本。

```golang
func DPrintf(format string, a ...interface{}) {
    if Debug > 0 {
        _, path, lineno, ok := runtime.Caller(1);
        _, file := filepath.Split(path)

        if (ok) {
            t := time.Now();
            a = append([]interface{} { t.Format("2006-01-02 15:04:05.00"), file, lineno }, a...);
            fmt.Printf("%s [%s:%d] " + format + "\n", a...);
        }
    }
}
```

其输出示例如下：

```
2019-05-02 09:28:35.04 [raft.go:652] Node[1] is processing, state: [LEADER], term 1, commitIndex: 12, logCount: 12, leader 1
```

#### Max和Min函数

golang是没有对于int值的`max`和`min`函数的，这里省略脏话100句。

```golang
func Min(a int, b int) (int) {
    if a < b {
        return a;
    } else {
        return b;
    }
}

func Max(a int, b int) (int) {
    if a > b {
        return a;
    } else {
        return b;
    }
}
```

#### Assert函数

是的，你没有看错，golang也没有提供`assert`函数。如果你嫌到处写`if`和`panic`太丑的话，可以使用这个`assert`函数。

```golang
func Assert(flag bool, format string, a ...interface{}) {
    if (!flag) {
        _, path, lineno, ok := runtime.Caller(1);
        _, file := filepath.Split(path)

        if (ok) {
            t := time.Now();
            a = append([]interface{} { t.Format("2006-01-02 15:04:05.00"), file, lineno }, a...);
            reason := fmt.Sprintf("%s [%s:%d] " + format + "\n", a...);
            panic(reason);
        } else {
            panic("");
        }
    }
}
```

#### Log Id

为了验证日志的一致性，我们在日志中额外加入一个UUID来进行标识。

```
import "math/rand"

func CreateLogId() (uuid string) {
    b := make([]byte, 16)
    _, err := rand.Read(b)
    if err != nil {
        fmt.Println("Error: ", err)
        return
    }

    uuid = fmt.Sprintf("%X-%X-%X-%X-%X", b[0:4], b[4:6], b[6:8], b[8:10], b[10:])

    return uuid
}
```

以上代码可以生成一个（伪）UUID对日志进行标识。推荐使用`math/rand`，因为这里我们使用伪随机数就够了。

> 注：这里的UUID只是看起来像一个UUID，实际上UUID有其特殊的规范与格式。但是由于golang内部没有提供可用的UUID库，所以只好随手模拟了一个。

#### 文件组织

默认的实现是把所有的东西都写到了`raft.go`文件里。一个非常大的文件可能会给我们的开发带来负担，所以我的做法是把所有的类声明放到`models.go`文件里。以避免文件的膨胀。

#### 锁与defer

在raft实现中，锁可以用来保证在多线程环境下数据的正确性。所以只要在涉及到raft内部状态的变化时，都需要加锁。一个常见的加锁pattern是：

```golang
rf.mu.Lock() // 加锁
defer rf.mu.Lock() // 在函数执行完成后解锁
```

这里推荐使用defer，因为手动控制锁实现是过于容易出错。但是defer也是有坑的！

不同于C++的大括号作用域，defer的触发时间是在函数执行完成之后，而并不是退出当前大括号时。这点非常需要注意，否则极易出现死锁。

如果我们想实现C++中`do { ... } while (0);`类似的lock guard pattern，可以使用以下实现：

```golang
func() {
    rf.mu.Lock()
    defer rf.mu.Unlock()
    // do something here
}()
```
这样一来，在执行完当前lambda之后，就会自动解锁。

#### 刷新定时器

由于raft算法里面使用了定时器，这里提供一个刷新定时器的golang代码。这样实现是为了每次在刷新的时候，清空定时器中原有的超时时间，以避免混乱。

```golang
func (rf *Raft) renewTimer(timeout time.Duration) {
    if (rf.timer == nil) {
        rf.timer = time.NewTimer(timeout)
    } else {
        if (!rf.timer.Stop()) {
            select {
            case <- rf.timer.C:
                // pass
            default:
                // pass
            }
        }
        rf.timer.Reset(timeout)
    }
}
```

以及，在定时器超时之后，不要忘了更新定时器。

### 2A - 投票与选举

#### 所需要类的声明

论文中的`Figure2`包含了算法中所有的类以及基本算法。在2A中，所有的类都会被用到。由于2A中只包括投票与选举，所以和日志相关的字段可以先忽略掉。

#### Checklist for 2A

* 实现raft状态机的三个状态：leader，follower和candidate
* 实现RPC函数：`sendRequestVote`（发送端）和`RequestVote`（接收端的回调函数）
* 实现RPC函数：`sendAppendEntries`（发送端）和`AppendEntries`（接收端的回调函数）    
* 保证raft状态机的任期号（`currentTerm`）是单调递增的
* 一个Follower对于某一个Term只能投出一票
* 实现Leader心跳，维护当前任期（Term）。
* 实现Follower选举超时（election timeout）
* 实现Candidate选举的三种场景
    * 获得多数选票，赢得选举。状态切换为Leader
    * 其它的节点已经被选为Leader。状态切换为Follower
    * 在选举中并未获得多数选票，状态切换为Follower
* 实现Candidate随机选举超时（randomized election timeout）

### 2B/2C - 日志复制与持久化

#### 基本工作流

日志复制的基本工作流如下：

Leader接受用户请求，将状态变化写入本机的日志流中，并且把日志复制到Followers。如果本条日志合法，Followers会将这条日志标记为“提交”（committed），然后再将这条日志“应用”（apply）到Raft协议之外的状态机。Follower在提交日志之后，就可以向Leader回报这条日志已经被提交。在本条日志被多数节点提交之后，Leader再将这条日志标记为提交。此时，用户的请求就可以被确认（ACK）了。

Raft的论文中，Leader需要维护`commitIndex`和`lastApplied`这两个状态。为了简单起见，我们可以忽略“应用”（apply）这个过程。这两个状态我们只需要维护`commitIndex`即可。

> Raft协议不是2PC，千万不要搞混了哦～

#### 回滚与滚回来

![rollback][3]

从上面的工作流我们可以看到，对于已经committed的日志，仍然有可能是不可靠的。

例如，在Term1时，节点1作业Leader提交到了日志(1, 2)，而Follower节点Node2和Node3分别提交到了日志(1, 2)和(1, 3)。此时Leader短暂断线，出发选举超时，就会进行下一轮的选举。如果节点Node2被选为Leader，那么节点Node3就会被Leader多出一条日志，这是不被允许的。如果节点Node3被选为Leader，那么Node2就比Leader在Term1少一条日志，需要补齐。

> 这里有人可能会怀疑，节点2比节点3少一条日志，那么按照论文里的说法，因为节点3的日志比较节点2要多，所以只有节点3才能赢得下一轮选举。这其实是不对的，如果节点3断线，节点1和节点2仍然可以组成一个quorum，选举出Leader。

所以我们需要考虑将已committed的日志回滚（向左滚），以及缺失的日志补齐（向右滚）。这里其实有一些优化的点，我们后文再说。

再次注意，保证日志的一致性是Raft协议正确性的必须保证，在这一点上一定要注意。

#### 乱序请求

本项目中，模拟的RPC协议并不能保证可靠性（会丢包）、有序性（会乱序），也没有SLA（没有超时时间的上限），更不用想拥塞控制。我们可以理解为它在底层使用了UDP协议，而不是TCP。所以我们不能做出任何假设。

#### Checklist for 2B/2C

* 日志的状态会影响Leader选举    
如果两份日志流的最后一条日志的Term不一样，那么我们认为Term号大的日志“比较新”。如果Term号一样，那么Index大的日志“比较新”
* 如果Leader和Follower的日志不一致，那么Follower需要拷贝Leader的日志（向左滚或向右滚的正确性）      
这里推荐使用Assert加断言进行保证，如果出错可以获得实时的现场
* 对于小于当前Term的日志，Leader不需要等多数Follower确认就可以直接commit
* 一个重要特性：如果两个日志的(Term, Index)一致，那么其内容也是一致的。并且在此日志之前的所有日志都必须是一致的
* 另一个重要特性：RPC请求是幂等的，也就是多次重复发送一个请求并不会破坏Raft协议的状态

### 最后的3个Case

最后的三个Case有一个共同点，就是对协议的效率和正确性有比较高的要求。即使前面的代码里你的实现是正确的，也有可能因为各种其它的原因造成Case挂掉。

建议首先解决正确性问题，再提升效率。

#### 向左滚的优化（重要！）

在论文的5.3节，介绍了一种回滚的优化。如果Leader和Follower在某个Index上的日志不一致，Leader的版本记为(Term1, Index)，Follower的版本记为(Term2, Index)。那么Follower需要回滚所有日志，直到Term小于`Min(Term1, Term2)`。

这样的好处是可以加快回滚的效率。虽然论文上表示这种优化并非必要，但是在模拟出来的极端网络环境下，这样的优化可以帮助我们通过一些比较变态的Case。

#### 其它的非官方优化

这里还有一些论文里没的提到的优化方案，不保证一定是正确的。

为了不剧透，放到单独的链接里了：[剧透警告！][4]

## 测试结果

![tests][5]

在Travis CI上面运行的测试。自我感觉实现的比较一般，所以你们的程序应该跑的比我快一点才正常。

## 总结

想要完整正确的实现这个项目，首先一定要把论文读懂。并且划出实现上应该注意的重点。

当遇到正确性问题时，一定要回归论文，大部分的问题都可以获得解答。当遇到性能问题时，可以参考作业上面的Hints，里面也有非常有用的信息。

MIT的这个课程还有基于raft实现kv storage的项目，后续如果有时间应该还会做吧。


  [1]: https://pdos.csail.mit.edu/6.824/labs/lab-raft.html
  [2]: https://raft.github.io/raft.pdf
  [3]: https://raw.githubusercontent.com/Wizmann/assets/3f1056d6f142755204092fb89a474dc964608bab/wizmann-pic/2019-05-02_14-40-52.png
  [4]: https://github.com/Wizmann/assets/blob/master/wizmann-pic/19-05-02/raft-hints.md
  [5]: https://raw.githubusercontent.com/Wizmann/assets/e35dd59aa533ddd19065f070dcb85a3734cc035d/wizmann-pic/19-05-02/2019-05-02_21-37-14.png
