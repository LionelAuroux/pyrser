import treematching as tm
from pyrser.parsing import *

def loop_over(tree, key=None):
    # capture rules
    bt = tm.Capture('rules', tm.Type(DeclRule, tm.Attrs(tm.Attr("name", tm.Type(str, tm.AnyValue())), strict=False)))
    e = tm.MatchingBTree(bt)
    m = e.match(tree)
    for it in m:
        if not key or key in it.capture:
            yield it.capture

    # capture nodes
    bt = tm.Capture('nodes', tm.Type(Capture, tm.Attrs(tm.Attr("name", tm.Type(str, tm.AnyValue())), strict=False)))
    e = tm.MatchingBTree(bt)
    m = e.match(tree)
    for it in m:
        if not key or key in it.capture:
            yield it.capture

    # capture __scope__
    bt = tm.Capture('nodes', tm.Type(DeclNode, tm.Attrs(tm.Attr("name", tm.Type(str, tm.AnyValue())), strict=False)))
    e = tm.MatchingBTree(bt)
    m = e.match(tree)
    for it in m:
        if not key or key in it.capture:
            yield it.capture

    # capture decorator
    bt = tm.Capture('decorators', tm.Type(Decorator, tm.Attrs(tm.Attr("name", tm.Type(str, tm.AnyValue())), strict=False)))
    e = tm.MatchingBTree(bt)
    m = e.match(tree)
    for it in m:
        if not key or key in it.capture:
            yield it.capture

    # capture directives
    bt = tm.Capture('directives', tm.Type(Directive, tm.Attrs(tm.Attr("name", tm.Type(str, tm.AnyValue())), strict=False)))
    e = tm.MatchingBTree(bt)
    m = e.match(tree)
    for it in m:
        if not key or key in it.capture:
            yield it.capture

    # capture hooks
    bt = tm.Capture('hooks', tm.Type(Hook, tm.Attrs(tm.Attr("name", tm.Type(str, tm.AnyValue())), strict=False)))
    e = tm.MatchingBTree(bt)
    m = e.match(tree)
    for it in m:
        if not key or key in it.capture:
            yield it.capture

def prepare(tree):
    """
    Transform a Raw Tree into a Prepared Tree.
    - expand decorator/directive into tree:
        - collect decorator
        - transform decorated Rules
            - clone Rule transformed by directive based on param value
            - public name bind on transformed rule

        - collect directive
        - transform directive
            - clone Rule transformed by directive based on param value
            - call mangled_rule instead

    - collect DeclRule
    - collect Capture/__scope__ nodes
    - list hooks & parameters

    one register per nodes
    one function per DeclRule
    """
    for it in loop_over(tree):
        pass

def to_dsl(tree):
    def from_grammar(tree):
        subitems = []
        if hasattr(tree, 'list'):
            for it in tree.list:
                subitems.append(from_grammar(it))
                if type(tree) is Alt and type(it) is Seq and len(it.list) > 1:
                    subitems[-1] = "[ " + subitems[-1] + " ]"
        if hasattr(tree, 'rule'):
            subitems.append(from_grammar(tree.rule))
        return to_dsl_item(tree, subitems)

    def to_dsl_item(tree, subitems):
        txt = ""
        if type(tree) is Grammar:
            txt += f"grammar {tree.name}\n"
            for it in tree.includes:
                part = []
                if it[0]:
                    part.append(f"from {repr(it[0])}")
                if it[1]:
                    part.append(f"import {it[1]}")
                if it[2]:
                    part.append(f"as {it[2]}")
                part[-1] += "\n"
                txt += " ".join(part)
            txt += "{\n"
            txt += "\n".join(subitems)
            txt += "}\n"
            
        elif type(tree) is Decorator:
            txt += f"@{tree.name}"
            if len(tree.param):
                txt += "("
                txt += ", ".join(tree.param)
                txt += ")"
            txt += "\n"
            txt += "".join(subitems) + "\n"
        elif type(tree) is DeclRule:
            txt += f"{tree.name} = " + " ".join(subitems) + "\n"
        elif type(tree) is Directive:
            txt += f"@{tree.name}"
            if len(tree.param):
                txt += "("
                txt += ", ".join(tree.param)
                txt += ")"
            txt += " "
            txt += "".join(subitems)
        elif type(tree) is Hook:
            txt += f"#{tree.name}"
            if len(tree.param):
                txt += "("
                txt += ", ".join(tree.param)
                txt += ")"
        elif type(tree) is Seq:
            txt += " ".join(subitems)
        elif type(tree) is Alt:
            txt += " | ".join(subitems)
        elif type(tree) is Rule:
            txt += f"{tree.name}"
        elif type(tree) is Rep1N:
            txt += "".join(subitems) + "+"
        elif type(tree) is Rep0N:
            txt += "".join(subitems) + "*"
        elif type(tree) is RepOptional:
            txt += "".join(subitems) + "?"
        elif type(tree) is DeclNode:
            txt += f"__scope__:{tree.name}"
        elif type(tree) is Capture:
            txt += "".join(subitems) + f":{tree.name}"
        elif type(tree) is Until:
            txt += "->" + "".join(subitems)
        elif type(tree) is Complement:
            txt += "~" + "".join(subitems)
        elif type(tree) is Neg:
            txt += "!" + "".join(subitems)
        elif type(tree) is LookAhead:
            txt += "!!" + "".join(subitems)
        elif type(tree) is Range:
            txt += f"'{tree.begin}'..'{tree.end}'"
        elif type(tree) is Text:
            txt += f"{tree.value}"
        elif type(tree) is Char:
            txt += f"{tree.value}"
        elif type(tree) is PeekText:
            txt += f"!!{repr(tree.value)}" # TODO: double quote
            pass
        elif type(tree) is PeekChar:
            txt += f"!!{repr(tree.value)}" ## TODO: simple quote
            pass
        else:
            raise ValueError(f"Unkown Parsing Item in Tree found {type(tree)}")
        return txt
        
        
    #bt = None
    #e = tm.MatchingBTree(bt, direction=tm.MatchDirection.TOP_DOWN)
    #txt = ""
    #m = e.match(tree, txt)
    return from_grammar(tree)
