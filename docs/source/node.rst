Building AST (Abstract Syntax Tree): Module ``node``
====================================================

Using Nodes:
~~~~~~~~~~~~

Pyrser provide 2 ways to fill nodes:

* Capture with ``:``
    
    In the DSL, ``CREATE`` a node and ``STORE`` the result of a rule in it::

        R = [
            ThisRuleReturnSomethingIn_ : weCaptureInThisNode
        ]
        
        ThisRuleReturnSomethingIn_ = [
            #putSomethingIn(_)
        ]

* Binding with ``:>``
    
    Change the content of a previously ``CREATED`` node to the result of a rule::
        
        R = [
            Create : aNodeHere
            #showThingReadByCreate(aNodeHere)
            aThing?:>aNodeHere
            #showAThing(aNodeHere)
        ]

    You could use ``__scope__`` to create a node from scratch. It's common to use it with binding::

        R = [
            __scope__:B  //
            Bla?:>B
            __scope__:bim
            [loop]+
        ]

        loop = [ 
            item:i
            #addBim(bim, i) // bim is a node visible here but attached to the scope of R
        ]

    In the previous rule, ``Bla`` is optional. So his content is only bind to ``B`` when ``Bla`` is parsed.


Life Cycle and Visibility:
~~~~~~~~~~~

Nodes lives and is visible thru rules in a logical way::

    R = [
        // _ is the return of R
        aRule : A
        [
            // A is visible and live
            anotherRule1 : B
            anotherRule2 : C
            |
            // B die
            // C die
            anotherRule3 : D
        ]
        // D die
    ]
    // A die
    
    anotherRule1 = [
        // A live
        // _ is the return of anotherRule1
        doSomething1 #doOn(A)
    ]

    anotherRule2 = [
        // A is visible and lives
        // B is visible and lives
        // _ is the return of anotherRule2
        doSomething2 #doOn(A, B)
    ]

    anotherRule3 = [
        // A is visible and lives
        // _ is the return of anotherRule3
        doSomething3
    ]

They are no difference between ``created`` nodes or ``binded`` nodes for the visibility/live cycle.

Python API: class Node
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pyrser.parsing.node
    :members:
    :undoc-members:
