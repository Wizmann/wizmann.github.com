Date: 2023-12-17
Title: 使用 SPIN/Promela 对多线程 Concurrent FIFO Queue 进行建模与验证
Tags: SPIN, Promela, SPIN/Promela, 多线程, multi-thread, Queue, FIFO
Slug: SPIN-Promela-Concurrent-Queue-1


## 引言

并发编程中设计和验证多线程数据结构是一项极大的挑战，即使是实现一个简单的数据结构（见[《实现一个无锁消息队列》][1]一文），都需要不少的脑力、讨论与实践才可以尽可能保证其正确性。

本文尝试使用 SPIN/Promela 对多线程环境下的 Concurrent FIFO Queue 的一种实现进行建模与验证。

## Concurrent FIFO Queue 的设计

为了保证多线程操作的正确性，我们采用了以下关键设计：

* Dummy Head 和 Dummy Tail 节点：引入这两个节点简化了队列操作逻辑，降低并发中的复杂性
* Dummy Tail Data 指针作为“锁”：这个方法确保多个线程不会同时操作尾节点，降低了对锁的依赖
* 利用指针赋值的原子性：通过这种方式，减少了锁的使用，提高了效率

## SPIN/Promela 建模中的考虑因素

在使用 SPIN/Promela 建模时，我们面临了几个挑战：

* 静态内存管理：SPIN/Promela 缺乏动态内存操作，因此我们实现了一个极简的手动管理的静态内存堆栈。
* 减少状态空间：队列的长度可以是无限的，这也就意味着无限的状态空间。因此，我们将队列的最大长度设为3，以减少状态的穷举空间。
* 模拟CAS操作：由于缺少CAS指令，我们使用 do 循环和 atomic 块来模拟，同时开启 weak fairness 避免无限循环。（见[《在SPIN/Promela中模拟CAS》][2]一文）
* LTL表达式的使用：使用 LTL 表达式来穷举检查所有可能的程序状态，包括边缘情况。
	* LTL表达式偶尔会有一些”反直觉“的情况出现
	* 例如在程序验证路径中，虽然理论上队列大小可以为0~3当中的任意数。但是也存在一种可能，即队列大小可以在2和3之间反复变化。如果我们声明“**永远** **最终** 一定存在 queue size==1” 的表达式会失败，因为队列大小在这种“人造场景”下永远不会为1。
	* 这种情况要求我们非常精确地设计 LTL 表达式
* 代码与断言的结合：因为 LTL 表达式的表达能力有限，需要结合代码中的 assert 语句来进行更全面的验证


## 代码示例
下面是我们用于建模和验证 Concurrent FIFO Queue 的 Promela 代码示例：

