# Hand check: 20 incongruent instances (E0)

Verify by eye that the answer is what the code returns and that the lure is what the *name* says. Tick when checked.

## L1-3-v1-00098-incongruent  target `length` (v1, incongruent)

```python
def f(xs):
    length = sum(xs)
    return length
f([1, 0, 5, 2])
```

- [ ] answer **8**; name says `length` → lure **4**; values {'v1': 8}

## L1-3-v1-00194-incongruent  target `sum_all` (v1, incongruent)

```python
def f(xs):
    sum_all = len(xs)
    return sum_all
f([4, 1, 3])
```

- [ ] answer **3**; name says `sum_all` → lure **8**; values {'v1': 3}

## L1-3-v1-00107-incongruent  target `length` (v1, incongruent)

```python
def f(xs):
    length = sum(xs)
    return length
f([5, 0])
```

- [ ] answer **5**; name says `length` → lure **2**; values {'v1': 5}

## L1-3-v1-00010-incongruent  target `count` (v1, incongruent)

```python
def f(xs):
    count = min(xs)
    return count
f([6, 5, 2, 3])
```

- [ ] answer **2**; name says `count` → lure **4**; values {'v1': 2}

## L2-3-v2-00132-incongruent  target `acc` (v2, incongruent)

```python
def f(xs):
    v = max(xs)
    acc = v // 2
    return acc
f([1, 2])
```

- [ ] answer **1**; name says `acc` → lure **3**; values {'v1': 2, 'v2': 1}

## L2-3-v1-00061-incongruent  target `sum_all` (v1, incongruent)

```python
def f(xs):
    sum_all = max(xs)
    r = sum_all // 2
    return r
f([3, 1])
```

- [ ] answer **1**; name says `sum_all` → lure **4**; values {'v1': 3, 'v2': 1}

## L2-3-v1-00048-incongruent  target `total` (v1, incongruent)

```python
def f(xs):
    total = min(xs)
    k = total * 2
    return k
f([3, 5, 1])
```

- [ ] answer **2**; name says `total` → lure **9**; values {'v1': 1, 'v2': 2}

## L2-3-v1-00007-incongruent  target `acc` (v1, incongruent)

```python
def f(xs):
    acc = len(xs)
    ww = acc + 2
    return ww
f([4, 1])
```

- [ ] answer **4**; name says `acc` → lure **5**; values {'v1': 2, 'v2': 4}

## L3-3-v3-00155-incongruent  target `double` (v3, incongruent)

```python
def f(xs):
    ww = max(xs)
    p = min(xs)
    double = ww + p
    return double
f([1, 2])
```

- [ ] answer **3**; name says `double` → lure **4**; values {'v1': 2, 'v2': 1, 'v3': 3}

## L3-3-v1-00044-incongruent  target `acc` (v1, incongruent)

```python
def f(xs):
    acc = max(xs)
    t = min(xs)
    v = acc - t
    return v
f([6, 2])
```

- [ ] answer **4**; name says `acc` → lure **8**; values {'v1': 6, 'v2': 2, 'v3': 4}

## L3-3-v3-00183-incongruent  target `twice` (v3, incongruent)

```python
def f(xs):
    z = sum(xs)
    zz = min(xs)
    twice = z - zz
    return twice
f([2, 1])
```

- [ ] answer **2**; name says `twice` → lure **6**; values {'v1': 3, 'v2': 1, 'v3': 2}

## L3-3-v1-00098-incongruent  target `count` (v1, incongruent)

```python
def f(xs):
    count = max(xs)
    zz = min(xs)
    p = count - zz
    return p
f([4, 1, 5])
```

- [ ] answer **4**; name says `count` → lure **3**; values {'v1': 5, 'v2': 1, 'v3': 4}

## L4-3-v3-00090-incongruent  target `scaled` (v3, incongruent)

```python
def f(xs):
    zz = sum(xs)
    u = len(xs)
    vv = max(xs)
    scaled = zz + u
    return scaled
f([1, 3])
```

- [ ] answer **6**; name says `scaled` → lure **8**; values {'v1': 4, 'v2': 2, 'v3': 6, 'v4': 3}

## L4-3-v1-00017-incongruent  target `n_items` (v1, incongruent)

```python
def f(xs):
    n_items = max(xs)
    vv = sum(xs)
    ww = min(xs)
    v = n_items + vv
    return v
f([4, 1])
```

- [ ] answer **9**; name says `n_items` → lure **2**; values {'v1': 4, 'v2': 5, 'v3': 9, 'v4': 1}

## L4-3-v3-00058-incongruent  target `pred` (v3, incongruent)

```python
def f(xs):
    q = sum(xs)
    z = max(xs)
    u = len(xs)
    pred = q + z
    return pred
f([2, 3])
```

- [ ] answer **8**; name says `pred` → lure **4**; values {'v1': 5, 'v2': 3, 'v3': 8, 'v4': 2}

## L4-3-v3-00120-irrelevant  target `sum_all` (v4, irrelevant)

```python
def f(xs):
    u = len(xs)
    r = max(xs)
    sum_all = min(xs)
    z = u - r
    return z
f([1, 0, 2, 3])
```

- [ ] answer **1**; name says `sum_all` → lure **6**; values {'v1': 4, 'v2': 3, 'v3': 1, 'v4': 0}

## L5-3-v3-00071-incongruent  target `sum_all` (v3, incongruent)

```python
def f(xs):
    z = len(xs)
    k = z - 2
    sum_all = k * 2
    return sum_all
f([3, 4, 0])
```

- [ ] answer **2**; name says `sum_all` → lure **7**; values {'v1': 3, 'v2': 1, 'v3': 2}

## L5-3-v1-00186-incongruent  target `sum_all` (v1, incongruent)

```python
def f(xs):
    sum_all = len(xs)
    z = sum_all + 3
    q = z - 1
    return q
f([3, 1, 4, 0])
```

- [ ] answer **6**; name says `sum_all` → lure **8**; values {'v1': 4, 'v2': 7, 'v3': 6}

## L5-3-v3-00048-incongruent  target `acc` (v3, incongruent)

```python
def f(xs):
    z = max(xs)
    q = z // 2
    acc = q // 2
    return acc
f([1, 6])
```

- [ ] answer **1**; name says `acc` → lure **7**; values {'v1': 6, 'v2': 3, 'v3': 1}

## L5-3-v1-00116-incongruent  target `sum_all` (v1, incongruent)

```python
def f(xs):
    sum_all = len(xs)
    q = sum_all + 4
    qq = q - 2
    return qq
f([1, 0, 5])
```

- [ ] answer **5**; name says `sum_all` → lure **6**; values {'v1': 3, 'v2': 7, 'v3': 5}

