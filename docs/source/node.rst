Building AST: Module ``node``
=============================

Using Nodes:
~~~~~~~~~~~~

Pyrser provide 2 ways to fill nodes:

* Capture with ``:``
    
    In the DSL, ``CREATE`` a node and ``STORE`` the result of a rule in it::
        
        R = [  ThisRuleReturnSomethingIn_ : weCaptureInThisNode ]
        
        ThisRuleReturnSomethingIn_ = [ #putSomethingIn(_) ]

* Binding with ``:>``
    
    Change the content of a previously ``CREATED`` node to the result of a rule::
        
        R = [ Create : aNodeHere #showThingReadByCreate(aNodeHere) aThing?:>aNodeHere #showAThing(aNodeHere) ]

Life Cycle:
~~~~~~~~~~~

Nodes lives thru rules in a logical way::

    R = [
        aRule : A
        [
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
        // _ live
        doSomething1
    ]

    anotherRule2 = [
        // A live
        // B live
        // _ live
        doSomething2
    ]

    anotherRule3 = [
        // A live
        // _ live
        doSomething3
    ]

They are no difference between ``created`` nodes or ``binded`` nodes for the live cycle.

Python API: class Node
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pyrser.parsing.node
    :members:
    :undoc-members:
