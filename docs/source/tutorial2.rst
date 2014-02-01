Tutorial II: Handling Type Checking (part 1):
=============================================

Parsing files is usefull, but you quickly need to do some type checking on your input to do some advanced DSL.
To handle this problem, the package ``pyrser.type_checking`` provide what you need.

1- Type semantics
-----------------

We provide some classes to describe types.

:class:`pyrser.type_checking.Symbol`: A Symbol represent a thing in your language.

:class:`pyrser.type_checking.Signature`: A Signature represent ``functions`` or ``variables`` in your language.

:class:`pyrser.type_checking.Set`: A Set represent a scope or a type (ADT).

Basically you could use the package like this::

        from pyrser.type_checking import *

        var = Signature('var1', 'int')
        f1 = Signature('fun1', 'int', '')
        f2 = Signature('fun2', 'int', 'int')
        f3 = Signature('fun3', 'int', 'int', 'double')
        tenv = Set(None, [var, f1, f2, f3])
        print(str(tenv))

This produce the following output::

    scope :
        fun fun1 : () -> int
        fun fun2 : (int) -> int
        fun fun3 : (int, double) -> int
        var var1 : int

So it's just a scope with few functions in it and a variable ``var1``.
Basically this kind of unamed scope could represent your global scope in your language.
But you could decide that this scope have a name. So::
    
    tenv.set_name('namespace1')
    print(str(tenv))

produce::

    scope namespace1 :
        fun namespace1.fun1 : () -> int
        fun namespace1.fun2 : (int) -> int
        fun namespace1.fun3 : (int, double) -> int
        var namespace1.var1 : int

Now your functions and vars are automatically decorated to be part of the namespace.
You could inspect the internal names used by your symbols::

    print(repr(tenv.keys()))

You get all internal names of your signatures::

    dict_keys(['namespace1_fun3_int_double_int', 'namespace1_fun2_int_int', 'namespace1_var1_int', 'namespace1_fun1__int'])

See: ``TODO TUTO OVERLOAD OF Symbol`` to understand how to change the ``decoration`` algorithm.

2- Type operations
------------------

With the previous classes, you got the basic abstraction for implements a name-based type system with functions/variables overloads.

In fact, the class :class:`pyrser.type_checking.Set` provide what you need for basic type operations.

Take a classical scope with few overloads of a function ``f``::

    scope = RawSet(Signature('f', 'void', 'int'), Signature('f', 'int', 'int', 'double', 'char'), Signature('f', 'double', 'int', 'juju'))
    scope |= RawSet(Signature('f', 'double', 'char', 'double', 'double'))

Add some locals variables (with possible overloads)::

    p11 = Signature('a', 'int')
    p12 = Signature('a', 'double')
    p21 = Signature('b', 'int')
    p22 = Signature('b', 'double')
    p31 = Signature('c', 'int')
    p32 = Signature('c', 'double')
    p33 = Signature('c', 'char')
    scope.update([p11, p12, p21, p22, p31, p32, p33])
    print(str(scope))

We get this setting::

    scope :
        var a : double
        var a : int
        var b : double
        var b : int
        var c : char
        var c : double
        var c : int
        fun f : (char, double, double) -> double
        fun f : (int, double, char) -> int
        fun f : (int, juju) -> double
        fun f : (int) -> void

We could easily infer what is the type of f,a,b,c in the sentence ``f(a, b, c)``.

First, we need to get all possible signature for ``a`` ::

    a = scope.get_by_symbol_name('a')
    print(str(a))

We get::

    scope :
        var a : double
        var a : int

We do the same for ``b`` and ``c``. After that, we choose only functions called f, with these sets of parameters::

    (fun, param) = scope.get_by_symbol_name('f').get_by_params(a, b, c)
    print(str(fun))

And we only got::

    scope :
        fun f : (int, double, char) -> int

In fact, ``get_by_symbol_name`` return also the set of parameters that must be used for these overloads::

    scope :
        var a : int
        var b : double
        var c : char

Here, we got a unique overload so the type checking completely resolved.

See: ``TODO TUTO ambiguity`` to understand how to understand multiple results.
