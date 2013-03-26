import ast

from pyrser import meta
from pyrser import parsing


class RuleVisitor(ast.NodeVisitor):
    def __init__(self):
        self.in_optional, self.in_loop, self.in_try = 0, 0, 0

    def generic_visit(self, node):
        raise TypeError("Unhandled {} node".format(node.__class__.__name__))

    def __exit_scope(self) -> ast.stmt:
        """Create the appropriate scope exiting statement.

        The documentation only shows one level and always uses
        'return False' in examples.

        'raise AltFalse()' within a try.
        'break' within a loop.
        'return False' otherwise.
        """
        if self.in_optional:
            return ast.Pass()
        if self.in_try:
            return ast.Raise(
                ast.Call(ast.Name('AltFalse', ast.Load()), [], [], None, None),
                None)
        if self.in_loop:
            return ast.Break()
        return ast.Return(ast.Name('False', ast.Load()))

    #TODO(bps): find a better name to describe what this does
    def _clause(self, pt: parsing.ParserTree) -> [ast.stmt]:
        """Normalize a test expression into a statements list.

        Statements list are returned as-is.
        Expression is packaged as:
        if not expr:
            return False
        """
        if isinstance(pt, list):
            return pt
        return [ast.If(ast.UnaryOp(ast.Not(), pt),
                       [self.__exit_scope()],
                       [])]

    def visit_Call(self, node: parsing.Call) -> ast.expr:
        """Generates python code calling the function.

        fn(*args)
        """
        return ast.Call(
            ast.Attribute(
                ast.Name('self', ast.Load),
                node.callObject.__name__,
                ast.Load()),
            [ast.Str(param) for param in node.params],
            [],
            None,
            None)

    def visit_CallTrue(self, node: parsing.CallTrue) -> ast.expr:
        """Generates python code calling the function and returning True.

        lambda: fn(*args) or True
        """
        return ast.Lambda(
            ast.arguments([], None, None, [], None, None, [], []),
            ast.BoolOp(
                ast.Or(),
                [
                    self.visit_Call(node),
                    ast.Name('True', ast.Load())]))

    def visit_Hook(self, node: parsing.Hook) -> ast.expr:
        """Generates python code calling a hook.

        self.evalHook('hookname', self.ruleNodes[-1])
        """
        return ast.Call(
            ast.Attribute(
                ast.Name('self', ast.Load()), 'evalHook', ast.Load()),
            [
                ast.Str(node.name),
                ast.Subscript(
                    ast.Attribute(
                        ast.Name('self', ast.Load()), 'ruleNodes', ast.Load()),
                    ast.Index(ast.UnaryOp(ast.USub(), ast.Num(1))),
                    ast.Load())],
            [],
            None,
            None)

    def visit_Rule(self, node: parsing.Rule) -> ast.expr:
        """Generates python code calling a rule.

        self.evalRule('rulename')
        """
        return ast.Call(
            ast.Attribute(ast.Name('self', ast.Load()),
                          'evalRule', ast.Load()),
            [ast.Str(node.name)], [], None, None)

    def visit_Capture(self, node: parsing.Capture) -> [ast.stmt] or ast.expr:
        """Generates python code to capture text consumed by a clause.

        #If all clauses can be inlined
        self.beginTag('tagname') and clause and self.endTag('tagname')

        if not self.beginTag('tagname'):
            return False
        <code for the clause>
        if not self.endTag('tagname'):
            return False
        """
        begintag = ast.Attribute(
            ast.Name('self', ast.Load()), 'beginTag', ast.Load())
        endtag = ast.Attribute(
            ast.Name('self', ast.Load()), 'endTag', ast.Load())
        begin = ast.Call(begintag, [ast.Str(node.tagname)], [], None, None)
        end = ast.Call(endtag, [ast.Str(node.tagname)], [], None, None)
        result = [begin, self.visit(node.pt), end]
        for clause in result:
            if not isinstance(clause, ast.expr):
                break
        else:
            return ast.BoolOp(ast.And(), result)
        res = []
        for stmt in map(self._clause, result):
            res.extend(stmt)
        return res

    def visit_Scope(self, node: parsing.Capture) -> [ast.stmt] or ast.expr:
        """Generates python code for a scope.

        if not self.begin():
            return False
        res = self.pt()
        if not self.end():
            return False
        return res
        """
        return ast.Name('scope_not_implemented', ast.Load())
        raise NotImplementedError()

    #TODO(bps): forbid nested alt
    def visit_Alt(self, node: parsing.Alt) -> [ast.stmt]:
        """Generates python code for alternatives.

        try:
            try:
                <code for clause>  #raise AltFalse when alternative is False
                raise AltTrue()
            except AltFalse:
                pass
            return False
        except AltTrue:
            pass
        """
        clauses = [self.visit(clause) for clause in node.ptlist]
        for clause in clauses:
            if not isinstance(clause, ast.expr):
                break
        else:
            return ast.BoolOp(ast.Or(), clauses)
        res = ast.Try([], [ast.ExceptHandler(
            ast.Name('AltTrue', ast.Load()), None, [ast.Pass()])], [], [])
        alt_true = [ast.Raise(ast.Call(
            ast.Name('AltTrue', ast.Load()), [], [], None, None), None)]
        alt_false = [ast.ExceptHandler(
            ast.Name('AltFalse', ast.Load()), None, [ast.Pass()])]
        self.in_try += 1
        for clause in node.ptlist:
            res.body.append(
                ast.Try(self._clause(self.visit(clause)) + alt_true,
                        alt_false, [], []))
        self.in_try -= 1
        res.body.append(self.__exit_scope())
        return [res]

    def combine_exprs_for_clauses(self, exprs: [ast.expr]) -> [ast.stmt]:
        expr = exprs[0] if len(exprs) == 1 else ast.BoolOp(ast.And(), exprs)
        return self._clause(expr)

    def visit_Seq(self, node: parsing.Seq) -> [ast.stmt] or ast.expr:
        """Generates python code for clauses.

        #Continuous clauses which can can be inlined are combined with and
        clause and clause

        if not clause:
            return False
        if not clause:
            return False
        """
        exprs, stmts = [], []
        for clause in node.ptlist:
            clause_ast = self.visit(clause)
            if isinstance(clause_ast, ast.expr):
                exprs.append(clause_ast)
            else:
                if exprs:
                    stmts.extend(self.combine_exprs_for_clauses(exprs))
                    exprs = []
                stmts.extend(self._clause(clause_ast))
        if not stmts:
            return ast.BoolOp(ast.And(), exprs)
        if exprs:
            stmts.extend(self.combine_exprs_for_clauses(exprs))
        return stmts

    def visit_RepOptional(self, node: parsing.RepOptional) -> ([ast.stmt] or
                                                               ast.expr):
        """Generates python code for an optional clause.

        <code for the clause>
        """
        cl_ast = self.visit(node.pt)
        if isinstance(cl_ast, ast.expr):
            return ast.BoolOp(ast.Or(), [cl_ast, ast.Name('True', ast.Load())])
        self.in_optional += 1
        cl_ast = self.visit(node.pt)
        self.in_optional -= 1
        return cl_ast

    def visit_Rep0N(self, node: parsing.Rep0N) -> [ast.stmt]:
        """Generates python code for a clause repeated 0 or more times.

        #If all clauses can be inlined
        while clause:
            pass

        while True:
            <code for the clause>
        """
        cl_ast = self.visit(node.pt)
        if isinstance(cl_ast, ast.expr):
            return [ast.While(cl_ast, [ast.Pass()], [])]
        self.in_loop += 1
        clause = self._clause(self.visit(node.pt))
        self.in_loop -= 1
        return [ast.While(ast.Name('True', ast.Load()), clause, [])]

    def visit_Rep1N(self, node: parsing.Rep0N) -> [ast.stmt]:
        """Generates python code for a clause repeated 1 or more times.

        <code for the clause>
        while True:
            <code for the clause>
        """
        clause = self.visit(node.pt)
        if isinstance(clause, ast.expr):
            return (self._clause(clause) + self.visit_Rep0N(node))
        self.in_loop += 1
        clause = self._clause(self.visit(node.pt))
        self.in_loop -= 1
        return self._clause(self.visit(node.pt)) + [
            ast.While(ast.Name('True', ast.Load()), clause, [])]


def rule_topython(rule: parsing.ParserTree) -> [ast.stmt]:
    return RuleVisitor().visit(rule)


def parserrule_topython(parser: parsing.BasicParser,
                        rulename: str) -> ast.FunctionDef:
    """Generates code for a rule.

    def rulename(self):
        <code for the rule>
        return True
    """
    visitor = RuleVisitor()
    rule = parser._rules[rulename]
    fn_args = ast.arguments([ast.arg('self', None)], None, None, [], None,
                            None, [], [])
    body = visitor._clause(rule_topython(rule))
    body.append(ast.Return(ast.Name('True', ast.Load())))
    return ast.FunctionDef(rulename, fn_args, body, [], None)
