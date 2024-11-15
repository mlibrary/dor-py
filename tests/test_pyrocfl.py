from pyrocfl import say_hello
from pyrocfl import propagate_rocfl_error
from pyrocfl import Number

# pytest
import sys
import io

def test_pyrocfl_say_hello_capture(capfd):
    say_hello()
    captured = capfd.readouterr()
    assert captured.out == "Hello from pyrocfl, implemented in Rust!\n"
    assert captured.err == ""

# unittest
from unittest import TestCase
from contextlib import redirect_stdout, redirect_stderr

class PyrocflTest(TestCase):

    def setUp(self):
        return super().setUp()

    def test_pyrocfl_say_hello(self):
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            print("Hello from Python")
            self.assertEqual(out.getvalue(), "Hello from Python\n")
            print("Error from Python", file=sys.stderr)
            self.assertEqual(err.getvalue(), "Error from Python\n")
            say_hello()
            self.assertNotEqual(out.getvalue(), "Hello from pyrocfl, implemented in Rust!\n")

    def test_error_propagation(self):
        with self.assertRaisesRegex(ValueError, "rocfl error"):
            propagate_rocfl_error()

    # @unittest.skip("TODO")
    def test_pyrocfl_number(self):
        n = Number(1)
        self.assertEqual(str(n), "1")
