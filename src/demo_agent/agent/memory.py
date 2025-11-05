#!/usr/bin/env python3

import json
from typing import List
from demo_agent.retriever.vectorstore import VectorStore
from demo_agent.agent.data import Message, Memento
from demo_agent.utils import read_json_file, JsonEncoder, logger


class Memory:
    def __init__(self, policy, memorizer) -> None:
        self.memories = dict() # {name: {"entries", "vector_space"}}
        self.message_to_text = (policy.message_to_text if hasattr(policy, "message_to_text") 
                                else lambda messages: [str(msg) for msg in messages])
        self.memorizer = memorizer
        if self.memorizer is not None:
            self.create("memory")
            # Keep mementos in RAM, and save to file when clean up.
            self.memory_in_ram = dict()
            if f := getattr(policy, "memory_saveup"):
                for k, v in read_json_file(f).items():
                    self.memory_in_ram[k] = Memento.from_json(v)
                values = [str(mem) for mem in self.memory_in_ram.values()]
                self.memories[policy.memory]["entries"].extend(values)
                self.memories[policy.memory]["vector_space"].insert(values)
        self.policy = policy
        self.test_mode = getattr(self.policy, "test_mode", False)

    def exists(self, name):
        return name in self.memories

    def create(self, name):
        if self.exists(name):
            return self.memories
        self.memories[name] = {"entries": list(), "vector_space": VectorStore()}

    def clean(self, name):
        del self.memories[name]

    def insert(self, name, messages: List[Message], one_message=False) -> None:
        if len(messages) == 0:
            return
        if not self.exists(name):
            self.create(name)
        if one_message is True:
            msg = ["\n".join(self.message_to_text(messages))]
        else:
            msg = self.message_to_text(messages)
        self.memories[name]["entries"].extend(msg)
        self.memories[name]["vector_space"].insert(msg)

        if self.test_mode is True:
            self.policy.max_history = 0
            self.policy.min_history = -len(self.memories[name]["entries"])
            self.pernanent_memory = True

        if (name == self.policy.history
                and self.policy.permanent_memory is True
                and len(self.memories[name]["entries"]) > self.policy.max_history):
            _mem_prompt = self.memorizer.policy.system_prompt() + "\n".join(
                    self.memories[name]["entries"][:-self.policy.min_history])
            logger.debug(f"Memorize prompt: {_mem_prompt}\n")
            if len(m := self.memorizer(_mem_prompt, print_response=False)) > 0:
                self._memorize(self.memorizer.policy.text(m[-1]))

            if self.test_mode is False:
                # Summarize all chat history and leave part chats in memory
                self.memories[name]["entries"] =\
                    self.memories[name]["entries"][-self.policy.min_history:]

    def _memorize(self, info) -> None:
        try:
            info = json.loads(info)
        except Exception:
            # If memorizer(llm) give memories in wrong fornat, the system will not memorize them.
            logger.warning(f"Memory not json format: {info}")
            return
        memories = []
        logger.info(f"Memory {info}")
        for mem in info.get("memories") or [info]:
            if Memento.is_valid(mem):
                k = "-".join([mem["subject"], mem["key"]])
                self.memory_in_ram[k] = Memento(**mem)
                memories.append(str(self.memory_in_ram[k]))
        self.memories[self.policy.memory]["entries"].extend(memories)
        self.memories[self.policy.memory]["vector_space"].insert(memories)

    def latest(self, name, k=3) -> List[str]:
        if not self.exists(name):
            return []
        if k > len(self.memories[name]["entries"]):
            return self.memories[name]["entries"]
        return self.memories[name]["entries"][-k:]

    def _restrieve(self, name, query, k, threshold) -> List[tuple[str, float]]:
        if not self.exists(name):
            return []
        return self.memories[name]["vector_space"].search(query, k, threshold)

    def retrieve(self, names:List[str], query:str, k=3, threshold=0.5) -> List[str]:
        if len(names) > 1:
            ret = []
            for n in names:
                ret.extend(self._restrieve(n, query, k, threshold))
            return [doc for doc, _ in sorted(ret, key=lambda x: x[1], reverse=True)]
        else:
            return [d for d, _ in self._restrieve(names[0], query, k, threshold)]

    def clean_up(self):
        if f := getattr(self.policy, "memory_saveup"):
            with open(f, "w") as fh:
                fh.write(json.dumps(self.memory_in_ram, cls=JsonEncoder, indent=4))

