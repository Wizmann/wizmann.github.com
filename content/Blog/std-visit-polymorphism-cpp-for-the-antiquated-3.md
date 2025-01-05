Date: 2025-1-4
Title: std::visit实现运行时多态 - C++ for the Antiquated（之三）
Tags: cpp, modern cpp
Slug: std-visit-polymorphism-cpp-for-the-antiquated-3

在传统的 **C++** 中，**运行时多态** 通常依赖于 **“接口 - 虚函数”** 机制，通过抽象类、具体类与对象的设计来实现。这种多态方式通常被称为 **子类型多态**（*Subtype Polymorphism*）。

在之前的文章中，我们介绍了现代 C++ 引入的 `std::variant` —— 一种类型安全的联合体，以及如何借助 `std::visit` 在类型安全的前提下，动态地访问联合体中的不同类型，并执行相应的逻辑。这种多态方式被称为 **临时多态**（*Ad-hoc Polymorphism*）。

除此之外，还有一种被称为 **参数化多态**（*Parametric Polymorphism*），即我们熟知的 **C++ 模板**。它允许我们编写与类型无关的代码，提供更强的泛型编程能力。由于本篇文章的重点并不在此，我们暂且不展开。

在本篇文章中，我们将重点对比 **子类型多态** 和 **临时多态** 的优劣，分析它们在实际场景中的应用与权衡，希望能更好地理解和选择合适的多态机制。

## **临时多态的实现原理**

**临时多态**（*Ad-hoc Polymorphism*）与 **子类型多态**（*Subtype Polymorphism*）在实现原理上有一定的相似性：它们都依赖于在类型中引入额外的信息来决定不同类型应执行的函数逻辑。  

- **子类型多态**：依赖于**虚表（vtable）** 和 **虚指针（vptr）**，通过运行时的动态分派来确定调用哪个派生类的成员函数。  
- **临时多态**：依赖一个 **枚举值（enum）** 来表示类型信息，通过显式的 `switch-case` 或 `if-else` 语句来选择不同的逻辑分支。

### **简单示例：模拟 std::visit**

> 这里只使用了传统C++的实现，关于`std::visit`的更详细的解读，可以参考本系列的“动手实现std::visit”一文。

```cpp
#include <iostream>
#include <string>
#include <cassert>

enum EType : uint8_t {
    TYPE_Int = 0,
    TYPE_Float = 1,
    TYPE_String = 2,
};

struct MyVariant {
    EType type;
    void* obj;
};

void MyVisitor(MyVariant& var) {
    switch (var.type) {
        case TYPE_Int: 
            std::cout << "Int: " << *(int*)var.obj << std::endl;
            break;
        case TYPE_Float:
            std::cout << "Float: " << *(float*)var.obj << std::endl;
            break;
        case TYPE_String:
            std::cout << "String: " << *(std::string*)var.obj << std::endl;
            break;
        default:
            assert(false && "Unknown type!");
            break;
    }
}

int main() {
    int i = 42;
    float f = 3.14f;
    std::string s = "Hello";

    MyVariant var1 = {TYPE_Int, &i};
    MyVariant var2 = {TYPE_Float, &f};
    MyVariant var3 = {TYPE_String, &s};

    MyVisitor(var1);
    MyVisitor(var2);
    MyVisitor(var3);

    return 0;
}
```

### **原理解析**

1. **EType 枚举**  
    - 定义了一个枚举类型 `EType`，用于标识 `MyVariant` 当前存储的具体类型。
2. **MyVariant 结构体**  
    - `type` 字段保存当前对象的类型信息。  
    - `obj` 字段是一个通用指针，指向实际存储的数据对象。  
3. **MyVisitor 函数**  
    - 通过 `switch-case` 语句，基于 `type` 字段选择不同的分支逻辑来访问和打印不同类型的数据。  
    - 如果遇到未知类型，程序会触发 `assert` 以防止未定义行为。

### **性能优化思考**

在实际应用中，`switch-case` 语句可能随着类型数量的增加而导致性能开销。可以通过二分查找（Binary Search）方法进行优化，减少 `switch-case` 的分支深度。
   
## 临时多态的性能分析

虚函数常因其较低的性能而受到批评。为了更好地了解这一点，我们将对比使用虚函数实现的“子类型多态”和通过 `std::visit` 实现的“临时多态”在性能上的差异。

