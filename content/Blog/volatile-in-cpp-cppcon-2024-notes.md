Title: C++ 的 `volatile`：它到底管啥、不管啥 @ （Ben Saks @ CppCon 2024）
Date: 2025-10-01 09:00
Tags: C++, volatile, 编译器优化, 并发, 内存模型, CppCon2024
Slug: volatile-in-cpp-cppcon-2024-notes

> CppCon 2024 — What Volatile Means (and Doesn’t Mean), Ben Saks 
> ([video][1], [slides][2])

<div class="alert alert-warning" role="alert">
  ⚠️ 本文根据视频字幕和 slides 由 AI 生成
</div>

---

## 0. 背景与提纲

* `volatile` 的使命：**阻止编译器做会伤害程序语义的某些优化**。很多 C++ 程序员并不清楚它到底提供哪些保护、又**不**提供哪些保护，从而误用：要么不必要地关掉了优化，要么以为得到了保护但其实没有，导致隐蔽的运行时缺陷。
* 本次内容覆盖：

1. 为什么需要 `volatile`；
2. 声明里 `volatile` 的正确放置方法；
3. 它能/不能提供的保护；
4. 编译器把 `volatile` 搞砸时的几种work around

---

## 1. 为什么需要 `volatile`：从 UART 驱动说起

### 1.1 设备寄存器与内存映射

* 设备驱动通过**设备寄存器**与硬件通信；寄存器可能用于：控制（control）、状态（status）、发送（transmit）、接收（receive）、波特率等（以 ARM E7T UART 为例）。
* 内存映射寄存器**看起来**像普通内存地址，但**读/写都可能有副作用**：写控制寄存器启动一次操作；读接收寄存器可能设置/清除状态位。优化器若改变访问次数，就可能改变副作用，导致驱动失效。

### 1.2 UART 发送路径与 TBE 语义

* `USTAT.TBE`（Transmit Buffer Empty）为 1 时，`UTXBUF` 可写。写入 `UTXBUF` 会触发发送并清零 `TBE`，发送完成后硬件再把 `TBE` 置 1。

---

## 2. 没有 `volatile` 会怎样：编译器会更高效的做错事

下面这段**故意不加 `volatile`** 的示例很“像对的”，但在优化器眼里全错了：

```cpp
std::uint32_t &USTAT0 = *reinterpret_cast<std::uint32_t *>(0x03FFD008);
std::uint32_t &UTXBUF0 = *reinterpret_cast<std::uint32_t *>(0x03FFD00C);

while ((USTAT0 & TBE) == 0) { }   // 忙等
UTXBUF0 = '\r';
while ((USTAT0 & TBE) == 0) { }   // 再等
UTXBUF0 = '\n';
```

优化器的推理链条（逐步“合理化”但错误的转化）：

1. `USTAT0` 看起来是普通对象，循环体为空，条件“从未变化”，把 busy loop 变成只判断一次、然后**直接进死循环**或**跳过循环**。
2. 第二个 `if`（或第二个 `while`）与第一个条件等价，且“无副作用相关性”，因此**删除第二个条件检查**。
3. 两次对 `UTXBUF0` 的写入相邻，第二次覆盖第一次，第一条**可删除**。最终只剩：

```cpp
if ((USTAT0 & TBE) == 0) { for(;;){} }
UTXBUF0 = '\n';
```

——更高效地**做错事**。

> 关闭整个区域的优化是一个粗暴但“可行”的办法，不过会错失许多有益优化；`volatile` 提供更**精确**的解决方案。

---

## 3. 加上 `volatile`：告诉编译器“别动我”

把寄存器声明成**指向 `volatile` 的引用**：

```cpp
std::uint32_t volatile &USTAT0 = *reinterpret_cast<std::uint32_t *>(0x03FFD008);
std::uint32_t volatile &UTXBUF0 = *reinterpret_cast<std::uint32_t *>(0x03FFD00C);
```

