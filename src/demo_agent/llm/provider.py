#!/usr/bin/env python3

import re
import json
import lmstudio as lms
from typing import List
from demo_agent.agent.policy import Message
from demo_agent.utils import logger

class Config:
    def __init__(self, name):
        self.model_name = name
        self.think_pattern = None
        name = self.model_name.split("/")[0]
        if name == "openai":
            self.analysis_pattern = re.compile(
                    r"<\|channel\|>analysis<\|message\|>(.*?)<\|end\|>$", re.DOTALL)
            self.call_pattern = re.compile(
                    r"<\|channel\|>commentary.*?<\|message\|>(.*)", re.DOTALL)
            self.final_pattern = re.compile(
                    r"<\|channel\|>final<\|message\|>$", re.DOTALL)
        elif name == "deepseek":
            self.think_pattern = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


activated_models = dict()
class Provider:
    def __init__(self, name="openai/gpt-oss-20b"):
        self.config = Config(name)
        self.model = lms.llm(name)
        activated_models[name] = self

    def __call__(self, prompt):
        return self.model.respond_stream(prompt)


def check_model_alive(name):
    return name in activated_models


class Advisor:

    def __init__(self, name, model_name, policy, tools):
        self.name = name
        if check_model_alive(model_name):
            self.provider = activated_models[model_name]
        else:
            self.provider = Provider(model_name)
        self.policy = policy
        self.tools = tools

    def _call(self, prompt, print_response) -> List[Message]:
        logger.debug(f"Prompt: {prompt}")
        tool_arguments = None
        is_final = False
        ret = []
        buf = ""
        for fragment in self.provider(prompt):
            piece = getattr(fragment, "content", str(fragment))
            buf += piece
            if m := self.provider.config.analysis_pattern.search(buf):
                ret.append(Message("assistant", m.group(1), channel="analysis"))
                buf = ""
                continue
            if m := self.provider.config.call_pattern.search(buf):
                tool_arguments = m.group(1)
                continue
            if self.provider.config.final_pattern.search(buf):
                is_final = True
                buf = ""
                continue
            if is_final and print_response:
                print(piece, end="", flush=True)

        if self.tools is not None and tool_arguments is not None and len(ret) > 0:
            # TODO: A trick for GPT-OSS, should use a general rule.
            # Assume the function name exists only in `analysis`.
            t_name = None
            for w in ret[-1].content.strip('.').split():
                if w in self.tools.tools:
                    t_name = w
            ret.append(Message("assistant", tool_arguments, channel="commentary"))
            t_out = self.tools.tools[t_name].func(**json.loads(tool_arguments))
            logger.info(f"Calling tool {t_name} with arguments {tool_arguments}, and get {t_out}")
            out_msg = Message("assistant", t_out, channel="commentary")
            ret.append(out_msg)
            ret.extend(self(prompt + "".join(self.policy.message_to_text(ret))))
            return ret

        ret.append(Message("assistant", buf, channel="final"))
        return ret

    def __call__(self, prompt, print_response=True) -> List[Message]:
        count = self.policy.retry_times
        while count > 0:
            try:
                return self._call(prompt, print_response)
            except Exception as e:
                count -= 1
                logger.error(f"Retry {count} times left, {e}")
        else:
            raise Exception(f"{__name__} retried {self.policy.retry_times} times but failed.)")

