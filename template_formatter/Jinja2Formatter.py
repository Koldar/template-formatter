import os
from typing import Dict, Any, Callable

import jinja2
from jinja2 import BaseLoader

from template_formatter.ITemplateFormatter import ITemplateFormatter


class Jinja2Formatter(ITemplateFormatter):

    def __init__(self):
        self.__template_loader = None
        self.__env = None
        self.__template = None

    def init_string(self, string: str, app_context: "AppContext"):
        self.__template_loader = BaseLoader()
        self._setup_env(app_context)
        self.__template = self.__env.from_string(string)

    def init_file(self, f: str, encoding: str, app_context: "AppContext"):
        self.__template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.abspath(os.path.dirname(f)),
            encoding=encoding
        )
        self._setup_env(app_context)
        self.__template = self.__env.get_template(os.path.basename(f))

    def render_template(self, model: Dict[str, Any], commons: Dict[str, Any], functions: Dict[str, Callable]) -> str:
        return self.__template.render(
            # data
            model=model,
            commons=commons,
            # commons function (they are so popular that we put them on the cwd)
            **functions
        )

    def reset(self):
        self.__template_loader = None
        self.__env = None
        self.__template = None

    def _setup_env(self, app_context: "AppContext"):
        self.__env = jinja2.Environment(
            loader=self.__template_loader,
            block_start_string=app_context.block_start_string,
            block_end_string=app_context.block_end_string,
            variable_start_string=app_context.expression_start_string,
            variable_end_string=app_context.expression_end_string,
            comment_start_string=app_context.comment_start_string,
            comment_end_string=app_context.comment_end_string,
            line_statement_prefix=app_context.line_statement_prefix
        )