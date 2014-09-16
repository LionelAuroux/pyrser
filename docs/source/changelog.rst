What's new in |release|
=======================

TODO:

    * bootstrap from DSL to cythonised python/C grammar
    * packrat cache on rules

WIP:

    * Need to improve Type System

version 0.0.4: 2014-09-15
~~~~~~~~~~~~~~~~~~~~~~~~~

    * A Diagnostic object for error handling
    * A Begin of Type System module for type checking
    * YML format for Node (and subclasses) pretty-printing
    * begins of backend to cython (need to finish stub for nodes,hooks,directives,rules)

version 0.0.2: 2014-02-12
~~~~~~~~~~~~~~~~~~~~~~~~~

    * syntax change (could be the last) "::= ... ;" into "= [ ... ]"
    * no more ._bool in node
    * no more X.value in node use self.value(X) instead
    * no more weakref
    * renaming parserStream in stream
    * renaming parserBase in base
    * improve stream with tag objects
    * add __scope__ for declaring nodes attach to a scope
    * renaming parserTree in functors
    * renaming dumpParserTree in to_dsl
    * no more following of rule (global node rewritten by a local capture)
    * use the ``set`` method from Node to modify a node in a hook.

version 0.0.1: 2013-09-26
~~~~~~~~~~~~~~~~~~~~~~~~~

    * initial version
    * usable grammar composition
    * usable DSL
    * usable functor
