#!/usr/bin/env python3

from demo_agent.llm.provider import Advisor
from demo_agent.llm.prompts import Prompt
from demo_agent.agent.memory import Memory
from demo_agent.agent.policy import Message, DefaultPolicy, MemorizePolicy
from demo_agent.tools import Tools
from demo_agent.utils import logger

import logging
logger.setLevel(logging.WARNING)


class Runner:
    gpt_model = "openai/gpt-oss-20b"
    def __init__(self):
        policy = DefaultPolicy()
        memorizer = None
        if getattr(policy, "permanent_memory", False) is True:
            memorizer = Advisor("memorize", self.gpt_model, MemorizePolicy(), None)
        self.memory = Memory(policy, memorizer)
        self.prompt = Prompt(policy)
        self.tools = Tools(policy)
        self.advisor = Advisor("chat", self.gpt_model, policy, self.tools)

    def __call__(self, query):
        mem = [Message(role="user", content=query)]
        q = self.prompt.generator(mem, self.memory, self.tools)
        mem.extend(self.advisor(q))
        self.memory.insert("chats", mem, one_message=True)

if __name__ == "__main__":
    runner = Runner()
    try:
        while True:
            q = input(">> ")
            runner(q)
            print()
    except KeyboardInterrupt:
        logger.info("handling memories ...")
        runner.memory.clean_up()

