from pyrser.type_system import *

c = Type('char')
i = Type('int')
d = Type('double')
b = Type('bignum')
f1 = Fun('fun', 'bignum', ['char'])
f2 = Fun('fun', 'int',  ['char'])
f3 = Fun('fun', 'char', ['int', 'double'])
f4 = Fun('fun', 'bignum',  ['double'])
scope = Scope('foo', [c, i, d, b, f1, f2, f3, f4])

l1 = Val(13, 'char')
l2 = Val(13, 'int')
l3 = Val(13, 'bignum')
literal = Scope(sig=[l1, l2, l3])

overloads = scope.get_by_symbol_name('fun')
print(str(overloads))

(fun, param) = overloads.get_by_params([literal])
print(str(fun))
print(str(param))

byret = fun.get_by_return_type('bignum')
print(str(byret))
