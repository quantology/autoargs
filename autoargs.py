"""Pythonic utility for making commandline arguments far simpler.
Intended to become the argparse-killer.
Python 3 only."""

import argparse
import inspect
import collections
import shlex
import functools
import sys
import io
import os
import contextlib
import importlib
import importlib.util

__version__ = "0.0.1"
__all__ = ["autoparser", "autoparse", "autocall", "recursive_autocall", "autorun", "cmdable"]

POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD

POSITIONAL_KINDS = {POSITIONAL_ONLY,
                    POSITIONAL_OR_KEYWORD,
                    VAR_POSITIONAL}
KEYWORD_KINDS = {KEYWORD_ONLY,
                 POSITIONAL_OR_KEYWORD}

EMPTY = inspect._empty

def autoparser(func, name=None, base_parser=None):
    """Automatically creates a parser from a function.

    >>> def f(x, y, z="c"):
    ...     print(x, y, z)
    >>> parser = autoparser(f)
    >>> parser.parse_args(["--help"])
    Traceback (most recent call last):
    ...
    SystemExit: 0
    >>> parser.parse_args(["a", "b"])
    Namespace(x='a', y='b', z='c')
    >>> autoparser(f).parse_args(["a", "b", "-z", "d"])
    Namespace(x='a', y='b', z='d')
    """
    name = func.__name__ if name is None else name
    if base_parser is None:
        parser = argparse.ArgumentParser(prog=name, description=func.__doc__)
    else:
        subparsers = base_parser.add_subparsers(help=func.__doc__)
        parser = subparsers.add_parser(name, help=func.__doc__)
    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        assert not name.startswith("-")
        kwargs = {}
        if (param.kind in POSITIONAL_KINDS and
                param.default is EMPTY):
            options = (name,)
        else:
            assert param.kind in KEYWORD_KINDS
            prefix = "-" if len(name) == 1 else "--"
            options = ("%s%s" % (prefix, name),)
            kwargs['required'] = param.default is EMPTY
        if param.kind == param.VAR_POSITIONAL:
            kwargs['nargs'] = "*"
        elif param.kind == param.VAR_KEYWORD:
            raise NotImplementedError("later (this is complicated...)")
        if param.default is not EMPTY:
            kwargs['default'] = param.default
        if param.annotation is not EMPTY:
            if isinstance(param.annotation, collections.Callable):
                kwargs['type'] = param.annotation
                if hasattr(param.annotation, "__name__"):
                    kwargs['help'] = param.annotation.__name__
            elif isinstance(param.annotation, str):
                kwargs['help'] = param.annotation
            elif isinstance(param.annotation, collections.Iterable):
                kwargs['choices'] = tuple(param.annotation)
            elif isinstance(param.annotation, int):
                kwargs['nargs'] = param.annotation
        parser.add_argument(*options, **kwargs)
    return parser

# simple util
@contextlib.contextmanager
def supressed_stderr():
    "redirect stderr in a context"
    orig_stderr = sys.stderr
    sys.stderr = io.StringIO()
    yield orig_stderr
    sys.stderr = orig_stderr

def cmdargs_to_namespace(cmdargs, parser, *, partial=False):
    "convert command-line args (string or list of strings) into a parsed namespace"
    if isinstance(cmdargs, str):
        cmdargs = shlex.split(cmdargs)
    if partial:
        with supressed_stderr():
            nargs = len(cmdargs)
            for i in range(nargs+1):
                subargs, remaining = cmdargs[:nargs-i], cmdargs[nargs-i:]
                try:
                    return parser.parse_args(subargs), remaining
                except SystemExit:
                    if i == nargs:
                        raise
    else:
        return parser.parse_args(cmdargs)

def namespace_to_pyargs(func, namespace, *, default_to_arg=True):
    """convert a namespace (mapping or object with attributes)
    into applicable args and kwargs for a function

    >>> def f(x, y, z="c"):
    ...     print(x, y, z)
    >>> namespace_to_pyargs(f, {'x': 1, 'y': 2})
    Traceback (most recent call last):
    ...
    KeyError: 'z'
    >>> namespace_to_pyargs(f, {'x': 1, 'y': 2, 'z': 3})
    ((1, 2, 3), OrderedDict())
    """
    if not isinstance(namespace, collections.Mapping):
        namespace = vars(namespace)
    sig = inspect.signature(func)
    args = tuple()
    kwargs = collections.OrderedDict()
    args_finished = False
    for name, param in sig.parameters.items():
        if param.kind == VAR_POSITIONAL:
            assert not args_finished
            args += tuple(namespace[name])
            args_finished = True
        elif param.kind == POSITIONAL_ONLY:
            assert not args_finished
            args += (namespace[name],)
        elif (param.kind == POSITIONAL_OR_KEYWORD and
              not args_finished and default_to_arg):
            args += (namespace[name],)
        else:
            args_finished = True
            kwargs[name] = namespace[name]
    return args, kwargs

