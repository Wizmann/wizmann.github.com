Title: 理解 C++ 同步原语的死锁风险
Date: 2025-06-22 10:00
Modified: 2025-06-22 10:00
Tags: C++, 并发编程, 死锁, 多线程, mutex, condition_variable, semaphore
Slug: cpp-sync-deadlock-risks


并发编程中最容易出错的地方之一，是对同步原语的误用，特别是死锁问题。使用 `std::mutex`、`std::condition_variable` 和 `std::semaphore` 等机制时，一些表面上看似合理的代码，可能在某些边界条件下导致程序卡死，且难以调试。

本文将列举一些典型易错模式，并提供对应的改进建议。

## std::mutex 的常见误用模式

### 1.1 多个 mutex 锁顺序不一致导致死锁
```cpp
// Thread A
std::lock_guard<std::mutex> lock1(mutex1);
std::lock_guard<std::mutex> lock2(mutex2);
// Thread B
std::lock_guard<std::mutex> lock2(mutex2);
std::lock_guard<std::mutex> lock1(mutex1); // ❌ 死锁风险
```
**问题分析**：两个线程以不同的顺序加锁，可能互相等待对方释放资源，造成死锁。
**建议**：
* 统一加锁顺序（如按锁的内存地址排序）
* 使用 `std::scoped_lock` 一次性加多个锁（C++17 起）：
```cpp
std::scoped_lock lock(mutex1, mutex2);
```

### 1.2 在持锁状态下调用外部函数
```cpp
std::lock_guard<std::mutex> lock(mutex);
some_external_function();  // ❌ 如果该函数内部也尝试加锁，可能死锁
```
**建议**：避免在持锁状态下调用外部函数。必要时应将调用逻辑移至锁作用域之外。

### 1.3 锁中递归调用自身或间接调用自己
```cpp
std::mutex m;
void foo() {
    std::lock_guard<std::mutex> lock(m);
    bar();
}
void bar() {
    foo();  // ❌ 间接递归调用，重复加锁，死锁
}
```
**建议**：
* 避免递归持有 `std::mutex`。
* 若必须递归使用，应改用 `std::recursive_mutex`，但应慎用。

### 1.4 使用裸指针或悬空 mutex 对象
```cpp
std::mutex* m = get_mutex();
std::lock_guard<std::mutex> lock(*m);  // ❌ 如果 m 已析构，行为未定义

```
**问题分析**：多个线程共享裸 mutex 指针，生命周期不可控，易造成悬空引用或崩溃。
**建议**：
* 使用智能指针管理 mutex 生命周期。
* 或将 mutex 作为静态变量或类成员持有。

### 1.5 手动加锁，异常或提前 return 导致未解锁
```cpp
m.lock();
if (error)
    return;  // ❌ 忘记解锁，死锁风险
m.unlock();
```
**建议**：始终使用 RAII 风格的 `std::lock_guard` 或 `std::unique_lock`，避免忘记解锁：
```cpp
std::lock_guard<std::mutex> lock(m);
if (error)
    return;  // ✅ 安全
```

## std::recursive_mutex 的误用风险
虽然 `std::recursive_mutex` 允许同一线程多次加锁，但它**不是死锁的万灵药**，常常掩盖设计缺陷或状态混乱。
### 示例问题：资源未及时释放
```cpp
std::recursive_mutex m;
void foo() {
    std::lock_guard<std::recursive_mutex> lock(m);
    // 很长的逻辑，期间可能递归调用自身
}
```
**问题分析**：虽然不会死锁，但锁持有时间可能过长，降低系统并发性。
**建议**：
* 优先重构逻辑，避免递归加锁。
* 仅在确实需要递归的少数场景使用。

## std::condition_variable 的常见陷阱

### 3.1 忘记使用谓词检查条件
```cpp
cv.wait(lock);  // ❌ 如果通知早于 wait，线程会永久阻塞
```
**建议**：始终使用谓词版本：
```cpp
cv.wait(lock, [] { return condition; });
```
**理由**：防止虚假唤醒和时序问题。

### 3.2 误用 `notify_one()` 与 `notify_all()`

```cpp
cv.notify_one();  // ❌ 多线程等待时，可能遗漏唤醒
```
**建议**：
* 多线程等待时，优先使用 `notify_all()`。
* 确保 notify 发生时 mutex 已持有，避免竞态。

### 3.3 wait 前未持有锁

```cpp
cv.wait(lock);  // ❌ lock 未加锁，行为未定义
```
**建议**：必须先通过 `std::unique_lock<std::mutex>` 加锁，确保 `wait()` 调用合法：
```cpp
std::unique_lock<std::mutex> lock(m);
cv.wait(lock, [] { return condition; });
```

## std::semaphore 的使用误区（C++20 起）

### 4.1 忘记配对 `release()`
```cpp
std::binary_semaphore sem(0);
sem.acquire();  // ❌ 若未调用 release，线程将永久阻塞
```

**建议**：
* 保证每次 `acquire()` 有对应的 `release()`。
* 使用带超时版本避免无限阻塞：
```cpp
if (!sem.try_acquire_for(std::chrono::seconds(2))) {
    // 超时处理逻辑
}
```

### 4.2 信号丢失：acquire 在 release 之后调用

```cpp
std::binary_semaphore sem(0);

void notify() {
    sem.release();  // ✅ 提前释放
}

void wait() {
    std::this_thread::sleep_for(std::chrono::milliseconds(10));  // ❌ 晚于 release 执行
    sem.acquire();  // ❌ 永久阻塞风险
}
```

**问题分析**：

* `std::binary_semaphore` 类似一个布尔标志，仅记录是否被释放过一次。
* 如果 `release()` 先于 `acquire()` 调用，且调用之间没有明确同步关系，信号可能“被丢失”。
* 由于 `binary_semaphore` 不累加信号（只能表示 0 或 1），先发生的 `release()` 在没有等待者时不会保存“通知”。
* 此问题在“先通知、后等待”场景中尤为常见，与 `condition_variable` 的使用误区类似。

**建议**：

* 保证 `acquire()` 的调用时机在 `release()` 之前或两者明确同步。
* 如需支持先通知后等待，改用 `std::counting_semaphore`，它支持信号积累。
* 或使用超时接口避免无限阻塞：

```cpp
if (!sem.try_acquire_for(std::chrono::seconds(2))) {
    // 超时处理逻辑
}
```

### 4.3 多线程共享时释放不足
```cpp
std::binary_semaphore sem(0);
void worker() {
    sem.acquire();
    // 做一些工作
}
void notify() {
    sem.release();  // ❌ 仅释放一次，其余线程会永久等待
}
```
**建议**：
* 对 N 个等待线程，应调用 N 次 `release()`。
* 或使用 `counting_semaphore` 表示资源总量。

## 5. 总结建议
* 所有锁的使用都应**结构化管理**，优先使用 RAII（如 `std::lock_guard`）。
* 加锁逻辑应**保持一致性**，避免递归加锁、交叉持锁、或生命周期不一致。
* 条件变量使用时应始终搭配**谓词检查**，避免时序或虚假唤醒问题。
* 对 `semaphore` 等底层原语，应设置**超时保护**，防止意外永久阻塞。
* 尽量避免裸指针、手动 lock/unlock 以及难以维护的状态共享逻辑。
