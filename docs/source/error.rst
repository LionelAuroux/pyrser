Error handling: Module ``error``
================================

Basically, ``parse`` functions of grammar return a boolean.
If the parsing was done, it's true.
If something was wrong, an exception error.Diagnostic is raised.::

    #!/usr/bin/env python3
    from pyrser import grammar
    from pyrser import error
    
    class Z(grammar.Grammar):
        entry = "main"
        grammar = """
            main = ['z'+]
        """
    
    z = Z()
    try:
        res = z.parse("xxx")
        if res:
            print("cool")
    except error.Diagnostic as e:
        print(e)

Sometimes you don't want exception, you could do it
with the extra parameter ``raise_diagnostic``, and so
the returned node by the ``parse`` function is False.
But you could get what's wrong with the diagnostic attribute. ::

    #!/usr/bin/env python3
    from pyrser import grammar
    
    class Z(grammar.Grammar):
        entry = "main"
        grammar = """
            main = ['z'+]
        """
    
    z = Z(raise_diagnostic=False)
    res = z.parse("xxx")
    if res:
        print("cool")
    else:
        print(res.diagnostic.get_content())

Here, we can't parse ``xxx``. We got the following message::

    ===============================================================================
    error : Parse error in 'main'
    from /tmp/tmpg7j29i at line:1 col:1 :
    xxx
    ^
    -------------------------------------------------------------------------------

Sometime you do wrong in the DSL part so you fucked up your python interpretor. Just catch the Diagnostic exception::

    #!/usr/bin/env python3
    from pyrser import error
    try:
        from pyrser import grammar
        
        class Z(grammar.Grammar):
            entry = "main"
            grammar = """
                main = ['z'+] -> error here
            """
        
        z = Z()
        res = z.parse("zzzz")
    except error.Diagnostic as e:
        print(e)

And you got::

    ===============================================================================
    error : Parse error in 'Base.eof' in EBNF bnf
    from /tmp/tmpvrf4_n at line:2 col:27 :
                main = ['z'+] -> error here
                              ^
    -------------------------------------------------------------------------------
    error : Parse error in 'Base.eof' in EBNF bnf
    
    -------------------------------------------------------------------------------


Python API: error module
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pyrser.error
    :members:
    :undoc-members:
