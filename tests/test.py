import os
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
        self.assertStdoutEqual(str(version.VERSION), lambda: main([
            "test", "--version"
        ]))

    def test_01(self):
        self.assertStdoutEqual("Hello Pluto!", lambda: main([
            '--configFile', "config.toml",
            '--writeOnStdout',
            "Hello {{ model.name }}!"
        ]))

    def test_02(self):
        self.assertStdoutEqual("Hello World!!", lambda: main([
            "--configFile", "config.toml",
            "--writeOnStdout",
            "--value", "surname", "World!",
            "Hello {{ model.surname }}!"
        ]))

    def test_03(self):
        self.assertStdoutEqual("Hello World!!", lambda: main([
            "--configFile", "config.toml",
            "--writeOnStdout",
            "--value", "person.surname", "World!",
            "Hello {{ model.person.surname }}!"
        ]))

    def test_04(self):
        self.assertStdoutEqual("Hello  Mario and  Paolo and !", lambda: main([
            "--configFile", "config.toml",
            "--writeOnStdout",
            "--value", "persons[0].surname", "Mario",
            "--value", "persons[1].surname", "Paolo",
            "Hello {% for p in model.persons %} {{ p.surname }} and {%endfor %}!"
        ]))

    def test_05(self):
        self.assertStdoutEqual("Hello Pluto!", lambda: main([
            '--configFile', "config.toml",
            '--format', 'format',
            '--writeOnStdout',
            "Hello {model.name}!"
        ]))

    def test_06(self):
        self.assertStdoutEqual("Hello Pluto!", lambda: main([
            '--configFile', "config.toml",
            '--format', 'format',
            '--writeOnStdout',
            "Hello {model.name}!"
        ]))

    def test_07(self):
        self.assertStdoutEqual("Hello Pluto 42!", lambda: main([
            '--configFile', "config.toml",
            '--format', 'format',
            '--writeOnStdout',
            "Hello {model.name} {model.age}!"
        ]))

    def test_08(self):
        self.assertStdoutEqual("Hello Pluto 042!", lambda: main([
            '--configFile', "config.toml",
            '--format', 'format',
            '--writeOnStdout',
            "Hello {model.name} {model.age:03}!"
        ]))

    def test_09(self):
        self.assertStdoutEqual("Hello Paolo!", lambda: main([
            '--configFile', "config.toml",
            '--format', 'format',
            '--writeOnStdout',
            "--value", "persons[0].surname", "Mario",
            "--value", "persons[1].surname", "Paolo",
            """Hello {model.persons[1].surname}!"""
        ]))

    def test_10(self):
        self.assertStdoutEqual("Hello  a and  a and !", lambda: main([
            "--configFile", "config.toml",
            "--writeOnStdout",
            "--value", "persons[0].surname", "Mario",
            "--value", "persons[1].surname", "Paolo",
            "Hello {% for p in model.persons %} {{ functions.replace_with_a(p.surname) }} and {%endfor %}!"
        ]))

    def test_11(self):
        self.assertStdoutEqual("Hello  a and  a and !", lambda: main([
            "--configFile", "config.toml",
            "--writeOnStdout",
            "--value", "persons[0].surname", "Mario",
            "--value", "persons[1].surname", "Paolo",
            "Hello {% for p in model.persons %} {{ replace_with_a(p.surname) }} and {%endfor %}!"
        ]))

    def test_12(self):
        self.assertStdoutEqual("Hello Pluto!", lambda: main([
            '--configFile', "config.toml",
            '--format', 'fstring',
            '--writeOnStdout',
            """'Hello {model.name}!'"""
        ]))

    def test_13(self):
        self.assertStdoutEqual("Hello a!", lambda: main([
            '--configFile', "config.toml",
            '--format', 'fstring',
            '--writeOnStdout',
            """'Hello {replace_with_a(model.name)}!'"""
        ]))

    def test_14(self):
        self.assertStdoutEqual("Hello Pluto!\n", lambda: main([
            '--configFile', "config.toml",
            '--format', 'python',
            '--writeOnStdout',
            """print(f'Hello {model.name}!')"""
        ]))

    def test_15(self):
        self.assertStdoutEqual("Hello 1, 2, 3\n", lambda: main([
            '--configFile', "config.toml",
            '--format', 'python',
            '--writeOnStdout',
            """print("Hello " + ', '.join(map(str, [1,2,3])))"""
        ]))

    def test_16(self):
        main([
            '--configFile', "config.toml",
            "--inputDirectory", f"""{os.path.join(os.getcwd(), "input", "foo")}""",
            '--trailingStringTemplateFile', '.template',
            f"--outputDirectory", f"""{os.path.join(os.getcwd(), "output", "foo")}""",
            '--format', 'fstring',
        ])

    def test_17(self):
        main([
            '--configFile', "config.toml",
            "--inputDirectory", f"""{os.path.join(os.getcwd(), "input", "foo2")}""",
            '--trailingStringTemplateFile', '.template',
            f"--outputDirectory", f"""{os.path.join(os.getcwd(), "output/foo2")}""",
            '--format', 'fstring',
        ])


if __name__ == '__main__':
    unittest.main()
