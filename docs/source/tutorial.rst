Tutorial I: A guided JSON parser:
=================================

The JSON spec here: http://json.org could be easily describe using pyrser.

1- python canevas
-----------------

To describe a file format you just need to write a class that inherits from ``pyrser.grammar.Grammar``::

    from pyrser import grammar

    class   JSON(grammar.Grammar):
        """Our future JSON parser"""
        pass

This empty class is just a container for the BNF description of our file format.
Pyrser uses just 2 class variable to hold BNF:

    * grammar: a docstring containing the BNF description.
    * entry: the name of the rule to use as entry point.

2- translate BNF
----------------

In the JSON spec, the first rule ``object`` is describe as:
::
    
    object
        {}
        { members }

This describes a rule name ``object`` as ``members`` surrounded by braces. ``members`` could be empty.
That BNF could be literaly translate as::

    from pyrser import grammar

    class   JSON(grammar.Grammar):
        """Our JSON parser"""
        entry = "object"
        grammar = """
            object ::= 
                '{' '}'
                | '{' members '}'
            ;
        """

But Pyrser BNF syntax provides the repeater ``?`` that allows you to describe ``object`` in a more concise way.
::

    grammar = """ 
        object ::= '{' members? '}'
        ;
    """

Using :doc:`dsl`, we translate completly the grammar.

3- BNF of list
----------------

In the JSON spec, a common pattern is used to describe list of items. example:
::
    
    members
        pair
        pair , members

    elements
        value
        value , elements

This kind of parser uses right recursivity to create list of item. Pyrser parsing engine uses LL(k) mechanism.
It's better to use repeater ``+`` or ``*`` to describe the list.

4- Basic JSON Parser
--------------------

With these advices, we could translate all the BNF::

    from pyrser import grammar

    class   JSON(grammar.Grammar):
        """Our JSON parser"""
        entry = "object"
        grammar = """
            object ::= 
                '{' members? '}'
            ;

            members ::= pair [',' pair]*
            ;

            pair ::= string ':' value
            ;

            value ::= 
                string
                | number
                | object
                | array
                | "true"
                | "false"
                | "null"
            ;

            array ::=
                '[' elements? ']'
            ;

            elements ::=  value [',' value]*
            ;

            number ::= @ignore("null") [int frac? exp?]
            ;

            int ::= '-'? 
                [
                    digit1_9s
                    | digit
                ]
            ;

            frac ::= '.' digits
            ;

            exp ::= e digits
            ;

            digit ::= '0'..'9'
            ;

            digit1_9 ::= '1'..'9'
            ;

            digits ::= digit+
            ;

            digit1_9s ::= digit1_9 digits
            ;

            e ::= ['e'|'E'] ['+'|'-']?
            ;
        """


note 1: We could notice the use of ``@ignore("null")`` in the rule ``number``.
This ``directive`` allow you to change ``ignore convention``.
See :doc:`directives` for more informations about directives.

note 2: We don't provide the ``string`` rule because this rule is a default rule provide by inheritance from
the grammar ``Grammar``.

5- Constructing an AST
----------------------

The aim of parsing is to translate a textual representation of information into data structures representation.
Here we need to translate JSON into python objects.
To do this, we want to fetch data during the parsing process and create objects on the fly by calling some
python chunks of code.

Pyrser provides to us two mechanisms:

    * hooks for event handling
    * nodes for data handling

Let's focus on the ``number`` rule. We want to capture the number and convert it in float.

nodes
~~~~~

To capture the result of a rule just ``suffix`` it by ':' and the name of the node::

    """
    ...
        number ::= @ignore("null") [int frac? exp?]:n
        ;
    ...
    """

hooks
~~~~~

To do something on ``n`` just send it thru a hook named ``is_num`` to some python code.
Just call a hook after reading string::

    """
    ...
        number ::= @ignore("null") [int frac? exp?]:n #is_num(n)
        ;
    ...
    """

By default ``is_num`` is an unknown hook. Let's declare it with the following syntax::

    from pyrser import meta

    @meta.hook(JSON)
    def is_num(self, arg):
        print(arg.value)
        return True

note: A hook is just a function with a special decorator. The function took at least one parameter ``self``.
This is the parser instance. ``arg`` is here the capturing node.
With the attribute ``value``, we could fetch the captured text (parsed by ``[int frac? exp?]``).

note: A hook must return True if the parsing must continue. You could stop parsing by returning False.
This return provoking a parse error.

return values
~~~~~~~~~~~~~

Well, we could capture data from the input and do something on it. But how returned to the ``caller`` our results?
For this, we must use the special node named ``_``. Indeed, ``_`` is bound to the rule resulting node.
So, we must patch our ``number`` rule and the ``is_num`` hook like this::

    ...
    """
        ...
            number ::= @ignore("null") [int frac? exp?]:n #is_num(_, n)
        ;
        ...
    """
    ...

``_`` is received by the ``is_num`` function as parameter. You can't modify it directly.
To return something with it you must create an arbitrary attribute (but the name ``value`` already used) to carry the output::

    from pyrser import meta

    @meta.hook(JSON)
    def is_num(self, ast, arg):
        ast.node = float(arg.value)
        return True

note: The ``float`` constructor interpret directly ``arg.value`` like ``1.0`` or ``-2e+2`` to create a float object.

We could process like this for all trivial values.

handling arrays
~~~~~~~~~~~~~~~

Let's focus on a more complex case, the ``array`` rule::

            array ::=
                '[' elements? ']'
            ;

            elements ::=  value [',' value]*
            ;

These kind of rules are not really optimized for a LL(k) parser. It's better to have in the same rule
the resulting node (``array``) and the list of items (list of ``value``). We could merge this two rules into
one::

        array ::=
            '[' [value [',' value] *]? ']'
        ;

In this form, it's easier to identify where to put a hook to create a python array, and where to put a hook
to add item into this array::

        array ::=
            '[' #is_array(_) [value:v #add_item(_, v) [',' value:v #add_item(_, v) ] *]? ']'
        ;

With the following hooks::

    @meta.hook(JSON)
    def is_array(self, ast):
        ast.node = []
        return True

    @meta.hook(JSON)
    def add_item(self, ast, item):
        ast.node.append(item.node)
        return True

We could proceed in the same way for ``object``.

6- Final JSON parser
----------------------



See :doc:`hooks` for more informations about hooks.

See :doc:`node` for more informations about nodes.