* 语义（概念层面）：对象会“自己变”，即便程序没有显式改它。
* 语义（机械层面）：**每一次对 `volatile` 对象的读/写都可能有副作用**，编译器**不能省略**，也**不能重排**不同 `volatile` 对象间的访问顺序。

因此：

```cpp
while ((USTAT0 & TBE) == 0) { }  // 必须真的反复读
UTXBUF0 = '\r';                  // 不得被搬到循环上方
```

这两者之间没有显式联系（只是两个地址），但**仅凭“都声明成 `volatile`”**，编译器就必须假定两者副作用相关而**保持顺序**。

**但要注意**：`volatile` 的保护是**以“对象”为单位**，不是“代码区域”。编译器仍然可以把**对非 `volatile` 对象的访问**与 `volatile` 访问**重排**（见 §5.1）。

---

## 4. 声明里 `volatile` 的摆放：别把“指针自己 volatile”搞成“指向的东西 volatile”

### 4.1 声明结构与关键术语

* 每个声明有两部分：**声明说明符**（type / non-type）+ **声明器**（名字与 `* & [] ()` 等）。
* `volatile` 和 `const` 都是**类型说明符**，与 `unsigned`、`long` 类似；`static` / `extern` 等是**非类型说明符**。**顺序对编译器不重要**：`unsigned long` 与 `long unsigned` 等价。

### 4.2 `volatile` 同时可出现在“类型说明符”与“声明器”里

* `volatile int *v[N]` 与 `int volatile *v[N]` ——**指向 `volatile int` 的指针**数组。
* `int *volatile v[N]` ——**`volatile` 指针**数组，指向**非 volatile** 的 `int`。这在寄存器场景**很少**需要。

### 4.3 牢记一个简单准则：**East const / East volatile**

> 先写不带 `cv` 的版本，再把 `const/volatile` 放到你想修饰的**类型或运算符的右侧**。

例子：把 `x` 声明为“**N 个 const 指针**，每个指向 **volatile uint32_t**”

```cpp
uint32_t          *      x[N];      // 起步
uint32_t          *const x[N];      // 指针是 const
uint32_t volatile *const x[N];      // 所指对象是 volatile
```

——**`x` 的最终类型**：`uint32_t volatile * const [N]`。

---

## 5. `volatile` 能做什么 & 不能做什么

### 5.1 顺序与重排

* **能**：保持所有 `volatile` 访问的**相对顺序**（即便是不同对象）。
* **不能**：禁止**非 `volatile`** 访问相对 `volatile` 的重排。典型反例（Eide & Regehr 2008 改编）：

```cpp
bool volatile buffer_ready;
char buffer[BUF_SIZE];

void buffer_init() {
  for (int i = 0; i < BUF_SIZE; ++i) buffer[i] = 0;
  buffer_ready = true;             // 可能被重排到循环前！
}
```

编译器可把 `buffer_ready=true` 提前，导致**过早信号**。若把 `buffer` 也声明为 `volatile` 可抑制此类重排，但**代价**是：之后所有对 `buffer` 的使用都失去优化空间。**正确做法**：线程通信请用**同步原语（mutex/semaphore/condvar）**。

小结：`volatile` **不是**多线程通信工具。标准库/线程库里的同步原语里已经“自带内存栅栏”，可表达所需的可见性与顺序。字幕 Q&A 也特别提到：低层可用**内存屏障**/“同步点”，但大多数应用用高层原语更可靠。

### 5.2 不保证原子性

* **`volatile` 只防“错误优化”，不提供原子性或同步。**
  对 `volatile` 对象的 `++`、`--`、`+=` 等操作在机器层面通常会被拆成“读 → 改 → 写”多步序列，因此**不是不可分割的**。在类型本身**不天然原子**的平台上（例如某些平台的 `double`），并发线程可能观察到**撕裂（torn）**的中间值。

