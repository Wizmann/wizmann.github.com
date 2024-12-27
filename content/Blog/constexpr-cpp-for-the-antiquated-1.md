Date: 2024-12-28
Title: constexpr详解 - C++ for the Antiquated（之一）
Tags: cpp, modern cpp
Slug: constexpr-cpp-for-the-antiquated-1

在这篇文章中，我们将深入讨论 C++ 中的常量表达式（`constexpr`）及其与传统的`const`常量的区别，并结合实际代码示例进行说明。同时，我们还会探讨`constexpr`函数在模板编程中的应用，以及 C++11 之后对常量表达式的优化与扩展。


## 常量表达式（constexpr）

在 C++ 中，`const` 关键字通常用于修饰变量、引用和指针，使得它们在运行时不能被修改。需要注意的是，`const` 并没有区分编译期常量和运行时常量，它只是保证了这些变量在运行时不可修改。

例如，使用 `const` 声明的变量在运行时其值是固定的，但并不意味着它们在编译时已知。

下面是传统 C++ 中 `const` 关键字的一些常见用法：

```cpp
#define CONSTANT_1 114514  // 宏也是一种常量
const char* helloworld1 = "helloworld";  // const 字符串
const int value1 = 1;  // 常量值
const int value2 = 2;
const int value3 = value1 + value2;  // 运行时计算
const int value8 = pow(value2, value3); 

const int arr_pow_of_2[] = {1, 2, 4};  // 数组初始化
```

在上述代码中，虽然 const 修饰的变量在程序运行期间不能修改，但它们的值是在运行时计算的。因此，我们无法在编译时将它们视为常量。所以，`const` 变量也可以有内存地址，并且在某些情况下可以使用 `const_cast` 强行进行修改。

```cpp
#include <cstdio>
#include <cstdint>
#include <iostream>
#include <cmath>

void MakeChange(const int& x) {
    *(const_cast<int*>(&x)) = x + 1;
}

int main() {
    int x = 1;
    MakeChange(x);
    std::cout << x << std::endl; // 输出：2
    return 0;
}
```

### 引入 constexpr

C++11 引入了 `constexpr`，它的字面意思是 `constant expression`（常量表达式），用于在编译时计算常量值。与 `const` 不同，`constexpr` 确保一个变量或者函数的值是在编译时已知的，编译器会在编译时对其进行求值。

通过使用 `constexpr`，我们可以定义编译时常量，并且 `constexpr` 函数在某些情况下也能够在编译期计算结果。

使用 `constexpr` 重写上述代码：

```cpp
constexpr const char* helloworld1 = "helloworld";
constexpr int value1 = 1;
constexpr int value2 = 2;
constexpr int value3 = value1 + value2;  // 编译期计算
constexpr int value8 = pow(value2, value3);  // 编译期计算

// 编译期初始化数组
constexpr const int arr_pow_of_2[] = {1, 2, 4};  
```

## 常量表达式函数

`constexpr` 不仅可以修饰变量，还可以修饰函数。`constexpr` 函数的特性是，若输入的参数是编译时常量，那么它的返回值也是一个编译时常量。

以下是一个计算 Fibonacci 数列的示例：

```cpp
constexpr uint64_t MOD = (1LL << 62) - 1;  // 编译时常量

constexpr uint64_t fib(uint64_t n) {
    uint64_t a = 0, b = 1;
    for (int i = 0; i < n; ++i) {
        uint64_t temp = a + b;
        a = b;
        b = temp % MOD;
    }
    return b;
}

int main() {
    // 在编译期计算 Fibonacci 数列
    constexpr uint64_t result = fib(123456);  
    std::cout << result << std::endl;
    return 0;
}
```

在这段代码中，`fib` 函数被标记为 `constexpr`，因此当传入常量参数时，编译器会在编译期间计算出 Fibonacci 数列的第 `123456` 项。需要注意的是，`constexpr` 函数的计算存在一些限制：

1. **递归深度限制**：constexpr 函数的递归深度通常受到编译器的限制，如果递归过深，编译器可能会产生错误或警告。
2. **计算效率**：尽管常量表达式函数可以在编译期计算，但对于复杂的运算，可能会增加编译时间，因为编译器需要进行更多的计算。

### constexpr vs 模板元编程

`constexpr` 函数的使用在某种程度上简化了模板元编程。传统的模板元编程可以实现与 `constexpr` 类似的功能，但代码结构通常更加复杂。下面是使用模板元编程计算 Fibonacci 数列的代码：

```cpp
const uint64_t MOD = 1999;

template <uint64_t N>
struct Fibonacci {
    static const uint64_t value = (Fibonacci<N - 1>::value + Fibonacci<N - 2>::value) % MOD;
};

template <> struct Fibonacci<0> { static const uint64_t value = 0; };
template <> struct Fibonacci<1> { static const uint64_t value = 1; };

int main() {
    std::cout << "Fibonacci(40): " << Fibonacci<40>::value << std::endl;
    return 0;
}
```

