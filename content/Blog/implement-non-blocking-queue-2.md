Date: 2024-04-14
Title: 实现一个无锁消息队列（续与勘误）
Tags: multi-thread, cas, cmpxchg, non-blocking, wait-free, 
Slug: implement-non-blocking-queue-2

- 本文内容主要参考自[Implementing Lock-Free Queue](https://people.cs.pitt.edu/~jacklange/teaching/cs2510-f17/implementing_lock_free.pdf)一文（以下简称“原论文”）
- 是对[实现一个无锁消息队列](https://wizmann.top/implement-non-blocking-queue.html)一文的内容进行补充
- ## TL；DR
	- 尽管[实现一个无锁消息队列](https://wizmann.top/implement-non-blocking-queue.html)一文中的实现是正确的，但是忽略了“非阻塞性”
		- 例如，当任一插入操作被阻塞，则其它插入操作均会陷入忙等待
		- 此实现与[A simple and correct shared-queue algorithm using Compare-and-Swap](https://dl.acm.org/doi/pdf/10.5555/110382.110466)的实现基本一致
	- 对于一个支持并发的数据结构，理应同时具备非阻塞性和无等待性
		- 非阻塞性（non-blocking）：无论是由于CPU调度或其他外部因素，数据结构的操作不能被中断或延迟
		- 无等待性（wait-free)：保证没有任何线程会遭受饥饿状态
	- 前一篇博文对其它实现的质疑，主要在于ABA问题，但这个问题是Compare&Swap所特有的，需要特定的实现来规避
- ## 理论基础
	- 我们的目标是实现一个支持并发enqueue/deque的队列
	- 对于这样的数据结构，有两个重要的特性
		- 非阻塞性（non-blocking）
			- 对于每一个执行线程，所有的操作将会在有限的次数内完成
			- 无论本线程或其它线程在执行过程中因其它原因（如CPU调度）执行过缓，或者被中断
		- 无等待性（wait-free)
			- 没有线程会饥饿
		- 基于锁的数据结构不符合上述特性，因为持有锁的线程可能会无限期地阻塞所有操作
		- “线性一致性”(Linearizability) —— 更强的正确性
			- 非并发操作应当按照它们的逻辑顺序执行，以保证操作的正确性，而并发操作则可以按任意顺序进行
	- "Fetch&Add" 与 "Compare&Swap"
		- 常用的原子操作，这里不做赘述
- ## 基于链表的无锁队列实现
	- 略，参考原论文与[无锁队列的实现](https://coolshell.cn/articles/8239.html)一文
- ## 基于数组的无锁队列实现
	- 略，参考原论文与[无锁队列的实现](https://coolshell.cn/articles/8239.html)一文
- ## ABA问题
	- Compare&Swap操作确保了值修改的原子性。指针作为值的一种，代表着某个内存地址，但Compare&Swap对指针的操作无法保证其指向的内存内容不被修改
	- 考虑到可能释放旧内存后再申请新内存，这两块内存虽逻辑不同却可能拥有同一地址，这对Compare&Swap操作造成了困扰
	- 解决方案是为指针加入引用计数（ref count），以确保内存在可访问时不会被释放或重用
- ## 性能对比
	- 上面我们已经提到，[A simple and correct shared-queue algorithm using Compare-and-Swap](https://dl.acm.org/doi/pdf/10.5555/110382.110466)一文中的方法缺少了“非阻塞性”，，但其性能与原论文中的实现十分接近
	- 但是在原理上，“非阻塞性”实现可以避免意外的线程停止或延迟
	- 疑问：是否会在P99级别的Latency上才会体现出明显的差异？
- ## 参考链接
	- [Implementing Lock-Free Queue](https://people.cs.pitt.edu/~jacklange/teaching/cs2510-f17/implementing_lock_free.pdf)
	- [A simple and correct shared-queue algorithm using Compare-and-Swap](https://dl.acm.org/doi/pdf/10.5555/110382.110466)
	- [Concurrency – Correctness of Concurrent Objects](https://cs.nyu.edu/~wies/teaching/cso-fa19/class27_concurrency.pdf)
- ## 后续
	- [Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms](https://www.cs.rochester.edu/~scott/papers/1996_PODC_queues.pdf)
	- [C++ 单生产者&单消费者 无锁队列](https://zhuanlan.zhihu.com/p/690872647)
	- [Single Producer Single Consumer Lock-free FIFO From the Ground Up - Charles Frasch - CppCon 2023](https://www.youtube.com/watch?v=K3P_Lmq6pw0&ab_channel=CppCon)


<div class="alert alert-info" role="alert">本文大（划掉）部分内容由ChatGPT4生成</div>
