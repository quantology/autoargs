import autoargs
import pytest
import functools
import operator


def test_simple():
    def join3(joiner, s1, s2, s3):
        return joiner.join([s1, s2, s3])
    assert autoargs.autocall(join3, ", 1 2 3") == "1,2,3"
    assert autoargs.autocall(join3, ["-", "a", "b", "cdef"]) == "a-b-cdef"
    with pytest.raises(SystemExit):
        autoargs.autocall(join3, "insufficient args")

def test_casting():
    def s(a: int, b: int, c: int):
        return a + b + c
    assert autoargs.autocall(s, "1 2 3") == 6
    assert autoargs.autocall(s, ["4", "5", "6"]) == 15
    with pytest.raises(SystemExit):
        autoargs.autocall(s, ["a", "b", "c"])

    def mytuple(a: int, b: float, c: complex):
        return (a, b, c)
    results = autoargs.autocall(mytuple, "10 14.1 5-2j")
    for val, typ in zip(results, [int, float, complex]):
        assert isinstance(val, typ)
    with pytest.raises(SystemExit):
        autoargs.autocall(s, ["14j", "13j", "10"])

def test_defaults():
    pass

def test_kwargs():
    pass

def test_varargs():
    def product(*args: float):
        return functools.reduce(operator.mul, args, 1.0)
    assert autoargs.autocall(product, ["5", "10", "0.5"]) == 25.0
    assert autoargs.autocall(product, "1 2 3 4") == 24

