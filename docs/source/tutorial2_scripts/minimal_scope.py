from pyrser.type_system import *

t1 = Type('int')
t2 = Type('double')
var = Var('var1', 'int')
f1 = Fun('fun1', 'int', [])
f2 = Fun('fun2', 'int', ['char'])
f3 = Fun('fun3', 'int', ['int', 'double'])
scope = Scope(sig=[t1, t2, var, f1, f2, f3])
print(str(scope))

scope = Scope('namespace1', [t1, t2, var, f1, f2, f3])

scope.set_name('namespace1')
print(str(scope))

print(repr(scope))
