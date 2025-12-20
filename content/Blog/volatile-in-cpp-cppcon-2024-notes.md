Title: C++ 的 `volatile`：它到底管啥、不管啥
Date: 2025-10-01 09:00
Tags: C++, volatile, 编译器优化, 并发, 内存模型, CppCon2024
Slug: volatile-in-cpp-cppcon-2024-notes

> CppCon 2024 — What Volatile Means (and Doesn’t Mean), Ben Saks 
> ([video][1], [slides][2])

---

CppCon 2024 上，Ben Saks 做了一场题为 *What Volatile Means (and Doesn’t Mean)* 的演讲，专门澄清 C++ 中 volatile 的真实语义，以及它被长期误用的原因。

volatile 的设计目标其实非常单一：**阻止编译器进行某些会破坏程序语义的优化**。
但在现实工程中，它要么被滥用（不必要地关掉优化），要么被误信（以为它能解决并发或同步问题），从而导致非常隐蔽、难以复现的 bug。

这篇文章整理了演讲中的核心观点，重点放在三个问题上：

* 为什么 volatile 存在
* 它到底保证了什么、不保证什么
* 在现实工程中，如何正确而克制地使用它

---

## 为什么需要 volatile

volatile 几乎唯一正当、也是最重要的使用场景，是**访问硬件寄存器**。

在嵌入式系统中，设备通常通过内存映射寄存器与 CPU 通信。这些寄存器在语法上看起来像普通内存，但语义完全不同：

写控制寄存器会触发一次硬件动作；
读状态寄存器可能清除或设置硬件标志位；
同一个地址的值，也可能在程序控制之外随时发生变化。

问题在于：**编译器并不知道这些事**。
如果你不告诉它某些访问有副作用，它就会把这些地址当成普通对象，自由地进行优化。

---

## 没有 volatile，编译器会“更高效地做错事”

下面这段代码是一个典型的 UART 发送路径示例，刻意没有使用 volatile：

```cpp
std::uint32_t &USTAT0  = *reinterpret_cast<std::uint32_t *>(0x03FFD008);
std::uint32_t &UTXBUF0 = *reinterpret_cast<std::uint32_t *>(0x03FFD00C);

while ((USTAT0 & TBE) == 0) { }
UTXBUF0 = '\r';
while ((USTAT0 & TBE) == 0) { }
UTXBUF0 = '\n';
```

从人类视角看，这段代码逻辑非常直观：
等待发送缓冲区空闲，然后依次发送 `\r\n`。

但在优化器眼里，情况完全不同：

循环体为空，条件看起来不会变化，busy wait 可能被折叠成一次判断，甚至直接变成死循环；
两次对状态寄存器的检查在语义上没有依赖关系，第二次检查可能被删除；
两次写发送缓冲区相邻，第二次覆盖第一次，于是第一次写被当作“无用代码”删除。

最终代码可能只剩下一次写入，甚至在某些情况下直接卡死。
这不是编译器“太聪明”，而是程序**没有表达真实语义**。

---

## volatile 的真实语义

给这些寄存器加上 volatile，本质上是在向编译器传达两点信息：

第一，这些对象的值可能在程序控制之外发生变化；
第二，对它们的每一次读写都可能有副作用，**不能被省略、合并或随意重排**。

典型写法如下：

```cpp
std::uint32_t volatile &USTAT0 =
    *reinterpret_cast<std::uint32_t *>(0x03FFD008);
std::uint32_t volatile &UTXBUF0 =
    *reinterpret_cast<std::uint32_t *>(0x03FFD00C);
```

有了这个声明，编译器就必须老老实实地：

* 在 busy wait 中反复读取状态寄存器；
* 保证对发送缓冲区的写不会被提前、合并或删除。

需要特别强调的是：
volatile 的约束单位是**对象**，而不是“一段代码”。
编译器仍然可以自由重排对**非 volatile 对象**的访问。

---

## volatile 的声明位置，别修饰错对象

volatile 和 const 一样，都是类型说明符。
它既可以修饰“指向的对象”，也可以修饰“指针本身”。

