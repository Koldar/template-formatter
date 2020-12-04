from typing import Optional, Dict, Any, Callable

from template_formatter.ITemplateFormatter import ITemplateFormatter


class PythonFormatter(ITemplateFormatter):

    def __init__(self):
        self.__template_string: Optional[str] = None

    def init_string(self, string: str, app_context: "AppContext"):
        self.__template_string = string

    def init_file(self, f: str, encoding: str, app_context: "AppContext"):
        with open(f, "r", encoding=encoding) as handle:
            self.__template_string = handle.read().strip()

    def render_template(self, model: Dict[str, Any], commons: Dict[str, Any], functions: Dict[str, Callable]) -> str:
        return self.__template_string.format(model=model, commons=commons, **functions)

    def reset(self):
        self.__template_string = None