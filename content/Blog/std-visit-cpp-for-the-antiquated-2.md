Date: 2025-1-1
Title: 动手实现std::visit - C++ for the Antiquated（之二）
Tags: cpp, modern cpp
Slug: std-visit-cpp-for-the-antiquated-2

## std::variant 与 std::visit

### std::variant

`std::variant` 是 C++17 引入的类型安全的联合体（type-safe union），可以在多个预定义类型中存储任意一个值。与传统的 `union` 不同，`std::variant` 能够在运行时安全地检查当前存储的类型，避免未定义行为。

其核心特点如下：

* 类型安全：访问值时进行类型检查，防止类型错误。
* 固定类型集合：存储类型在编译时确定。
* 异常安全：在赋值失败时会进入无效状态（std::monostate）。

### std::visit

`std::visit` 是一个访问器函数，用于访问 `std::variant` 中当前存储的值。它通过一个可调用对象（如 Lambda 表达式）来处理存储的值，从而实现编译时多态。

其核心特点如下：

* 统一访问接口：无论存储的是哪种类型，都可以通过同一个函数进行访问。
* 类型安全：确保所有可能的类型都被正确处理。

### 代码示例

```cpp
#include <iostream>
#include <vector>
#include <variant>
#include <type_traits>

int main() {
    std::vector<std::variant<int, float, std::string>> items {
        10,
        3.14f,
        "foobar"
    };

    for (const auto& item : items) {
        std::visit([](const auto& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, int>) {
                std::cout << "int: " << arg << std::endl;
            } else if constexpr (std::is_same_v<T, float>) {
                std::cout << "float: " << arg << std::endl;
            } else if constexpr (std::is_same_v<T, std::string>) {
                std::cout << "std::string: " << arg << std::endl;
            } else {
                static_assert(always_false<T>::value, "Unhandled type!");
            }
        }, item);
    }

    return 0;
}
```

### 代码分析

1. **`std::variant<int, float, std::string>`**  
   - 这是一个类型安全的联合体，可以存储 `int`、`float` 或 `std::string` 中的任意一种类型。  
   - 将多个 `std::variant` 存储在 `std::vector` 中，形成一个统一的容器。

2. **`std::visit`**  
   - 使用 `std::visit` 访问每个 `std::variant` 元素。  
   - 传入一个**泛型 Lambda 表达式**，通过 `if constexpr` 在编译时分发到不同的分支，处理不同类型的值。

3. **`if constexpr` 与 `std::is_same_v`**  
   - 使用 `std::is_same_v` 判断存储的实际类型。  
   - 根据类型进行不同的输出操作。

4. **类型安全**  
   - 如果添加一个未处理的类型，编译器会在 `static_assert` 中报错，提醒开发者补充处理逻辑。

## 使用传统C++实现std::visit

### 实现std::variant

在传统 C++ 中，我们只有简单的 `union` 来实现“联合体”语义。然而，`union` 存在一些局限性：

* 无法存储非平凡类型（例如 `std::string`）。
* 无法跟踪当前存储的类型。
* 无法进行类型安全检查。

而 `std::variant` 通过类型索引和类型匹配来提供类型安全，支持多种类型的存储与访问。

### 实现 std::visit

实现 `std::visit` 需要使用一个可调用对象（例如 Visitor）来访问 `std::variant` 中的值。具体来说，它在编译时根据实际类型匹配相应的 `operator()` 方法。

示例代码如下：

```cpp
#include <iostream>
#include <vector>
#include <variant>
#include <type_traits>

struct Visitor {
    int operator()(const int& item) const {
        std::cout << "int: " << item << std::endl;
        return 0;
    }

    int operator()(const float& item) const {
        std::cout << "float: " << item << std::endl;
        return 1;
    }

    int operator()(const std::string& item) const {
        std::cout << "string: " << item << std::endl;
        return 2;
    }
};

int main() {
    std::variant<int, float, std::string> item(114.514f);

    // 获取当前类型的索引
    std::cout << item.index() << std::endl; // 输出: 1 (float 的索引)

    // 获取当前存储的值
    std::cout << std::get<float>(item) << std::endl; // 输出: 114.514

    try {
        std::cout << std::get<int>(item) << std::endl;
    } catch (const std::bad_variant_access& e) {
        std::cout << e.what() << std::endl; // 类型不匹配，抛出异常
    }

    // 使用 Visitor 访问值
    std::cout << std::visit(Visitor{}, item) << std::endl; // 输出: 1 (float 类型返回 1)

    return 0;
}
```

### 实现的核心要点

实现 `std::visit` 的关键在于以下几个方面：

* **类型索引 (`index()`)**  
  根据传入的 `std::variant` 参数类型，确定其在类型集合中的索引。
  
* **类型访问 (`std::get<T>`)**  
  根据传入的模板类型 `T`，获取存储的值。如果类型不匹配，抛出异常，确保类型安全。
  
* **类型分派 (`std::visit`)**  
  根据当前存储的类型，调用 `Visitor` 中对应的 `operator()` 方法。可以通过 `switch-case` 或模板匹配来实现类型分发。

### 代码实现0 - 基本框架

