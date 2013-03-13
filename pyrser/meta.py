# Some meta prog stuff

from functools import wraps


### PRIVATE FUNC
def _get_base_class(cls):
    base = cls
    while True:
        newbase = base.__bases__[0]
        if len(newbase.__bases__) == 0:
            return base
        base = newbase


### CHECK PROTO FUNCTION
# No argument
def strict(f):
        @wraps(f)
        def _wrapper(*args, **kvargs):
                # list of param in co_varnames
                pidx = 0
                for arg in f.__code__.co_varnames:
                    # type hint in annotations
                    if arg in f.__annotations__:
                        typeofarg = f.__annotations__[arg]
                        if (typeofarg is type and
                                not isinstance(args[pidx], typeofarg)):
                            raise Exception(
                                "wrong type in param {} pos {} : {} expected "
                                "{}".format(arg, pidx, type(args[pidx]),
                                            f.__annotations__[arg]))
                    pidx += 1
                res = f(*args, **kvargs)
                if not isinstance(res, f.__annotations__["return"]):
                    raise Exception(
                        "wrong type in return : {} expected {}".format(
                            type(res), f.__annotations__[arg]))
                return res
        return _wrapper


### ADD Method to class AS PARTIAL CLASS
# one argument, the class
def add_method(cls):
    def _wrapper(f):
        # add the method name into the class
        if hasattr(cls, f.__name__):
            raise Exception("Already have the " + f.__name__ + " method")
        setattr(cls, f.__name__, f)

        def _wrapped(self, *args, **kvargs):
            # call the method
            return f(self, *args, **kvargs)
        return wraps(f)(_wrapped)
    return _wrapper


def hook(cls, txt=None):
    """Add a hook in a parserBase child class."""
    #TODO(bps): attach to parser directly and not to the father of all parsers
    rootparser = _get_base_class(cls)
    if not hasattr(rootparser, 'class_hook_list'):
        setattr(rootparser, 'class_hook_list', {})

    def _wrapper(f):
        if hasattr(cls, f.__name__):
            raise Exception("Already have the " + f.__name__ + " method")
        setattr(cls, f.__name__, f)
        bindname = txt
        if bindname is None:
            bindname = f.__name__
        rootparser.class_hook_list[bindname] = f

        def _wrapped(*args, **kv):
            print("BIND!!!: <%s>" % globals())
            return f(*args, **kv)
        return wraps(f)(_wrapped)
    return _wrapper


### ADD A rule in a parserBase child class
def rule(cls, txt=None):
    rootparser = _get_base_class(cls)
    # the class_rule_list is unique in ParserBase
    if not hasattr(rootparser, 'class_rule_list'):
        setattr(rootparser, 'class_rule_list', {})

    def _wrapper(f):
        if hasattr(cls, f.__name__):
            raise Exception("Already have the " + f.__name__ + " method")
        setattr(cls, f.__name__, f)
        bindname = txt
        if bindname is None:
            bindname = f.__name__
        rootparser.class_rule_list[bindname] = f

        def _wrapped(*args, **kv):
            return f(*args, **kv)
        return wraps(f)(_wrapped)
    return _wrapper