* 使用虚函数实现的[代码](https://gist.github.com/Wizmann/df65af6d214c3b4ae296363839477b94)
* 使用`std::visit` + `std::variant<object>` 实现的[代码](https://gist.github.com/Wizmann/f1494312a8e0cf30b97e9d8580fa9d6d)
* 使用`std::visit` + `std::variant<ptr>` 实现的[代码](https://gist.github.com/Wizmann/a25708bcd732df8f6e3d158f7105b6c9)

结果如下：

```
# 使用g++ --std=c++17 -O2编译运行

# 使用虚函数实现
Total Object Creation Time: 55.53 ms
Total Visit Time: 6.99 ms

# 使用std::visit + std::variant<object>实现
Total Object Creation Time: 26.88 ms
Total Visit Time: 5.93 ms

# 使用std::visit + std::variant<ptr>实现
Total Object Creation Time: 52.15 ms
Total Visit Time: 6.05 ms
```

### 结果分析
* 内存管理开销：
    使用虚函数的子类型多态实现通常需要动态申请和释放内存，从而引入了额外的内存管理开销。而使用基于 `std::variant<object>`的临时多态可以一次性分配所有内存，虽然可能存在一定程度的内存浪费，但避免了频繁的动态内存管理。
* 性能接近，`std::visit` 略优：
    虽然虚函数和 `std::visit` 的性能差距不大，但 `std::visit` 略微优于虚函数。两者都引入了额外的开销以实现多态。

## 通过临时多态实现Vistor模式

Visitor模式是一种行为设计模式，用于将数据结构的操作与数据结构本身分离。它通常通过“子类型多态”来实现，其中每个具体类型的对象都接受一个访问者（Visitor）并对其进行相应的处理。使用虚函数和继承是实现这一模式的一种方式，但有时我们可以用更轻量的方式来实现，比如通过临时多态结合 `std::variant` 和 `std::visit`。

### 使用虚函数实现Visitor模式

我们首先来看一个传统的通过子类型多态实现Visitor模式的例子：

```cpp
struct IVisitor;

struct IResource {
    virtual void accept(IVisitor* visitor) = 0;
};
struct IVisitor {
    virtual void visit(IResource* res) = 0;
};

class MyResource : public IResource {
public:
    void accept(IVisitor* visitor) override {
        visitor->visit(this);
    }
};

class MyVisitor : public IVisitor {
public:
    void visit(IResource* res) override {
        // 处理资源
    }
};
```

这种实现方式虽然能很好地分离数据和操作，但它也有一些不足之处：

- 每次调用 `visit` 都需要通过虚函数来间接调用方法，这会引入额外的性能开销。
- `visitor` 无法在 `visit` 时直接获取资源对象的类型信息，通常需要额外传递类型信息或者让资源类暴露更多的接口。

### 使用 `std::visit` 实现Visitor模式

通过 `std::visit` 和 `std::variant`，我们可以显式地通过类型信息来处理每种资源类型，避免了虚函数调用的开销，同时使得代码更加简洁和类型安全。下面是一个通过临时多态实现Visitor模式的例子：

```cpp
using ResourceUnion = std::variant<ResourceA, ResourceB, ResourceC>;

std::vector<ResourceUnion> resources;
for (auto& res : resources) {
    std::visit([](auto& res) {
        using T = std::decay_t<decltype(res)>;
        if constexpr (std::is_same_v<T, ResourceA>) {
            // 处理类型为 ResourceA 的资源
        } else if constexpr (std::is_same_v<T, ResourceB>) {
            // 处理类型为 ResourceB 的资源
        } else if constexpr (std::is_same_v<T, ResourceC>) {
            // 处理类型为 ResourceC 的资源
        } else {
            static_assert(always_false_v<>, "Unhandled type!");
        }
    }, res);
}
```

### 优点与分析

1. **类型安全**：
   使用 `std::visit` 时，编译器可以根据类型推断并为每种类型生成不同的代码路径，从而避免了运行时错误和类型错误，提升了类型安全性。

2. **性能**：
   由于不再依赖虚函数，`std::visit` 能避免每次调用 `visit` 时的虚函数开销，从而提高了性能。

3. **简洁性**：
   通过 `std::variant` 和 `std::visit`，代码更加简洁且不需要繁琐的继承结构。每个资源类型只需关注其自身的实现，而无需处理不同访问者的逻辑。

4. **扩展性**：
   如果要新增资源类型，只需在 `std::variant` 中添加新类型，并在 `std::visit` 的 lambda 表达式中添加对应的分支，避免了修改现有代码的风险。

## 临时多态的优点与缺点

### 优点：
1. **类型安全**：`std::variant` 与 `std::visit` 确保了类型安全，避免了许多传统多态机制中的错误。
2. **性能优化**：相较于虚函数，`std::visit` 通过类型折叠和编译时分支优化，通常表现出更好的性能，尤其在没有动态内存管理时。
3. **自由组织功能函数**：你可以灵活地将功能函数组织在一个地方，而无需修改每个具体类型。

### 缺点：
1. **职责分散**：每个类型的行为都可能分散到多个`visit`函数中，导致代码难以维护。
2. **高耦合风险**：当新增类型时，所有访问逻辑需要修改，可能带来较高的耦合度，尤其在类型较多时。

## 参考

* C++20高级编程（罗能） —— 1.6 运行时多态
* [深入理解面向对象中的多态](https://wiyi.org/polymorphism-in-java.html)
* [C++ 访问者模式讲解和代码示例](https://refactoringguru.cn/design-patterns/visitor/cpp/example)
