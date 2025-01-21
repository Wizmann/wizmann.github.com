Date: 2025-1-21
Title: 动手实现智能指针 （上篇） - C++ for the Antiquated（之四）
Tags: cpp, modern cpp
Slug: std-smart-ptrs-cpp-for-the-antiquated-4

智能指针（如 `std::shared_ptr` 和 `std::weak_ptr`）已经成为现代 C++ 编程的重要工具，尽管它们并不算是“新兴”的特性。在 C++11 标准之前，Boost 库就已经引入了智能指针的实现，特别是 `boost::shared_ptr` 和 `boost::weak_ptr`，它们为 C++11 的智能指针特性奠定了基础。因此，可以说智能指针在 C++ 中的发展历程已经有很长时间，而它们的引入极大地简化了内存管理和避免了常见的内存泄漏和悬挂指针问题。

本文（上下两篇）将探讨以下几个主题：

* C++ 中智能指针的实现原理
* 非侵入式智能指针与侵入式智能指针的区别
* 如何实现一个侵入式智能指针版本的`shared_ptr` 和 `weak_ptr`
* 讨论完美转发（`std::forward<T>`）在智能指针中的应用

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

### `std::weak_ptr`的实现

`std::weak_ptr` 是与 `std::shared_ptr` 配合使用的智能指针，它解决了 `shared_ptr` 在某些场景下的循环引用问题。

循环引用问题发生在两个或多个对象通过 `shared_ptr` 相互引用时，导致引用计数永远不为零，从而引发内存泄漏。为了避免这个问题，我们引入了 `weak_ptr`。

#### 为什么需要 `weak_ptr`

`std::weak_ptr` 不增加引用计数，因此它不会影响对象的生命周期。当一个对象的所有 `shared_ptr` 被销毁后，`weak_ptr` 将变为“悬挂”状态。这与普通指针的“空悬指针”（dangling pointer）不同，空悬的 `weak_ptr` 会返回空指针 `nullptr`，表明该对象的生命周期已经结束。

`weak_ptr` 提供了一种访问 `shared_ptr` 的方式，但并不控制对象的销毁，因此它可以有效避免循环引用问题。

通过 `weak_ptr`，我们可以在不延长对象生命周期的前提下，检查对象是否仍然存在，并访问它。具体来说，`weak_ptr` 可以通过调用 `lock()` 方法来创建一个 `shared_ptr`，如果对象还存在（即引用计数大于零），则返回一个有效的 `shared_ptr`，否则返回空指针。
```

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
        if (--weak_count == 0) {
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

## 总结

智能指针作为 C++ 中的重要资源管理工具，在避免内存泄漏和简化资源管理方面发挥着关键作用。根据实现方式的不同，智能指针可分为两大类：**非侵入式智能指针**（Non-intrusive Smart Pointers）和**侵入式智能指针**（Intrusive Smart Pointers）。这两类智能指针在内存管理、性能优化、设计复杂度等方面有着各自的优势和适用场景。

非侵入式智能指针通常不要求管理对象本身进行改动，更易于使用和维护，但可能在性能上存在一定开销。相较之下，侵入式智能指针通过在对象中嵌入额外的管理数据（如引用计数）来优化性能，适用于性能要求较高的场景，但需要对对象结构进行修改，使用上相对更复杂。

在下篇的文章中，我们将深入探讨侵入式智能指针的设计与实现，并对比这两类智能指针的优缺点，帮助读者更好地理解它们的使用场景及选择依据。
