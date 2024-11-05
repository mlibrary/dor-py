import sys
import io
from unittest import TestCase
from contextlib import redirect_stdout, redirect_stderr

from pyrocfl import say_hello

def test_pyrocfl_say_hello_capture(capfd):
    say_hello()
    captured = capfd.readouterr()
    assert captured.out == "Hello from pyrocfl, implemented in Rust!\n"
    assert captured.err == ""

class PyrocflTest(TestCase):

    def setUp(self):
        return super().setUp()

    def test_pyrocfl_say_hello(self):
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            # test that say_hello prints to nothing to sys.stdout
            say_hello()
            self.assertEqual(out.getvalue(), "")
            print("Hello from Python")
            self.assertEqual(out.getvalue(), "Hello from Python\n")
            print("Error from Python", file=sys.stderr)
            self.assertEqual(err.getvalue(), "Error from Python\n")


