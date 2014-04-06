************
Introduction
************

About pyrser
============

Pyrser is a package that allows you to quickly describe a grammar aiming to parse something.
Pyrser uses a DSL similar to EBNF to describe grammar rules.
This DSL doesn't include any language construction, here python.
In pyrser, we don't mix parsing rules and code.
Pyrser's DSL could be use for another language in near future.

Pyrser provides only two abstractions:
    * hooks : that connect one event in your grammar to a method in your handling class.
    * nodes : that bind the rule result to a name that you could use with hook.

A minimal use of pyrser is ::

    from pyrser import grammar
    
    class   Helloworld(grammar.Grammar):
        entry = "main"
        grammar = """
            main = [["hello" | "world"]+ eof]
        """
    
    import sys
    hw = Helloworld()
    if hw.parse_file(sys.argv[1]):
        print("OK")

This piece of code allow you to read a list of the words ``hello`` or ``world``.

See :doc:`tutorial` to understand how this sample works.

PEG Parser
==========

Pyrser is a PEG parser engine (http://en.wikipedia.org/wiki/Parsing_expression_grammar).
PEGs parser allow you to superset LL(k), LR(k), and deal with "not so context-free" grammar.
To write PEG parser, just remember:

    * Don't use left recursivity.
    * Repetition operators are always greedy
    * You have infinite positive or negative lookahead.
    * Ambiguity is always resolved by yielding the first successful recognition in alternation (``|``).
    * With hooks, Pyrser allows you to choose alternation contextually during parsing.

Install pyrser
==============
You need python 3.3+

To install pyrser on your system, run the following command::

    pip install pyrser
