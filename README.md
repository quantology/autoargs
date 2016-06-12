## autoargs is argparse made easy

Have you ever felt like using argparse pulled you out of your Pythonic comfort zone? Argparse lets you skip the boilerplate when making apis to the command line:

    >>> from autoargs import autocall, cmdable
    >>> def str_repeat(s: str, n: int):
    ...     print((s * n).strip())
    >>> autocall(str_repeat, ["args are easy!\n", "3"])
    args are easy!
    args are easy!
    args are easy!
    
    >>> @cmdable
    >>> def product(*args: float):
    ...     return functools.reduce(operator.mul, args, 1.0)
    >>> product.cmd(["5", "10", "0.5"])
    25.0
    
    >>> @cmdable
    >>> def aggregate(*args: float, op: {'sum', 'mul'}):
    ...     if op == "sum":
    ...         return sum(args)
    ...     elif op == "mul":
    ...         return product(*args)
    >>> aggregate.cmd(["--help"])
    usage: aggregate [-h] --op {mul,sum} [args [args ...]]
    
    positional arguments:
      args
    
    optional arguments:
      -h, --help      show this help message and exit
      --op {mul,sum}

    >>> aggregate.cmd("--op mul 1 2 3 4")
    24.0
    
Want to expose all of your modules functions to the command line, with nice parsers? That should be easy, right?

    if __name__ == "__main__":
        main = autoargs.namespace_dispatcher(locals(), sys.argv[0], __all__, __doc__)
        autoargs.recursive_autocall(main, sys.argv[1:])

And now, suddenly your module is exposed to the command line, and each of the functions in your `__all__` is exposed as a subparser.

Some things to note:
 - All args coming in from the command line are by default strings. If you want something else, annotate the arg with a function taking a string and returning the type you want.
 - var kwargs are currently not supported (if you have any ideas on what the expected behavior of those should be, please comment on the github)

### TODO:
 - finish documentation
   - especially on recursive autocall and dispatchers (it's really cool, but a bit arcane)
 - add more examples
 - better readme...
 - custom class for annotating args that lets you do more than one thing at once
