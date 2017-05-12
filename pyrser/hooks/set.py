from pyrser import meta
from pyrser.parsing import Node
from pyrser.parsing.base import BasicParser


@meta.hook(BasicParser, "set")
def set_node(self, dst, src):
    """
        Basically copy one node to another.
        usefull to transmit a node from a terminal
        rule as result of the current rule.

        example::

            R = [
                In : node #set(_, node)
            ]

        here the node return by the rule In is
        also the node return by the rule R
    """
    if not isinstance(src, Node):
        dst.value = src
    else:
        dst.set(src)
        idsrc = id(src)
        iddst = id(dst)
        if iddst not in self.id_cache:
            print("DST: %s" % repr(dst))
            print("RULE_NODES %s" % repr(self.rule_nodes))
            print("IDCACHE %s" % repr(self.id_cache))
        if idsrc in self.id_cache:
            k = self.id_cache[idsrc]
            k2 = self.id_cache[iddst]
            if k in self.rule_nodes:
                self.tag_cache[k2] = self.tag_cache[k]
    return True


@meta.hook(BasicParser, "setcapture")
def set_node_as_int(self, dst, src):
    """
        Set a node to a value captured from another node

        example::

            R = [
                In : node #setcapture(_, node)
            ]
    """
    dst.value = self.value(src)
    return True

@meta.hook(BasicParser, "setint")
def set_node_as_int(self, dst, src):
    """
        Set a int literal to a node

        example::

            R = [
                In : node #setint(node, 12)
            ]
    """
    dst.value = int(src)
    return True


@meta.hook(BasicParser, "setstr")
def set_node_as_str(self, dst, src):
    """
        Set a str literal to a node

        example::

            R = [
                In : node #setstr(node, "toto")
            ]
    """
    dst.value = src
    return True


@meta.hook(BasicParser, "get")
def get_subnode(self, dst, ast, expr):
    """
        get the value of subnode

        example::

            R = [
                __scope__:big  getsomethingbig:>big
                #get(_, big, '.val') // copy big.val into _
            ]
    """
    dst.value = eval('ast' + expr)
    return True
