import autoargs

def main(arg1: int, arg2: int, *, val=10, val2:int):
    """my docstring"""
    return arg1 + arg2 + val + val2

def example(a, b: int, *others, d: float, e=10):
    """Here is my docstring"""
    return str(locals())

import numpy

@cmdable
def f2(x: int, y: int, *z: int, op: {'sum', 'mul'}='mul'):
    "aggregate x, y, and z's by mul or sum"
    all_vals = [x, y] + list(z)
    print(all_vals)
    if op == 'sum':
        return sum(all_vals)
    elif op == 'mul':
        return numpy.product(all_vals)

@cmdable
def f1(x: int, y: int, *z: int):
    "agg x, y, and z's by sum"
    return f2(x, y, *z, op='sum')

@cmdable
def f3(*, op):
    if op == "sum":
        return f1
    elif op == "mul":
        return f2

if __name__ == "__main__":
    #result = autoargs.autorun(main)
    result = autoargs.autorun(example)
    print(result)
