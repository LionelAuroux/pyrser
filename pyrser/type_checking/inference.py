# inference mechanisms
from pyrser.type_checking import *


class Inference:
    # TO REDEFINE IN AST
    def type_algos(self) -> ('self.infer_algo',
                             'self.feedback_algo', ['args']):
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

    def feedback(self, map_type: dict, final_type: TypeName):
        print("Feedback type of this node: %s : %s" % (repr(self), final_type))
        # get algo
        type_algo = self.type_algos()
        type_algo[1](map_type, final_type)

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
        # 1 - fetch all possible types for the call expr
        call_expr.type_node = Scope()
        call_expr.type_node.set_parent(self.type_node)
        call_expr.infer_type()
        f = call_expr.type_node
        # 2 - fetch all possible types for each parameters
        tparams = []
        for p in params:
            p.type_node = Scope()
            p.type_node.set_parent(self.type_node)
            p.infer_type()
            tparams.append(p.type_node)
        # 3 - select overloads
        print("check for proto: ((%s))" % tparams[0])
        if len(tparams) > 1:
            print("check for proto 2ieme: ((%s))" % tparams[1])
        (final_call_expr, final_tparams) = f.get_by_params(tparams)
        print("CALL %s" % str(final_call_expr))
        for p in final_tparams[0]:
            print("PP %s" % str(p))
        if len(final_tparams) > 1:
            for p in final_tparams[1]:
                print("PP %s" % str(p))
        # 4 - record overloads
        self.type_node = final_call_expr
        nversion = len(final_call_expr)
        if nversion > 1:
            # too many choice
            self.type_node.need_feedback = True
            return
        elif nversion == 0:
            # ERREUR DE TYPAGE
            return
        # 5 - handle polymorphism
        my_map = dict()
        my_type = list(self.type_node.values())[0]
        if my_type.tret.is_polymorphic():
            print("HAVE RET POLY :%s" % type(my_type))
            # try to get from real tret
            sig = list(call_expr.type_node.values())[0]
            if not sig.tret.is_polymorphic():
                print("HAVE R TYPE %s" % sig.tret)
                print("%s" % sig)
                my_map.update(sig.resolution)
                my_type.set_resolved_name(
                    sig.resolution,
                    my_type.tret,
                    sig.tret
                )
        arity = len(my_type.tparams)
        for i in range(arity):
            p = my_type.tparams[i]
            if p.is_polymorphic():
                # take type in final_tparams
                print("HAVE P[%d] POLY" % i)
                sig = list(final_tparams[0][i].values())[0]
                if not sig.tret.is_polymorphic():
                    print("P HAVE REAL TYPE %s" % sig.tret)
                    print("SIG.RESOL <%s>" % sig)
                    my_map[p.value] = sig.resolution[sig.tret.value]
                    my_type.set_resolved_name(sig.resolution, p, sig.tret)
        print("AFTER RESOLV %s" % my_type)
        print("NEW SIG %s" % my_type.get_compute_sig())
        self.type_node.clear()
        self.type_node.add(my_type)
        # 6 - feedback
        for i in range(arity):
            p = my_type.tparams[i]
            if params[i].type_node.need_feedback:
                print("FEED BACK P[%d] %s" % (i, p))
                print("FEED MAP %s" % my_map)
                params[i].feedback(my_map, p)

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
        self.type_node.add(EvalCtx.from_sig(Val(literal, t)))
        print("LITCTX [%s]" % str(self.type_node))
        print("RVAL %s" % repr(list(self.type_node.values())[0].resolution))

    def infer_operator(self, op):
        """
        Infer type of OPERATOR!
        Classic (?1, ?1) -> ?1
        """
        print("Infer op of this node: %s" % repr(op))
        # by default all operator are polymorphic
        self.type_node.add(Signature(op, '?1', ['?1', '?1']))
        self.type_node.need_feedback = True
        print("NEED FEEDBACK")

    ## FEEDBACK ALGOS

    def feedback_block(self, map_type: dict, final_type: TypeName):
        # normally nothing to do!?!?!
        for e in body:
            if e.type_node.need_feedback:
                e.type_node.feedback(None)

    def feedback_subexpr(self, map_type: dict, final_type: TypeName):
        self.type_node = self.type_node.get_by_return_type(final_type)
        if expr.type_node.need_feedback:
            expr.type_node.feedback(final_type)

    def feedback_fun(self, map_type: dict, final_type: TypeName):
        print("feedback FUN")
        self.type_node = self.type_node.get_by_return_type(final_type)
        # ...

    def feedback_id(self, map_type: dict, final_type: TypeName):
        print("feedback ID")
        # instancie META!!!
        if len(self.type_node) > 1:
            self.type_node = self.type_node.get_by_return_type(final_type)
            if len(self.type_node) != 1:
                # ERROR TYPE !!!?!?
                pass
        else:
            the_sig = list(self.type_node.values())[0]
            if the_sig.tret.is_polymorphic():
                self.type_node = EvalCtx.from_sig(the_sig)
                self.type_node.set_resolved_name(map_type, the_sig.tret,
                                                 final_type)
                #self.type_node = self.type_node.get_compute_sig()
                print("New EVAL CTX %s" % self.type_node)

    def feedback_literal(self, map_type: dict, final_type: TypeName):
        print("feedback LITERAL")
        self.type_node = self.type_node.get_by_return_type(final_type)

    def feedback_operator(self, map_type: dict, final_type: TypeName):
        print("feedback OP")
        self.type_node = self.type_node.get_by_return_type(final_type)
