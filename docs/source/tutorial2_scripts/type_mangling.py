from pyrser.type_system import *

class MySymbol(Symbol):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def show_name(self):
        return '.'.join(self.get_scope_names()) + '.' + self.name

    def internal_name(self):
        return '_'.join(self.get_scope_names()) + '.' + self.name


class MyFun(MySymbol, Fun):

    def __init__(self, *args, **kwargs):
        MySymbol.__init__(self, *args, **kwargs)
        Fun.__init__(self, *args, **kwargs)

    def show_name(self):
        paramstr = ''
        if self.tparams is not None:
            paramstr = ', '.join(self.tparams)
        return super().show_name() + '(' + paramstr + ')'


class MyVar(MySymbol, Var):

    def __init__(self, *args, **kwargs):
        MySymbol.__init__(self, *args, **kwargs)
        Var.__init__(self, *args, **kwargs)


t1 = Type('int')
t2 = Type('char')
t3 = Type('double')
v1 = MyVar('G', 'int')
v2 = MyFun('G', 'int')
val = Scope(sig=[v1, v2])
f1 = MyFun('fun1', 'int', [])
f2 = MyFun('fun2', 'int', ['char'])
f3 = MyFun('fun3', 'int', ['int', 'double'])
scope = Scope(sig=[t1, t2, t3, val, f1, f2, f3])
print(str(scope))

print(repr(scope))