```promela
#define MAX_CAPACITY 3
#define NUM_NODES MAX_CAPACITY + 2
#define EMPTY -1
#define INVALID_PTR -1

#define QUEUE_NOT_FULL (memptr > 0)
#define QUEUE_NOT_EMPTY (memptr < MAX_CAPACITY)
#define QUEUE_IS_EMPTY (memptr == MAX_CAPACITY)
#define QUEUE_IS_FULL (memptr == 0)

#define HEAD 0

typedef QueueNode {
  int nextptr;
  int data;
};

// 1 dummy head + 1 dummy tail + #(data nodes)
QueueNode nodes[NUM_NODES];

// data nodes + dummy tail
int memory[MAX_CAPACITY + 1];
int memptr = MAX_CAPACITY;
int tail;
int queue_size = 0;

bool running = false;

init {
    int i = 0;
    for (i : 0 ..  NUM_NODES - 1) {
        nodes[i].nextptr = INVALID_PTR;
        nodes[i].data = EMPTY;
    }

    for (i : 0 ..  MAX_CAPACITY - 1) {
        memory[i] = i + 2;
    }
    memory[MAX_CAPACITY] = -1;

    nodes[HEAD].nextptr = HEAD + 1;
    tail = HEAD + 1;

    atomic {
      run worker(0);
      run worker(1);
    }
    running = true;
}

inline update_queue_size() {
    d_step {
        int cur = HEAD;
        int size = 0;
        do
            :: nodes[cur].nextptr != INVALID_PTR -> {
                size++;
                assert(cur != INVALID_PTR);
                cur = nodes[cur].nextptr
            }
            :: else -> break;
        od
        assert(nodes[cur].nextptr == INVALID_PTR);
        size--; // remove HEAD
        assert(size >= 0 && size <= MAX_CAPACITY);
        queue_size = size;
    }
}

inline enqueue(workerId) {
    int cur1 = INVALID_PTR;
    atomic {
        if
        :: (memptr - 1 >= 0) -> {
            cur1 = memory[memptr - 1];
            memory[memptr - 1] = -1;
            memptr--;
            assert(nodes[cur1].data == EMPTY);
            assert(nodes[cur1].nextptr == INVALID_PTR);
        }
        :: else -> skip
        fi
    }

    if
    :: cur1 != INVALID_PTR -> {
        do
        :: (true) -> {
            // CAS
            atomic {
                if
                :: (nodes[tail].data == EMPTY) -> {
                    nodes[tail].data = workerId;
                    break
                }
                :: else -> skip;
                fi
            }
            update_queue_size();
        }
        od

        nodes[tail].nextptr = cur1;
        tail = cur1;
    }
    :: else -> skip
    fi
}

inline dequeue(workerId) {
    int cur2 = INVALID_PTR;
    do
    :: (true) -> {
        int nxt2 = nodes[HEAD].nextptr;
        cur2 = INVALID_PTR;
        if
        :: (nxt2 != tail) -> {
            cur2 = nxt2;
            atomic {
                update_queue_size();
                if
                :: (nodes[HEAD].nextptr == nxt2 && nxt2 != tail) -> {
                    nodes[HEAD].nextptr = nodes[cur2].nextptr;
                    nodes[cur2].nextptr = INVALID_PTR;
                    nodes[cur2].data = EMPTY;
                    update_queue_size();
                    break
                }
                :: else -> skip;
                fi
            }
        }
        :: else -> break
        fi
    }
    od

    if
    :: (cur2 != INVALID_PTR) -> {
        d_step {
            assert(nodes[cur2].nextptr == INVALID_PTR);
            assert(nodes[cur2].data == EMPTY);
            assert(memptr + 1 <= MAX_CAPACITY);

            int i;
            for (i : 0 ..  memptr - 1) {
                assert(memory[i] != cur2);
            }
            assert(memory[memptr] == -1);

            memory[memptr] = cur2;
            memptr++;
        }
    }
    :: else -> skip
    fi
}

proctype worker(int workerId) {
end:
    do
    :: (QUEUE_NOT_FULL) -> enqueue(workerId);
    :: (QUEUE_NOT_EMPTY) -> dequeue(workerId);
    od
}

ltl valid_first_node { []( running -> ((nodes[HEAD].nextptr != INVALID_PTR) && (nodes[HEAD].nextptr < NUM_NODES)) ); }
ltl not_always_empty { [](running -> (QUEUE_IS_EMPTY -> <>QUEUE_NOT_EMPTY)); };
ltl not_always_full { [](running -> (QUEUE_IS_FULL -> <>QUEUE_NOT_FULL)); };
ltl size_change_by_1 { [](running -> (
                            (queue_size == 0 U queue_size == 1) ||
                            (queue_size == 1 U (queue_size == 0 || queue_size == 2)) ||
                            (queue_size == 2 U (queue_size == 1 || queue_size == 3)) ||
                            (queue_size == 3 U queue_size == 2))) }
```

## 讨论

### 混合编程的可能性

我们是否可以通过 Promela 与 C/C++ 的混合编程来解决模型中的一些困难？这种方法或许能提供更加灵活的解决方案，但代价又是什么呢？

### LTL语句的合理性

在多线程环境下验证数据结构的正确性始终是一项艰巨的任务。对于代码中使用的LTL语句，是否需要继续完善以保证其在更多（甚至所有）场景下的正确性?

### 对于其他实现的验证

在[《实现一个无锁消息队列》][1]一文中，涉及了更多的多线程队列模型，后续会对其进行验证。


<div class="alert alert-info" role="alert">本文大（划掉）部分内容由ChatGPT4生成</div>

[1]: /implement-non-blocking-queue.html
[2]: /simple-cas-model-in-spin-promela.html
