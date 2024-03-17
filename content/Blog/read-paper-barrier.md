Date: 2014-05-08 19:05:26 
Title: 内存屏障初探
Tags: cpp, memory-barrier, asm, multiprocess, multithread, thread, cocurrency
Slug: read-paper-barrier

## 原文地址

[Barrier February 17th, 2007](http://ridiculousfish.com/blog/posts/barrier.html)


## 前言：多核时代的挑战

尽管80核心的浮点运算巨兽仍然遥不可及，多核处理器的时代已经到来。多核处理器的概念并非新鲜事物，在Power Macintosh 9500中就已经采用了多核处理器技术。现在，让我们深入理解多核处理器的内在机制。

## 线程技术探讨

### 名词解释

#### 线程

线程是一种拥有共享地址空间的、能被抢占式调度的执行上下文。

#### 多线程

多线程是一种用于简化控制流、绕过阻塞系统调用的方法，并不专门用于实现程序的并行化。

#### 并发多线程

物理上并行执行的线程，旨在通过利用多核处理器优化系统性能。

### “并发多线程”的挑战

尽管并发多线程被广泛讨论，其挑战并非源自自然原因，而是我们自己的设计选择所造成的。主要问题在于，针对单线程程序的过度优化在多线程环境中不再适用。

具体来说，由于CPU的执行速度远超内存响应速度，我们开始对内存内容进行“预测”，从而避免CPU等待内存检查。这里的“预测”实际上是CPU和编译器对内存状态做出的越来越激进的假设。

## 示例分析

### 写线程示例

```cpp
// 初始时 variable1 = variable2 = 0;
while (1) {
    variable1++;
    variable2++;
}
```

### 读线程示例

```cpp
while (1) {
    local2 = variable2;
    local1 = variable1;
    if (local2 > local1) {
        print("Error!");
    }
}
```

正常逻辑下，local2 应当始终小于或等于 local1，因为 variable1 总是在 variable2 之后增加。

然而，现实是否如此？

```cpp
#include <cstdio>
#include <iostream>
#include <ctime>
#include <pthread.h>
#include <sys/time.h>
#include <unistd.h>

using namespace std;

unsigned variable1 = 0;
unsigned variable2 = 0;
#define ITERATIONS 200000000

void *writer(void *unused) {
    for (;;) {
        variable1 = variable1 + 1;
        variable2 = variable2 + 1;
    }
    return NULL;
}

void *reader(void *unused) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    unsigned i, failureCount = 0;
    for (i=0; i < ITERATIONS; i++) {
        unsigned v2 = variable2;
        unsigned v1 = variable1;
        if (v2 > v1) failureCount++;
    }
    gettimeofday(&end, NULL);
    double seconds = end.tv_sec + end.tv_usec / 1000000. - start.tv_sec - start.tv_usec / 1000000.;
    printf("%u failure%s (%2.1f percent of the time) in %2.1f seconds\n",
           failureCount, failureCount == 1 ? "" : "s",
           (100. * failureCount) / ITERATIONS, seconds);
    exit(0);
    return NULL;
}

int main(void) {
    pthread_t thread1, thread2;
    pthread_create(&thread1, NULL, writer, NULL);
    pthread_create(&thread2, NULL, reader, NULL);
    for (;;) sleep(1000000);
    return 0;
}
```

输出结果：``0 failures (0.0 percent of the time) in 1.2 seconds``


### 貌似是正确的？

程序运行的正如我们预期的那样，那么我们可以确信程序是一定正确的吗？

不能。

因为程序中的两个线程如果在同一个CPU上被调度，我们永远都会得到正确的结果。

### 线程与不同的CPU进行绑定

```cpp
void *writer(void *unused) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    sched_setaffinity(0, sizeof(cpuset), &cpuset);
    // ...
}

void *reader(void *unused) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(2, &cpuset);
    sched_setaffinity(0, sizeof(cpuset), &cpuset);
    // ...
}

// p.s. 我机器是i5双核四线程，所以绑在了CPU0和CPU2上
```

结果：```0 failures (0.0 percent of the time) in 1.4 seconds```

### 似乎仍然是准确的

尽管如此，我们考虑到CPU对变量的操作其实是作用在寄存器上，而variable1和variable2紧密相邻，这可能导致它们位于缓存的同一行。因此，它们有可能会同时被写入缓存并一起写回内存。

为了观察不同的效果，我们尝试将这两个变量分别放置在堆和栈上。

```
0 failures (0.0 percent of the time) in 1.2 seconds
0 failures (0.0 percent of the time) in 1.2 seconds
2000000000 failures (100.0 percent of the time) in 1.2 seconds
```

**太感人了！**

### 我们的敌人 —— 编译器

> Multithreading bugs are very delicate.

并行多线程的错误总是那么的奇妙，也许你的程序运行了几天安然无恙，但是在某一天某一时突然出现了难以复现的精妙bug。

如果多个线程调度在同一个CPU核心上，Bug会被掩盖。    
如果多个变量在CPU同一行Cache上，Bug会被掩盖。    
如果你人品足够好的话，Bug同样会被掩盖。

但是，如果我们排除了以上的情况后，问题就浮现出来了。

我们来看一看reader的反汇编代码：

```cpp
(gdb) disas reader
Dump of assembler code for function reader(void*):
   0x0000000000400950 <+0>: push   %rbx
   0x0000000000400951 <+1>: xor    %eax,%eax
   0x0000000000400953 <+3>: mov    $0x10,%ecx
   0x0000000000400958 <+8>: mov    $0x80,%esi
   0x000000000040095d <+13>:    xor    %ebx,%ebx
   0x000000000040095f <+15>:    sub    $0xa0,%rsp
   0x0000000000400966 <+22>:    mov    %rsp,%rdi
   0x0000000000400969 <+25>:    mov    %rsp,%rdx
   0x000000000040096c <+28>:    rep stos %rax,%es:(%rdi)
   0x000000000040096f <+31>:    xor    %edi,%edi
   0x0000000000400971 <+33>:    movq   $0x4,(%rsp)
   0x0000000000400979 <+41>:    callq  0x400790 <sched_setaffinity@plt>
   0x000000000040097e <+46>:    lea    0x80(%rsp),%rdi
   0x0000000000400986 <+54>:    xor    %esi,%esi
   0x0000000000400988 <+56>:    callq  0x400710 <gettimeofday@plt>
   0x000000000040098d <+61>:    mov    0x2006e4(%rip),%rax        # 0x601078 <variable2_p>
   0x0000000000400994 <+68>:    mov    0x2006e6(%rip),%edx        # 0x601080 <variable1>
   0x000000000040099a <+74>:    mov    (%rax),%ecx
   0x000000000040099c <+76>:    mov    $0x77359400,%eax
   0x00000000004009a1 <+81>:    nopl   0x0(%rax)
   0x00000000004009a8 <+88>:    cmp    %ecx,%edx
   0x00000000004009aa <+90>:    adc    $0x0,%ebx
   0x00000000004009ad <+93>:    sub    $0x1,%eax
   0x00000000004009b0 <+96>:    jne    0x4009a8 <reader(void*)+88>
   0x00000000004009b2 <+98>:    lea    0x90(%rsp),%rdi
   0x00000000004009ba <+106>:   xor    %esi,%esi
   0x00000000004009bc <+108>:   callq  0x400710 <gettimeofday@plt>
   0x00000000004009c1 <+113>:   cvtsi2sdq 0x98(%rsp),%xmm0
   0x00000000004009cb <+123>:   cvtsi2sdq 0x90(%rsp),%xmm1
   0x00000000004009d5 <+133>:   movsd  0x1a3(%rip),%xmm3        # 0x400b80
   0x00000000004009dd <+141>:   mov    %ebx,%eax
   0x00000000004009df <+143>:   cvtsi2sdq 0x88(%rsp),%xmm2
   0x00000000004009e9 <+153>:   cmp    $0x1,%ebx
   0x00000000004009ec <+156>:   mov    $0x400b3d,%ecx
   0x00000000004009f1 <+161>:   mov    $0x1,%edi
   0x00000000004009f6 <+166>:   divsd  %xmm3,%xmm0
   0x00000000004009fa <+170>:   mov    %ebx,%edx
   0x00000000004009fc <+172>:   mov    $0x400b40,%esi
   0x0000000000400a01 <+177>:   divsd  %xmm3,%xmm2
   0x0000000000400a05 <+181>:   addsd  %xmm0,%xmm1
   0x0000000000400a09 <+185>:   cvtsi2sdq 0x80(%rsp),%xmm0
   0x0000000000400a13 <+195>:   subsd  %xmm0,%xmm1
   0x0000000000400a17 <+199>:   cvtsi2sd %rax,%xmm0
   0x0000000000400a1c <+204>:   mov    $0x400b3c,%eax
   0x0000000000400a21 <+209>:   cmovne %rax,%rcx
   0x0000000000400a25 <+213>:   mov    $0x2,%eax
   0x0000000000400a2a <+218>:   mulsd  0x156(%rip),%xmm0        # 0x400b88
   0x0000000000400a32 <+226>:   subsd  %xmm2,%xmm1
   0x0000000000400a36 <+230>:   divsd  0x152(%rip),%xmm0        # 0x400b90
   0x0000000000400a3e <+238>:   callq  0x400700 <__printf_chk@plt>
   0x0000000000400a43 <+243>:   xor    %edi,%edi
   0x0000000000400a45 <+245>:   callq  0x4006f0 <exit@plt>
```

简而言之，关键在以下几句：

```cpp
0x000000000040098d <+61>:    mov    0x2006e4(%rip),%rax        # 0x601078 <variable2_p>
0x0000000000400994 <+68>:    mov    0x2006e6(%rip),%edx        # 0x601080 <variable1>
0x000000000040099a <+74>:    mov    (%rax),%ecx
0x000000000040099c <+76>:    mov    $0x77359400,%eax
0x00000000004009a1 <+81>:    nopl   0x0(%rax)
0x00000000004009a8 <+88>:    cmp    %ecx,%edx
0x00000000004009aa <+90>:    adc    $0x0,%ebx
0x00000000004009ad <+93>:    sub    $0x1,%eax
0x00000000004009b0 <+96>:    jne    0x4009a8 <reader(void*)+88>
```

我们可以看出，循环体在+88～+96行，而对variable1与variable2的取值都放在了循环以外。

> 注：   
> adc是带进位加法，adc $0x0, %ebx => %ebx = $0x0 + %ebx + CF    
> cmp的结果正是放在CF（大于表示为溢出），ZF（相等表示为0），PF（小于表示为-1,则低8位全为1,故有偶数个1）

正是这个“小意外”，导致了我们的结果要不是100%正确，要不是100%错误。

#### 使用volitile（？）

让我们修改一下代码：

```cpp
volatile unsigned variable1 = 0;
volatile unsigned *variable2_p = NULL;
#define ITERATIONS 500000000LL // 调小一下数据规模，因为volatile太慢了_(:з」∠)_
```

我得出的来的结果是：
```
0 failures (0.0 percent of the time) in 9.6 seconds
```

而作者得出的结果是：
（时间上的差异不计，因为我们的数据规模不一样，我实验的次数要多一些。
```
fish ) ./a.out
12462711 failures (24.9 percent of the time) in 3.7 seconds
```

从作者的结果来看，看起来效果好了很多，虽然慢了30多倍，但是结果并不是全对全错了。

而从我的结果来看，volatile看似神丹妙药，解决了所有的问题。(both g++ and clang++)

**这是为什么呢?**

其原因在于体系结构的差异。volatile只能保证如下两点：

* volatile变量的访问不会优化成寄存器访问，而是每次都去访问“内存”（这个引号一会再解释）
* volatile变量间的访问顺序不会被编译器乱序

而其他的一切，volatile和编译器都不会给出任何保证。

例如，不同的CPU都有其内部的私有Cache，CPU的内存访问，如果命中了Cache，则不会真正的访问内存。但由于其私有Cache对于其它的CPU是不可见的，使用volatile就埋下的Bug的种子。

虽然在我们的实验中，程序运行的很好，没有出现Bug。但是，一是由于多线程的Bug都是subtle和delicate的，我不能保证在一个需要7x24工作的服务器程序中，它不会出现任何Bug；二是至少我们的代码是** not portable **的，如果有一天，我们从x86-64平台切换到了``PowerPC``？或是``IA64``？我们不能保证在这些体系结构上，编译器和CPU能为我们提供同样的保障。

于是有人高声疾呼： volatile不能用来做为多线程的同步机制！

> 补充于20240317：在一台老旧的安卓手机上重复了实验，volatile确实无法提供相关的保障

```
~/tmp $ clang++ -O2 a.cc && ./a.out
99880586 failures (49.9 percent of the time) in 3.0 seconds
```

#### 小心CPU的行为

在先前的实验中，尽管程序的表现与预期一致，但我们无法确保CPU将始终按顺序执行代码。实际上，CPU可能会对操作顺序进行优化，例如，将var1++和var2++的执行顺序调换，这在当前主流的CPU中是常见的做法。

值得注意的是，由于乱序执行会导致功耗增加，某些处理器如ARM和Intel Atom已经取消了这一机制。然而，我们无法预知未来代码可能会在哪种硬件架构上运行，例如ARM集群，这需要我们保持警惕。

#### 避免使用锁
通常情况下，通过引入互斥锁（mutex）似乎能够解决并发问题。然而，根据作者的测试，引入互斥锁可能会导致程序速度降低至原来的1/130，而自旋锁（spinlock）也可能使得速度降低至原来的1/4。

因此，我们应该暂缓，仔细考虑作者接下来的建议。

### 内存屏障的应用
在多CPU环境中，处理器往往独立运行，不会协调彼此的操作。

目前，我们面临两个并不理想的解决方案：一是将所有线程限制在单个CPU上运行，二是通过引入重量级锁来同步操作。这些方法都不尽人意，且效率低下。

实际上，我们需要做的是，通过内存屏障技术，暂时阻止编译器或CPU对程序中的数据读写操作进行重排序。
```cpp
for (;;) {
    variable1 = variable1 + 1;
    barrier();
    *variable2 = *variable2 + 1;
}
```
这样我们保证了，在var1++必然早于var2++。var2++后面也可以加一道barrier，只不过在我们的场景下，提供这种保证是不必须的。

作者又做了一次试验。

```
fish ) ./a.out
260 failures (0.0 percent of the time) in 0.9 seconds
```

这次且错误减少了许多。

我们再把读线程写加上memory barrier.

```cpp
for (i=0; i < ITERATIONS; i++) {
    unsigned v2 = *variable2;
    barrier();
    unsigned v1 = variable1;
    if (v2 > v1) failureCount++;
}
```

看看结果：

```
fish ) ./a.out
0 failures (0.0 percent of the time) in 4.2 seconds
```

程序表现出了正确的结果。

我们可以看出，如果你对线程A的读写顺序做出要求，必然的，你也要对线程B的顺序做要求，以此类推，线程C，线程D……

所以，**Memory barriers always come in pairs, or triplets or more.**

同样的，线程锁也是这样的，自己锁自己总不是一种愉快的体验（笑

### CPU的乱序执行

我们可以看到PowerPC有三种内存屏障，而DEC Alpha平台有更多。这意味着，CPU使用更激进的策略来重排指令，而强制限制其重排的代价是非常高的。

而x86平台则非常守序，作者猜测其原因是由于早期x86的指令技术并非完善，而在那时内存与CPU的速度不像现在这样悬殊，所以x86使用了``strongly ordered memory``而非像上面几款CPU一样的采用过多的指令重排序。如今，由于x86背上了向前兼容性的包袱，看似我们的"好日子"一直不会结束。

x86-64，做为x86的64位升级版，同样没有实现``weakly ordered``，或者说，保留了实现``weakly ordered``的权利。而``IA64``平台，如``Itanium``，则实现了``weakly ordered``。

作者猜测x86_64之所以保守，是为了与IA64平台对抗。x86_64的对于x86良好的兼容性可以让程序员多活几年，所以x86_64在市场的表现更好。

作者还表示，而苹果放弃IA64平台转投x86-64多少有一些可惜，因为苹果并没有移植性问题，PowerPC已经逐渐衰落，为什么不试试IA64呢。

实际上，根据Wikipedia，现在支持IA64的操作系统非常少，只有WinNT Family，Red Hat Linux，Debian/Gentoo/Suse以及其它。而从Windows Server 2008 R2之后，Microsoft也表示不再支持Itanium。所以从现在看来，IA64平台相对x86/x64来说，是失败的。

### 双重检查锁

让我们看一下如下的Obj-C代码

```objc
+ getSharedObject {
    static id sharedObject;
    if (! sharedObject) {
        LOCK;
        if (! sharedObject) {
            sharedObject = [[self alloc] init];
        }
        UNLOCK;
    }
    return sharedObject;
}
```

这是非常经典的一种DCLP(Double Checked Lock Pattern)的实现。

这个看起来不错，但是你已经知道这并不靠谱了。当我们初始化我们的共享单例，先要再修改类内的指针，使其指向一块声明好的内存，再初始化一个sharedObject的instance。

不过，你是知道的，CPU和编译器会把一切都搞砸，它们会以任意的顺序执行我们的命令，同时处理器之间互相不通气，于是就会出现如下的情况：

线程A为指针声明了一段空间，但是还没来及初始化这个instance，线程A就被挂起了。

之后线程B接管一切，发现指针有值，结果因为访问了野指针导致程序挂掉。

不过根据上面的文章，你们应该知道怎么处理这个问题了 —— 试试内存屏障！

p.s. 如果大家对obj-c不熟悉的话，可以看我另外一篇文章。那篇文章是关于Scott Meyers大神写的一篇论文，专门用来讨论DCLP问题的。

```objc
+ getSharedObject {
    static id sharedObject;
    if (! sharedObject) {
        LOCK;
        if (! sharedObject) {
            id temp = [[self alloc] init];
            OSMemoryBarrier();
            sharedObject = temp;
        }
        UNLOCK;
    }
    OSMemoryBarrier();
    return sharedObject;
}
```


而在《C++ and the Perils of Double-Checked Locking》一文中，Scott Meyers和Andrei Alexandrescu给出的解决方案如下。

```cpp
Singleton* Singleton::instance () {
    Singleton* tmp = pInstance;
    // insert memory barrier
    // clear the cache to flush ``pInstance``
    // prevents "downwards migration" of Singleton’s construction (by another thread);
    if (tmp == 0) {
        Lock lock;
        tmp = pInstance;
        if (tmp == 0) {
            tmp = new Singleton;
            // insert memory barrier
            // prevent optimistic that eliminate the temporary variable ``tmp``
            // prevents "upwards migration" of pInstance’s initialization
            pInstance = tmp;
        }
    }
    return  tmp;
}
```

两种解决方案的memory barrier插入的位置不同。但是都不能说是错的。因为一个是传static instance，一个是传pointer。

其实还有更“暴力”的方法。

直接来一把大锁，哐当把整个函数锁起来，并且在每一个线程内保留一个**本线程专属**指向单例的指针（做cache）。这样N个线程只需要调用这个函数N次，线程竞争也相对少很多。并且根据Linux下的futex技术，无竞争下的锁相对节省了不少资源。

```cpp
Singleton* Singleton::instance() {
    Lock lock;
    if(pInstance == 0) {
        pInstance = new Singleton;
    }
    return pInstance;
}
```

### 我们真的需要这么做吗

上面的obj-c代码中，保证双重检查锁正确的，其实是第二个内存屏障。但是，在那里，我们需要的其实是一个"data dependency barrier"。

Linux内核中给出很多经过精心优化的内存屏障，我们在这里可以使用。不过，要在使用的时候写好注释，一是为了未来的验证，二是为了记录自己当时的思路。

毕竟多线程的操作要小心再小心，我们需要充足的理由，更多的小心来应对。

```obj-c
+ getSharedObject {
    static id sharedObject;
    if (! sharedObject) {
        LOCK;
        if (! sharedObject) {
            id temp = [[self alloc] init];
            OSMemoryBarrier();
            sharedObject = temp;
        }
        UNLOCK;
    }
    /* data dependency memory barrier here */
    return sharedObject;
}
```

### 一切都结束了吗？

是的。不过让我们总结一下吧。

![Mutex Tank](https://github.com/Wizmann/assets/raw/master/wizmann-tk-pic/barrier_tank.png)

* 处理器和编译器并不能充分保证代码执行的顺序，它们会把你的代码到处移动。所以**Be warned and wary!**
* 多线程的错误是非常subtle和delicate的，所以我们很难设计测试用例
* 因此，别指责QA了，他们也不是故意的。RD要对自己的代码负责
* 锁很安全，但是也很重
* 内存屏障是一种更快的，不阻塞的，不会死锁的一种锁的替代物。它们总要花费更多的心思，并且也不是到处可用的银弹。但是它确实很快，有更好的伸缩性。
* 内存屏障往往是成对出现的。了解第二个内存屏障要出现在哪里，有助于你理解你的代码，即使你所使用的体系结构不需要第二个内存屏障。

### 扩展阅读

[LINUX KERNEL MEMORY BARRIERS](https://www.kernel.org/doc/Documentation/memory-barriers.txt)

[Memory Consistency and Event Ordering in Scalable Shared-Memory Multiprocessors](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.17.8112)
