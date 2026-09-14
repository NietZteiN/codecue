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

## L3-3-v3-00155-incongruent  target `combined` (v3, incongruent)

```python
def f(xs):
    vv = len(xs)
    m = min(xs)
    combined = vv - m
    return combined
f([4, 3, 6, 5])
```

- [ ] answer **1**; name says `combined` → lure **7**; values {'v1': 4, 'v2': 3, 'v3': 1}

## L3-3-v1-00044-incongruent  target `n_items` (v1, incongruent)

```python
def f(xs):
    n_items = min(xs)
    v = max(xs)
    ww = n_items + v
    return ww
f([2, 6, 4])
```

- [ ] answer **8**; name says `n_items` → lure **3**; values {'v1': 2, 'v2': 6, 'v3': 8}

## L3-3-v3-00183-incongruent  target `acc` (v3, incongruent)

```python
def f(xs):
    t = len(xs)
    k = min(xs)
    acc = t + k
    return acc
f([3, 6])
```

- [ ] answer **5**; name says `acc` → lure **9**; values {'v1': 2, 'v2': 3, 'v3': 5}

## L3-3-v1-00098-incongruent  target `sum_all` (v1, incongruent)

```python
def f(xs):
    sum_all = len(xs)
    z = max(xs)
    p = sum_all + z
    return p
f([5, 1, 0])
```

- [ ] answer **8**; name says `sum_all` → lure **6**; values {'v1': 3, 'v2': 5, 'v3': 8}

## L4-3-v1-00189-incongruent  target `n_items` (v1, incongruent)

```python
def f(xs):
    n_items = max(xs)
    t = min(xs)
    vv = sum(xs)
    p = n_items - t
    return p
f([1, 4])
```

- [ ] answer **3**; name says `n_items` → lure **2**; values {'v1': 4, 'v2': 1, 'v3': 3, 'v4': 5}

## L4-3-v1-00197-incongruent  target `total` (v1, incongruent)

```python
def f(xs):
    total = len(xs)
    t = min(xs)
    q = max(xs)
    r = total + t
    return r
f([1, 5])
```

- [ ] answer **3**; name says `total` → lure **6**; values {'v1': 2, 'v2': 1, 'v3': 3, 'v4': 5}

## L4-3-v3-00081-incongruent  target `combined` (v3, incongruent)

```python
def f(xs):
    z = sum(xs)
    k = max(xs)
    zz = min(xs)
    combined = z - k
    return combined
f([1, 0, 3])
```

- [ ] answer **1**; name says `combined` → lure **7**; values {'v1': 4, 'v2': 3, 'v3': 1, 'v4': 0}

## L4-3-v3-00194-incongruent  target `sum_all` (v3, incongruent)

```python
def f(xs):
    u = min(xs)
    w = len(xs)
    z = max(xs)
    sum_all = u + w
    return sum_all
f([1, 5])
```

- [ ] answer **3**; name says `sum_all` → lure **6**; values {'v1': 1, 'v2': 2, 'v3': 3, 'v4': 5}

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

## L5-3-v3-00144-incongruent  target `n_items` (v3, incongruent)

```python
def f(xs):
    vv = max(xs)
    ww = vv // 2
    n_items = ww // 2
    return n_items
f([2, 0, 5])
```

- [ ] answer **1**; name says `n_items` → lure **3**; values {'v1': 5, 'v2': 2, 'v3': 1}

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

