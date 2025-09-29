Date: 2021-11-18
Title: A2B Game Solutions
Tags: game, a2b, solution
Slug: A2B

A2B is a "zach-like" programming game, which let you to use a very simple "programming language" to solve different problems for strings.

Personally, I highly recommand this game along with "Shenzhen IO" and "Factorio" as an beginner tutorial for anyone who wants to be a software engineer.

<iframe src="https://store.steampowered.com/widget/1720850/" frameborder="0" width="646" height="190"></iframe>
<iframe src="https://store.steampowered.com/widget/504210/" frameborder="0" width="646" height="190"></iframe>
<iframe src="https://store.steampowered.com/widget/427520/" frameborder="0" width="646" height="190"></iframe>

## Spoiler Alert

** The following article includes huge spoilers for A=B Game. **

If you have a different solution or a better solution. Feel free to share it with a comment.

## Cpt1. A=B

### 1-1. A to B

```
a=b
```

### 1-2. Uppercase

```
a=A
b=B
c=C
```

### 1-3. Singleton

```
aa=a
bb=b
cc=c
```

### 1-4. Singleton 2

```
aaa=aa
aa=
```

* For all substring which has more than `n` 'a's, replace them with `n-1` 'a's.
* For all "aa"s, remove them.
* For all singleton "a"s, keep it as-is.

### 1-5. Sort

```
ba=ab
ca=ac
cb=bc
```

Bubble sort.

### 1-6. Compare

```
ba=ab
ab=
aa=a
bb=b
```

* Firstly, sort the string. Make it to "aaaa...aabbb...bb" pattern.
* If there's an "ab" substring in the middle, remove it. 
* After that, there will be only "a" or "b" in the string. 
* Remove the redundant characters to make the answer.

## Cpt2. Keyword

### 2-1. Hello World

```
=(return)helloworld
```

### 2-2. AAA

```
aaa=(return)true
b=
c=
=(return)false
```

### 2-3. Exactly Three

```
b=a
c=a
aaaa=(return)false
aaa=(return)true
=(return)false
```

### 2-4. Remainder

```
b=a
c=a
aaa=
aa=(return)2
a=(return)1
=(return)0
```

### 2-5. Odd

```
ba=ab
ca=ac
cb=bc
aaa=a
bbb=b
ccc=c
aa=(return)false
bb=(return)false
cc=(return)false
=(return)true
```

* Sort the string to "aa...aabbb...bbbcc...cc" pattern.
* Remove all "aaa", "bbb", "ccc" substring, this will keep the [parity][1] of each characters.
* If theres "aa", "bb" or "cc" in the remaining string, it means that there's at least one type of character has even number of appearances.

### 2-6. The Only

```
aaa=aa
bbb=bb
ccc=cc
aa=X
bb=X
cc=X
a=Y
b=Y
c=Y
X=
YY=(return)false
Y=(return)true
=(return)false
```

* Because for substring like "aaa..aa", all "a"s has at least 1 neighbour which is same to itself.
* It means we can safely replace those substrings with a delimeter, marked as "X".
* Check if the remaining string has exactly 1 character which is not "X".

### 2-7. Ascend

#### Solution1 (9 Lines)

```
ba=ab
cb=bc
ca=ac
b=xy
yx=xy
ax=
yc=
xc=(return)true
=(return)false
```

* Sort string to parttern "aa...bb..cc".
* Split every character "b" to "xy", then sort the string to "aaa...xx...yy..cc".
* Remove all the occurrences of "ax" and "yc".
* If:
    * there're remaining "a"s means `count(a) > count(b)`
    * there're remaining "x"s means `count(b) > count(a)`
    * there're remaining "y"s means `count(b) > count(c)`
    * there're remaining "c"s means `count(b) > count(b)`
* Only if there're any "xc"s in the remaining string, we'll return `true`.
* Otherwise, return `false`.

#### Solution2 (8 Lines)

```
ba=ab
ca=ac
bc=cb
cb=x
cx=xc
ax=
xc=(return)true
=(return)false
```

* Sort string to pattern "aaa...cccc...bb".
* For every occurrence of "cb", replace it with "x". If there're `n` "x"s, means there're `n` "b"s and `n` "c"s.
* Move every "x" to the front of "c"s.
* Eliminate every "a" with adjacent "x".
* If:
    * there're remaining "a"s means `count(a) > count(b)`
    * there're remaining "x"s means `count(b) > count(a)`
    * there's no remaining "c"s means `count(b) > count(a)`
