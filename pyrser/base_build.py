#!/usr/bin/env python3

from pyrser import builder
import pathlib as pl

if __name__ == "__main__":
    here = pl.Path(__file__).resolve().parent
    builder.compile(here / "Base")
