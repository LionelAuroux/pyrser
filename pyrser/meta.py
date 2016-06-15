#: Some meta prog stuff
import functools
import inspect
import collections
import copy


def enum(*sequential, **named):
    """
    Build an enum statement
    """
    #: build enums from parameter
    enums = dict(zip(sequential, range(len(sequential))), **named)
    enums['map'] = copy.copy(enums)
    #: build reverse mapping
    enums['rmap'] = {}
    for key, value in enums.items():
        if type(value) is int:
            enums['rmap'][value] = key
    return type('Enum', (), enums)


#From PEP 362: http://www.python.org/dev/peps/pep-0362/
def checktypes(func):
    """Decorator to verify arguments and return types."""
    sig = inspect.signature(func)

    types = {}
    for param in sig.parameters.values():
        # Iterate through function's parameters and build the list of
        # arguments types
        param_type = param.annotation
        if param_type is param.empty or not inspect.isclass(param_type):
            # Missing annotation or not a type, skip it
            continue

        types[param.name] = param_type

        # If the argument has a type specified, let's check that its
        # default value (if present) conforms with the type.
        if (param.default is not param.empty and
                not isinstance(param.default, param_type)):
            raise ValueError(
                "{func}: wrong type of a default value for {arg!r}".format(
                    func=func.__qualname__, arg=param.name)
            )

    def check_type(sig, arg_name, arg_type, arg_value):
        # Internal function that encapsulates arguments type checking
        if not isinstance(arg_value, arg_type):
            raise ValueError("{func}: wrong type of {arg!r} argument, "
                             "{exp!r} expected, got {got!r}".
                             format(func=func.__qualname__, arg=arg_name,
                                    exp=arg_type.__name__,
                                    got=type(arg_value).__name__))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Let's bind the arguments
        ba = sig.bind(*args, **kwargs)
        for arg_name, arg in ba.arguments.items():
            # And iterate through the bound arguments
            try:
                type_ = types[arg_name]
            except KeyError:
                continue
            else:
                # OK, we have a type for the argument, lets get the
                # corresponding parameter description from the signature object
                param = sig.parameters[arg_name]
                if param.kind == param.VAR_POSITIONAL:
                    # If this parameter is a variable-argument parameter,
                    # then we need to check each of its values
                    for value in arg:
                        check_type(sig, arg_name, type_, value)
                elif param.kind == param.VAR_KEYWORD:
                    # If this parameter is a variable-keyword-argument
                    # parameter:
                    for subname, value in arg.items():
                        check_type(sig, arg_name + ':' + subname, type_, value)
                else:
                    # And, finally, if this parameter a regular one:
                    check_type(sig, arg_name, type_, arg)

        result = func(*ba.args, **ba.kwargs)

        # The last bit - let's check that the result is correct
        return_type = sig.return_annotation
        if (return_type is not sig.empty and
                isinstance(return_type, type) and
                not isinstance(result, return_type)):

            raise ValueError(
                '{func}: wrong return type, {exp} expected, got {got}'.format(
                    func=func.__qualname__, exp=return_type.__name__,
                    got=type(result).__name__)
            )
        return result

    return wrapper


# TODO: could be better in a tool module?
#: Addtototo
def set_one(chainmap, thing_name, callobject):
    """ Add a mapping with key thing_name for callobject in chainmap with
        namespace handling.
    """
    namespaces = reversed(thing_name.split("."))
    lstname = []
    for name in namespaces:
        lstname.insert(0, name)
        strname = '.'.join(lstname)
        chainmap[strname] = callobject


def _get_base_class(cls):
    base = cls
    while base.__bases__[0] is not object:
        base = base.__bases__[0]
    return base


def add_method(cls):
    """Attach a method to a class."""
    def wrapper(f):
        #if hasattr(cls, f.__name__):
        #    raise AttributeError("{} already has a '{}' attribute".format(
        #        cls.__name__, f.__name__))
        setattr(cls, f.__name__, f)
        return f
    return wrapper


def hook(cls, hookname=None, erase=False):
    """Attach a method to a parsing class and register it as a parser hook.

       The method is registered with its name unless hookname is provided.
    """
    if not hasattr(cls, '_hooks'):
        raise TypeError(
            "%s didn't seems to be a BasicParser subsclasse" % cls.__name__)
    class_hook_list = cls._hooks
    class_rule_list = cls._rules

    def wrapper(f):
        nonlocal hookname
        add_method(cls)(f)
        if hookname is None:
            hookname = f.__name__
        if not erase and (hookname in class_hook_list or hookname in class_rule_list):
            raise TypeError("%s is already define has rule or hook" % hookname)
        if '.' not in hookname:
            hookname = '.'.join([cls.__module__, cls.__name__, hookname])
        set_one(class_hook_list, hookname, f)
        return f
    return wrapper


def rule(cls, rulename=None, erase=False):
    """Attach a method to a parsing class and register it as a parser rule.

       The method is registered with its name unless rulename is provided.
    """
    if not hasattr(cls, '_rules'):
        raise TypeError(
            "%s didn't seems to be a BasicParser subsclasse" % cls.__name__)
    class_hook_list = cls._hooks
    class_rule_list = cls._rules

    def wrapper(f):
        nonlocal rulename
        add_method(cls)(f)
        if rulename is None:
            rulename = f.__name__
        if not erase and (rulename in class_hook_list or rulename in class_rule_list):
            raise TypeError("%s is already define has rule or hook" % rulename)
        if '.' not in rulename:
            rulename = cls.__module__ + '.' + cls.__name__ + '.' + rulename
        set_one(class_rule_list, rulename, f)
        return f
    return wrapper


# module variable for DirectiveWrapper registering
_directives = collections.ChainMap()


def directive(directname=None):
    """Attach a class to a parsing class and register it as a parser directive.

        The class is registered with its name unless directname is provided.
    """
    global _directives
    class_dir_list = _directives

    def wrapper(f):
        nonlocal directname
        if directname is None:
            directname = f.__name__
        f.ns_name = directname
        set_one(class_dir_list, directname, f)
        return f
    return wrapper


# module variable for FunctorDecorator registration
_decorators = collections.ChainMap()


def decorator(directname=None):
    """
        Attach a class to a parsing decorator and register it to the global
        decorator list.
        The class is registered with its name unless directname is provided
    """
    global _decorators
    class_deco_list = _decorators

    def wrapper(f):
        nonlocal directname
        if directname is None:
            directname = f.__name__
        f.ns_name = directname
        set_one(class_deco_list, directname, f)

    return wrapper
