import abc
from typing import Dict, Any, Callable


class ITemplateFormatter(abc.ABC):

    @abc.abstractmethod
    def init_string(self, string: str, app_context: "AppContext"):
        pass

    @abc.abstractmethod
    def init_file(self, f: str, encoding: str, app_context: "AppContext"):
        pass

    @abc.abstractmethod
    def render_template(self, model: Dict[str, Any], commons: Dict[str, Any], functions: Dict[str, Callable]) -> str:
        pass

    @abc.abstractmethod
    def reset(self):
        pass