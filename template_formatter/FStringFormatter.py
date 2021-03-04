from typing import Dict, Any, Callable, Optional

from template_formatter.ITemplateFormatter import ITemplateFormatter


class FStringFormatter(ITemplateFormatter):

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
        # we assume in __template_string there is a string endpoint
        result = eval("f\"\"\"" + self.__template_string + "\"\"\"", global_dict, {})
        # it is a string, hence we need to remove the trailing characters
        return result.strip('\'\"')

    def reset(self):
        self.__template_string = None
