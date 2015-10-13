import autoargs

def main(arg1: int, arg2: int, *, val=10, val2:int):
    """my docstring"""
    return arg1 + arg2 + val + val2

def example(a, b: int, *others, d: float, e=10):
    """Here is my docstring"""
    return str(locals())

if __name__ == "__main__":
    #result = autoargs.autorun(main)
    result = autoargs.autorun(example)
    print(result)
