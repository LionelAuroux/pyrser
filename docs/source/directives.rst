Directives
==========

You could configure the pyrser engine to consume some character for you.

Default ignore convention
~~~~~~~~~~~~~~~~~~~~~~~~~

``blanks``:
    Default convention. Consume space,\\t,\\f,\\r and \\n silently.

``null``:
    Consume nothing silently.

``C/C++``:
    Like blanks but handle also C/C++ comments.

.. automodule:: pyrser.directives.ignore
