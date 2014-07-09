Tutorial II: Handling Type System (part 1):
=============================================

Parsing files are useful, but we quickly need to do some type checking on our input to do some advanced DSL.
To handle this problem, the package ``pyrser.type_system`` provide what we need.

1- Type semantics
-----------------

We provide some classes to describe types.

:class:`pyrser.type_system.Symbol`: A Symbol represents a thing in our
language.

:class:`pyrser.type_system.Signature`: A Signature is an abstract type common
to ``Val``, ``Var`` and ``Fun``. It is the common denominator of the typing
system and provides the capability to get a string representation of a symbol.

:class:`pyrser.type_system.Val`: A Val represents a litteral value in our
language.

:class:`pyrser.type_system.Var`: A Var represents a named variable in our
language.

:class:`pyrser.type_system.Fun`: A Val represents a named function in our
language.

:class:`pyrser.type_system.Scope`: A Scope represents a scope or a type (ADT
or Abstract Data Type).

Basically we could use the package like this:

.. include:: tutorial2_scripts/minimal_scope.py
    :code: python
    :end-line: 10

And produce the following output:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/minimal_scope.py' 0,7

We're actually generating the signatures of one variable and three functions and
add them to an unnamed :py:class:`pyerser.type_system.Scope`, thus creating an
anonymous scope that could be our language's global scope. This is the reason
why we instantiate the :class:`pyrser.type_system.Scope` object using the
keyword ``sig`` (also second positionnal argument): by not giving a first
parameter which is an identifier naming the scope, we anonymize it.  If we
wanted to name it, we could have created it as follows:

.. include:: tutorial2_scripts/minimal_scope.py
    :code: python
    :start-line: 10
    :end-line: 12

Or, after creating the object, we can attribute the proper name:

.. include:: tutorial2_scripts/minimal_scope.py
    :code: python
    :start-line: 12
    :end-line: 15

that would produce the output:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/minimal_scope.py' 8,15

Now our functions and vars are automatically decorated to be part of the
namespace. We could inspect the internal names used by our symbols:

.. include:: tutorial2_scripts/minimal_scope.py
    :code: python
    :start-line: 16
    :end-line: 17

We get all internal names of our signatures:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/minimal_scope.py' 16,17

2- Type operations
------------------

With the previous classes, we got the basic abstraction to implement a name-based type system with functions/variables overloads.

In fact, the class :class:`pyrser.type_system.Scope` provides what we need for basic type operations.

Let's take a classical scope with few overloads of a function ``f``:

.. include:: tutorial2_scripts/type_operations.py
    :code: python
    :start-line: 2
    :end-line: 4

Then add some locals variables (with possible overloads):

.. include:: tutorial2_scripts/type_operations.py
    :code: python
    :start-line: 5
    :end-line: 17

We get this setting:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/type_operations.py' 0,16

We could easily infer what is the type of f,a,b,c in the sentence
``f(a, b, c)``.  In order to do this, we must first retrieve all the possible
signatures for each parameter.  Then, we need to retrieve all possible
signatures for the given function and filter them with the set of signatures
for each parameter, leaving only the plausible overloads for us to check.

Since ``a`` is already at hands (a literal value should always be represented
by a scope containing all the possible type overloads), we first need to get
all possible signature for ``b``:

.. include:: tutorial2_scripts/type_operations.py
    :code: python
    :start-line: 18
    :end-line: 20

We get:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/type_operations.py' 17,27

As you may have understood,
:py:meth:`pyrser.type_system.Scope.get_symbol_by_name` returns a sub-set of
the Scope instance itself. Thus, we get another Scope, on which we can operate
further.

We do the same for ``c``. After that, we choose only functions called f, with
these sets of parameters:

.. include:: tutorial2_scripts/type_operations.py
    :code: python
    :start-line: 22
    :end-line: 24

And we only got:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/type_operations.py' 29,36

As we can see, some types (``int`` and ``double``) are resolved to a
:py:class:`pyrser.type_system.Type` , while ``char`` is left unresolved. This
is because no declaration exists for the type ``char`` within our scope.
Indeed, the type system tried to retrieve the types associated to the different
parameters of a resolved function.

On another note, :py:meth:`pyrser.type_system.Scope.get_by_symbol_name`
also returns the Scope containing the different sets of parameters that must be
used for each overload:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/type_operations.py' 38,39

Here, we got a unique overload so the type checking resolved the types to the
proper function.

3 - Type mangling
-----------------

Now that we know how to look for a signature within a scope, we may want to
have a bit more control about how the unique identifiers are generated for the
signatures. Indeed, the whole typing system is based on a few classes which
provide the unique identifiers. Modifying how those identifiers are generated
can allow us to enable or disable function overload for a toy language, for
instance.

Remember, in the first section of this tutorial, we had the following code:

.. include:: tutorial2_scripts/minimal_scope.py
    :code: python
    :end-line: 10

which displayed the signatures as a list:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/minimal_scope.py' 16,17

It is actually the Symbol class that controls how those unique signature
identifiers are generated. The :py:class:`pyrser.type_system.Symbol` class
actually looks like this:

.. literalinclude:: ../../pyrser/type_system/symbol.py
    :pyobject: Symbol.show_name