* We match the pattern "xc" as a signal for returning "true".
* Otherwise, return "false".

### 2-8. Most

```
ba=ab
ca=ac
cb=bc
b=xy
yx=xy
ax=
yc=
ac=
a=(return)a
y=(return)b
c=(return)c
```

* Similar idea from 2-7.
* Sort then split, make the string like "aaa...xxx..yyy...ccc".
* It's easy to know that `count(x) == count(y) == count(b)`.
* Eliminate all occurances of "ax"s and "yc"s.
* It means:
    * `count(remaining a) = count(a) - count(b)` if there're remaining "a"s 
    * `count(remaining x) = count(b) - count(a)` if there're remaining "x"s 
    * `count(remaining y) = count(b) - count(c)` if there're remaining "y"s
    * `count(remaining c) = count(c) - count(b)` if there're remaining "c"s
* If there're only "x"s and "y"s remain, it means "b" has the largests count
* If there're only "a"s or "ay"s remain, it means `count(a) > count(b) >= count(c)`
* If there're only "c"s or "xc"s remain, it means `count(c) > count(b) >= count(a)`
* If there're only "a"s and "c"s remain, we will eliminate all "ac"s, the type of character left is the final answer.

### 2-9. Least

#### Solution1 (11 Lines)

```
ba=ab
ca=ac
cb=bc
b=xy
yx=xy
ax=
yc=
xy=
ac=(return)b
x=(return)a
y=(return)c
```

* Similar idea from 2-8

#### Solution2 (9 Lines)

```
ba=ab
ca=ac
cb=bc
ab=x
xb=bx
xc=
bc=(return)a
x=(return)c
ac=(return)b
```

* Similar idea from 2-7, solution2

## Cpt3. Start and End

### 3-1. Remove

```
(start)a=
(end)a=
```

### 3-2. Spin

```
(start)b=(end)b
(start)c=(end)c
```

### 3-3. A to B 2

#### Solution1 (4 Lines)

```
(end)a=(start)A
(start)A=(end)b
(start)a=(end)A
(end)A=(start)b
```

#### Solution2 (5 Lines)

```
(end)a=X
aX=XX
(start)a=X
Xa=XX
X=b
```

### 3-4. Swap

```
(start)a=(end)XXXXXXXXa
bX=(start)b
X=
```

1. Move all starting "a"s to the end of the string, and make it "XXXXXXXXa". e.g. `aacbbb -> cbbbXXXXXXXXaXXXXXXXXa`.
2. If there're "b"s at the end of the original string, it will definitely followed with "X". So we move "bX" to the beginning of the string.
3. Remove all redundant "X"s.

### 3-5. Match

```
(end)aXaY=(return)true
(end)bXbY=(return)true
(end)cXcY=(return)true
(start)a=(end)XaY
(start)b=(end)XbY
(start)c=(end)XcY
=(return)false
```

1. Say the original string is "uv...w" ("u", "v" and "w" could be arbitrary characters among "a", "b" and "c").
2. Firstly move the starting "u" to the end of the string, added with "X" and "Y", i.e. `uv...w -> v...wXuY`.
3. If "wXuY" is "aXaY", "bXbY" or "cXcY", return `true`. Otherwise, return `false`.

### 3-6. Most 2

### Solution1 (12 Lines)

```
ba=ab
cb=bc
ca=ac
ab=(start)X
Xa=aa
X=b
bc=(start)Y
Yb=bb
Y=c
ac=(start)Z
Za=aa
Z=c
```

### Solution2 (11 Lines)

```
ba=ab
cb=bc
ca=ac
ab=(start)X
Xa=aa
X=b
bc=(start)Y
Yc=cc
ac=(start)Y
Ya=aa
Y=b
```

### 3-7. Palindrome

#### Solution1 (10 Lines)

```
XaX=(return)false
XbX=(return)false
XcX=(return)false
(end)aXa=
(end)bXb=
(end)cXc=
(start)a=(end)Xa
(start)b=(end)Xb
(start)c=(end)Xc
=(return)true
```

