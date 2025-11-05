#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Literal, Optional
from demo_agent.utils import obj2json


@dataclass
class Memento:
    subject: str
    key: str
    value: str
    confidence: float = 0

    def __repr__(self, threshold: float = 0) -> str:
        if threshold > 0 and self.confidence < threshold:
            return ""
        return f"\"{self.subject}\"'s {self.key} is {self.value}"

    @staticmethod
    def is_valid(mem) -> bool:
        if not isinstance(mem, dict):
            return False
        if len({"subject", "key", "value"} & mem.keys()) == 3:
            return True
        return False

    def to_json(self):
        return obj2json(self, ["subject", "key", "value", "confidence"])

    @staticmethod
    def from_json(j):
        return Memento(j["subject"], j["key"], j["value"], j.get("confidence", 0))


Role = Literal["system", "user", "assistant", "tool"]
Channel = Literal["analysis", "commentary", "final"]

@dataclass
class Message:
    role: Role
    content: str
    channel: Optional[Channel] = None
    constrain: Optional[str] = None
    timestamp: Optional[str] = None
    name: Optional[str] = None

    def __repr__(self):
        lead = '-'.join([i for i in [self.role, self.channel, self.constrain, self.timestamp, 
                                     self.name] if i is not None])
        return f"[{lead}] {self.content}"


    @staticmethod
    def from_json(j):
        return Message(j["role"], j["content"],
                       j.get("channel"), j.get("constrain"), j.get("timestamp"), j.get("name"))

    def to_json(self):
        return obj2json(self, ["role", "content", "channel", "constrain", "timestamp", "name"])

