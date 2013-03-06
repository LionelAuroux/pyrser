# Copyright (C) 2013 Lionel Auroux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

# forward decl
class ParserBase:
    pass
### ADD A hook in a parserBase child class
def     hook(cls, txt=None):
    rootparser = _get_base_class(cls)
    if not hasattr(rootparser, 'class_hook_list'):
        setattr(rootparser, 'class_hook_list', {})
    def _wrapper(f):
        if hasattr(cls, f.__name__):
            raise Exception("Already have the " + f.__name__ + " method")
        setattr(cls, f.__name__, f)
        bindname = txt
        if bindname == None:
            bindname = f.__name__
        rootparser.class_hook_list[bindname] = f
        def _wrapped(*args, **kv):
            print("BIND!!!: <%s>" % globals())
            return f(*args, **kv)
        return wraps(f)(_wrapped)
    return _wrapper

### ADD A rule in a parserBase child class
def     rule(cls, txt=None):
    rootparser = _get_base_class(cls)
    # the class_rule_list is unique in ParserBase
    if not hasattr(rootparser, 'class_rule_list'):
        setattr(rootparser, 'class_rule_list', {})
    def _wrapper(f):
        if hasattr(cls, f.__name__):
            raise Exception("Already have the " + f.__name__ + " method")
        setattr(cls, f.__name__, f)
        bindname = txt
        if bindname == None:
            bindname = f.__name__
        rootparser.class_rule_list[bindname] = f
        def _wrapped(*args, **kv):
            return f(*args, **kv)
        return wraps(f)(_wrapped)
    return _wrapper
