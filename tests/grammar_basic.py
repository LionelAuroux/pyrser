from collections import ChainMap
oldsetitem = ChainMap.__setitem__
def new_set_item(self, k, v):
    global oldsetitem
    print("SET IN CM: %s %s" % (k, v))
    return oldsetitem(self, k, v)
ChainMap.__setitem__ = oldsetitem

import unittest
import pyrser
from pyrser import Grammar, meta, parsing


class GrammarBasic_Test(unittest.TestCase):
    def test_01_list_word(self):
        # directive must be declare before class definition
        @meta.directive(pyrser.parsing.Parser, "ignore")
        class Ignore(parsing.DirectiveWrapper):
            def begin(self, parser, convention: str):
                if convention == "null":
                    parser.push_ignore(parsing.Parser.ignore_null)
                return True
            def end(self, parser, convention: str):
                parser.pop_ignore()
                return True
        class   WordList(Grammar):
            grammar = """
                wordlist ::= [word:w #add_to(wordlist, w)]+
                ;

                word ::= @ignore("null") ['a'..'z'|'A'..'Z']+
                ;
            """
            entry = "wordlist"

        @meta.hook(parsing.Parser)
        def add_to(self, mylist, word):
            if not hasattr(mylist, 'lst'):
                mylist.lst = [word.value]
            else:
                mylist.lst.append(word.value)
            return True
        res = WordList().parse("ab cd ef gh")
        print("%r" % res.lst)
