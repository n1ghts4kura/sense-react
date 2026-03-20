# dspy_llm/online/deepseek.py
# Use online DeepSeek API.
#
# @author n1ghts4kura
# @date 2026-03-20
#


import dspy
from typing import Literal

from dotenv import load_dotenv
load_dotenv()


class DeepSeekLM(dspy.LM):

    def __init__(
        self,
        type: Literal["chat", "reasoner"] = "chat",
        *args,
        **kwargs
    ):
        super().__init__(
            model = f"deepseek/deepseek-{type}",
            model_type = "chat",
            *args,
            **kwargs
        )
