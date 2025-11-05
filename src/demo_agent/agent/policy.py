#!/usr/bin/env python3

import re
from typing import List, Dict, Any
from demo_agent.agent.data import Message


class DefaultPolicy:
    def __init__(self, project_name="default"):
        self.model_routes = {
            # default same with "chat" channel
            "chat": "gpt-oss-20b",
            "memorize": "gpt-oss-20b",
        }
        self.test_mode = False # Force do every steps ignoring the requirements.

        self.retry_times = 3

        self.history = "chats"
        self.max_history = 30
        self.min_history = 10

        self.permanent_memory = True
        self.memory = "memory"
        self.memory_saveup = f"data/pernanent_memory/{project_name}.memory.json"
        self.max_retrieve_memory = 10

    def system_prompt(self) -> str:
        return "".join(self.message_to_text([Message("system", (
            "You are a helpful, reliable assistant."
            "Prefer concise answer. Use tools when they materially improve accuracy."
            "Never reveal analysis, only output the final answer."
        ))]))

    def tool_prompt(self) -> str:
        return (
                "When the user asks a question:\n"
                "- Think first whether you need to use a tool from the tool box based on tool "
                "descriptions.\n"
                '- If yes, return a valid JSON block, and must answer based on the result of the '
                'tool\n'
                "- If not, answer directly in natural language based on Memory and Chats.\n"
                )

    @staticmethod
    def message_to_text(messages: List[Message]) -> List[str]:
        def _text(msg: Message):
            # OpenAI Harmony format
            ret = [f"<|start|>{msg.role}"]
            if msg.channel is not None:
                ret.append(f"<|channel|>{msg.channel}")
            if msg.constrain is not None:
                ret.append(f"<|constrain|>{msg.constrain}")
            ret.append(f"<|message|>{msg.content}<|end|>")
            return "".join(ret)

        ret = []
        for msg in messages:
            ret.append(_text(msg))
        return ret

    def choose_model(self, intent: str) -> str:
        return self.model_routes.get(intent, self.model_routes["chat"])

    def plan(self, history: List[Message], query: str) -> Dict[str, Any]:
        # TODO: Can make some judgements baseded on query and history.
        return {query: history}

    def validate_tool_args(self, name: str, args: Dict[str, Any]) -> None:
        if name == "math" and not isinstance(args.get("expressions"), str):
            raise ValueError("math.expressions must be a string")


class MemorizePolicy:
    text_pattern = re.compile(r'<\|message\|>.*?({.*})', re.DOTALL)
    def __init__(self):
        # TODO: Add policies for memorizing history when necessary.
        self.retry_times = 2
        self.confidence_threshold = 0
        return

    def text(self, msg: Message) -> str:
        if m := self.text_pattern.search(msg.content):
            return m.group(1)
        return str(dict())

    def system_prompt(self) -> str:
        return """
        You are a Memory Builder agent for an AI assistant.
        Your job is to compress conversation history AND extract long-term memories.

        Rules:

        - The assistant must not hallucinate facts not in the conversation.
        - If no memories, return an empty list.
        - Focus on facts that matter for future helpfulness.
        - This system supports OpenAI Harmony style messages.
        - Do NOT wrap JSON in markdown.
        - Do NOT call Function, just give the required JSON.
        
        Tasks:
        
        1) Summarize the history:
           - keep **facts, decisions, plans, problems, solutions**
           - remove filler, greetings, jokes, chit-chat
           - maintain clarity and neutrality
           - keep it as short as possible while preserving meaning
        
        2) Extract persistent memories:
           - Distinguish **USER vs ASSISTANT** info
           - Store identities, names, preferences, roles, goals, constraints, skills
           - Only store long-term helpful info (not short-lived context)
           - If user assigns a name or persona to the assistant and assistant accepts → store as assistant memory
           - Use atomic facts (1 piece of info per memory)
           - Avoid sensitive information unless user offered it
        
        3) Output format:
           - Output a JSON with `memories` with 4 keys (subject, key, value, confidence)
        
        JSON schema:
        {
         "memories": [
           {
             "subject": "user" | "assistant",
             "key": "name|role|preference|goal|profile|constraint|fact",
             "value": "<atomic fact>",
             "confidence": 0.0-1.0
           }
         ]
        }
        
        END INSTRUCTIONS.
        """

    @staticmethod
    def message_to_text(messages: List[Message]) -> List[str]:
        return DefaultPolicy.message_to_text(messages)


if __name__ == "__main__":
    mem_p = MemorizePolicy()
    text = """<|message|>User wants to be remembered as Jim.
            JSON:
        {
          "memories": [
            {
              "subject": "user",
              "key": "name",
              "value": "Jim",
              "confidence": 1.0
            }
          ]
        }"""
    print(mem_p.text(Message("system", text)))
