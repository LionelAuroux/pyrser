import unittest
from pyrser.error import *
from pyrser.parsing import *
from pyrser.passes.to_yml import *
import os


current_file = os.path.abspath(__file__)


class InternalError_Test(unittest.TestCase):

    def test_locationinfo_01(self):
        li = FileInfo(current_file, 1, 8)
        s = li.get_content()
        self.assertEqual(s,
                         ("from {f} at line:1 col:8 :\n".format(f=current_file)
                          + "import unittest\n%s^" % (' ' * 7)),
                         "Bad FileInfo.get_content")
        li = FileInfo(current_file, 1, 8, 8)
        s = li.get_content()
        self.assertEqual(s,
                         ("from {f} at line:1 col:8 :\n".format(f=current_file)
                          + "import unittest\n%s~~~~~~~~" % (' ' * 7)),
                         "Bad FileInfo.get_content")
        li = FileInfo.from_current()
        s = li.get_content()
        self.assertEqual(
            s,
            ("from {f} at line:26 col:9 :\n".format(f=current_file)
             + "{i}li = FileInfo.from_current()\n".format(i=(' ' * 8))
             + "{i}^".format(i=(' ' * 8))),
            "Bad FileInfo.get_content"
        )
        parser = Parser()
        parser.parsed_stream(
            "   this\n  is\n      a\n test stream",
            name="root"
        )
        parser.read_text("   this\n  is\n")
        st = StreamInfo(parser._stream)
        s = st.get_content()
        self.assertEqual(
            s,
            ("from root at line:3 col:1 :\n"
             + "      a\n"
             + "      ^"),
            "Bad FileInfo.get_content"
        )

    def test_notify_02(self):
        nfy = Notification(
            Severity.WARNING,
            "it's just a test",
            FileInfo(current_file, 1, 8)
        )
        s = nfy.get_content()
        self.assertEqual(
            s,
            ("warning : it's just a test\n"
             + "from {f} at line:1 col:8 :\n".format(f=current_file)
             + "import unittest\n%s^" % (' ' * 7)),
            "Bad FileInfo.get_content"
        )

    def test_diagnostic_03(self):
        diag = Diagnostic()
        diag.notify(
            Severity.ERROR,
            "Another Test",
            FileInfo(current_file, 1, 8)
        )
        diag.notify(
            Severity.WARNING,
            "Just a Test",
            FileInfo(current_file, 2, 6)
        )
        infos = diag.get_infos()
        self.assertEqual(infos, {0: 0, 1: 1, 2: 1}, "Bad Diagnostic.get_infos")
        self.assertTrue(diag.have_errors(), "Bad Diagnostic.have_errors")
        s = diag.get_content()
        self.assertEqual(
            s,
            ((("=" * 79) + '\n')
             + "error : Another Test\n"
             + "from {f} at line:1 col:8 :\n".format(f=current_file)
             + "import unittest\n"
             + (" " * 7) + '^' + '\n'
             + ('-' * 79) + '\n'
             + "warning : Just a Test\n"
             + "from {f} at line:2 col:6 :\n".format(f=current_file)
             + "from pyrser.error import *\n"
             + (" " * 5) + '^' + '\n'
             + ('-' * 79)
             ),
            "Bad Diagnostic.get_content"
        )
