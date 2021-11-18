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

> To be continued...

[1]: https://en.wikipedia.org/wiki/Parity_(mathematics)
