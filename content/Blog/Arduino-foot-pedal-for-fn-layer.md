Date: 2021-04-08
Title: 利用Arduino制作脚踏板Fn层开关
Tags: Arduino, ahk, autohotkey, fn-layer, keyboard
Slug: Arduino-foot-pedal-for-fn-layer

## 背景

之前焊了两个客制化键盘，一个是ErgoDone，一个是仿minila配列的60键盘。这两个键盘的共同特点是双手大拇指各有一个额外的开关，我将其做为Fn层的开关，用来开启两个fn层：Vim和NumPad（是啥并不重要，可以理解为功能键的重映射）。

这两把键盘都是Cherry红轴。最近想把之前的酷冷扰民青轴87键用起来，但是因为它是标准配列，所以没有Fn键。重新焊一把新键盘或者换轴又太贵了。所以想用软硬结合的方法，额外做两个脚踏板按键，用来控制相应的Fn层。

## 所需要的零件

* 一把正(yang)常(jian)配列的键盘
* Arduino Pro Micro （TB，25包邮，大概买贵了）
* 两个脚踏板（TB，23两个包邮）
* 一根USB 2.0公母线（PDD，3块钱。用来分离脚踏板开关和面包板）
* 小号面包板一个（TB，5块）
* 1个1K欧的电阻（成本不计，我用了两个）
* 一些跳线和导线（成本不计）

## 电路设计

![circuit][1]

> 画图网站上只有Arduino Uno，这里需要Arduino Leonardo或者Arduino Pro Micro以支持键盘模拟

像我上面说的，可以只使用一个下拉电阻。我为了跳线好看，就用了两个。

![realworld][2]

代码：

```c
#include "Keyboard.h"

const int F18_Pin = 5;
const int F19_Pin = 8;

int RXLED = 17; // The RX LED has a defined Arduino pin
int TXLED = 30; // The TX LED has a defined Arduino pin

const int KEY_COUNT = 2;

const int PINS[2] = {F18_Pin, F19_Pin};
const int LEDS[2] = {RXLED, TXLED};
const int MAPPED_KEYS[2] = {0xF5, 0xF6};

int previousButtonState[2] = {HIGH, HIGH};

void setup() {
  for (int i = 0; i < KEY_COUNT; i++) {
    pinMode(PINS[i], INPUT);
  }
  // initialize control over the keyboard:
  Keyboard.begin();
  pinMode(RXLED, OUTPUT); // Set RX LED as an output
  pinMode(TXLED, OUTPUT); // Set TX LED as an output
}

void loop() {
  // read the pushbutton:
  for (int i = 0; i < KEY_COUNT; i++) {
    int buttonPin = PINS[i];
    int buttonState = digitalRead(buttonPin);
    if (previousButtonState[i] != buttonState) {
      if (buttonState == HIGH) {
        //Keyboard.press(MAPPED_KEYS[i]);
        Keyboard.press(MAPPED_KEYS[i]);
        digitalWrite(LEDS[i], LOW);
      } else {
        Keyboard.release(MAPPED_KEYS[i]);
        digitalWrite(LEDS[i], HIGH);
      }
    }
    // save the current button state for comparison next time:
    previousButtonState[i] = buttonState;
  }
  delay(100);
}
```

照着示例代码改的，简单的很，有手就行。

## 接线设计

我使用了接线端子连接导线，优点是方便，缺点是难看，老大一坨，还不一定稳当。后面会考虑用高级一点的接线方法。

还剪了一根USB2.0公母线，用来做“键线分离”。因为USB2.0里面有四根线，两个脚踏板开关共用GND线，正极各用一根，还有一根富裕。其实也可以用音频线。

## 软件设计

由于我们并没有修改正常键盘的配列，所以需要用软件方法来对Fn层进行重映射。

从上面的代码我们可以看出，两个脚踏板开关分别被映射到了F18和F19。所以我们就把这两个键当作Fn，使用AutoHotKey制作Fn层。

```ahk
#MaxHotkeysPerInterval 1000

F19::Return

#If GetKeyState("F19", "P")
	a::SendInput {Home}
	e::SendInput {End}
	x::SendInput {Delete}
	d::SendInput {PgDn}
	m::SendInput {AppsKey}
	u::SendInput {PgUp}
	h::SendInput {Left}
	j::SendInput {Down}
	k::SendInput {Up}
	l::SendInput {Right}
	b::SendInput {Backspace}
	
	
F18::Return

#If GetKeyState("F18", "P")
	a::SendInput {1}
	s::SendInput {2}
	d::SendInput {3}
	f::SendInput {4}
	g::SendInput {5}
	h::SendInput {6}
	j::SendInput {7}
	k::SendInput {8}
	l::SendInput {9}
	;::SendInput {0}
	q::SendInput {!}
	w::SendInput {@}
	e::SendInput {#}
	r::SendInput {$}
	t::SendInput {`%}
	y::SendInput {^}
	u::SendInput {&}
	i::SendInput {*}
	o::SendInput {(}
	p::SendInput {)}
	1::SendInput {F1}
	2::SendInput {F2}
	3::SendInput {F3}
	4::SendInput {F4}
	5::SendInput {F5}
	6::SendInput {F6}
	7::SendInput {F7}
	8::SendInput {F8}
	9::SendInput {F9}
	0::SendInput {F10}
	-::SendInput {F11}
	=::SendInput {F12}
```

代码简单粗暴。

## 总结

又要重学打字了，除了用手之外，还要用脚。。。

感觉自己程序员当不下去之后，可以去电子厂上班了（做梦

[1]: https://github.com/Wizmann/assets/blob/df8691c2f4385919f024b7200a875485a8d0fb8b/wizmann-tk-pic/Snipaste_2021-04-08_00-23-08.png?raw=true
[2]: https://github.com/Wizmann/assets/blob/abaecd1c3cc70e5860fb459345686eae18245580/wizmann-tk-pic/WeChat%20Image_20210408004402.jpg?raw=true
