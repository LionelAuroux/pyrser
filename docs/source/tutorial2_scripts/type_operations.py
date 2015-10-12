from pyrser.type_system import *
from pyrser.passes.to_yml import *
scope = Scope(sig=[Fun('f', 'void', ['int']), Fun('f', 'int', ['int', 'double', 'char']), Fun('f', 'double', ['int', 'juju'])])
scope |= Scope(sig=[Fun('f', 'double', ['char', 'double', 'double'])])

t1 = Type('int')
t2 = Type('double')
p11 = Val('14', 'int')
p12 = Val('14', 'double')
p21 = Var('b', 'int')
p22 = Var('b', 'double')
p31 = Var('c', 'int')
p32 = Var('c', 'double')
p33 = Var('c', 'char')
a = Scope(sig=[p11, p12])
scope.update([t1, t2, p11, p12, p21, p22, p31, p32, p33])
print(str(scope))

b = scope.get_by_symbol_name('b')
print(str(b))
c = scope.get_by_symbol_name('c')

(fun, param) = scope.get_by_symbol_name('f').get_by_params([a, b, c])
print(str(fun))
print(str(param))

nia = scope.get_by_symbol_name('f')
print("NIA:" + str(nia))
print("A:" + str(a))

(f, p) = nia.get_by_params([a, b, c])
print("END:" + str(f))