```cpp
double volatile v = 0.0;  // 某些平台上 double 非原子
// 线程 A
v = 8.67;
v = 53.09;   // B 可能在此两步之间读到“半写入”的值
// 线程 B
auto x = v;  // 可能既不是 8.67 也不是 53.09
```

* **标准演进提醒的是“误用”而非赋予能力。**
  由于这些用法（对 `volatile` 的自增/自减/复合赋值）**极易被误解**，它们在 **C++20 被标记为弃用**；考虑到大量存量代码与现实反馈，**C++23 又（部分）撤销了弃用**。但无论“是否弃用”，这些操作的**本质并未改变**——它们**仍不具备原子性**。

* **正确做法**
  * 需要原子读写/复合操作：使用 `std::atomic<T>` 及合适的内存序。
  * 只需建立内存序屏障：使用 `atomic_thread_fence(...)`。
  * 访问硬件寄存器：继续用 `volatile` 来**防止优化器消掉/重排访问**，但**不要**把它当作并发同步工具。


### 5.3 `const volatile` 的组合

* 实务中很常见：**只读状态寄存器**可以声明为 `const volatile`，以防止误写、又保持“硬件会变”的可见性：

```cpp
std::uint32_t const volatile &USTAT0 = *reinterpret_cast<std::uint32_t*>(0x03FFD008);
```

### 5.4 其它不合适的用途

**Cache 预热不要用 `volatile` 去“强行保留一次读取”**（即防止优化器删除未使用的读）。这会扩大优化屏障、引入不必要的排序/等待，却**不等于**真正的“预取”。

**更合适的做法**：

* 使用平台提供的**预取内建**（如 `_mm_prefetch` 或编译器内建的 `__builtin_prefetch` 等），它们以“提示”的方式把 cache line 提前带入，而不引入实际的数据依赖或强制读。
* 在数据结构层面，结合 C++17 的 `std::hardware_constructive_interference_size` / `std::hardware_destructive_interference_size`，通过**字段分组与填充**减少伪共享、提升命中率。

---

## 6. 当编译器把 `volatile` 搞砸了

Eide & Regehr（EMSOFT’08）随机程序测试：**5 个系列编译器的 13 个版本**，每个都至少在一种情形**错误处理**了 `volatile`；新版本**未必更少 bug**（GCC 4.2.4 比 4.0.4 还多）。在安全关键系统里，这后果很严重。

### 6.1 方案一：局部禁用优化

```cpp
// 方式 A：GCC 函数级属性
void [[gnu::optimize("O0")]] f() { /* ... */ }   // O0=最少优化
// 方式 B：GCC #pragma
#pragma GCC push_options
#pragma GCC optimize("O0")
void g() { /* ... */ }
#pragma GCC pop_options
```

> 注意：不同编译器的 pragma 与属性写法不同，且通常是**函数级**生效。

### 6.2 方案二：换版本/换编译器

同一编译器不同版本的 `volatile` bug 差异显著，且**新**不一定**好**。

### 6.3 方案三：非内联函数“包裹”读/写（经典 workaround）

> Eide & Regehr 的实验显示：把对 `volatile` 的读/写包在**非内联函数**里，能修复他们测到的 **~96%** 的误编译场景（不同编译器与版本）。

**普通读/写：**

```cpp
int volatile v_int;
int x = v_int;       // 读
v_int = 256;         // 写
```

**包裹版（关键在“非内联”）：**

```cpp
int vol_read_int(int volatile &vp) { return vp; }
int volatile &vol_id_int(int volatile &v) { return v; }

int volatile v_int;
int x = vol_read_int(v_int);   // 强化“每次都要真的去读”
vol_id_int(v_int) = 256;       // 强化“这一次写不能合并/删除”
```

**原理**
编译器在优化**非内联**调用时必须非常保守：

