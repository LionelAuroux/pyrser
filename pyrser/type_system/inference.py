# inference mechanisms
from pyrser.type_system import *
from pyrser.error import *
from pyrser.passes.to_yml import *


class Inference:
    # TO REDEFINE IN AST
    def type_algos(self) -> ('self.infer_algo',
                             'self.feedback_algo', ['args']):
        """
        Sub class must return a Tuple of 3 elements:
            - the method to use to infer type.
            - the list of params to used when infer a type.
            - the method to use when feedback a type.

        This is useful to connect AST members to generic algo or
        to overload some specific semantic for your language.
        """
        raise Exception(("%s must inherit from Inference and define" +
                        " type_algos(self) method to support" +
                        " Pyrser Type Systems.") % type(self).__name__)

    def infer_type(self, diagnostic=None):
        # get algo
        type_algo = self.type_algos()
        type_algo[0](type_algo[1], diagnostic)

    def feedback(self, diagnostic=None):
        # get algo
        type_algo = self.type_algos()
        type_algo[2](diagnostic)

    ## INFER ALGOS

    def infer_block(self, body, diagnostic=None):
        """
        Infer type on block is to type each of is sub-element
        """
        # create root type_node for RootBlock
        if not hasattr(self, 'type_node'):
            self.type_node = Scope(is_namespace=False)
        #diagnostic.notify(Severity.INFO, "Infer Block", self.info)
        for e in body:
            e.type_node = Scope(is_namespace=False)
            # linked scope
            e.type_node.set_parent(self.type_node)
            e.infer_type(diagnostic)

    def infer_subexpr(self, expr, diagnostic=None):
        """
        Infer type on the subexpr
        """
        #diagnostic.notify(Severity.INFO, "Infer SubExpr", self.info)
        expr.type_node = Scope(is_namespace=False)
        # linked scope
        expr.type_node.set_parent(self.type_node)
        expr.infer_type(diagnostic)
        self.type_node.clear()
        self.type_node.update(expr.type_node)

    def infer_fun(self, args, diagnostic=None):
        call_expr, arguments = args
        diagnostic.notify(Severity.INFO, "Infer Function call '%s'" % call_expr.value, self.info)
        # 1 - fetch all possible types for the call expr
        call_expr.type_node = Scope(is_namespace=False)
        # linked scope
        call_expr.type_node.set_parent(self.type_node)
        call_expr.infer_type(diagnostic=diagnostic)
        f = call_expr.type_node
        # 2 - fetch all possible types for each parameters
        tparams = []
        i = 0
        for p in arguments:
            p.type_node = Scope(is_namespace=False)
            # linked scope
            p.type_node.set_parent(self.type_node)
            p.infer_type(diagnostic=diagnostic)
            i += 1
            tparams.append(p.type_node)
        # 3 - select overloads
        (final_call_expr, final_tparams) = f.get_by_params(tparams)
        # 4 - record overloads
        self.type_node.clear()
        self.type_node.update(final_call_expr)
        nversion = len(final_call_expr)
        if nversion > 1:
            # too many choice
            self.type_node.need_feedback = True
            return
        elif nversion == 0:
            # TODO: Try type reconstruction if final_tparams[x][0].is_polymorphic
            # ...
            # type error
            details = "\ndetails:\n"
            details += "overloads:\n"
            for fun in f.values():
                details += str(fun.get_compute_sig()) + "\n"
            details += "parameters:\n"
            i = 0
            # TODO: change by final_tparams
            for p in tparams:
                details += "- param[%d] type " % i
                ptypes = []
                for alt in p.values():
                    ptypes.append(alt.tret)
                details += '|'.join(ptypes)+ "\n"
                i += 1
            # TODO: when f are empty
            diagnostic.notify(
                Severity.ERROR,
                "can't match overloads with parameters for function '%s'" % str(f.first().name),
                self.info,
                details
            )
            return
        # here len(self.type_node) == 1 && len(final_tparams) == 1
        # 5 - handle polymorphism
        # TODO: INSIDE A CLASS?
        my_map = dict()
        my_type = self.type_node.first()
        if my_type.tret.is_polymorphic:
            diagnostic.notify(Severity.INFO, "polymorphic return type %s" % str(my_type.get_compute_sig()), self.info)
            # if tret is polymorphic, take type from call_expr if unique, else type come from parameter resolution
            sig = call_expr.type_node.first()
            if len(call_expr.type_node) == 1 and not sig.tret.is_polymorphic:
                diagnostic.notify(Severity.INFO, "call_expr have real type '%s'" % sig.tret, self.info)
                my_map.update(sig.resolution)
                my_type.set_resolved_name(
                    sig.resolution,
                    my_type.tret,
                    sig.tret
                )
        arity = len(my_type.tparams)
        for i in range(arity):
            p = my_type.tparams[i]
            # use AST Injector
            if final_tparams[0][i].first()._translate_to is not None:
                t = final_tparams[0][i].first()._translate_to
                old = arguments[i]
                n = t.notify
                diagnostic.notify(n.severity, n.msg, old.info, details=n.details)
                arguments[i] = self.type_node.callInjector(old, t)
                scope = Scope(is_namespace=False)
                scope.need_feedback = False
                scope.add(t.fun)
                scope.set_parent(self.type_node)
                old.type_node.set_parent(scope)
                arguments[i].type_node = scope
            if p.is_polymorphic:
                # take type in final_tparams
                diagnostic.notify(Severity.INFO, "- param[%d] polymorphic type" % i, arguments[i].info)
                # here len(final_tparams) == 1, only one set for parameters
                sig = final_tparams[0][i].first()
                if not sig.tret.is_polymorphic:
                    diagnostic.notify(Severity.INFO, "- argument[%d] real type '%s'" % (i, sig.tret), arguments[i].info)
                    my_map[p.value] = sig.resolution[sig.tret.value]
                    my_type.set_resolved_name(sig.resolution, p, sig.tret)
        diagnostic.notify(Severity.INFO, "after resolution %s" % str(my_type.get_compute_sig()), self.info)
        # 6 - feedback
        self.map_type = my_map
        self.final_type = my_type.tret
        self.feedback(diagnostic)
        # 7 - Are we finish? Global type reconstruction

    def infer_id(self, ident, diagnostic=None):
        """
        Infer type from an ID!
        - check if ID is declarated in the scope
        - if no ID is polymorphic type
        """
        # check if ID is declared
        defined = self.type_node.get_by_symbol_name(ident)
        if len(defined) > 0:
            # set from matchings declarations
            self.type_node.update(defined)
        else:
            diagnostic.notify(Severity.ERROR, "%s never declared" % self.value, self.info)

    #def infer_id_self_type(self, ident, diagnostic=None):
    #    """
    #    Infer type from an ID!
    #    - check if ID is declarated in the scope
    #    - if no ID is polymorphic type
    #    """
    #    # check if ID is declared
    #    defined = self.type_node.get_by_symbol_name(ident)
    #    if len(defined) > 0:
    #        # set from matchings declarations
    #        self.type_node.update(defined)
    #    else:
    #        # TODO: est de type polymorphique local ... pas tout le temps ?1
    #        # a faire dans une declaration ... ou a l'affectation
    #        # mais pas la
    #        self.type_node.add(Var(ident, '?1'))
    #        self.type_node.need_feedback = True

    def infer_literal(self, args, diagnostic=None):
        """
        Infer type from an LITERAL!
        Type of literal depend of language.
        We adopt a basic convention
        """
        literal, t = args
        self.type_node.add(EvalCtx.from_sig(Val(literal, t)))

    #def infer_operator(self, op, diagnostic=None):
    #    """
    #    Infer type of OPERATOR!
    #    Classic (?1, ?1) -> ?1
    #    """
    #    # by default all operator are polymorphic
    #    # TODO: search proto from scope and need operators in scope
    #    self.type_node.add(Fun(op, '?1', ['?1', '?1']))
    #    self.type_node.need_feedback = True

    ## FEEDBACK ALGOS

    def feedback_block(self, diagnostic=None):
        # normally nothing to do!?!?!
        type_algo = self.type_algos()
        # TODO: body?
        for e in type_algo[1]:
            if e.type_node.need_feedback:
                e.type_node.feedback(diagnostic)

    def feedback_subexpr(self, diagnostic=None):
        self.type_node = self.type_node.get_by_return_type(self.final_type)
        self.type_node.need_feedback = False
        if expr.type_node.need_feedback:
            expr.type_node.feedback(diagnostic)

    def feedback_leaf(self, diagnostic=None):
        self.type_node = self.type_node.get_by_return_type(self.final_type)
        self.type_node.need_feedback = False

    def feedback_fun(self, diagnostic=None):
        self.type_node = self.type_node.get_by_return_type(self.final_type)
        self.type_node.need_feedback = False
        arguments = self.type_node.first().tparams
        nargs = len(arguments)
        type_algo = self.type_algos()
        call_expr, args = type_algo[1]
        if call_expr.type_node.need_feedback:
            diagnostic.notify(Severity.INFO, "feed back call_expr = %s" % self.final_type, call_expr.info)
            call_expr.map_type = self.map_type
            call_expr.final_type = self.final_type
            call_expr.feedback()
        for i in range(nargs):
            p = arguments[i]
            if args[i].type_node.need_feedback:
                diagnostic.notify(Severity.INFO, "feed back p[%d] = %s" % (i, p), args[i].info)
                diagnostic.notify(Severity.INFO, "feed map %s" % self.map_type, args[i].info)
                args[i].map_type = self.map_type
                args[i].final_type = p
                args[i].feedback(diagnostic)

    def feedback_id(self, diagnostic=None):
        # instancie META!!!
        if len(self.type_node) > 1:
            self.type_node = self.type_node.get_by_return_type(self.final_type)
            if len(self.type_node) != 1:
                # ERROR TYPE !!!?!?
                diagnostic.notify(Severity.ERROR, "Type error: too many candidates %s" % str(self.type_node), self.info)
        else:
            the_sig = list(self.type_node.values())[0]
            if the_sig.tret.is_polymorphic:
                self.type_node = EvalCtx.from_sig(the_sig)
                self.type_node.set_resolved_name(self.map_type, the_sig.tret,
                                                 self.final_type)
                # TODO: Why this fucking line... I forgot
                #self.type_node = self.type_node.get_compute_sig()
