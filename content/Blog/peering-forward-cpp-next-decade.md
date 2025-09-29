Title: 展望未来十年：C++ 的下一步 —— Herb Sutter @ CppCon 2024
Date: 2025-09-29 10:00
Category: C++
Tags: C++, CppCon, Herb Sutter, 编译期编程, 安全性, 反射, 元类
Slug: peering-forward-cpp-next-decade

<div class="alert alert-warning" role="alert">
  ⚠️ 本文根据视频字幕和 slides 由 AI 生成
</div>

---

Keynote：[**Peering Forward: C++’s Next Decade**（CppCon 2024）](https://github.com/CppCon/CppCon2024/blob/main/Presentations/Peering_Forward_Cpps_Next_Decade.pdf)

---

## TL;DR（官方脉络）

* **重大进展在路上**：`std::execution` 并发/并行、类型与内存安全改进、反射 + 代码生成（“注入”）、Contracts；其中部分内容**已进入 C++26** 的初始投票/合入节奏。
* **主旋律**：把更多工作“左移”到编译期；以 **安全性对标（parity）** 为目标（而非完美），逐步减少未定义行为；通过**泛化带来简化**，让代码直接表达“意图”。

---

## 1) 术语澄清：三种“安全”，别混了

Herb 明确区分了三个层面的“安全”，并给出行业场景示例（ISO/IEC 23643:2020 术语脉络）：

* **Software security（网络/信息安全）**：让软件能抵御恶意攻击、保护资产（电网、医院、银行、个人数据等）。
* **Software safety（生命/功能安全）**：避免对人、财产、环境造成不可接受的风险（如医院设备、自动驾驶/武器）。
* **Programming language safety（语言/内存安全）**：对程序正确性的静态/动态保证，既能提升前两者，也能普遍提高质量。

Herb 把“内存安全攻击”称作一场**进行中的冷战**，强调这既有现实紧迫性，也影响语言设计优先级。

---

## 2) 大方向：C++26/29 的主线与“安全对标”目标

* **优先处理的四大类问题**：类型、边界、初始化、生命周期（正好对应最严重的四类 CWE，且现代语言普遍做得更好）。
* **“安全 Profile” 框架**（Stroustrup & Dos Reis）：把（多半已知的）静态安全规则**上移到编译期**，可按“代码体积/模块”选择地逐步启用，并**可增量演进**。给“Profile”下了明确定义：一组在编译期强制的规则，保证消除某类缺陷。
* **采用策略**：仍旧坚持“默认性能与可控性”，同时做到“安全随处可用”，愿景是**“今天：靠警惕；明天：可选择 opt-out”**。

---

## 3) C++26 新武器：“erroneous behavior”（错误行为）

### 3.1 背景与改变

* 读取未初始化局部变量，传统上是 **UB（未定义行为）** —— 这会导致“时间旅行/泄密”等坏结果。C++26 将**引入“错误行为（erroneous behavior）”** 的概念：**行为被明确定义为“就是错”**，编译器需写入“错误值”，从而避免“UB 的魔法”破坏安全。
* **量化收益**：预计可**自动消除一大类（5%-10%）** 的漏洞/缺陷，而且**无需改动旧代码，只要重编译即可**——这对“可采纳性”极为关键。

### 3.2 小例子（信息泄露不再发生）

```cpp
auto f1() {
    char a[] = {'s','e','c','r','e','t'};
}

auto f2() {
    char a[6];           // 未初始化
    print(a);            // C++26: 打印“错误值”（绝不会是 "secret"）
}

int main() { f1(); f2(); }
```

如上示例中，旧世界里常见的“泄密”将不再发生。

> 为什么不“统一零初始化”？Herb 给出的理由包括：零并不总是语义正确值，且会**掩盖真实问题**（让静态/动态工具难以发现），还有成本因素（大对象清零）。需要时也可以**显式 opt-out**：`int a [[indeterminate]];`。

---

## 4) “初始化前置”与“边界安全”：从规范到工程可采纳

* **不要强行“声明即初始化”或“用模式填充”**：这类“塞入无意义写入”的做法会给优化与静态分析带来困境。真正想要的是**“首次使用前必然完成初始化（definite initialization）”**。Herb 指出 C#、Ada 等已有实践，且在 **Cpp2** 中已实现原型：

  * 局部变量默认**未初始化**（性能优先），但**任一路径首次使用前必须完成构造**；
  * 通过直接构造或“out 形参的填充函数”均可；
  * 这样即可组合化地表达“初始化策略”。
* **边界检查（Bounds）**：在 **Cpp2** 的实证中，对**连续容器的 `a[b]`** 注入 `0 <= b && b < size(a)` 形式的**调用点检查**，违例通过契约处理（可自定义）。无需改 STL 或大多数容器实现，也适用于 C 数组（在衰变前）。这类检查可通过将来标准的 **“bounds Profile”** 一键启用（理念上“启用 Profile 并重编译”）。

**示例（越界检测理念）**：

```cpp
//   int              a[] = {1,2,3};
//   std::vector<int> a   = {1,2,3};

print(a[1]);  // ok
print(a[3]);  // 触发边界违例（在 Cpp2 原型中通过契约报告）
```



---

## 5) “海啸将至”：反射 + 代码生成（a.k.a. 注入）

Herb 认为 **反射 + 生成** 将是**未来十年最重要的语言能力**，与 `constexpr` 一同构成“把更多意图抬到编译期”的关键通道；并强调 **C++ 是我们想要的“编译期语言”，也是我们想要的“GPU 语言”**。

### 5.1 P2996：以“命令行解析器”为例

```cpp
struct MyOpts {
    std::string file_name = "input.txt"; // --file_name <string>
    int         count     = 1;           // --count <int>
};

int main(int argc, char* argv[]) {
    MyOpts opts = parse_options<MyOpts>(
        std::vector<std::string_view>(argv+1, argv+argc));
    std::cout << "opts.file="  << opts.file_name << '\n';
    std::cout << "opts.count=" << opts.count     << '\n';
}
```

`parse_options` 利用反射枚举数据成员、识别标识符、推导成员类型，并拼接生成解析逻辑（示例里可见 `nonstatic_data_members_of`, `identifier_of`, `type_of`, 以及“**splices**/注入语法”）。

> 实现进展：已有 **EDG** 与 **Clang** 原型跟进 P2996（EDG：Daveed Vandevoorde；Clang：Dan Katz/Bloomberg；另有 Lock3、Circle、cppfront 等相关探索）。

### 5.2 P0707（metafunctions/metaclass）：“接口”一键生成

**手写接口类**（纯虚 + 析构 + 禁复制）：

```cpp
class IFoo {
public:
  virtual int  f() = 0;
  virtual void g(std::string) = 0;
  virtual ~IFoo() = default;
  IFoo() = default;
  IFoo(IFoo const&) = delete;
  void operator=(IFoo const&) = delete;
};
```

**用元类表达“意图”**：

```cpp
class(interface) IFoo {
  int  f();
  void g(std::string);
};
```

底层可由 `interface(...)` 元函数在编译期**反射原型并生成**上述纯虚骨架与语义约束。

> 幻灯还给出了 `interface` 的实现片段：使用 `identifier_of`, `members_of`, `return_type_of`, `parameter_list_of` 等元函数在编译期**拼接类定义**。

### 5.3 “通过泛化获得简化”：三条“北极星”准则

1. **源代码中所有信息都必须可反射**（包括属性、默认值等）。
2. **凡是能手写的源代码，都必须能生成**（类型、自由函数、对 `std::` 模板的特化等）。
3. **所有代码（手写或生成）都必须可见**（可 pretty-print、可调试、可展开）。
   此处还延展到**编译期产物**（如 `.winmd` 等）也应能在编译期生成。

---

## 6) 生态/工具的“可表达性扩展”：从 Qt/COM 到物理数据模型

Herb 展示了若干“把外部代码生成/IDL/脚本**收回到 C++ 源**”的**草案式**思路：

* **Qt moc**：用 `class(Qclass) ...` + `property/signal/slot` 的语义化声明，代替额外的 `.moc` 生成链路。
* **COM/WinRT**：以 `class(rt_interface<...>)` 形式表达 IDL 语义（比如 `property<UINT, SomeClass>`），统一到编译期反射+生成。
* **粒子物理的 podio**：将原本的 YAML 数据模型描述迁回到 **`class(podio::datatype)`** 里，用 `constexpr` 静态字符串与生成管线**在常规 C++ 编译中完成同等产物**。

---

## 7) 更多实用范例

* **instrumented vector**：对模板实体执行 **“identity+增强”** 的生成（示例在 `operator[]` 包裹统计逻辑），说明“反射+生成”不仅能**复制粘贴**，还能**普遍地为一类实体注入横切逻辑**（计数、日志、检测等）。
* **编译期 regex**：对比 **CTRE** 与 **cppfront 的 `@regex`**，均通过编译期解析/生成专用匹配器以获高效实现，体现“**把意图抬到编译期**”的性能与可维护性价值。

---

## 8) GPU 与 `constexpr` 的共同语言：C++ 本体

幻灯强调了一个观察：多年来 C++ 在 **`constexpr` 的可执行性** 与 **GPU 编程模型** 的融合路径上不断前进，**“C++ 就是我们想要的编译期语言，也是 GPU 语言”**，因此**不要引入背离 C++ 本体的“特殊循环/方言”**，而是尽可能让**同一语言**在不同阶段/目标上自然工作。

---

## 9) 风险与设计护栏

* 这类演进需要“**北极星**”（目标用例的前瞻清单）与“**护栏**”（防止底层碎片化导致拼不上整体图景）。
* 建议目标：**P0707 元函数**、**Andrei 的 instrumented_vector**、以及“**反射+再生成任意类型（恒等变换）**”。
* 应**吸取 C#、D、Lock3、cppfront** 等经验，避免“只顾底层细节而忽略端到端场景”。

---

## 10) 结语：欢迎来到 C++ 的下一个十年

Herb 的判断：**反射+生成** 将主导下一个十年；
它会**让难事变易**（如 复杂 Template MetaProgramming、表达式模板），也会**让“原本做不到”的事成为可能**（如大规模生成式编程）。第一阶段的标准化蓝图**已经在望**。
