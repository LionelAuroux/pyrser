Tutorial III: Handling Type System (part 2) Toy Language For Typing:
=======================================================================

1 - Using inference with a Toy Language
---------------------------------------

To go further with type checking, we need a little toy language to implement
different kinds of typing strategy.

With this objective, we will target the implementation of a light type system
for our toy language. This type system should have behaviors close to most
scripting languages and support operations such as adding any value to a string
value:

.. literalinclude:: tutorial3_scripts/transtyping.tl4t

would yield::

    toto42

Thus, in our language that we'll call ``TL4T`` (Toy Language For Typing), we
will need two types of statements:
    * Variable declaration (with optional affectation)
    * Expressions to manipulate our variables (and using builtin functions)


Here is the definition of our ``TL4T`` language:

.. program-output:: python3 splice.py 'cat ../../tests/bnf/tl4t.bnf' 0,12 18,24 63,244 246,247 252,277 279,-1

Within this BNF, we defined a few hooks:
    * ``info`` to get location informations from the source file (line and
column)
    * ``new_*`` for each AST Node to be built.

For instance, the ``new_declvar`` hook is defined as:

.. literalinclude:: ../../tests/grammar/tl4t.py
    :pyobject: new_declvar

This way we can declare a variable with a type, and the ``new_declvar`` hook
builds an AST Node of type ``DeclVar``. For our code sample, this will thus
create a node for the variable ``s``, typed as a ``string``.

After this, we just use the affectation expression which will use the computed
result of the expression ``"toto" + 42``. In most languages, every binary
operator is actually a function taking two similarly typed parameters, and
yielding a result of the same type. In our case, we have already declared a
binary operator called ``+``::

    fun + : (string, string) -> string

With only this operator defined, we would get the following error::

    can't match overloads with parameters for function '+': details:
    overloads:
        fun + : (string, string) -> string
    parameters:
     - param[0] type string
     - param[1] type int | char

This means that our literal ``42``, as shown in the second tutorial of this
series, is typed as either an ``int`` or a ``char`` (the pipe in the output
shows the alternative types available). We can see in this error message that
the type or our literal does not allow us to resolve the ambiguity.

Pyrser offers the facilities to define subtyping relations, but to be more
generic, we could define some implicit conversion rules between types.
Indeed, Pyrser offers another API: :class:`pyrser.type_system.Translator`.

To implement a ``Translator``, we have to use the method ``addTranslator`` of
the ``Scope`` as follows, assuming ``glob`` is our global scope::

    f = Fun('tostr', 'string', ['int'])
    glob.add(f)
    n = Notification(Severity.INFO, 'implicit conversion string -> int')
    glob.addTranslator(Translator(f, n))

As we can see, the implicit translating function ``f`` is added into the
scope, and will be used for any attempt to resolve type ambiguities. For
example, we would then retrieve the following evalctx after calling the type
system to get the ``+`` operator::

    XXX TO BE REPLACED XXX
    evalctx:
        translator
        {
            int: {
                string
            }
        }
        int:
        string:

On another note, the evalctx contains information expliciting the fact that a
translator must be used before the ambiguity can be resolved.

Note that it is only the type informations that are used when resolving
ambiguities (using ``get_by_params``), but the actual ``tostr`` function is not
part of the final AST. We need to connect our typing semantic with the AST
built by our ``new_*`` hooks when parsing a ``TL4T`` sample. This is the aim
of the Inference module.

2 - Inference module
--------------------

The inference module offers multiple algorithms and strategies in order to add
type inference to a language. The advised way to use the Inference module is to
define our AST Nodes as children classes of the Inference classes.

The Inference class offers methods to infer:
    * block
    * special expressions
    * functions
    * identifiers
    * literals

To summarize, since the designer of the language is free to design the
language's AST, the Inference module cannot know in advance which method to
call on which AST Node. In order to address this, it uses a convention that
asks the AST Nodes to implement the method ``type_algos`` which returns a tuple
describing the functions to use on this very node.

In order to understand how it works, let's take a look at the ``TL4T``
implementation. For this, we will focus on the implementation of the
``Terminal``, ``Literal`` and ``Id`` AST Nodes which are derivations of the
``NodeInfo`` (which is the root of TL4T's AST Nodes and inherits from the
Inference Node):

.. literalinclude:: ../../tests/grammar/tl4t.py
    :pyobject: NodeInfo

.. literalinclude:: ../../tests/grammar/tl4t.py
    :pyobject: Terminal

.. literalinclude:: ../../tests/grammar/tl4t.py
    :pyobject: Literal

.. literalinclude:: ../../tests/grammar/tl4t.py
    :pyobject: Id

So, we can see that both ``Literal`` and ``Id`` do implement the ``type_algos``
method, which returns a tuple of three values. Those values are:
    * the method to use for inference (here we use the default one of the
Inference module, inherited from the Inference class)
    * the parameters to give to the inference method (packed within a tuple if
multiple arguments are required)
    * the optional feedback strategy