在这个模板元编程示例中，Fibonacci 结构体使用递归模板计算 Fibonacci 数列的第 N 项。这与 `constexpr` 函数类似，但模板元编程的语法更加繁琐。`constexpr` 的优势在于它能够写出更加接近正常逻辑代码的形式，并且具有更强的表达能力

### C++14 对常量表达式函数的增强

在 C++14 中，常量表达式函数得到了进一步的增强。具体增强包括：

* **支持局部变量**：`constexpr`  函数可以声明和初始化局部变量，但不能声明未初始化的变量、`static` 或 `thread_local` 变量。
* **支持 if 和 switch 语句**：`constexpr` 函数可以使用 `if` 和 `switch` 语句来控制流程，但不能使用 `got`o。
* **支持循环语句**：`constexpr` 函数支持所有类型的循环语句，包括 `for`、`while` 和 `do-while`。
* **修改生命周期**：在 constexpr 函数内部，可以修改局部变量和非常量引用参数
* **返回值可以是 void**：`constexpr` 函数可以声明返回类型为 `void`。

## 常量表达式与模板函数

在 C++11 引入 `constexpr` 后，建议在所有需要常量语义的场景中使用 `constexpr`。`constexpr` 变量和函数作为编译时常量，在模板函数中具有广泛的应用场景，能够显著提升程序的效率和可读性。

```cpp
#include <cstdio>
#include <cstdint>

template <typename T>
constexpr T square(T x) {
    return x * x;
}

int main() {
    constexpr uint64_t square2 = square(2);       // 计算常量的平方
    constexpr double square2_0 = square(2.0);     // 计算浮点数的平方
    printf("%lu\t%.04lf\n", square2, square2_0);  // 输出结果
    return 0;
}
```

模板函数 `square` 使用了 `constexpr`，确保在编译时就可以计算结果。对于不同类型的参数（如整数、浮点数），模板会自动进行实例化。

如果模板参数不是编译期常量，`constexpr` 将不会在编译期执行，但函数本身仍然是有效的。

## constexpr 函数中的动态内存分配

在 C++20 中，`constexpr` 函数得到了进一步增强，支持在编译期进行动态内存分配，但仍然存在一些限制。

 `std::array` 的所有数据都存储在栈上，而不是堆上。严格的说，`std::array`不涉及动态内存分配。所以`std::array`可以在`constexpr`函数中被初始化、修改并返回。

```cpp
#include <cstdio>
#include <cstdint>
#include <vector>
#include <array>

template <int maxstep=100>
constexpr std::array<int, maxstep> Collatz(int x) {
    std::array<int, maxstep> path;
    int idx = 0;
    while (true) {
        path[idx++] = x;
        if (x == 1) {
            break;
        }
        if (x % 2 == 0) {
            x /= 2;
        } else if (x % 2 == 1) {
            x = x * 3 + 1;
        }
    }
    return path;
}


int main() {
    constexpr auto path = Collatz(12345);
    for (auto item : path) {
        if (item == 0) {
            break;
        }
        printf("%d\n", item);
    }
    return 0;
}
```

而对于`std::string`或者`std::vector`这种 需要在堆上分配内存的数据结构，我们则不可以在constexpr函数中直接返回。但是可以在constexpr函数中则用其进行计算。

```cpp
#include <cstdio>
#include <cstdint>
#include <vector>
#include <array>
#include <string>

constexpr int square(int x) {
    return x * x;
}

constexpr int CountPrimes(int n) {
    std::vector<int> primes{2, 3};
    for (int i = 5; i <= n; i += 2) {
        bool flag = true;
        for (auto prime : primes) {
            if (i % prime == 0) {
                flag = false;
                break;
            }
            if (square(prime) >= i) {
                break;
            }
        }
        if (flag) {
            primes.push_back(i);
        }
    }
    return primes.size();
}


int main() {
    constexpr int cnt = CountPrimes(100);
    printf("%d\n", cnt);
    return 0;
}
```

## constexpr virtual 函数

在 C++20 中，`constexpr` 函数可以与 `virtual` 关键字结合使用，实现在编译期进行多态求值。

虚函数的 constexpr 限制：constexpr 虚函数只能在编译期求值，前提是其被调用的具体对象类型是确定的。

在 constexpr 上下文中调用 virtual 函数时，调用将绑定到具体派生类的实现。

```cpp
#include <cstdio>
#include <cstdint>

struct Base {
    constexpr virtual int Value() const = 0; // 虚拟 constexpr 函数
};

struct Derived1 : Base {
    constexpr int Value() const override { return 1; }
};

struct Derived2 : Base {
    constexpr int Value() const override { return 2; }
};

constexpr int Calc() {
    Base* d1 = new Derived1(); // constexpr 中分配内存
    Base* d2 = new Derived2();
    int value = d1->Value() + d2->Value(); // 调用虚函数
    delete d1; // 必须释放内存
    delete d2;
    return value;
}

int main() {
    constexpr auto v = Calc(); // 在编译期计算
    printf("%d\n", v);
    return v;
}

```

## 常量表达式用于模板函数的类型判断

