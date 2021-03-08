# Intoduction #

This project allows you to generate a file from a jinja2 template file


# Installation

```
pip install template-formatter
```

# Motivating example

Often you need to create a file or a string according to a specific template. When you need to perform it in python, it is all fine and dandy.
However, the problem arises when you are dealing with a different programming language (e.g., C, Latex) that can perform said task, but in a much less easy way.
You can use this program to easiluy template files and string and then use them inside another environment.

# Usage

This executable allows to customize templated strings or file according some criterion.
I have intended this application to be just a wrapper to jinja2. However, you can also pass a string
to the program according to other template syntaxes (e.g., f-strings or python `format`).

See the tests for usages of this program. Here there is a non comprehensive ways to use this program

```
template-formatter --version

template-formatter --help

template-formatter --format="format" --writeOnStdout --value "foo" 3 --value "bar" 5 "{model.foo} + {model.bar}"
```

# For the developer

```
pip install -i https://test.pypi.org/simple/ pmake
pmake build install 
```