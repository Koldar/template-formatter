import pprint
from typing import Dict, Any, Callable, List, Optional


class ValueKeyNotFound(Exception):

    def __init__(self, key, dictonary):
        self.key = key
        self.dictionary = dictonary


class DynamicObject(object):

    _slots = "_dictionary", "_list", "_value"

    def __init__(self):
        self._dictionary: Optional[Dict[str, Any]] = None
        self._list: Optional[List[Any]] = None
        self._value: Any = None

    def __getattr__(self, item: str) -> Any:

        if item in self._slots:
            return self.__dict__[item]
            # object.__getattribute__(self, item)
        elif item in '__len__':
            return self.__len__
        else:
            if self._dictionary is None:
                self._dictionary = {}

            if item not in self._dictionary:
                self._dictionary[item] = DynamicObject()
            return self._dictionary[item]

    def __contains__(self, item):
        if self._dictionary is None:
            self._dictionary = {}
        return item in self._dictionary

    def __iter__(self):
        if self._dictionary is not None:
            return iter(self._dictionary)
        elif self._list is not None:
            return iter(self._list)
        else:
            return iter(self._value)

    def __getitem__(self, item: int):
        if self._list is None:
            self._list = []
        while True:
            if 0 <= item < len(self._list):
                break
            self._list.append(DynamicObject())
        return self._list[item]

    def set_field(self, k: str, v: Any):
        if self._dictionary is None:
            self._dictionary = {}
        self._dictionary[k] = v

    def set_value(self, v: Any):
        self._value = v

    def __str__(self) -> str:
        if self._list is not None:
            return "[" + ', '.join(map(str, self._list)) + "]"
        elif self._dictionary is not None:
            return "{" + ', '.join(map(lambda x: f"{x[0]}={x[1]}", self._dictionary.items())) + "}"
        else:
            # it is a value
            return str(self._value)


class Jinja2Model(object):

    def __init__(self):
        self.values: DynamicObject = DynamicObject()
        self.functions: Dict[str, Callable] = {}
        self.commons: Dict[str, Any] = {}

    def __str__(self) -> str:
        pp = pprint.PrettyPrinter(indent=4, sort_dicts=True)
        obj = {
            "values": self.values,
            "functions": self.functions,
            "commons": self.commons
        }
        return pp.pformat(obj)