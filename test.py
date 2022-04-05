def flatten(lst):
    for v in lst:
        if isinstance(v, list):
            yield from flatten(v)
        else:
            yield v


a = ['av', 3, 4, 5, 6]
b = [7, 8, 9]
a.insert(-1, b)
print([*flatten(a)])