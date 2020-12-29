Date: 2020-12-29
Title: 我到底从UW-CSE341学到了什么
Tags: 公开课, PL, Functional Programming, OCaml, Racket
Slug: UW-CSE341-au20

> TL;DR 什么也没学到

[课程首页][1]

Coursera-课程-[A][2], [B][3], [C][4]

介绍当中说，本课程主要内容是FP，并且顺道讨论一下程序语言的设计。

UW官方上面的课程只有Slides和assignments，video不提供。Coursera有video，但是版本比较老，是2013年的。下面的讨论都是基于au20的新版本。

简单来说，前半学期（hw1-hw4)是关于OCaml，一种静态类型的FP。后半学期(hw5-hw7)是Racket，一种动态语言FP。课程里面80%+（的难度）都在于新的FP编程语言，只包含少数PL的内容。例如HW4中，需要实践一个简单粗暴的tokenizer/parser；HW6实现了一个虚假的编程语言MUPL，这个实现并不需要你解析代码，而是手写解析好的语法树，在上面实现求值、闭包、递归等。

> 调试与debug也是一个非常蛋疼的问题，尤其是Racket写闭包的时候。。。

学习建议：

1. OCaml的部分比较简单，7天一个小长假就可以搞定。做为平时的娱乐调剂也可以，周期不会超过一个月。
2. 如果不想使用OCaml，可以尝试F#。因为都是一个流派的，语法接近。使用VS还可以有实时的提示。
3. Racket的部分难度较大，主要是与平时所使用的语言差别较大。没啥好办法，只能多打log。
4. HW7难度不高，但是提供的代码里面有一个在构造函数里面Call虚函数的迷惑操作。
5. 多写测试。

Repo地址：https://github.com/Wizmann/UW-CSE341-au20

仅供参考。


[1]: https://sites.google.com/cs.washington.edu/cse341au20/home
[2]: https://www.coursera.org/learn/programming-languages
[3]: https://www.coursera.org/learn/programming-languages-part-b
[4]: https://www.coursera.org/learn/programming-languages-part-c
