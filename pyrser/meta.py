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
