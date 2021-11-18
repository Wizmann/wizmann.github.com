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

> To be continued...