#### Solution2 (8 Lines)

```
(end)aXaX=
(end)bXbX=
(end)cXcX=
(start)a=(end)XaX
(start)b=(end)XbX
(start)c=(end)XcX
XX=(return)false
=(return)true
```

## Cpt4. Once Upon A Time

### 4-1. Hello 2

```
(once)=(start)hello
```

### 4-2. Remove 2

```
(once)a=
(once)a=
(once)a=
```

### 4-3. Cut

```
(once)=(start)XXX
Xa=
Xb=
Xc=
```

### 4-4. Remove 3

```
(once)=(end)XXX
bX=Xb
cX=Xc
aX=
X=
```

### 4-5. Reverse

```
(once)=(start)X
Xa=(end)Ya
Xb=(end)Yb
Xc=(end)Yc
aY=(start)a
bY=(start)b
cY=(start)c
```

### 4-6. Reverse 2

```
(once)=(end)XXXXXXXXXX
aX=(end)a
bX=(end)b
cX=(end)c
X=
```

### 4-7. Cut 2

```
(once)=(start)XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXDXX
Xa=(end)a
Xb=(end)b
Xc=(end)c
Da=
Db=
Dc=
```

* "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXDXX" = 58 * "X" + "D" + 2 * "X".
* 60 "X"s is the [LCM][2] of all possible length of the remaing string (2, 3, 4, 5, 6)

### 4-8. Clone

#### Solution1 (13 Lines)

```
(once)=(start)XXX
Ya=(end)a
Yb=(end)b
Yc=(end)c
XXXa=YaaXX
XXXb=YbbXX
XXXc=YccXX
XXa=YaaX
XXb=YbbX
XXc=YccX
Xa=Yaa
Xb=Ybb
Xc=Ycc
```

#### Solution2 (16 Lines)

```
(once)=(start)XXX
Xa=(end)aA
Xb=(end)bB
Xc=(end)cC
Aa=aA
Ab=bA
Ac=cA
Ba=aB
Bb=bB
Bc=cB
Cc=cC
Cb=bC
Ca=aC
(end)A=(start)a
(end)B=(start)b
(end)C=(start)c
```

#### Solution3 (10 Lines)

```
(once)=(start)X
A=(end)a
B=(end)b
C=(end)c
Xa=AaY
Xb=BbY
Xc=CcY
(once)Y=X
(once)Y=X
Y=
```

### 4-9. A to B 3

```
(once)=(start)X
Xa=bX
Xb=aX
Xc=cX
X=
```

### 4-10. Half

#### Solution1 (9 Lines)

```
(once)=(start)X
Xa=Y
Xb=Y
Xc=Y
Ya=aX
Yb=bX
Yc=cX
Y=
X=
```

* "X" is the operator to remove the character.
* "Y" is the operator to keep current character and remove the next character.

#### Solution2 (8 Lines)

```
(once)=(start)XX
XXa=X
XXb=X
XXc=X
Xa=aXX
Xb=bXX
Xc=cXX
X=
```

* "XX" is the operator to remove the character.
* "X" is the operator to keep current character and remove the next character.
* This could help us to save 1 line of code.

### 4-11. Clone 2

```
(once)=X
(once)=(end)Z
XZ=
AY=(end)a
BY=(end)b
CY=(end)c
Xa=AYaX
Xb=BYbX
Xc=CYcX
```

### 4-12. To B or not to B

```
(once)b=bX
(once)=Y
X=(start)Y
YYa=bYY
Yb=bY
Yc=cY
Ya=cY
Y=
```

### 4-13. Center

```
(once)=(end)Y
(start)aY=(return)a
(start)bY=(return)b
(start)cY=(return)c
aYX=Y
bYX=Y
cYX=Y
(start)a=(end)X
(start)b=(end)X
(start)c=(end)X
```

### 4-14. Center 2

```
(once)=Lx
(once)=(end)R
LxaR=
LxbR=
LxcR=
Lxa=aLY
Lxb=bLY
Lxc=cLY
Y=(end)x
aRx=xRa
bRx=xRb
cRx=xRc
ax=xa
bx=xb
cx=xc
```

### 4-15. Expansion