在 C++17 中引入的 `if constexpr` 提供了一种更加简洁和可读的方式来进行模板元编程的类型判断。根据类型特性，在编译期选择不同的分支路径。

```cpp
#include <cstdio>
#include <cstdint>
#include <iostream>
#include <cmath>
#include <type_traits>

template <typename T>
bool equal(const T& a, const T& b) {
    if constexpr (std::is_integral_v<T>) {
        return a == b; // 整数类型直接比较
    } else if constexpr (std::is_floating_point_v<T>) {
        return fabs(a - b) <= 1e-3; // 浮点数进行误差比较
    } else {
        static_assert(std::is_arithmetic_v<T> || std::is_pointer_v<T>, "not supported");
    }
}

int main() {
    std::cout << std::boolalpha;
    std::cout << equal(1, 1) << std::endl;                 // true
    std::cout << equal(1L, 1L) << std::endl;               // true
    std::cout << equal(1.0000001, 1.000002) << std::endl;  // true
    std::cout << equal(1.0000001, 2.000002) << std::endl;  // false
    return 0;
}
```

在传统C++中，我们常用`std::enable_if`来实现类似的功能。但是很明显，语法会显得过于笨重。

```
#include <type_traits>
#include <cmath>
#include <cstdio>

// 整数类型
template <typename T>
typename std::enable_if<std::is_integral<T>::value, bool>::type
equal(const T& a, const T& b) {
    return a == b;
}

// 浮点类型
template <typename T>
typename std::enable_if<std::is_floating_point<T>::value, bool>::type
equal(const T& a, const T& b) {
    return std::fabs(a - b) <= 1e-3;
}

// 其他类型
template <typename T>
typename std::enable_if<
    !(std::is_integral<T>::value || std::is_floating_point<T>::value), bool>::type
equal(const T& a, const T& b) {
    static_assert(std::is_arithmetic<T>::value || std::is_pointer<T>::value, "not supported");
    return false;
}

int main() {
    puts(equal(1, 1) ? "true" : "false");                      // 整数
    puts(equal(1.0000001, 1.000002) ? "true" : "false");        // 浮点
    return 0;
}
```

## 使用`consteval`强制使用编译期求值

`consteval` 是在 C++20 中引入的关键字，用于声明立即函数（immediate function）。立即函数要求在编译时进行求值，不能在运行时调用。
如果调用一个`consteval`。如果调用 `consteval` 函数时无法在编译期计算，编译器将报错。

`constexpr` 函数在某些情况下可能会退化为运行时调用，`consteval` 可以避免这种情况。

例如：

```
#include <iostream>

// consteval 强制要求在编译时进行计算
consteval int factorial(int n) {
    return (n <= 1) ? 1 : (n * factorial(n - 1));
}

int main() {
    constexpr int result = factorial(5); // OK：在编译时计算
    std::cout << "Factorial of 5 is: " << result << std::endl;

    // int runtime = 5;
    // std::cout << "Factorial of runtime: " << factorial(runtime) << std::endl;
    // 错误：factorial 必须在编译时调用

    return 0;
}
```

## 使用`constinit`显式要求编译时初始化

`constinit` 关键字用于显式要求全局或静态变量在编译期完成初始化。
如果变量无法在编译时初始化，编译器将报错。
`constinit` 不能用于局部变量。

与 `constexpr` 不同，`constinit` 变量可以在运行时被修改。
线程安全性：在多线程环境中，`constinit` 确保变量在编译期初始化，避免线程安全问题。


```
#include <array>

// 编译时初始化
constexpr int compute(int v) { return v * v * v; }
constinit int global = compute(10);

// 错误：constinit 变量不能依赖运行时初始化
// constinit int another = global;

int main() {
    global = 100; // 允许在运行时修改

    // 错误：constinit 变量不是常量，不能用作数组大小
    // std::array<int, global> arr;

    std::cout << "Global value: " << global << std::endl;
    return 0;
}
```

## 总结

* `constexpr`在多数情况下可以替代`const`以表达“编译期常量”的语义，可用于函数、变量、类等场景。constexpr 支持在编译期和运行期进行求值，但在某些情况下可能会退化为运行期求值。
* 常量表达式函数 提供了一种更清晰的编译期计算方式，能够在一定程度上取代复杂且晦涩的模板元编程。随着 C++ 标准的演进，`constexpr` 函数逐步支持了更复杂的语法和逻辑，例如条件语句、循环语句和局部变量。但对于极端复杂的计算场景，编译期计算可能导致显著的编译时间开销。
* `constexpr`可以在模板函数中用于类型判断，通过`if constexpr`语法有效地取代`std::enable_if`，从而简化模板编程，提高代码的可读性和可维护性。
* `constexpr`函数的隐式退化风险：在某些场景下，`constexpr` 函数可能在运行时执行。若需要严格保证仅在编译期求值，可以使用 `consteval` 来强制进行编译期求值，避免不必要的运行时开销。
* `constinit`提供了一种显式要求变量在编译时完成初始化的机制，适用于非`constexpr`变量。这在全局和静态变量的初始化中尤为有用，同时也保证了多线程环境下的初始化安全性。
