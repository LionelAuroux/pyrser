# Copyright (C) 2013 Pascal Bertrand
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ast

from pyrser import meta
from pyrser.parsing.python import parserBase


def exit_scope(in_loop: bool, in_try: bool) -> ast.stmt:
    """Create the appropriate scope exiting statement.
    
    The documentation only shows one level and always uses
    'return False' in examples.

    'raise AltFalse()' within a try.
    'break' within a loop.
    'return False' otherwise.
    """
    if in_try:
        return ast.Raise(ast.Call(ast.Name('AltFalse', ast.Load()),
            [], [], None, None), None)
    if in_loop:
        return ast.Break()
    return ast.Return(ast.Name('False', ast.Load()))


#TODO(bps): find a better name to describe what it does
def clause_(clause: parserBase.ParserTree, in_loop: bool, in_try: bool) -> [ast.stmt]:
    """Normalize a test expression into a statements list.
    
    Statements list are returned as-is.
    Expression is packaged as:
    if not expr:
        return False
    """
    res = clause.topython(in_loop, in_try)
    if isinstance(res, list):
        return res
    return [ast.If(ast.UnaryOp(ast.Not(), res), [exit_scope(in_loop, in_try)],
        [])]


@meta.add_method(parserBase.Call)
def topython(self, in_loop: bool=False, in_try: bool=False) -> ast.expr:
    """Generates python code calling the function.

    fn(*args)
    """
    return ast.Call(
        ast.Attribute(
            ast.Name('self', ast.Load),
            self.callObject.__name__,
            ast.Load()),
        [ast.Str(param) for param in self.params],
        [],
        None,
        None)

@meta.add_method(parserBase.CallTrue)
def topython(self, in_loop: bool=False, in_try: bool=False) -> ast.expr:
    """Generates python code calling the function and returning True.

    lambda: fn(*args) or True
    """
    return ast.Lambda(
        ast.arguments([], None, None, [], None, None, [], []),
        ast.BoolOp(
            ast.Or(),
            [
                super(parserBase.CallTrue, self).topython(in_loop, in_try),
                ast.Name('True', ast.Load())]))


@meta.add_method(parserBase.Hook)
def topython(self, in_loop: bool=False, in_try: bool=False) -> ast.expr:
    """Generates python code calling a hook.

    self.evalHook('hookname', self.ruleNodes[-1])
    """
    return ast.Call(
        ast.Attribute(ast.Name('self', ast.Load()), 'evalHook', ast.Load()),
        [
            ast.Str(self.name),
            ast.Subscript(
                ast.Attribute(ast.Name('self', ast.Load()), 'ruleNodes', ast.Load()),
                ast.Index(ast.UnaryOp(ast.USub(), ast.Num(1))),
                ast.Load())],
        [],
        None,
        None)


@meta.add_method(parserBase.Rule)
def topython(self, in_loop: bool=False, in_try: bool=False) -> ast.expr:
    """Generates python code calling a rule.

    self.evalRule('rulename')
    """
    return ast.Call(
        ast.Attribute(ast.Name('self', ast.Load), 'evalRule', ast.Load()),
        [ast.Str(self.name)],
        [],
        None,
        None)


#TODO(bps): Handle more cases or patch ParserTree nodes accordingly.
#TODO(bps): forbid nested alt
@meta.add_method(parserBase.Alt)
def topython(self, in_loop: bool=False, in_try: bool=False) -> [ast.stmt]:
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
    print("AST: %s" % dir(ast))
    res = ast.Try(
        [],
        [ast.ExceptHandler(
            ast.Name('AltTrue', ast.Load()),
            None,
            [ast.Pass()])],
        [],
        [])
    for clause in self.clauses:
        res.body.append(
            ast.Try(
                (clause_(clause, in_loop, in_try=True) +
                 [ast.Raise(
                     ast.Call(
                         ast.Name('AltTrue', ast.Load()),
                         [],
                         [],
                         None,
                         None),
                     None)]),
                [ast.ExceptHandler(
                    ast.Name('AltFalse', ast.Load()),
                    None,
                    [ast.Pass()])],
                [],
                []))
    res.body.append(exit_scope(in_loop, in_try))
    return [res]


