# little grammar for test
from pyrser import grammar


class CSV(grammar.Grammar):
    entry = "csv"
    grammar = """
        csv = [ [@ignore("null") line : l #add_line(_, l)]+ eof ]

        line =
        [
            item : c #add_col(_, c)
            [';' item : c #add_col(_, c)]*
            eol
        ]

        item = [ [id | num] : i #add_item(_, i) ]
    """


class CSV2(grammar.Grammar, CSV):
    entry = "csv2"
    # copy the result of CSV.csv as result of csv2
    grammar = """
        csv2 = [ CSV.csv:>_ ]

        item = [ [CSV.item]?:>_ ]
    """
