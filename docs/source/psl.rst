Pyrser Selector Language
========================

After building an AST, you want to handle it.
The classic way is to use visitors to walk and transform the tree.

But this is boring, and sometimes confusing.

A better way is to use PSL expressions (Pyrser Selector Language).

Like regexes for charaters, PSL allow you to describe tree patterns, use it to match trees, and transform it.

PSL is founded on two major concepts:
    - hooks
    - events

Inside a block you write many expressions to match a tree and you describe a ``hook`` to call a python function when then pattern is found in the tree.
you could also set an ``event`` to handle preconditions on other expressions.


.. include:: ../../pyrser/ast/psl.bnf
