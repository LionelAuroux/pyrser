#from types import DictType, ListType
from copy import copy

from functools import wraps


def new_node(oParent, sType=None):
    if oParent is not None and id(oParent) in oParent:
        oNode = oParent[id(oParent)]
        oNode['parent'] = oParent
# FIXME : faire tests pour savoir si c'est bon
        # del oParent[id(oParent)]
    else:
        oNode = {'parent': oParent}

    if sType is not None and 'type' not in oNode:
        oNode['type'] = sType
    return oNode


def node(sType=None):
    def wrapper(oTarget):
        @wraps(oTarget)
        def wrapped(*lArgs):
            #if type(lArgs[0]) != DictType:
            if type(lArgs[0]) is not dict:
                oNode = new_node(lArgs[1], sType)
                bRes = oTarget(lArgs[0], oNode)
            else:
                oNode = new_node(lArgs[0], sType)
                bRes = oTarget(oNode)
            return bRes
        return wrapped
    return wrapper


def clean_tree(oParent, sName):
    #if type(oParent) == DictType:
    if type(oParent) is dict:
        for iKey, iValue in oParent.iteritems():
            if iKey != 'parent'\
                    and iValue != oParent:
                clean_tree(iValue, sName)
        if sName in oParent:
            del oParent[sName]
    #elif type(oParent) == ListType:
    elif type(oParent) is list:
        for iValue in oParent:
            if iValue != oParent:
                clean_tree(iValue, sName)


def slide(oNode, sName):
    oTmp = copy(oNode)
    oNode.clear()
    if id(oNode) in oTmp:
        del oTmp[id(oNode)]
    oNode[sName] = oTmp

    oNode['parent'] = oTmp['parent']
    oTmp['parent'] = oNode
    return oNode


def next(oNode, sName):
    if sName not in oNode:
        oNode[sName] = {"parent": oNode}
    oNode[id(oNode)] = oNode[sName]
    return oNode


def next_is(oNode, oSubNode):
    oNode[id(oNode)] = oSubNode
    return oNode


def next_clean(oNode):
    if id(oNode) in oNode:
        del oNode[id(oNode)]
    return oNode


def has_next(oNode):
    return id(oNode) in oNode


#### ADD A BASE CLASS FOR NODES

class ParserTree:
    pass


class Node(dict):
    """
    Base class for node manipulation
    """
    def __init__(self, val=True):
        if type(val) == bool:
            self._bool = val
        elif type(val) == Node:
            self._bool = val._bool
        else:
            raise Exception("Construction Node from Node or Boolean")

    def __bool__(self):
        return self._bool

    def __str__(self):
        items = []
        if len(self) > 0:
            items.append(repr(self))
        for k, v in vars(self).items():
            if isinstance(v, ParserTree):
                items.append(".%s = %s" % (k, v.dumpParseTree()))
            else:
                items.append(".%s = %s" % (k, repr(v)))
        return ", ".join(items)
