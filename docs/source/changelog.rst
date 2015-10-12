What's new in |release|
=======================

Goals for 1.0:

    * Effect System
    * bootstrap from DSL to cythonised python/C grammar with PSL
    * packrat cache on rules
    * C stub
    * other languages stubs (Go, javascript...)

WIP:

    * Improvement of Type System
    * Documentation and Tutorials

version 0.0.10: 2015-10-12
~~~~~~~~~~~~~~~~~~~~~~~~~~

    * Doc fix: content and theme (switch to bizstyle)
    * Remove dependencies in the setup.py (cython)

version 0.0.6: 2015-09-15
~~~~~~~~~~~~~~~~~~~~~~~~~
    
    * Extra dependencies for Doc generation with Sphinx
    * Elements of PSL (Pyrser Selector Language)
    * bug fix: complement(~)

version 0.0.5: 2014-09-15
~~~~~~~~~~~~~~~~~~~~~~~~~

    * A Diagnostic object for error handling
    * A Begin of Type System module for type checking
    * YML format for Node (and subclasses) pretty-printing
    * Begins of backend to cython (need to finish stub for nodes,hooks,directives,rules)

version 0.0.2: 2014-02-12
~~~~~~~~~~~~~~~~~~~~~~~~~

    * Syntax change (could be the last) "::= ... ;" into "= [ ... ]"
    * No more ._bool in node
    * No more X.value in node use self.value(X) instead
    * No more weakref
    * Renaming parserStream in stream
    * Renaming parserBase in base
    * Improve stream with tag objects
    * Add __scope__ for declaring nodes attach to a scope
    * Renaming parserTree in functors
    * Renaming dumpParserTree in to_dsl
    * No more following of rule (global node rewritten by a local capture)
    * Use the ``set`` method from Node to modify a node in a hook.

version 0.0.1: 2013-09-26
~~~~~~~~~~~~~~~~~~~~~~~~~

    * Initial version
    * Usable grammar composition
    * Usable DSL
    * Usable functors
