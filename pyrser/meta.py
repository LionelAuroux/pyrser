#
# Some meta prog stuff

from functools import wraps

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
                        if typeofarg is type and not isinstance(args[pidx], typeofarg):
                            raise Exception("wrong type in param %s pos %d : %s expected %s" % (arg, pidx, type(args[pidx]), f.__annotations__[arg]))
                    pidx += 1
                res = f(*args, **kvargs)
                if not isinstance(res, f.__annotations__["return"]):
                    raise Exception("wrong type in return : %s expected %s" % (type(res), f.__annotations__[arg]))
                return res
        return _wrapper

### ADD Method to class AS PARTIAL CLASS
# one argument, the class
def add_method(class_name):
    def _wrapper(f):
        # add the method name into the class
        setattr(class_name, f.__name__, f)
        def _wrapped(self, *args, **kvargs):
            # call the method
            return f(self, *args, **kvargs)
        return wraps(f)(_wrapped)
    return _wrapper

### SET Method as rule if the class is kind of ParserBase
# TODO: didn't work
# to get class name from self -> self.__class__.__name__
#def rule(rule_name):
#    def _wrapper(f):
#        def _wrapped(self, *args, **kvargs):
#            if self
#            return f(self, *args, **kvargs)
#        return wraps(f)(_wrapped)
#    return _wrapper