寄存器访问中，几乎总是需要“所指对象是 volatile”，而不是“指针是 volatile”。

一个简单且不容易出错的经验法则是 **East const / East volatile**：
先写不带修饰的类型，再把 const 或 volatile 放到你想修饰的那个类型或运算符的右边。

例如，“N 个 const 指针，指向 volatile 的 uint32_t”：

```cpp
uint32_t volatile *const x[N];
```

---

## volatile 能做什么，不能做什么

### 顺序保证是有限的

volatile 能保证所有 volatile 访问之间的相对顺序不会被打乱，即使它们是不同的对象。

但它并不能阻止编译器把**非 volatile 的访问**重排到 volatile 之前或之后。

下面这个例子是经典反例：

```cpp
bool volatile buffer_ready;
char buffer[BUF_SIZE];

void buffer_init() {
    for (int i = 0; i < BUF_SIZE; ++i)
        buffer[i] = 0;

    buffer_ready = true;
}
```

编译器完全可以把 `buffer_ready = true` 提前执行，
导致另一个线程看到“准备好了”，但数据实际上还没初始化完。

这也是为什么必须明确一点：
**volatile 不是线程同步工具**。
线程通信应使用 mutex、condition variable、原子类型或内存栅栏。

---

### volatile 不提供原子性

volatile 只影响优化行为，不提供任何原子性保证。

对 volatile 对象的自增、复合赋值或普通写入，通常都会被拆成多条机器指令。在并发环境中，这可能导致数据竞争，甚至读到“撕裂”的中间值。

因此：

* 需要原子操作，使用 `std::atomic<T>`
* 需要建立顺序关系，使用同步原语或内存栅栏
* 访问硬件寄存器，使用 volatile，但不要指望它解决并发问题

---

### const volatile 的组合很常见

对于“硬件会变，但软件只读”的状态寄存器，可以使用 const volatile：

```cpp
std::uint32_t const volatile &USTAT0 =
    *reinterpret_cast<std::uint32_t *>(0x03FFD008);
```

这样既防止误写，又明确告诉编译器该值可能随时变化。

---

## 当编译器把 volatile 搞砸时

现实并不完美。Eide 和 Regehr 在 EMSOFT 2008 的研究中发现，多款主流编译器在某些情况下都曾错误优化 volatile，而且新版本未必更少。

工程上常见的应对方式有三种：

第一，局部关闭优化，只在问题函数中降级优化级别；
第二，更换编译器或版本；
第三，用**非内联函数包裹 volatile 读写**。

实践表明，第三种方法在多数工具链上都非常有效。

```cpp
int vol_read_int(int volatile &v) { return v; }
int volatile &vol_id_int(int volatile &v) { return v; }
```

关键点在于：**这些函数必须是非内联的**。
函数调用本身会形成一个优化边界，迫使编译器保守处理副作用，从而避免错误合并、删除或重排访问。

---

## 实用清单

* 访问硬件寄存器：使用 volatile，只读寄存器使用 const volatile
* 声明时注意修饰对象，不要把指针和所指对象写反
* 不要用 volatile 做线程通信
* volatile 不等于原子性
* 遇到工具链问题时，考虑局部关优化、换版本或非内联包裹

---

## 总结

volatile 的核心价值只有一个：
**告诉编译器，这里的读写可能有副作用，不能被省略、合并或重排。**

它不会解决线程可见性、顺序或原子性问题。
在硬件寄存器访问中，它不可或缺；在并发编程中，它几乎从不适合。

一旦越界使用，问题往往不会立刻爆炸，而是以最难调试的方式潜伏下来。
 
<div class="alert alert-warning" role="alert">
  ⚠️ 本文根据视频字幕和 slides 由 AI 生成
</div>

[1]: https://www.youtube.com/watch?v=GeblxEQIPFM&list=PLHTh1InhhwT6U7t1yP2K8AtTEKmcM3XU_&index=2&t=2s
[2]: https://github.com/CppCon/CppCon2024/blob/main/Presentations/What_Volatile_Means_(and_Doesn't_Mean).pdf
