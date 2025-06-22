Title: 使用31mm灯片打造拓竹LED001的低配平替方案
Date: 2025-06-22
Slug: led001-mini-alternative
Tags: 3D打印, 3D模型, DIY, LED, 灯具设计

拓竹 LED001 套件的标准尺寸为 **直径 59mm、高度 35mm**（包含灯座和灯板），售价约为 28 元。虽然这是一款常见的标准件，市面上也能买到价格更便宜（约 10 元）的兼容产品，但对于一些轻量级实验或原型用途来说，这个体积可能还是偏大。

举例来说，如果我们将整个 3D 模型按某一维度缩小 50%，理论上材料使用量可以减少 75%，既降低成本，也更便于快速迭代。

幸运的是，拼多多等平台上可以找到 **直径 31mm 的小尺寸灯片**，带焊 USB 线的版本不到 5 元，裸灯片甚至不到 3 元。只要设计一个对应尺寸的灯板与灯座，我们就能轻松实现 LED001 的低配小型替代方案。

---

## 灯板设计

常见的 31mm 灯片实际直径略大，因此建议灯板设计的内径设为 **33mm**，外径 **35mm** 为宜。同时预留走线孔和散热孔，确保电源线可以顺利穿过，避免过热。

此外，可选择是否加入导光板：

* **不加导光板**：亮度更集中，但可能刺眼。
* **加入导光板**：可适当柔化光线，提升视觉舒适度。

导光板厚度建议在 **0.6mm ~ 1mm** 之间，厚一些会降低亮度但提升均匀度。

示意图如下：

![][5]
![][6]

---

## 灯座设计

在 MakerWorld 平台上可以找到许多 LED001 的灯座模型，这些模型大多采用标准的旋转卡扣设计。我们可以复用这些设计，简单调整尺寸即可适配小尺寸灯片。

推荐使用这个 [灯座模型][2]：

![][1]

按 **60% 比例** 缩小，使其内径为约 **36mm**，同时扩大出线孔（可以直接在模型中添加负零件。后期用锉刀加工也可以，但是不推荐）。

![][3]

修改后可直接打印。
👉 缩小版模型可直接下载：[点击这里][4]

---

## 灯体适配（简单版）

对于原本就设计用于 LED001 套件的灯体，我们同样可以将其 **等比例缩小至 60%**，从而适配我们的小型灯板与灯座。

以 [“涟漪”台灯模型][7] 为例：

![][10]

按 60% 缩小后，仅需约 **28.2g 材料** 即可打印完成，而原模型则需约 **88.7g**。

![][8]
![][9]

---

## 灯体适配（进阶版）

有些灯体模型并非专为 LED001 卡扣设计，或者我们使用的是自己建模的结构，但仍希望引入 LED001 的灯座卡口进行标准化连接。

这时，可以利用 **Bambu Lab 切片软件**的布尔运算功能，快速完成“翻模”操作，而无需手动建模。

参考这个[教学视频][11]，简要步骤如下：

1. **导入模型**

   * 导入 LED 灯座卡扣模型并缩放到合适尺寸。
   * 创建一个略大于开孔的圆柱体模型。
![][12]
2. **布尔运算 - 获取翻模件**

   * 将两个模型居中对齐。
   * 右键组合 -> 使用布尔运算“差集”，选择“从中减去”圆柱体，“与之相减”为卡扣模型。勾选“删除输入”。
![][13]

3. **制作孔洞模型**

   * 用生成的“翻模件”再对目标底座进行一次“差集”操作，即可获得精准匹配卡扣的孔位。
![][14]
![][15]

---

## 小结

通过使用市售 31mm 灯片搭配自制小型灯板和灯座，我们可以：

* **大幅降低成本**（灯片约 3 元，整体成本 <10 元）
* **节省打印材料**（体积缩小后材料用量减少约 70%~75%）
* **保持模块化设计**（可复用 LED001 卡口标准）

适用于快速原型开发、创意DIY灯具、小空间照明等场景。

---

## 更多作品展示

**瑞幸 LOGO 小夜灯**

* 灯罩材质：JAYO PETG 透明蓝
* LOGO 部分：PLA 蓝色 + 白色

![][16]

---

**火焰灯（融合设计）**

* 灯罩：JAYO PETG 透明
* 灯座：JAYO PETG 黑 + PLA 红
* 模型融合自[灵魂火焰灯][18] 和 [调光底座][19]

![][17]


[1]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/deng-zuo-led001.png
[2]: https://makerworld.com.cn/zh/models/637818-led001deng-gua-pei-di-zuo?from=search#profileId-576969
[3]:https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/deng-zuo-led001-D18.png
[4]:https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/led001%E5%BA%95%E5%BA%A7-D18.3mf
[5]:https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/dengban-D33.png
[6]:https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/dengban-3mf-D33.png
[7]: https://makerworld.com.cn/zh/models/1099900-lian-yi-tai-deng-tao-jian-ban?from=search#profileId-1148153
[8]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/lianyi-components.png
[9]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/lianyi-light.png
[10]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/lianyi-3mf.png
[11]: https://www.bilibili.com/video/BV1pjPiekEqP/
[12]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/copy-model-step1.png
[13]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/copy-model-step2.png
[14]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/copy-model-step3.png
[15]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/copy-model-step4.png
[16]: https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/sample1.png
[17]:https://raw.githubusercontent.com/Wizmann/wizmann.github.com/refs/heads/source/content/statistics/LED001-alternative/sample2.png
[18]: https://makerworld.com.cn/zh/models/1166865-ling-hun-huo-yan-deng-led-deng-tao-jian-mh001?from=search#profileId-1232590
[19]: https://makerworld.com.cn/zh/models/676999-diao-guang-di-zuo-001ledxi-lie-tong-yong?from=search#profileId-622765
