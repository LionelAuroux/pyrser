# This pass is for converting functors into IR algos bricks
# for easy target language transformation
from pyrser import meta
from pyrser import fmt
from pyrser import parsing

@meta.add_method(parsing.Parser)
def to_ir(self) -> parsing.ir.IR:
    gram = parsing.ir.Grammar(self.__class__.__name__)
    for k, v in self.__class__._rules.items():
        if isinstance(v, parsing.Functor):
            rule = parsing.ir.Rule(k)
            rule.expr = v.to_ir()
            gram.rules.append(rule)
    return gram

@meta.add_method(parsing.Rule)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Hook)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.PeekText)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.PeekChar)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Text)
def to_ir(self) -> parsing.ir.IR:
    return parsing.ir.Block([
        parsing.ir.ReturnOnEof(),
        parsing.ir.SaveCtx(),
        parsing.ir.GetC(),
        #parsing.ir.EqualBlock(self.char).block = parsing.ir.Block([
        #    parsing.ir.IncPos(),
        #    parsing.ir.ValidateCtx(),
        #    parsing.ir.Return()
        #]),
        #parsing.ir.RestoreCtx(),
        #parsing.ir.Return()
    ])

@meta.add_method(parsing.Char)
def to_ir(self) -> parsing.ir.IR:
    return parsing.ir.Block([
        parsing.ir.ReturnOnEof(),
        parsing.ir.SaveCtx(),
        parsing.ir.GetC(),
        #parsing.ir.EqualBlock(self.char).block = parsing.ir.Block([
        #    parsing.ir.IncPos(),
        #    parsing.ir.ValidateCtx(),
        #    parsing.ir.Return()
        #]),
        #parsing.ir.RestoreCtx(),
        #parsing.ir.Return()
    ])

@meta.add_method(parsing.Scope)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Directive)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Capture)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.DeclNode)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Bind)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Error)
def to_ir(self) -> parsing.ir.IR:
    pass

# concatenate all IR of a seq
@meta.add_method(parsing.Seq)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Alt)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Neg)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Complement)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Until)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.UntilChar)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.LookAhead)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Neg)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.RepOptional)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Rep0N)
def to_ir(self) -> parsing.ir.IR:
    pass

@meta.add_method(parsing.Rep1N)
def to_ir(self) -> parsing.ir.IR:
    pass
