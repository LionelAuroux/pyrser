from pyrser.parsing.functors import *
from pyrser import grammar as g
import pyrser.ast.psl as psl

class Skip2(Functor):
    pass

def add_skip1(capture, user_data):
    print("captured nodes %s" % repr(capture))
    a = capture['b']

def add_skip2(capture, user_data):
    print("captured nodes %s" % repr(capture))
    s = capture['s']
    a = capture['a']
    idx = s.ptlist.index(a)
    if idx:
        s.ptlist.insert(idx, Skip2())


class Transform:
    def __init__(self):
        self.psl_expr = psl.PSL()
        self.psl_comp = self.psl_expr.compile("""
        {
            Seq([*:Leaf?(...) -> a , ...], ...) -> s => #addskip2;
            Leaf?(...) -> b => #addskip1;
        }
        """)

    def transform_rules(self, rname: str, rcode: Functor) -> None:
        # transorm a Functor object
        print("%s: %r" % (rname, rcode))
        d = {"addskip1": add_skip1, "addskip2": add_skip2}
        psl.match(rcode, self.psl_comp, d, None)
        

    def transform(self, rules) -> None:
        for rname, rcode in rules.items():
            if issubclass(type(rcode), Functor):
                self.transform_rules(rname, rcode)
            else:
                # TODO: transform a function
                pass

    def transform_grammar(self, gram: g.Grammar) -> None:
        # transform grammar ancestor first
        for subg in reversed(gram._rules.maps):
            self.transform(subg)
