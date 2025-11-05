#!/usr/bin/env python3

import logging
import json
from demo_agent.tools.math import math_func
from typing import Callable, Dict, List
from dataclasses import dataclass


@dataclass
class Tool:
    description: str
    arguments: Dict[str, str]
    func: Callable

    def __repr__(self) -> str:
        return self.description


class Tools:
    def __init__(self, policy):
        self.policy = policy
        self.tools = {
                "math_tool": Tool(
                    description="A tool for doing math.",
                    arguments={"expression": "string"},
                    func=math_func
                    ),
                "browse_tool": Tool(
                    description="A tool for searching internet by search engine.",
                    arguments={"query": "string"},
                    func=math_func
                    )
            }

    @staticmethod
    def _text(tool: Tool) -> str:
        return str(tool)

    def _retrieve(self, query, k=10, threshold=0.1):
        return self.tools

    def get_description(self, query) -> List[str]:
        ret = []
        for name, tool in self._retrieve(query).items():
            ret.append(f'["name": "{name}", "descroption": "{tool.description}", '
                       f'"arguments": {json.dumps(tool.arguments)}]')
        return ret


import sys
import inspect
def print_classes_in_current_module():
    current_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj):
            print(name, obj)