.. literalinclude:: ../../pyrser/type_system/symbol.py
    :pyobject: Symbol.internal_name

And the implementation of the :py:class:`pyrser.type_system.Fun` class is the
following:

.. literalinclude:: ../../pyrser/type_system/fun.py
    :pyobject: Fun.internal_name

If we follow properly how the ``internal_name`` method of the
:class:`pyrser.type_system.Fun` class works, we can see that the higher level
class (:class:`pyrser.type_system.Fun` in our case) can use internally it's
parent class's ``internal_name`` method. That part is actually up to the
implementor, as it could also define a wholly different mangling method.

In reality, three classes express the different typing concepts that enter into
account when trying to generate unique signature identifiers. Those are the
concepts of Value, Variable and Function, which classes are respectively the
classes Val, Var and Fun. So in order to re-define the mangling for your own
language, you may need to redefine up to four classes:
:class:`pyrser.type_system.Symbol`, :class:`pyrser.type_system.Val`,
:class:`pyrser.type_system.Var` and :class:`pyrser.type_system.Fun`.

Now, let us try to define a mangling fit for a language that would not
support any overloading for a given symbol, meaning that a variable could not
have the same name as a function:

.. include:: tutorial2_scripts/type_mangling.py
    :code: python
    :end-line: 37

Note that ``MyVar`` only re-uses ``MySymbol``'s ``show_name`` and
``internal_name`` methods. Thus, we can see that using the ``show_name`` (used
mostly when printing out an object for display purposes), we can differentiate
``MyFun`` from ``MyVar``, even though the ``internal_name`` is the same for
both classes. So now, the unique identifier being the same, the typing system
won't allow having more than one unique name registered, and thus prevents us
from registering both a variable and a function having the same namespaces and
name.

We can try out the following piece of code:

.. include:: tutorial2_scripts/type_mangling.py
    :code: python
    :start-line: 38

Which yields the following output, where we can see that the mangling was
handled by our code:

.. program-output:: python3 tutorial2_scripts/type_mangling.py


4 - Type resolution and disambiguation
--------------------------------------

In most languages, the typing system can encounter situations where the type is
not as obvious as a one on one match. Indeed, a lot of languages have to
resolve (either following a standard resolution model or yielding an error)
situations where multiples signatures match the one we are looking for. As we
just saw, since we can redefine the unique internal identifier generation for
the typing system's classes, depending on the method used, we could fall more
or leass easily in one of those situations.

For instance, let's assume that our mangling supports function overloads, like
the C++ language does. Then, let's assume the following symbols to have been
declared in a fictive language that we're trying to type-check:

.. include:: tutorial2_scripts/type_disambiguation.py
    :code: python
    :end-line: 12

As a pre-requisite, let us assume that a number litteral in our language can be
typed in multiple ways. For instance, a number litteral can be typed as a
character, an integer, or as a big number. Then, when some parsed code will
contain a litteral, the following set of
:class:`pyrser.type_system.Val` will be built:

.. include:: tutorial2_scripts/type_disambiguation.py
    :code: python
    :start-line: 12
    :end-line: 17

Now, we have a user input, where the written code is a function call to
``fun``, with a number litteral as a parameter, that we could translate to the
following typing code:

.. include:: tutorial2_scripts/type_disambiguation.py
    :code: python
    :start-line: 17
    :end-line: 20

Now, we display the following scope:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/type_disambiguation.py' 0,24

Here, since the overloads list contains more than one item, it may be easily
resolvable by using the get_by_params (returning a tuple of a scope and a list
of scopes) on the overloads :class:`pyrser.type_system.Scope`:

.. include:: tutorial2_scripts/type_disambiguation.py
    :code: python
    :start-line: 20
    :end-line: 23

Indeed, :py:meth:`pyrser.type_system.Scope.get_by_params` takes care of
matching the available signatures with the multiple sets for each parameter.
Now, if the ``fun`` scope contains more than one signature, it means that we
have an unresolved type.  That could mean a lot of differents things, but for
now, let's try to reduce this choice.

If we only got one signature in the resulting ``fun`` scope, then the typing
system would have validated the types of the input, and we could go on and fiddle
with the generation. Let us see what an unresolved func and param look like:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/type_disambiguation.py' 27,41

In this case, we can see that using the literal as parameter was not enough to
resolve the type of the function we want to use, but we can see a difference
between the two: the return type. So we can filter once again over the return
type:

.. include:: tutorial2_scripts/type_disambiguation.py
    :code: python
    :start-line: 25

and we then get the following output:

.. program-output:: python3 splice.py 'python3 tutorial2_scripts/type_disambiguation.py' 42,47

As we can see, by using this last filter, we could identify an unique function
signature matching our user input. Alas, in some cases, it's not as easy.
Indeed, in some languages you might have polymorphic types, that the Scope
class cannot resolve itself. It requires the help of another typing module: the
:py:mod:`pyrser.type_system.Inference.py`. Sometimes, even the inference
module cannot resolve something, and then we fall in the case of an error, that
will be up to us to notify to the user.

See ``Tuto III`` to dive deeper into the usage of pyrser, and see how to add
mechanisms for the typing system to have a more powerful resolver, adding Type
coercion, and using the Inference module.
