import unittest

from pyrser import fmt

class InternalFmt_Test(unittest.TestCase):
    def test_00(self):
        """Test pprint functions"""
        data = fmt.block("{", "}", ['a', 'b', 'c'])
        self.assertEqual(str(data), "{abc}", "Failed to format block")
        data = fmt.sep(",", ['a', 'b', 'c'])
        self.assertEqual(str(data), "a,b,c", "Failed to format sep")
        data = fmt.block("{", "}", [fmt.sep(",", ['a', 'b', 'c'])])
        self.assertEqual(str(data), "{a,b,c}", "Failed to format block/sep")
        data = fmt.sep(",", [fmt.block("{", "}", ['a', 'b']), fmt.block("{", "}", ['c', 'd'])])
        self.assertEqual(str(data), "{ab},{cd}", "Failed to format sep/block")
        data = fmt.end(";\n", ['a', 'b', 'c'])
        self.assertEqual(str(data), "a;\nb;\nc;\n", "Failed to format a list end by ';\n'")
        data = fmt.tab(fmt.block("{\n", "}\n", ['a\n', 'b\n', 'c\n']))
        self.assertEqual(str(data), "{tab}{{\n{tab}a\n{tab}b\n{tab}c\n{tab}}}\n".format(tab= (" " * 4)),
            "Failed to indent")
        data = fmt.block("{\n", "}\n", [fmt.tab(['a\n', 'b\n', 'c\n'])])
        self.assertEqual(str(data), "{{\n{tab}a\n{tab}b\n{tab}c\n}}\n".format(tab= (" " * 4)),
            "Failed to indent")
        data = fmt.block("{\n", "}\n", [fmt.tab(fmt.end("\n", ['a', 'b',
                        fmt.tab(fmt.block("[\n", "]", ['b\n', 'g\n', 'o\n', 'e\n'])), 'c']))])
        self.assertEqual(str(data), ("{{\n{tab}a\n{tab}b\n"
                    + "{tab}[\n{tab}b\n{tab}g\n{tab}o\n{tab}e\n{tab}]\n"
                    + "{tab}c\n}}\n").format(tab= (" " * 4)),
            "Failed to indent")
        data = fmt.block("{\n", "}\n", [fmt.tab(fmt.end("\n", ['a', 'b',
                        fmt.block("[\n", "]", [fmt.tab(fmt.tab(['b\n', 'g\n', 'o\n', 'e\n']))]), 'c']))])
        self.assertEqual(str(data), ("{{\n{tab}a\n{tab}b\n"
                    + "{tab}[\n{tab2}b\n{tab2}g\n{tab2}o\n{tab2}e\n{tab}]\n"
                    + "{tab}c\n}}\n").format(tab=(" " * 4), tab2=(" " * 8)),
            "Failed to indent")

        data = fmt.block("{\n", "}\n", fmt.tab(['a\n', fmt.block("{\n", "}\n",
                    fmt.tab(['d\n', 'e\n', 'f\n'])), 'c\n']))
        self.assertEqual(str(data), ("{{\n{tab}a\n"
                    + "{tab}{{\n{tab2}d\n{tab2}e\n{tab2}f\n{tab}}}\n"
                    + "{tab}c\n}}\n").format(tab=(" " * 4), tab2=(" " * 8)),
            "Failed to indent")
        data = fmt.block("{\n", "}\n", fmt.tab(fmt.block("{\n", "}\n",
                fmt.tab(fmt.end(";\n", ["a", "b", "c"])))))
        self.assertEqual(str(data), ("{{\n{tab}{{\n"
                    + "{tab2}a;\n{tab2}b;\n{tab2}c;\n"
                    + "{tab}}}\n}}\n").format(tab=(" " * 4), tab2=(" " * 8)),
            "Failed to indent")
