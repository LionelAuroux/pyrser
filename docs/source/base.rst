Base of all parser
===================

When you inherit from ``pyrser.grammar.Grammar``, you get namespace in your grammar called ``Base`` that provide a lot of default rules.
This namespace follows the grammars aggregation principle of pyrser.

Grammar composition
~~~~~~~~~~~~~~~~~~~

rules of thumb:

    * You could inherit from N grammar to create a new one, but the first base class *must* be ``grammar.Grammar``::

        from pyrser import grammar
        from other import A, B, C

        class MyGrammar(grammar.Grammar, A, B, C):
            pass
    
    * Each inherited rules from a base class is prefixed by the base class name. This is the namespace.
    * Each inherited rules exists with and without the namespace prefix in your child class::
        
        class A(grammar.Grammar):
            grammar="rule ::= id eof;"

        class B(grammar.Grammar, A):
            # here exist ``A.rule`` and ``rule``.
            pass

    * A rule name in a child class could clash with the raw rule name from a base class (without namespace prefix).
    * So the prefixed rule name always exists::

        class A(grammar.Grammar):
            grammar="rule ::= id eof;"

        class B(grammar.Grammar, A):
            grammar="rule ::= A.rule | string eof;"


Default rules
~~~~~~~~~~~~~

So the namespace Base provide a lot of basic rules.

``Base.eof``:
    Read a End-of-File.

``Base.eol``:
    Read a portable End-of-Line.

``Base.id``:
    Read an identifier ['a'..'z'|'A'..'Z'|'_']['a'..'z'|'A'..'Z'|'0'..'9'|'_']*

``Base.num``:
    Read a ['0'..'9']+

``Base.char``:
    Read a something surrounded by ' like in C programming language for char.

``Base.string``:
    Read a something surrounded by " like in C programming language for string.

``Base.read_char``:
    Read one arbitrary char.

Python API: class parserBase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: pyrser.parsing.parserBase
