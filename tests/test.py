import unittest
from unittest.mock import patch
from io import StringIO
from typing import Callable

from template_formatter import version
from template_formatter.main import main


class MyTestCase(unittest.TestCase):

    def assertStdoutEqual(self, expected:str, actual_func: Callable[[], str]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            actual_func()
            self.assertEqual(fake_out.getvalue(), expected + "\n")

    def assertStdoutContains(self, expected:str, actual_func: Callable[[], str]):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            actual_func()
            self.assertTrue(fake_out.getvalue() in expected)

    # def test_help(self):
    #     self.assertStdoutContains("template-formatter [-h]", lambda: main(["test", "--help"]))

    def test_version(self):
        self.assertStdoutEqual(str(version.VERSION), lambda: main(["test", "--version"]))

    def test_01(self):
        self.assertStdoutEqual("Hello Pluto!", lambda: main([
                                                             '--configFile', "config.toml",
                                                             '--writeOnStdout',
                                                             "Hello {{ model.name }}!"]))

    def test_02(self):
        self.assertStdoutEqual("Hello World!!", lambda: main([
                                                              "--configFile", "config.toml",
                                                              "--writeOnStdout",
                                                              "--value", "surname", "World!",
                                                              "Hello {{ model.surname }}!"]))

    def test_03(self):
        self.assertStdoutEqual("Hello World!!", lambda: main([
                                                              "--configFile", "config.toml",
                                                              "--writeOnStdout",
                                                              "--value", "person.surname", "World!",
                                                              "Hello {{ model.person.surname }}!"]))

    def test_04(self):
        self.assertStdoutEqual("Hello  Mario and  Paolo and !", lambda: main([
                                                            "--configFile", "config.toml",
                                                            "--writeOnStdout",
                                                            "--value", "persons[0].surname", "Mario",
                                                            "--value", "persons[1].surname", "Paolo",
                                                            "Hello {% for p in model.persons %} {{ p.surname }} and {%endfor %}!"]))


if __name__ == '__main__':
    unittest.main()