The multiple ``infer_*`` methods have each their own way of decomposing the
argument tuple, which means that as a language writer, we need to pay attention
to which inference method to return, and associate the proper parameters with
it. It is not mandatory to use a method from the Inference module, and we could
write our own inference methods with their own behavior.

To explain what is the feedback strategy, it is required to understand how the
inference works roughly. As a reminder, the inference uses two kinds of leaf
nodes as a basis: ``Literal`` and ``Id``. For simplicity we will call those
nodes the Inference leaves. The role of the leaves is to return their potential
types, which is a ``Scope`` containing one or more types. Then, the biggest
part of the Inference module's work is to resolve the types of the function
calls, by identifying the best match within all the possibilities. This is done
through the function call inference: the ``infer_fun`` method from the
:class:`pyrser.type_system.Inference` class.

It is important to understand that the function call inference is not about
names but about the whole call expression. A function call is composed of a
call expression and a list of parameters. For instance, here are a few
examples::

    f(1, 2, 3);
    tab[i](1, 2, 3);
    f(1, 2, 3)(4, 5, 6);

Here, the call expression is ``f`` in the first example; ``tab[i]`` in the
second example; ``f`` in the first part of the third example (with parameters
``(1, 2, 3)``) and finally ``f(1, 2, 3)`` in the second part of the third
example (with parameters ``(4, 5, 6)``).

Now that the notion of call expression has been clarified, we can get to the
resolution itself. The resolution is done in a few steps, in the following
order:
    1 - Collect types associated to the call expresion

    2 - Collect types of each parameters

    3 - Compute the intersection of the first two steps (using the ``Scope``'s
``get_by_params`` method)

    4 - Record overloads and decide if the inference can continue

    5 - Instantiate the polymorphic types resolved within the function call

    6 - Feedback resolved types from step 3 and 5

    7 - Collect the information at a global level

At the first and second steps, multiples choices could have been returned by
the inference leaves, which would mean that their types were left undecided.
The undecisiveness is lifted by the third and fifth steps, so we need to
propagate the resolved types in the different children nodes of the call
expression and parameters.

It is possible that at the fourth step, the type of the function could not be
uniquely resolved. Since this does not mean that the expression is invalid
with only the information at hand, we need to tell the higher level to resolve
this with the broader information it has access to. This is what feedback is.

Back to the feedback strategies, there is one feedback strategy per inference
method existing within the Inference class. The feedback strategy does not
require any additional parameter, since all the information it needs access to
is contained within the typing AST.


3 - Implicit type conversions
-----------------------------

To continue our first objective, we could plug all component together Parser, AST, Type semantics, Inference module.
As previously shown, we could explain to inference to use some function to one type to another but at this point the final AST wasn't modify.
To do so, we must write as customer of pyrser an Injector function and provide it to a scope to be used by inference system.
Injector functions must respect the following signature::

    def myInjectionFunction(old: Node, trans: Translator) -> Node

Our function receive the old AST node, and the Translator. We must build a function call AST node in our language dialect and return it. i.e.::

    
    def createFunWithTranslator(old: Node, trans: Translator) -> Node:
        f = trans.fun
        n = trans.notify
        return Expr(Id(f.name), [old])

Here ``Expr`` is just the AST node that represent all expressions as function calls.
Our function could be add to our global scope with the ``addTranslatorInjector`` function.
Finally, we write::

        test = TL4T()
        res = test.parse("""
            s = "toto" + 42;
        """)
        txt = res.to_tl4t()
        res.type_node = Scope(is_namespace=False)
        res.type_node.add(Type("string"))
        res.type_node.add(Type("int"))
        res.type_node.add(Var("s", "string"))
        res.type_node.add(Fun("=", "string", ["string", "string"]))
        res.type_node.add(Fun("+", "string", ["string", "string"]))
        f = Fun("tostr", "string", ["int"])
        res.type_node.add(f)
        n = Notification(
            Severity.WARNING,
            "implicit conversion of int to string"
        )
        res.type_node.addTranslator(Translator(f, n))
        res.type_node.addTranslatorInjector(createFunWithTranslator)
        res.infer_type(res.diagnostic)
        print(res.to_tl4t())

Will show us::

        s = "toto" + tostr(42);

Our AST is correctly modify by the Injector function.
Notice that we could control the severity of the notification from INFO to ERROR. That's an easy way to allow or to forbid things.
Let's modify ``Severity.WARNING`` by ``Severity.ERROR``::
        
        n = Notification(
            Severity.WARNING,
            "implicit conversion of int to string"
        )
        res.type_node.addTranslator(Translator(f, n))
        res.type_node.addTranslatorInjector(createFunWithTranslator)
        res.infer_type(res.diagnostic)
        if res.diagnostic.have_errors:
            print(res.diagnostic.get_content(with_locinfos=True))

Now we got an error in our Diagnostic object::

        -------------------------------------------------------------------------------
        error : implicit conversion of int to string
        from test.tl4t at line:2 col:26 :
                    s = "toto" + 42;
                                 ^

It's up to you to decide how you manage errors logged in the Diagnostic object.