* 它**看不穿**函数体的副作用，必须**按源代码精确调用**对应次数，不敢合并/删除/跨调用重排访问；这与我们要求的 “`volatile` 每次访问都要发生、且访问之间保持顺序” 高度一致，起到“**冗余保险**”作用。
* 调用点天然形成**优化边界**，编译器会假设调用可能读写内存或触发外部副作用，从而不把与之相关的访存上提、下沉或合并。

**问题到底可能出在哪里（workaround 要解决的就是这些）**
历史上，部分优化器曾把“对普通内存合法的变换”**误用**到 `volatile` 上，导致：

* **删除/合并访问**（DSE/CSE）：把“前一次写会被后一次覆盖”当真，删掉前一次；或把多次读缓存成一次寄存器值——而对 `volatile`，**每次访问都必须发生**。
* **循环外提**（LICM）：把“看似不变”的 `volatile` 读取搬出循环，导致只读一次；设备寄存器值可能变化，这会出错。
* **错序/跨语句重排**：把 `volatile` 访问与其他访问错误换序，改变硬件交互因果。对不同 `volatile` 对象之间也必须保持顺序。
* **向量化/跨基本块合并**：合并访存或调整时序，违背 “每次都要发生且按序” 的要求。上述问题均在论文与讲稿中有例示或讨论。

**实践注意事项**

* **严禁被“自动内联”偷走护城河**：模板版本或较高优化级别下，编译器可能**自动内联**这些小函数——一旦内联，优化边界消失，等同没加。解决：给函数（含模板实例）显式加 `[[gnu::noinline]]` / 对应编译器的 `noinline` 标记，并留意 LTO/IPO 设置。讲者在 GNU ARM Embedded Toolchain 10.2.1 上就遇到过自动内联，最终用 `[[gnu::noinline]]` 压住。
* **它是工程折中，不是语言保证**：**~96%** 是经验数据，而非标准承诺；若仍遇到工具链缺陷，可配合“局部降优化级（O0）”“更换编译器/版本”等手段联合使用。
* **性能权衡**：非内联调用在热路径/ISR 中有成本。可仅在特定编译器/配置下启用包裹，或将包裹函数放在对正确性至关重要、但调用频率相对适中的路径上。

小结：问题出在优化器把“对普通内存安全的变换”（删除/合并/外提/重排）套在了 `volatile` 上；“非内联函数包裹”利用**调用边界的保守性**，强制保留**每一次**访问并**按原序**执行，从而在实践中大幅降低误编译风险。


### 用于 UART 的实战改造：

```cpp
std::uint32_t vol_read_u32(std::uint32_t volatile &v) { return v; }
std::uint32_t volatile &vol_id_u32(std::uint32_t volatile &v) { return v; }

std::uint32_t volatile &USTAT0 = *reinterpret_cast<std::uint32_t *>(0x03FFD008);
std::uint32_t volatile &UTXBUF0 = *reinterpret_cast<std::uint32_t *>(0x03FFD00C);

while ((vol_read_u32(USTAT0) & TBE) == 0) { }
vol_id_u32(UTXBUF0) = '\r';
```

实测有效；**模板版**易被 -O1 起自动内联，需加 `[[gnu::noinline]]` 抑制（MSVC 可用 `__declspec(noinline)`，Clang/GCC 也支持 `__attribute__((noinline))`）。务必确认**没被内联**。

---

## 7. 实用清单（Checklist）

1. **硬件寄存器**：指向寄存器的对象一律 `volatile`；只读寄存器用 `const volatile`。
2. **East volatile**：把 `volatile` 放在你想修饰的**类型/运算符右边**，别把“指针 volatile”写成“指向对象 volatile”或反过来。
3. **线程通信**：**不要**用 `volatile`；请用 `mutex / semaphore / condvar / std::atomic(*) / fence`。
4. **原子性**：`volatile` ≠ 原子；增量/复合赋值可能数据竞争。
5. **遇到编译器问题**：
   * 局部关优化（属性/pragma）；
   * 换版本/换编译器；
   * **非内联函数包裹**（并确认没被内联）。
