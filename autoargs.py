import argparse
import sys
import imp
import inspect
import collections

def autoparser_fn(fn, name=None, base_parser=None):
    name = fn.__name__ if name is None else name
    if base_parser is None:
        parser = argparse.ArgumentParser(prog=name, description=fn.__doc__)
    else:
        parser = base_parser.add_subparsers(title=name, help=fn.__doc__)
    sig = inspect.signature(fn)
    positional_kinds = {inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.VAR_POSITIONAL}
    keyword_kinds = {inspect.Parameter.KEYWORD_ONLY,
                     inspect.Parameter.POSITIONAL_OR_KEYWORD}
    for name, param in sig.parameters.items():
        assert not name.startswith("-")
        kwargs = {}
        if (param.kind in positional_kinds and 
            param.default is inspect._empty):
            options = (name,)
        elif param.kind in keyword_kinds:
            prefix = "-" if len(name) == 1 else "--"
            options = ("%s%s" % (prefix, name),)
            if param.default is inspect._empty:
                kwargs['required'] = True
        if param.kind == param.VAR_POSITIONAL:
            kwargs['nargs'] = "*"
        elif param.kind == param.VAR_KEYWORD:
            raise NotImplementedError("later")
        if param.default is not inspect._empty:
            kwargs['default'] = param.default
        if param.annotation is not inspect._empty:
            if isinstance(param.annotation, collections.Callable):
                kwargs['type'] = param.annotation
            elif isinstance(param.annotation, str):
                kwargs['help'] = param.annotation
        parser.add_argument(*options, **kwargs)
    return parser

def autoparser_mod(module, name=None):
    pass

def autoparse(obj, name=None, args=None):
    if isinstance(obj, collections.Callable):
        parser = autoparser_fn(obj, name=name)
        return parser.parse_args(args)
    else:
        raise NotImplementedError("haven't finished modules yet...")

def autorun(fn, name=None, args=None): # todo: modules?
    parsed = autoparse(fn)
    kwargs = vars(parsed)
    args = ()
    sig = inspect.signature(fn)
    for name, param in sig.parameters.items():
        if name not in kwargs: continue
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            args += (kwargs.pop(name),)
        elif param.kind == param.VAR_POSITIONAL:
            args += tuple(kwargs.pop(name))
    return fn(*args, **kwargs)

def automodule():
    top_parser = argparse.ArgumentParser(prog="autoargs", description="")
    top_parser.add_argument("script", help="<path to script>[:fn_name]")
    top_args, other_args = top_parser.parse_known_args()
    script = top_args.script
    if ":" in script:
        script, fn_name = script.rsplit(":", 1)
    else:
        fn_name = "main"
    module = imp.load_source(script, script)