```cpp
template <typename... Ts>
class MyVariant {
public:
    template <typename T>
    MyVariant(const T& item) {
        setValue(item);
    }
    
private:
    template <typename T>
    void setValue(const T& item) {
        // TODO
    }
    
    // 用于存储“联合体”的数据
    union Storage {
        Storage() {}
        ~Storage() {}
        std::aligned_union_t<0, Ts...> data;
    } storage;
};
```

### 代码实现1 - index()函数

我们使用经典的模板递归来查找类型对应的索引。同时，利用 `constexpr` 来简化编译时计算的过程。

```cpp
template <std::size_t N, typename... Types>
using TupleElement = typename std::tuple_element<N, std::tuple<Types...>>::type;

template <typename T, typename... Types>
struct TypeIndex;

template <typename T, typename First, typename... Rest>
struct TypeIndex<T, First, Rest...> {
    static constexpr int value = std::is_same<T, First>::value 
        ? 0 
        : (TypeIndex<T, Rest...>::value == -1 ? -1 : TypeIndex<T, Rest...>::value + 1);
};

template <typename T>
struct TypeIndex<T> {
    static constexpr int value = -1;
};

template <typename T, typename... Ts>
constexpr bool containsType() {
    return TypeIndex<T, Ts...>::value != -1;
}
```

通过上述代码，我们实现了在编译期确定传入类型对应的类型索引。

```cpp
template <typename... Ts>
template <typename T>
void MyVariant<Ts...>::setValue(const T& item) {
    using TargetType = std::decay_t<T>;
    static_assert(containsType<TargetType>(), "Type not supported");
    new (&storage.data) TargetType(item);
    typeIndex = getTypeIndex<TargetType>();
}
```

### 代码实现2 - `get()` 函数

我们实现了一个函数 `MyVariant::get()`，通过检查 `typeIndex` 来确保获取的类型与存储类型一致。

我们也能可以通过`MyGet`函数模拟`std::get<T>`函数的行为。

```cpp
template <typename... Ts>
class MyVariant;

template <typename T, typename... Ts>
T& MyGet(MyVariant<Ts...>& var) {
    return var.template get<T>();
}

template <typename... Ts>
template <typename T>
T& MyVariant<Ts...>::get() {
    using TargetType = std::decay_t<T>;
    if (TypeIndex<T, Ts...>::value != typeIndex) {
        throw std::runtime_error("Wrong type");
    }
    return *reinterpret_cast<TargetType*>(&storage.data);
}
```

### 代码实现3 - `visit`函数

接下来是 `visit()` 函数的实现。它通过递归方式依次访问 `std::variant` 中的每种类型，并调用与之对应的处理函数。

```cpp
template <std::size_t N, typename... Types>
using TupleElement = typename std::tuple_element<N, std::tuple<Types...>>::type;

template <typename... Ts>
template <typename TVisitor>
auto MyVariant<Ts...>::visit(TVisitor&& visitor) {
    using FirstType = TupleElement<0, Ts...>;
    using RetT = decltype(visitor(std::declval<FirstType>()));

    return visitImpl<RetT, TVisitor, Ts...>(std::forward<TVisitor>(visitor));
}

template <typename... Ts>
template <typename RetT, typename TVisitor, typename First, typename... Rest>
RetT MyVariant<Ts...>::visitImpl(TVisitor&& visitor) {
    if (getTypeIndex<First>() == typeIndex) {
        return visitor(get<First>());
    } else {
        // 递归访问剩余的类型
        return visitImpl<RetT, TVisitor, Rest...>(std::forward<TVisitor>(visitor));
    }
}

template <typename... Ts>
template <typename RetT, typename TVisitor>
RetT MyVariant<Ts...>::visitImpl([[maybe_unused]]TVisitor&& visitor) {
    // 基础情况：所有类型都已检查，未找到匹配的类型
    throw std::runtime_error("Wrong type");
}
```

## 总结

在本文中，我们实现了一个简单版的 `std::variant` 和 `std::visit`，通过传统 C++ 实现了类型安全的联合体数据结构。我们依次通过以下步骤构建了这一系统：

1. **`MyVariant` 类的基本框架**：通过联合体 (`union`) 存储不同类型的数据，并使用模板构造函数动态设置值。
   
2. **类型索引 (`index()`) 的实现**：使用模板递归技术结合 `constexpr` 来实现类型的编译时索引查找，从而在运行时根据类型索引来访问对应的值。

3. **`get()` 函数**：实现了获取存储值的函数，并通过类型检查确保类型安全。如果访问了错误类型的数据，则抛出异常。

4. **`visit()` 函数**：实现了一个可扩展的访问机制，使得不同类型的值可以通过同一个 `Visitor` 被访问和处理。通过递归的方式，系统能够动态地访问不同类型的值，并调用相应的处理函数。

通过这些实现，我们成功模拟了 C++ 标准库中的 `std::variant` 和 `std::visit` 功能。同时，通过对比可以看出，现代 C++ 提供了更强大的模板元编程能力。利用这些特性，我们能够使用更直观的语法，在编译期间实现高效且类型安全的联合体访问，从而提供一种灵活、类型安全的方式来处理多类型数据。