6. **缓存预取**: 别靠 `volatile`，用 `_mm_prefetch` 等内建；缓存行布局可参考 C++17 的“硬件构造/破坏性干涉尺寸”常量。
    * `std::hardware_constructive_interference_size`：构造性干涉尺寸。把经常一起访问的数据项放在不超过这个尺寸的距离内，倾向于落在同一 cache line，提升命中（“一起热”）。
    * `std::hardware_destructive_interference_size`：破坏性干涉尺寸。把可能被不同线程同时写的对象间隔至少这么大，尽量不落在同一 cache line，避免伪共享（false sharing，“互相拖累”）。

---

## 8. 关键代码片段汇总

* **错误示例（无 `volatile`）→ 被优化坏**：忙等、两次写入被合并，仅发送 `'\n'`（详见 §2）。
* **正确示例（有 `volatile`）**：

```cpp
std::uint32_t volatile &USTAT0 = *reinterpret_cast<std::uint32_t*>(0x03FFD008);
std::uint32_t volatile &UTXBUF0 = *reinterpret_cast<std::uint32_t*>(0x03FFD00C);
while ((USTAT0 & TBE) == 0) { }
UTXBUF0 = c;
```

* **`const volatile` 状态寄存器**：

```cpp
std::uint32_t const volatile &USTAT0 = *reinterpret_cast<std::uint32_t*>(0x03FFD008);
```

* **East volatile 模板**：

```cpp
uint32_t volatile *const x[N]; // “N 个 const 指针，指向 volatile uint32_t”
```

* **非内联包裹读/写**：

```cpp
//（模板版要 `[[gnu::noinline]]` 或对应编译器的 noinline）
int vol_read_int(int volatile &vp) { return vp; }
int volatile &vol_id_int(int volatile &v) { return v; }
```

* **GCC 局部关优化**：

```cpp
void [[gnu::optimize("O0")]] f() { /* ... */ }

#pragma GCC push_options
#pragma GCC optimize("O0")
void g() { /* ... */ }
#pragma GCC pop_options
```

* **缓存预取**：

```cpp
#include <atomic>
#include <new>

// 把两个热点计数器拆到不同的 cache line，避免伪共享
struct alignas(std::hardware_destructive_interference_size) Counter {
    std::atomic<long> value{0};
};

struct HotPair {
    // 把经常一起读的字段放在“构造性干涉尺寸”内，利于同线命中
    alignas(std::hardware_constructive_interference_size) int a;
    int b;
};

void touch(Counter& c1, Counter& c2, const HotPair* hp) {
    // 平台预取（示例：x86 SSE/AVX），编译器/平台不同可用 __builtin_prefetch
    // _mm_prefetch(reinterpret_cast<const char*>(hp), _MM_HINT_T0);
  
    c1.value.fetch_add(1, std::memory_order_relaxed);
    c2.value.fetch_add(1, std::memory_order_relaxed);
    int t = hp->a + hp->b; (void)t;
}
```

---

## 9. 压轴总结（Takeaways）

* `volatile` 的**唯一核心价值**：告诉编译器“这里的读写可能有副作用，请**别省略、别合并、别重排**这些访问”。它**不会**解决线程可见性/顺序/原子性问题。
* **多线程通信**：请用同步原语/原子库/内存序；`volatile` 不适用。
* **工程上**：若你怀疑编译器把 `volatile` 搞坏了，优先考虑**局部关优化 / 换编译器版本 / 非内联包裹**三种方法，并**确认没被内联**。


[1]: https://www.youtube.com/watch?v=GeblxEQIPFM&list=PLHTh1InhhwT6U7t1yP2K8AtTEKmcM3XU_&index=2&t=2s
[2]: https://github.com/CppCon/CppCon2024/blob/main/Presentations/What_Volatile_Means_(and_Doesn't_Mean).pdf
