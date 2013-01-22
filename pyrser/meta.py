#
# Some meta prog stuff

from functools import wraps

### CHECK PROTO FUNCTION
# No argument
def strict(f):
        @wraps(f)
        def _wrapper(*args, **kwds):
                # list of param in co_varnames
                pidx = 0
                for arg in f.__code__.co_varnames:
                    # type hint in annotations
                    if arg in f.__annotations__:
                        typeofarg = f.__annotations__[arg]
                        if typeofarg is type and not isinstance(args[pidx], typeofarg):
                            raise Exception("wrong type in param %s pos %d : %s expected %s" % (arg, pidx, type(args[pidx]), f.__annotations__[arg]))
                    pidx += 1
                res = f(*args, **kwds)
                if not isinstance(res, f.__annotations__["return"]):
                    raise Exception("wrong type in return : %s expected %s" % (type(res), f.__annotations__[arg]))
                return res
        return _wrapper

### ADD Method to class AS PARTIAL CLASS
# one argument
def add_method(cClass):
    def _wrapper(f):
        # add the method name into the class
        setattr(cClass, f.__name__, f)
        def _wrapped(self, *args, **kwds):
            # call the method
            return f(self, *args, **kwds)
        return wraps(f)(_wrapped)
    return _wrapper
