Writing a BNF grammar
=====================

BNF Syntax
~~~~~~~~~~

Pyrser use the following DSL to describe a grammar.

``R ::= ...;``:
    Define a rule named R.

``A B``:
    Match A, and then match B if it succeeds. Like python's ``and``.

``A | B``:
    Try to match A. If it fails, match B instead. Like python's ``or``.

``[ ... ]``:
    Group some clauses.

``A*``:
    Match A zero or more times.

``A+``:
    Match A one or more times.

``A?``:
    Try to match A.

``!A``:
    Negative lookahead. Fails if the next item in the input matches A. Consumes no input.

``!!A``:
    Positive lookahead. Fails if the next item in the input does *not* matches A. Consumes no input.

``~A``:
    Complement of A. Consumes one character if the next item in the input matches does *not* matches A.

``->A``:
    Read until A. Consumes N character until the next item in the input matches A.

``'a'``:
    Read the character ``'a'`` in the input.

``"foo"``:
    Read the text ``"foo"`` in the input.

``'a'..'z'``:
    Read the next character if its value is between ``'a'`` and ``'z'``.

``expr:node``:
    Bind the result of the expr to the variable node.

``#hook_without_parameter``:
    Call a hook without parameter.

``#hook(p1, "p2", 3)``:
    Call a hook with ``p1`` as node, ``"p2"`` as str, ``3`` as int.

``@foo R``:
    Apply the directive ``foo`` to the rule ``R``.

``@foo(p1, "p2", 3) R``:
    Apply the directive ``foo`` to the rule ``R`` with parameter to the directive (as hooks).

Python API: class EBNF
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: pyrser.dsl.EBNF
