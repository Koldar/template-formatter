from typing import Optional, Dict, Any, Callable

from template_formatter.ITemplateFormatter import ITemplateFormatter


class PythonFormatFormatter(ITemplateFormatter):

    def __init__(self):
        self.__template_string: Optional[str] = None

    def init_string(self, string: str, app_context: "AppContext"):
        self.__template_string = string

    def init_file(self, f: str, encoding: str, app_context: "AppContext"):
        with open(f, "r", encoding=encoding) as handle:
            self.__template_string = handle.read().strip()

    def render_template(self, model: Dict[str, Any], commons: Dict[str, Any], functions: Dict[str, Callable]) -> str:
        global_dict = dict()
        global_dict["model"] = model
        global_dict["commons"] = commons
        global_dict["functions"] = functions
        for k, v in functions.items():
            global_dict[k] = v
        return self.__template_string.format(**global_dict)

    def reset(self):
        self.__template_string = None
