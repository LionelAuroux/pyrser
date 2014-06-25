import unittest
from pyrser.error import *
from pyrser.parsing import *
from pyrser.passes.to_yml import *
import os


current_file = os.path.abspath(__file__)


class InternalError_Test(unittest.TestCase):

    def test_locationinfo_01(self):
        li = LocationInfo(current_file, 1, 8)
        s = li.get_content()
        self.assertEqual(s,
                         ("from {f} at line:1 col:8 :\n".format(f=current_file)
                          + "import unittest\n%s^" % (' ' * 7)),
                         "Bad LocationInfo.get_content")
        li = LocationInfo(current_file, 1, 8, 8)
        s = li.get_content()
        self.assertEqual(s,
                         ("from {f} at line:1 col:8 :\n".format(f=current_file)
                          + "import unittest\n%s~~~~~~~~" % (' ' * 7)),
                         "Bad LocationInfo.get_content")
        li = LocationInfo.from_here()
        s = li.get_content()
        self.assertEqual(
            s,
            ("from {f} at line:26 col:9 :\n".format(f=current_file)
             + "{i}li = LocationInfo.from_here()\n".format(i=(' ' * 8))
             + "{i}^".format(i=(' ' * 8))),
            "Bad LocationInfo.get_content"
        )
        parser = Parser()
        parser.parsed_stream(
            "   this\n  is\n      a\n test stream"
        )
        parser.read_text("   this\n  is\n")
        st = LocationInfo.from_stream(parser._stream, is_error=True)
        s = st.get_content()
        self.assertEqual(
            s,
            ("from {f} at line:3 col:1 :\n".format(f=st.filepath)
             + "      a\n"
             + "^"),
            "Bad LocationInfo.get_content"
        )

        def intern_func():
            li = LocationInfo.from_here(2)
            s = li.get_content()
            return s
        s = intern_func()
        self.assertEqual(
            s,
            ("from {f} at line:54 col:9 :\n".format(f=current_file)
             + "{i}s = intern_func()\n".format(i=(' ' * 8))
             + "{i}^").format(i=(' ' * 8)),
            "Bad LocationInfo.get_content"
        )

    def test_notify_02(self):
        nfy = Notification(
            Severity.WARNING,
            "it's just a test",
            LocationInfo(current_file, 1, 8)
        )
        s = nfy.get_content(with_locinfos=True)
        self.assertEqual(
            s,
            ("warning : it's just a test\n"
             + "from {f} at line:1 col:8 :\n".format(f=current_file)
             + "import unittest\n%s^" % (' ' * 7)),
            "Bad LocationInfo.get_content"
        )

    def test_diagnostic_03(self):
        diag = Diagnostic()
        diag.notify(
            Severity.ERROR,
            "Another Test",
            LocationInfo(current_file, 1, 8)
        )
        diag.notify(
            Severity.WARNING,
            "Just a Test",
            LocationInfo(current_file, 2, 6)
        )
        infos = diag.get_infos()
        self.assertEqual(infos, {0: 0, 1: 1, 2: 1}, "Bad Diagnostic.get_infos")
        self.assertTrue(diag.have_errors, "Bad Diagnostic.have_errors")
        s = diag.get_content(with_locinfos=True)
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
