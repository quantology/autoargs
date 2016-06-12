from autoargs import cmdable
import functools
import operator

@cmdable
def join3(joiner, s1, s2, s3):
    """
    >>> join3.cmd(", 1 2 3")
    '1,2,3'
    >>> join3.cmd(["-", "a", "b", "cdef"])
    'a-b-cdef'
    >>> join3.cmd("insufficient args")
    Traceback (most recent call last):
    ...
    SystemExit: 2
    """
    return joiner.join([s1, s2, s3])


@cmdable
def my_sum(a: int, b: int, c: int):
    """
    >>> my_sum.cmd("1 2 3")
    6
    >>> my_sum.cmd(["4", "5", "6"])
    15
    >>> my_sum.cmd(["a", "b", "c"])
    Traceback (most recent call last):
    ...
    SystemExit: 2
    """
    return a + b + c

@cmdable
def my_tuple(a: int, b: float, c: complex):
    """
    >>> my_tuple.cmd("10 14.1 5-2j")
    (10, 14.1, (5-2j))
    >>> my_tuple.cmd(["14j 13j 10"])
    Traceback (most recent call last):
    ...
    SystemExit: 2
    """
    return (a, b, c)

@cmdable
def product(*args: float):
    """
    >>> product.cmd(["5", "10", "0.5"])
    25.0
    >>> product.cmd("1 2 3 4")
    24.0
    """
    return functools.reduce(operator.mul, args, 1.0)
