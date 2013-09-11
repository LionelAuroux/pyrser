************
Introduction
************

About pyrser
============

Pyrser is a package that allows you to quickly describe a grammar aiming to parse something.
Pyrser uses a DSL to describe grammar rules.
This DSL doesn't include any language construction, here python.
The Pyrser's DSL could be use for another language in near future.

Pyrser provides only two abstractions:
    * hooks : that connect one event in your grammar to a method in your handling class.
    * nodes : that bind the rule result to a name that you could use with hook.

A minimal use of pyrser is ::

    from pyrser import grammar
    
    class   Helloworld(grammar.Grammar):
        entry = "main"
        grammar = """
            main ::= ["hello" | "world"]* eof
            ;
        """
    
    import sys
    hw = Helloworld()
    if hw.parse_file(sys.argv[1]):
        print("OK")

This piece of code allow you to read a list of ``hello`` or ``word``.

See :doc:`tutorial` to understand how works this sample.

Install pyrser
==============
You need python 3.3+

To install pyrser on your system, run the following command::

    pip install pyrser