def autoparse(func, cmdargs, *, default_to_arg=True): # doctest: +IGNORE_EXCEPTION_DETAIL
    """Automatically creates a parser, applies it to command line arguments,
    and returns the relevant args and kwargs.

    >>> def f(x, y, z="c", *, prefix=''):
    ...     print(prefix, x, y, z)
    >>> autoparse(f, "-h")
    Traceback (most recent call last):
    ...
    SystemExit: 0
    >>> autoparse(f, ["a", "b"])
    (('a', 'b', 'c'), OrderedDict([('prefix', '')]))
    >>> autoparse(f, "a b -z d")
    (('a', 'b', 'd'), OrderedDict([('prefix', '')]))
    """
    parser = autoparser(func)
    namespace = cmdargs_to_namespace(cmdargs, parser)
    return namespace_to_pyargs(func, namespace, default_to_arg=default_to_arg)

def autocall(func, cmdargs, *, default_to_arg=True): # doctest: +IGNORE_EXCEPTION_DETAIL
    """Automatically creates a parser, applies it to command line arguments,
    and applies the parsed arguments to the function.

    >>> def f(x, y, z="c", *, prefix=''):
    ...     print(prefix, x, y, z)
    >>> autocall(f, "-h")
    Traceback (most recent call last):
    ...
    SystemExit: 0
    >>> autocall(f, ["a", "b"])
     a b c
    >>> autocall(f, "a b -z d")
     a b d
    """
    args, kwargs = autoparse(func, cmdargs, default_to_arg=default_to_arg)
    return func(*args, **kwargs)

def recursive_autocall(func, cmdargs, name=None, doc=None):
    if isinstance(cmdargs, str):
        cmdargs = shlex.split(cmdargs)
    base_parser = None
    while cmdargs or base_parser is None:
        assert isinstance(func, (collections.Callable, collections.Mapping))
        if not isinstance(func, collections.Callable) and isinstance(func, collections.Mapping):
            func = namespace_dispatcher(func, name=name, doc=doc)
        parser = autoparser(func, name=name, base_parser=base_parser)
        namespace, new_cmdargs = cmdargs_to_namespace(cmdargs, parser, partial=True)
        args, kwargs = namespace_to_pyargs(func, namespace)
        result = func(*args, **kwargs)
        func = result
        base_parser = parser
        used_args = cmdargs[:len(cmdargs) - len(new_cmdargs)]
        name = str(used_args[0]) if len(used_args) == 1 else str(used_args)
        cmdargs = new_cmdargs
    return result

def cmdable(func):
    """Wrapper function that adds a few autoarg methods as attributes to any function
    
    >>> @cmdable
    ... def f(x: int, y: int):
    ...     return x + y
    >>> f.pyargs("1 2")
    ((1, 2), OrderedDict())
    >>> f.cmd("1 2")
    3
    >>> f.recursive_cmd(["1", "2"])
    3
    """
    func.pyargs = functools.partial(autoparse, func)
    func.cmd = functools.partial(autocall, func)
    func.recursive_cmd = functools.partial(recursive_autocall, func)
    return func

def namespace_dispatcher(namespace, name, subset=None, doc=None):
    """
    if __name__ == "__main__":
        main = namespace_dispatcher(locals(), sys.argv[0], __all__, __doc__)
        recursive_autocall(main, sys.argv[1:])
    """
    if not isinstance(namespace, collections.Mapping):
        namespace = vars(namespace)
    if subset is None:
        valid_calls = [k for k, v in namespace.items()
                       if isinstance(v, collections.Callable)]
    else:
        valid_calls = subset
    def _dispatcher(selection: valid_calls):
        if selection in valid_calls:
            return namespace[selection]
    if name is not None:
        _dispatcher.__name__ = name
    _dispatcher.__doc__ = doc
    return _dispatcher

def script_dispatcher(path, name=None):
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(path):
        raise OSError("path does not exist", path)
    if name is None:
        base = os.path.basename(path) or os.path.basename(os.path.dirname(path))
        name, _ = os.path.splitext(base)
    assert sys.version_info >= (3, 3)
    if sys.version_info.minor >= 5:
        spec = importlib.util.spec_from_file_location(name, path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
    else:
        from importlib.machinery import SourceFileLoader
        loaded = SourceFileLoader(name, path).load_module()
    return namespace_dispatcher(loaded, loaded.__name__, loaded.__all__, loaded.__doc__)

def module_dispatcher(module_name):
    loaded = importlib.import_module(module_name)
    return namespace_dispatcher(loaded, loaded.__name__, loaded.__all__, loaded.__doc__)

def autorun(what, cmdargs):
    if isinstance(what, str):
        try:
            dispatcher = script_dispatcher(what)
        except OSError:
            dispatcher = module_dispatcher(what)
    elif isinstance(what, collections.Callable):
        dispatcher = what
    else:
        dispatcher = namespace_dispatcher(what, name=None)
    recursive_autocall(dispatcher, cmdargs)

if __name__ == "__main__":
    autorun(sys.argv[1], sys.argv[2:])
