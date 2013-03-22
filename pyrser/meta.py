# Some meta prog stuff
import functools
import inspect


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
                func=func.__qualname__, arg=param.name))

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
                got=type(result).__name__))
        return result

    return wrapper


def _get_base_class(cls):
    base = cls
    while base.__bases__[0] is not object:
        base = base.__bases__[0]
    return base


def add_method(cls):
    """Attach a method to a class."""
    def wrapper(f):
        if hasattr(cls, f.__name__):
            raise AttributeError("{} already has a '{}' attribute".format(
                cls.__name__, f.__name__))
        setattr(cls, f.__name__, f)
        return f
    return wrapper


def hook(cls, hookname=None):
    """Attach a method to a class and register it as a parser hook.

       The method is registered with its name unless hookname is provided.
    """
    #TODO(bps): why share hooks with every parsers?
    rootparser = _get_base_class(cls)
    if not hasattr(rootparser, 'class_hook_list'):
        setattr(rootparser, 'class_hook_list', {})
    class_hook_list = rootparser.class_hook_list

    def wrapper(f):
        nonlocal hookname
        add_method(cls)(f)
        if hookname is None:
            hookname = f.__name__
        class_hook_list[hookname] = f
        return f
    return wrapper


def rule(cls, rulename=None):
    """Attach a method to a class and register it as a parser rule.

       The method is registered with its name unless rulename is provided.
    """
    #TODO(bps): why share rules with every parsers?
    rootparser = _get_base_class(cls)
    if not hasattr(rootparser, 'class_rule_list'):
        setattr(rootparser, 'class_rule_list', {})
    class_rule_list = rootparser.class_rule_list

    def wrapper(f):
        nonlocal rulename
        add_method(cls)(f)
        if rulename is None:
            rulename = f.__name__
        class_rule_list[rulename] = f
        return f
    return wrapper
