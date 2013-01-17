# Copyright (C) 2012 Candiotti Adrien
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

#from types import DictType, ListType
from copy import copy

from functools import wraps


def new_node(oParent, sType=None):
    if oParent != None\
            and id(oParent) in oParent:
        oNode = oParent[id(oParent)]
        oNode['parent'] = oParent
# FIXME : faire tests pour savoir si c'est bon
        # del oParent[id(oParent)]
    else:
        oNode = {'parent': oParent}

    if sType != None\
            and 'type' not in oNode:
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