@meta.add_method(parserBase.Clauses)
def topython(self, in_loop: bool=False, in_try: bool=False) -> [ast.stmt]:
    """Generates python code for clauses.

    if not clause:
        return False
    if not clause:
        return False
    """
    res = []
    for clause in self.clauses:
        res.extend(clause_(clause, in_loop, in_try))
    return res


@meta.add_method(parserBase.Capture)
def topython(self, in_loop: bool=False, in_try: bool=False) -> [ast.stmt]:
    """Generates python code to capture text consumed by a clause.

    if not self.beginTag('tagname'):
        return False
    <code for the clause>
    if not self.endTag('tagname'):
        return False
    """
    return [
        ast.If(
            ast.UnaryOp(
                ast.Not(),
                ast.Call(
                    ast.Attribute(
                        ast.Name('self', ast.Load()),
                        'beginTag',
                        ast.Load()),
                    [ast.Str(self.tagname)],
                    [],
                    None,
                    None)),
            [exit_scope(in_loop, in_try)],
            []),
        ast.If(
            ast.UnaryOp(ast.Not(), self.clause.topython(in_loop, in_try)),
            [exit_scope(in_loop, in_try)],
            []),
        ast.If(
            ast.UnaryOp(
                ast.Not(),
                ast.Call(
                    ast.Attribute(
                        ast.Name('self', ast.Load()),
                        'endTag',
                        ast.Load()),
                    [ast.Str(self.tagname)],
                    [],
                    None,
                    None)),
            [exit_scope(in_loop, in_try)],
            [])]


@meta.add_method(parserBase.Rep0N)
def topython(self, in_loop: bool=False, in_try: bool=False) -> [ast.stmt]:
    """Generates python code for a clause repeated 0 or more times.

    while True:
        <code for the clause>
    """
    return [ast.While(ast.Name('True', ast.Load()),
                clause_(self.clause, in_loop=True, in_try=in_try), [])]


@meta.add_method(parserBase.Rep1N)
def topython(self, in_loop: bool=False, in_try: bool=False) -> [ast.stmt]:
    """Generates python code for a clause repeated 1 or more times.

    <code for the clause>
    while True:
        <code for the clause>
    """
    return clause_(self.clause, in_loop, in_try) + [
        ast.While(
            ast.Name('True', ast.Load()),
            clause_(self.clause, in_loop=True, in_try=in_try),
            [])]


@meta.add_method(parserBase.RepOptional)
def topython(self, in_loop: bool=False, in_try: bool=False) -> [ast.stmt]:
    """Generates python code for an optional clause.

    <code for the clause>
    """
    return ast.Lambda(
        ast.arguments([], None, None, [], None, None, [], []),
        ast.BoolOp(ast.Or(), [
            self.clause.topython(in_loop, in_try),
            ast.Name('True', ast.Load())]))


@meta.add_method(parserBase.Scope)
def topython(self, in_loop: bool=False, in_try: bool=False) -> [ast.stmt]:
    """Generates python code for a scope.

    if not self.begin():
        return False
    res = self.clause()
    if not res:
        return False
    if not self.end():
        return False
    return res
    """
    raise NotImplementedError


@meta.add_method(parserBase.ParserBase)
def rule_topython(self, rule_name: str) -> ast.FunctionDef:
    """Generates code for a rule.

    func rulename(self):
        <code for the rule>
        return True
    """
    rule = self._ParserBase__rules[rule_name]
    return ast.FunctionDef(
        rule_name,
        ast.arguments([ast.arg('self', None)], None, None, [], None, None, [],
            []),
        rule.topython() + [ast.Return(ast.Name('True', ast.Load()))],
        [],
        None)
