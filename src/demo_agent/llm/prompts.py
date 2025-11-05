#!/usr/bin/env python3
from typing import List
from demo_agent.agent.data import Message


class Prompt:
    """
    <|start|>system<|message|>You are a helpful, reliable assistant.Prefer concise answer. 
    Use tools when they materially improve accuracy.Never reveal analysis, only output the final 
    answer.<|end|>
    When you use a tool, give information as a JSON format and must answer based on the output
    of the tool.
    [Memory]
    Your name is Mary.
    User's name is Tom.
    [Available tools]
    {"name": "math", "parameters": "an eval math string"}
    [Chats]
    <|start|>user<|message|>what is the result of 101/3+12/0.001-12/0.01, must use a tool<|end|>
    """
    def __init__(self, policy):
        self.policy = policy

    def generator(self, messages: List[Message], memory, tools):
        query = "\n".join(self.policy.message_to_text(messages))
        prompts = [self.policy.system_prompt()]
        need_tool = len(tool_desc := tools.get_description(query)) > 0
        if need_tool:
            prompts.append(self.policy.tool_prompt())

        if memory.exists(self.policy.memory):
            # Long-term memory
            mem = memory.retrieve([self.policy.memory], query, threshold=0.5)
            if len(mem) > 0:
                prompts.append('[Memory]')
                prompts.extend(mem)

        if need_tool:
            prompts.append("\n".join([
                "[Available Tools]",
                "\n".join(tool_desc)
            ]))

        prompts.append("\n[Chats]")
        if memory.exists(self.policy.history):
            prompts.extend(memory.latest(self.policy.history))

        prompts.append(query)
        return "\n".join(prompts)


