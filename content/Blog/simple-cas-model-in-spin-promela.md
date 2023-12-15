Date: 2023-12-15
Title: 在SPIN/Promela中模拟CAS（Compare-and-Swap）
Tags: SPIN, Promela, SPIN/Promela, CAS, Compare-ans-Swap, 多线程
Slug: simple-cas-model-in-spin-promela


CAS（Compare-And-Swap）是一种在多线程编程中常用的数据同步方法，它通过比较和交换操作来保证数据的一致性。然而，在SPIN/Promela中没有直接的CAS对应实现。

让我们来看一个例子。考虑以下Promela代码，它模拟了两个工作线程 worker0 和 worker1 使用CAS机制交替修改共享变量 x 的场景：

```promela
int x = 0;
bool running = false;

proctype worker0() {
end:
    do
    :: (true) -> {
        atomic {
            if
            :: (x == 0) -> { x = 1; }
            :: else -> skip;
            fi
        }
    }
    od
}

proctype worker1() {
end:
    do
    :: (true) -> {
        atomic {
            if
            :: (x == 1) -> { x = 0; }
            :: else -> skip;
            fi
        }
    }
    od
}

init {
    atomic {
      run worker0()
      run worker1();
    }
    running = true;
}

ltl not_always_0 { [](running -> <>(x == 1)); };
```


从直观上理解，LTL表达式 not_always_0 应该被满足，因为 worker0 和 worker1 应该会交替执行，从而在未来的某个时刻使 x == 1 成立。

然而，在SPIN的实际运行中，我们可能会遇到一个问题：如果 worker0 在任何点停止执行，worker1 就会陷入死循环，这种情况被称为“饥饿”（starvation）。

为了解决这一问题，我们可以在SPIN中使用 -f 选项来保证弱公平性（weak fairness）。弱公平性意味着，如果一个可执行的动作在无限长的执行序列中有无限次的执行机会，那么它最终必须得到执行。这确保了即使一个动作暂时无法执行，它最终也会有机会执行。

在这个模型中，应用弱公平性可以确保 worker0 和 worker1 最终都有机会交替执行。这使得模型能够模拟现实的多线程CPU执行场景，从而验证了LTL属性 not_always_0 的正确性。

* 详细命令
```bash
spin -a simple-cas.pml
./pan -m10000 -a -f
```

* 参考链接
  * [Concise Promela Reference > Executing a Promela system](https://spinroot.com/spin/Man/Quick.html)

<div class="alert alert-info" role="alert">本文大（划掉）部分内容由ChatGPT4生成</div>
