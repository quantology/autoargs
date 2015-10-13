import shlex
import collections
def pythonic_parse(argv):
    if isinstance(argv, str):
        argv = shlex.split(argv)
    in_kws = False
    args = []
    kwargs = collections.OrderedDict()
    kwname = None
    for symbol in argv:
        if not in_kws:
            if symbol.startswith("-"):
                in_kws = True
            else:
                args.append(symbol)
        if in_kws:
            if kwname is not None:
                if symbol.startswith("-"):
                    kwargs[kwname] = True
                    kwname = None
                else:
                    kwargs[kwname] = symbol
                    kwname = None
                    continue
            if symbol.startswith("--"):
                if "=" in symbol:
                    kwname, val = symbol[2:].split("=", 1)
                    kwargs[kwname] = val
                    kwname = None
                else:
                    kwname = symbol[2:]
            elif symbol.startswith("-"):
                if len(symbol) > 2:
                    kwargs[symbol[1]] = symbol[2:]
                else:
                    kwname = symbol[1]
            else:
                raise ValueError("expected kwarg symbol, got %s" % symbol)
    if kwname is not None:
        kwargs[kwname] = True
    return args, kwargs
