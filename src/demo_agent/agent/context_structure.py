#!/usr/bin/env python3

from demo_agent.agent.policy import Role

class OpenAIHarmony:
    def __init__(self):
        self.mode = "manual"

    def convert(self, role: Role, channel=None):
        if channel is None:
            return f"<|start|>"