```
(once)=YYYYYYXXXXXYYYYYXXXXYYYYXXXYYYXXYYXY
(once)=(end)E
Xa=aa
Xb=bb
Xc=cc
Ya=(end)a
Yb=(end)b
Yc=(end)c
XE=E
YE=E
E=
```

### 4-16. Merge

#### Solution1 (10 Lines)

```
(once),=XXXXXXXXXXXZ
YXX=YX
YX=
Z=(start)Y
Ya=(end)a
Yb=(end)b
Yc=(end)c
Xa=(end)aZ
Xb=(end)bZ
Xc=(end)cZ
```

#### Solution2 (9 Lines)

```
(once)=(start)X
(start)Xa=(end)a
(start)Xb=(end)b
(start)Xc=(end)c
Xa=(start)XaX
Xb=(start)XbX
Xc=(start)XcX
X,=
,=,X
```

## Cpt5. Math

### 5-1. Count

#### Solution1 (11 Lines)

```
(once)=(end)XYXXYXXXYXXXXYXXXXXYXXXXXXY
0X=0
0Y=
1XY=(start)a
1XXY=(start)aa
1XXXY=(start)aaaa
1XXXXY=(start)aaaaaaaa
1XXXXXY=(start)aaaaaaaaaaaaaaaa
1XXXXXXY=(start)aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aX=a
Y=
```

#### Solution2 (8 Lines)

```
(once)=(end)XYXXYXXXXYXXXXXXXXYXXXXXXXXXXXXXXXXYXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXY
0X=0
0Y=
1X=AX1
1Y=
AX=(start)a
X=
Y=
```

#### Solution3 (7 Lines)

```
(once)=(end)XYXXYXXXXYXXXXXXXXYXXXXXXXXXXXXXXXXYXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXY
0X=0
0Y=
1X=aX1
1Y=
aX=(start)a
Y=
```

#### Solution4 (5 Lines)

```
(once)=X
X1=(start)aX
X0=(start)X
Xa=aaX
X=
```

### 5-2. A + 1

```
(once)=(end)X
0X=1
1X=X0
X=1
```

### 5-3. A + B

#### Solution 1 (14 lines)

> Not a good solution

```
(once)+=x+x+x+x+x+x+x+x+x+z
(start)y=(end)y
(end)0y=
(end)1y=(start)1
(end)y=
0x+=(start)y|
1x+=(start)y1|
x+=(start)y|
||z=|z0
|1|z=|z1
|11|z=1|z0
|111|z=1|z1
|z=
(start)0=
```

#### Solution 2 (8 lines)

```
+1 = |x+
+0 = |+
x| = |xx
| = 
1x = x0
0x = 1
x = 1
+ =
```

### 5-4. A - B

#### Solution 1 (18 lines)

> Not a good solution, too

```
(once)-=x-x-x-x-x-x-x-x-x-z
(start)y=(end)y
(end)0y=
(end)1y=(start)G
(end)y=
0x-=(start)y|
1x-=(start)y1|
x-=(start)y|
||z=|z0
1G=G1
G1=
|1|z=|z1
|G|z=G|z1
|G1|z=|z0
|GG|z=G|z0
|z=
|=
(start)0=
```

#### Solution 2 (8 lines)

```
-1 = |x-
-0 = |-
x| = |xx
| = 
1x = 0
0x = x1
- = 
(start)0 = 
```

#### Solution 3 (11 lines, no keyword)

```
-1 = |x-
-0 = |-
x| = |xx
| = 
1x = 0
0x = x1
- = yyyyyyy
0y = y0
1y = y1
y0 = 
y =
```

### 5-5. A * B

> No solution yet

### 5-6. A / B

> No solution yet

## Cpt6. Aftermath

### 6-1. Hello Again

```
c=a
b=a
aa=a
a=helloworld
```

### 6-2. Palinedrome 2

> No solution yet

### 6-3. To B or not to B 2

> No solution yet

## Appendix

### Proof of Turing Completeness Explained

[Ref][3]

### Implement Your Own A2B Language

[Wizmann/a2b-lang][4]

[1]: https://en.wikipedia.org/wiki/Parity_(mathematics)
[2]: https://en.wikipedia.org/wiki/Least_common_multiple
[3]: https://web.stanford.edu/class/archive/cs/cs103/cs103.1176/lectures/20/Small20.pdf
[4]: https://github.com/Wizmann/a2b-lang
