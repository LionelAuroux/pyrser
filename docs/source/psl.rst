Pyrser Selector Language
========================

What?
~~~~~

After building an AST, you want to handle it.
The classic way is to use visitors to walk and transform the tree.

But this is boring, and sometimes confusing.

A better way is to use PSL expressions (Pyrser Selector Language).

Like regexes for charaters, PSL allow you to describe tree patterns, use it to match trees, and transform it.

PSL is founded on two major concepts:
    - hooks
    - events

Inside a block you write many expressions to match a tree and you describe a **hook** to call a python function when then pattern is found in the tree.
you could also set an **event** to handle preconditions on other expressions.

Instanciate a PSL compiler and compile an expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import pyrser.ast.psl as psl
    
    
    parser = psl.PSL()
    psl_comp = parser.compile("""
    {
        A() => #hook;
    }
    """)

Basic: Type, Capture and Hook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, we write **pattern** in the left hand side of the **=>** operator, and we write a **hook** name in the right hand side of the same operator.

Here

.. code:: python

    A()

is our first **pattern**.

This syntax denote the matching of all instance of **class A** without any attributes.

To use it, we need call the ``match`` function, to pass a **tree** and to connect our **hook** to a python function.

.. code:: python

    import pyrser.ast.psl as psl
    
    def my_hook(capture, user_data):
        print("captured nodes %s" % repr(capture))
            
    class A:
        pass

    parser = psl.PSL()
    psl_comp = parser.compile("""
    {
        A() => #hook;
    }
    """)
    t = [1, 2, A(), 3]
    psl.match(t, psl_comp, {'hook': my_hook})

Cool, we got **captured nodes {}**

PSL Grammar
~~~~~~~~~~~

Here the complete grammar of PSL in pyrser:

.. include:: ../../pyrser/ast/psl.bnf
    :code: antlr
