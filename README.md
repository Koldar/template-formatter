# Intoduction #

This project allows you to gnerate a file from a jinja2 template file

# Installation

```
pip install -i https://test.pypi.org/simple/ template-formatter
```

# Usage

This executable allows to customize templated strings or file according some criterion.
I have intended this application to be just a wrapper to jinja2. However, you can also pass a string
to the program according to other template syntaxes (e.g., f-strings or python `format`).

See the tests for usages of this program.

# For the developer

```
pip install -i https://test.pypi.org/simple/ pmake
pmake build install 
```