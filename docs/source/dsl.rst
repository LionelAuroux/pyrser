Writing a BNF grammar
=====================

BNF Syntax
~~~~~~~~~~

Pyrser use the following DSL to describe a grammar.

``R = [ expr1 expr2 ... ]``:
    Define a rule named R as a sequence of clauses defined by ``expr``. ``[]`` are mandatory at this level.

``expr``:
    expr is one of the following statements.

``expr1 expr2``:
    Match expr1, and then match expr2 if it succeeds. Like python's ``and``.

``expr1 | expr2``:
    Try to match expr1. If it fails, match expr2 instead. Like python's ``or``.
    
``expr1 expr2 | expr3 expr4`` :
    Try to match ``expr1`` and then ``expr2``. If it fails, match ``expr3`` and then ``expr4``!

``[ expr1 expr2 expr3 ... ]``:
    Group some clauses. Allow to inverse priority.

``expr*``:
    Match expr zero or more times.

``expr+``:
    Match expr one or more times.

``expr?``:
    Try to match expr.

``!expr``:
    Negative lookahead. Fails if the next item in the input matches expr. Consumes no input.

``!!expr``:
    Positive lookahead. Fails if the next item in the input does *not* matches expr. Consumes no input.

``~expr``:
    Complement of expr. Consumes one character if the next item in the input matches does *not* matches expr.

``->expr``:
    Read until expr. Consumes N character until the next item in the input matches expr.

``A``:
    Call the rule ``A``.

``'a'``:
    Read the character ``a`` in the input.

``"foo"``:
    Read the text ``foo`` in the input.

``'a'..'z'``:
    Read the next character if its value is between ``a`` and ``z``.

``expr:node``:
    Fetch the result of expr, create the variable ``node`` and bind the result to it.

``__scope__:node``:
    Create the variable ``node``. This variable is attach to the scope of the rule.

``expr:>node``:
    Bind the result of the expr to the existing variable ``node``.

``#hook_without_parameter``:
    Call a hook without parameter.

``#hook(p1, "p2", 3)``:
    Call a hook with ``p1`` as ``pyrser.parsing.node.Node``, ``"p2"`` as ``str``, ``3`` as ``int``.

``@foo expr``:
    Apply the directive ``foo`` to the expression ``expr``.

``@foo(p1, "p2", 3) expr``:
    Apply the directive ``foo`` to the expression ``expr`` with parameter to the directive (as hooks).
Note: ``expr`` is compose of all basics expression except for pipe (``|``) operator.

Python API: class EBNF
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: pyrser.dsl.EBNF
