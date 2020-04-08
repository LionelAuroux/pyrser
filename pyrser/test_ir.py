import sys
import logging
import pathlib as pl

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
here = pl.Path(__file__).resolve().parent

def test_ir_00():
    from pyrser.parsing import *
    pass
