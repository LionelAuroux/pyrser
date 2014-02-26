# inference mechanisms
from pyrser.type_checking import *

class Inference:
    # TO REDEFINE IN AST
    def type_algos(self) -> ('self.infer_algo', 'self.feedback_algo', ['args']):
        """
        Sub class must return a Tuple of 4 elements:
            - the method to use to infer type.
            - the method to use when feedback type.
            - the list of params to used when infer or feedback type.

        This is useful to connect AST members to generic algo or
        to overload some specific semantic for your language.
        """
        raise Exception(("%s must inherit from Inference and define" +
                        " type_algos(self) method to support" +
                        " Pyrser Type Systems.") % type(self).__name__)

    def infer_type(self):
        print("Infer type of this node: %s" % repr(self))
        # get algo
        type_algo = self.type_algos()
        type_algo[0](*type_algo[2])

    def feedback(self, final_type):
        print("Feedback type of this node: %s" % repr(self))
        # get algo
        type_algo = self.type_algos()
        type_algo[1](final_type, *type_algo[2])

    ## INFER ALGOS

    def infer_block(self, body):
        """
        Infer type on block is to type each of is sub-element
        """
        # create root type_node for RootBlock
        if not hasattr(self, 'type_node'):
            self.type_node = Scope()
        print("Infer Block: %s" % repr(body))
        for e in body:
            e.type_node = Scope()
            e.type_node.set_parent(self.type_node)
            e.infer_type()

    def infer_subexpr(self, expr):
        """
        Infer type on the subexpr
        """
        print("Infer SubExpr: %s" % repr(expr))
        expr.type_node = Scope()
        expr.type_node.set_parent(self.type_node)
        expr.infer_type()

    def infer_fun(self, call_expr, params):
        print("Infer fun call of this node: %s" % repr(call_expr))
        # first fetch all possible types for the call expr
        call_expr.type_node = Scope()
        call_expr.type_node.set_parent(self.type_node)
        call_expr.infer_type()
        f = call_expr.type_node
        # second fetch all possible types for each parameter
        tparams = []
        for p in params:
            p.type_node = Scope()
            p.type_node.set_parent(self.type_node)
            p.infer_type()
            tparams.append(p.type_node)
        # select overloads
        (final_call_expr, final_tparams) = f.get_by_params(*tparams)
        print("CALL %s" % str(final_call_expr))
        nversion = len(final_call_expr)
        if nversion == 0:
            # ERREUR DE TYPAGE
            pass
        elif nversion == 1:
            # FOUND ONLY ONE TYPE
            # feedbacks
            for i in range(len(final_tparams)):
                p = final_tparams[i]
                print("P %s" % str(p))
                if tparams[i].need_feedback:
                    tparams[i].feedback(p)

    def infer_id(self, ident):
        """
        Infer type from an ID!
        - check if ID is declarated in the scope
        - if no ID is polymorphic type
        """
        print("Infer ID of this node: %s" % repr(ident))
        # check if ID is declared
        defined = self.type_node.get_by_symbol_name(ident)
        if len(defined) > 0:
            # set from matchings declarations
            self.type_node.update(defined)
        else:
            self.type_node.add(Var(ident, '?1'))
            self.type_node.need_feedback = True
            print("NEED FEEDBACK")
            print(str(self.type_node))

    def infer_literal(self, literal, t):
        """
        Infer type from an LITERAL!
        Type of literal depend of language.
        We adopt a basic convention
        """
        print("Infer LITERAL of this node: %s" % repr(literal))
        self.type_node.add(Val(literal, t))
        print(str(self.type_node))

    def infer_operator(self, op):
        """
        Infer type of OPERATOR!
        Classic (?1, ?1) -> ?1
        """
        print("Infer op of this node: %s" % repr(op))
        # by default all operator are polymorphic
        self.type_node.add(Signature(op, '?1' , '?1', '?1'))
        self.type_node.need_feedback = True
        print("NEED FEEDBACK")

    ## FEEDBACK ALGOS

    def feedback_block(self, final_type, body):
        self.type_node = final_type
        for e in body:
            if e.type_node.need_feedback:
                e.type_node.feedback(final_type)

    def feedback_subexpr(self, final_type, expr):
        self.type_node = final_type
        if expr.type_node.need_feedback:
            expr.type_node.feedback(final_type)

    def feedback_fun(self, final_type, call_expr, params):
        print("feedback FUN")
        self.type_node = final_type
        # ...

    def feedback_id(self, final_type, ident):
        print("feedback ID")
        # instancie META!!!
        self.type_node = final_type

    def feedback_literal(self, final_type, literal, t):
        print("feedback LITERAL")
        self.type_node = final_type

    def feedback_operator(self, final_type, op):
        print("feedback OP")
        self.type_node = final_type
