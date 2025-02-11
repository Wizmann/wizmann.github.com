Date: 2025-1-21
Title: 动手实现智能指针 （上篇） - C++ for the Antiquated（之四）
Tags: cpp, modern cpp
Slug: std-smart-ptrs-cpp-for-the-antiquated-4

智能指针（如 `std::shared_ptr` 和 `std::weak_ptr`）已经成为现代 C++ 编程的重要工具，尽管它们并不算是“新兴”的特性。在 C++11 标准之前，Boost 库就已经引入了智能指针的实现，特别是 `boost::shared_ptr` 和 `boost::weak_ptr`，它们为 C++11 的智能指针特性奠定了基础。因此，可以说智能指针在 C++ 中的发展历程已经有很长时间，而它们的引入极大地简化了内存管理和避免了常见的内存泄漏和悬挂指针问题。

本文将围绕以下主题展开讨论：

- C++ 智能指针的实现原理  
- 非侵入式智能指针与侵入式智能指针的区别  
- 利用 `atomic` 避免多线程竞态条件
- 如何实现侵入式版本的 `shared_ptr` 和 `weak_ptr`  
- 采用 `concept` 约束模板类型  
- 探讨完美转发（`std::forward<T>`）在智能指针中的应用  

## C++ 中的智能指针

### `std::shared_ptr`的实现

`std::shared_ptr` 是一种智能指针，能够自动管理对象的生命周期。它通过引用计数的方式来跟踪有多少个 `shared_ptr` 实例指向同一个对象，确保当最后一个 `shared_ptr` 被销毁时，对象的内存能够自动释放。

#### 引用计数与原子操作

`std::shared_ptr` 的核心机制是引用计数。每个 `shared_ptr` 会维护一个引用计数。当多个 `shared_ptr` 指向同一个对象时，计数器会增加；当一个 `shared_ptr` 被销毁时，计数器会减少。如果计数器归零，表明没有任何 `shared_ptr` 再指向该对象，这时对象会被删除。

引用计数通常由一个控制块（control block）管理。控制块不仅保存引用计数，还会保存对象本身以及与对象生命周期相关的其他信息。`std::shared_ptr` 的实现一般使用“非侵入式引用计数”（即不嵌入对象本身）。

示例代码如下：

```cpp
template <typename T>
class control_block {
public:
    control_block(T* ptr)
        : ref_count(1), obj(ptr) {}

    // 增加引用计数
    void add_ref() { ++ref_count; }

    // 减少引用计数
    void release_ref() {
        if (--ref_count == 0) {
            delete obj;  // 删除对象
            delete this; // 删除控制块
        }
    }

    T* get() { return obj; }

private:
    std::atomic<int> ref_count;    // 引用计数
    T* obj;                        // 实际对象
};
```

#### 简化版 `shared_ptr` 实现

下面是一个简化版的 `shared_ptr` 实现示例。这个版本仍然有一些重要细节需要注意，比如原子操作和异常安全等问题，但可以帮助理解 `shared_ptr` 的基本原理：

```cpp
template <typename T>
class my_shared_ptr {
private:
    T* ptr;
    control_block<T>* ctrl_block;

public:
    explicit my_shared_ptr(T* p = nullptr) 
        : ptr(p), ctrl_block(new control_block<T>(p)) {}

    // 拷贝构造函数
    my_shared_ptr(const my_shared_ptr& other) 
        : ptr(other.ptr), ctrl_block(other.ctrl_block) {
        if (ctrl_block) {
            ctrl_block->add_ref();
        }
    }

    // 析构函数
    ~my_shared_ptr() {
        if (ctrl_block) {
            ctrl_block->release_ref();
        }
    }

    T* operator->() { return ptr; }
    T& operator*() { return *ptr; }
};
```

### `std::weak_ptr`的实现

`std::weak_ptr` 是与 `std::shared_ptr` 配合使用的智能指针，它解决了 `shared_ptr` 在某些场景下的循环引用问题。

循环引用问题发生在两个或多个对象通过 `shared_ptr` 相互引用时，导致引用计数永远不为零，从而引发内存泄漏。为了避免这个问题，我们引入了 `weak_ptr`。

#### 为什么需要 `weak_ptr`

`std::weak_ptr` 不增加引用计数，因此它不会影响对象的生命周期。当一个对象的所有 `shared_ptr` 被销毁后，`weak_ptr` 将变为“悬挂”状态。这与普通指针的“空悬指针”（dangling pointer）不同，空悬的 `weak_ptr` 会返回空指针 `nullptr`，表明该对象的生命周期已经结束。

`weak_ptr` 提供了一种访问 `shared_ptr` 的方式，但并不控制对象的销毁，因此它可以有效避免循环引用问题。

通过 `weak_ptr`，我们可以在不延长对象生命周期的前提下，检查对象是否仍然存在，并访问它。具体来说，`weak_ptr` 可以通过调用 `lock()` 方法来创建一个 `shared_ptr`，如果对象还存在（即引用计数大于零），则返回一个有效的 `shared_ptr`，否则返回空指针。

#### 控制块的扩展

为了支持`std::weak_ptr`， 我们需要扩展控制块的功能 ，使其能同时管理对象的引用计数（`ref_count`）和弱引用计数（`weak_count`），从而保持对对象的生命周期的正确管理。

```cpp
template <typename T>
class control_block {
public:
    control_block(T* ptr)
        : ref_count(1), weak_count(1), obj(ptr) {}

    // 增加引用计数
    void add_ref() { ++ref_count; }
    
    // 增加引用计数
    bool lock() { 
        int prev = ref_count.load();  // 使用加载当前值，避免重复读取
        while (prev > 0 && !ref_count.compare_exchange_weak(prev, prev + 1)) {
            prev = ref_count.load();   // 如果失败，重新加载当前值
        }
        return prev > 0;  // 如果 prev > 0，表示锁定成功
    }

    // 减少引用计数
    void release_ref() {
        if (--ref_count == 0) {
            delete obj;  // 删除对象
            release_control_block(); // 尝试删除控制块
        }
    }

    // 增加弱引用计数
    void add_weak_ref() { ++weak_count; }

    // 减少弱引用计数
    void release_weak_ref() {
        if (weak_count.fetch_sub(1) == 1) {
            delete this; // 删除控制块
        }
    }

    T* get() { return obj; }

private:
    // 删除控制块，只有在弱引用计数为0时才删除控制块
    void release_control_block() {
        if (weak_count == 0) {
            delete this; // 删除控制块
        }
    }

    std::atomic<int> ref_count;    // 强引用计数
    std::atomic<int> weak_count;   // 弱引用计数
    T* obj;                        // 实际对象
};
```

#### `weak_ptr` 的简化版实现

下面是一个简化版的 `weak_ptr` 实现，它与 `shared_ptr` 共享相同的控制块。`weak_ptr` 本身不增加引用计数，因此不会影响对象的生命周期。

```cpp
template <typename T>
class my_weak_ptr {
public:
    my_weak_ptr() : ctrl_block(nullptr) {}

    // 从 shared_ptr 构造 my_weak_ptr
    my_weak_ptr(const std::shared_ptr<T>& shared)
        : ctrl_block(shared.ctrl_block) {
        ctrl_block->add_weak_ref();
    }

    ~my_weak_ptr() {
        if (ctrl_block) {
            ctrl_block->release_weak_ref();
        }
    }

    // 尝试获取指向对象的 shared_ptr
    std::shared_ptr<T> lock() {
        return std::shared_ptr<T>(*this);
    }

private:
    control_block<T>* ctrl_block; // 控制块
};

template <typename T>
class my_shared_ptr {
private:
    T* ptr;
    control_block<T>* ctrl_block;
public:
    // ...
    my_shared_ptr(const my_weak_ptr<T>& weak_ptr) {
        if (weak_ptr.ctrl_block && weak_ptr.ctrl_block->lock()) {
            ptr = weak_ptr.ptr;
            ctrl_block = weak_ptr.ctrl_block();
        } else {
            throw exception("bad weak ptr");
        }
    }
    // ...
};
```

## 理解并优化`std::atomic<T>`操作

在上面的代码示例中，我们使用了`std::atomic<int>`作为智能指针的引用计数。与直接使用`int`变量不同，`std::atomic<int>`可以在多线程环境中正确地管理对同一智能指针的引用计数。

然而，在上述代码中，我们仅使用了`std::atomic<int>`的基本操作（如自增、自减和赋值等），这些操作默认使用`memory_order_seq_cst`内存序（稍后会讨论）。在多线程编程中，`std::atomic<T>`提供了多种内存序（memory ordering）选项，用以控制操作的可见性和执行顺序，以确保数据一致性。不同的内存序策略决定了编译器和CPU对指令的重排序程度。

开发者的目标是选择合适的内存序，优化程序性能，同时确保程序的正确性。

### 内存序的核心概念

理解内存序的关键在于**重排序**和**跨线程可见性**：

1. **重排序（Reordering）**  
   编译器和CPU可能会重排指令，以优化性能。例如，它们可能会提前执行某些计算，或者将存储操作推迟执行。正确使用`std::atomic`可以防止某些关键操作被错误地重排序。

2. **可见性（Visibility）**  
   在多线程环境中，一个线程对变量的修改可能不会立即被其他线程看到，或者多个线程对同一变量的操作顺序可能不确定。原子操作的内存序决定了其他线程何时能看到这些修改。

### 不同内存序的作用及使用场景

#### `memory_order_relaxed`（松散顺序，最低开销）

- **特点**：不保证顺序，仅保证操作是**原子的**。
- **作用**：确保同一`std::atomic<T>`变量的读写操作是原子的，但不提供线程间的同步，不影响可见性或顺序。
- **适用场景**：适用于**数据竞争不影响程序正确性**的场景，如**无依赖的计数**（统计线程数、事件计数等）。

**示例**

```cpp
std::atomic<int> counter{0};
counter.fetch_add(1, std::memory_order_relaxed);  // 仅保证原子性，不保证可见性
```

这里，`fetch_add`确保`counter`自增操作不会丢失，但不同线程的修改可能会被延迟看到。

#### `memory_order_acquire`（获取，防止重排序到前）

- **特点**：保证**当前线程**在`acquire`之后的所有操作不会被重排序到`acquire`之前，因此，其他线程中相同原子变量的释放操作（release operation）之前的写入对当前线程是可见的。
- **适用场景**：用于**读取**共享数据，确保当前线程能够看到其他线程之前对该变量的修改。

#### `memory_order_release`（释放，防止重排序到后）

- **特点**：确保**当前线程**在`release`之前的所有操作不会被重排序到`release`之后，因此，当前操作所在线程之前的写入，在其他线程施加占有操作（acquire operation）之后是可见的。
- **适用场景**：用于**写入**共享数据，确保其他线程能在`acquire`读取时看到修改。

**示例**

```cpp
std::atomic<int> flag{0};
int data = 0;

void producer() {
  data = 42;
  flag.store(1, std::memory_order_release);  // 让消费者可以看到 data=42
}

void consumer() {
  while (flag.load(std::memory_order_acquire) != 1);  // 确保 data=42 可见
  std::cout << data << std::endl;  // 确保 data 的修改对本线程可见
}
```

- `store(release)`确保`data=42`发生在`flag=1`之前。
- `load(acquire)`确保`flag=1`之后，`data=42`对消费者线程可见。
- 通过`acquire-release`，消费者线程能够正确看到生产者线程的`data`修改。

#### `memory_order_acq_rel`（获取-释放，双向同步）

- **特点**：结合`acquire`和`release`，用于**读-改-写（Read-Modify-Write, RMW）**操作，确保：
  - 读取时使用`acquire`语义，保证之前的修改对当前线程可见。
  - 写入时使用`release`语义，保证当前修改对后续线程可见。
- **适用场景**：用于**读-改-写**（如`fetch_add()`、`exchange()`）操作，确保多个线程能够正确协调。

**示例**

```cpp
std::atomic<int> value{0};
value.fetch_add(1, std::memory_order_acq_rel);  // 读写都保证可见性
```

在这里，`fetch_add`同时读取旧值并写入新值：
- 读取时使用`acquire`语义，确保它能看到其他线程的修改。
- 写入时使用`release`语义，确保它的修改能被其他线程看到。

#### `memory_order_seq_cst`（顺序一致性，最严格）

- **特点**：所有使用`memory_order_seq_cst`的原子操作在**所有线程看来**都是按照相同的顺序执行的，即全局一致的时序。
- **适用场景**：
  - 需要严格同步的场景，如**锁**、**同步变量**、**临界区保护**等。
  - 适用于**多线程交互复杂**、难以管理依赖关系的情况。

**保证**：
- `seq_cst`确保所有操作严格按照全局统一顺序执行，避免乱序问题。

### 直观比喻

* `relaxed`：随意写笔记，但不保证别人能看到。
* `acquire`：**进门检查公告栏**，确保看到之前的通知。
* `release`：**离开时更新公告栏**，让后来的人看到。
* `acq_rel`：**进门看公告 + 走前更新公告**。
* `seq_cst`：**所有人按同样顺序写、看公告**，保证一致性。

根据不同场景合理选择内存序，可以提高并发程序的正确性和性能。

### 优化控制块中的原子变量

```cpp
#include <atomic>

template <typename T>
class control_block {
public:
    control_block(T* ptr)
        : ref_count(1), weak_count(1), obj(ptr) {}

    // 增加引用计数
    void add_ref() {
        ref_count.fetch_add(1, std::memory_order_relaxed);
    }
    
    // 尝试增加强引用计数（仅当对象仍然存活时）
    bool lock() { 
        int prev = ref_count.load(std::memory_order_acquire);
        while (prev > 0) {
            if (ref_count.compare_exchange_weak(prev, prev + 1, 
                std::memory_order_acquire, std::memory_order_relaxed)) {
                return true; // 成功锁定
            }
        }
        return false; // 对象已被释放
    }

    // 释放强引用
    void release_ref() {
        if (ref_count.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            delete obj;  // 删除对象
            release_control_block(); // 尝试删除控制块
        }
    }

    // 增加弱引用计数
    void add_weak_ref() {
        weak_count.fetch_add(1, std::memory_order_relaxed);
    }

    // 释放弱引用计数
    void release_weak_ref() {
        if (weak_count.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            delete this; // 删除控制块
        }
    }

    T* get() { return obj; }

private:
    // 删除控制块，仅当弱引用计数也归零时
    void release_control_block() {
        if (weak_count.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            delete this; // 删除控制块
        }
    }

    std::atomic<int> ref_count;    // 强引用计数
    std::atomic<int> weak_count;   // 弱引用计数
    T* obj;                        // 实际对象
};

```

## 参考

* [C++内存管理：shared_ptr/weak_ptr源码](https://zhuanlan.zhihu.com/p/532215950)
* [当析构函数遇到多线程 ── C++ 中线程安全的对象回调](https://www.cnblogs.com/Solstice/archive/2010/02/10/dtor_meets_threads.html)
* [程序员的自我修养（⑫）：C++ 的内存顺序](https://liam.page/2021/12/11/memory-order-cpp-02/)
