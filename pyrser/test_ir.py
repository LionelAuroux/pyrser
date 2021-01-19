import sys
import logging
import pathlib as pl
from pyrser.parsing import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
here = pl.Path(__file__).resolve().parent

from pyrser import preproc

def test_ir_00():
    gram = Grammar("A",
        [("test1.pg", "B", "C"),
        ("test2.pg", "D", None),
        (None, "E", None),
        ],
        DeclRule("main",
            Rep0N(
                Alt(
                    Capture("toto", Text("hello")),
                    Text("World")
                )
            )
        ),
    )
    print(preproc.to_dsl(gram))
    assert False

    ###
    rules = []
    for it in preproc.loop_over(gram):
        if 'rules' in it:
            rules.append(it['rules'].name)
        if 'nodes' in it:
            rules.append(it['nodes'].name)
    assert rules == ['main', "toto"], "failed loop_over"

    rules = []
    for it in preproc.loop_over(gram, 'rules'):
        if 'rules' in it:
            rules.append(it['rules'].name)
    assert rules == ['main'], "failed loop_over"
