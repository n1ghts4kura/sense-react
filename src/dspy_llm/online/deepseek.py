# dspy_llm/online/deepseek.py
# Use online DeepSeek API.
#
# @author n1ghts4kura
# @date 2026-03-20
#


import dspy

from dotenv import load_dotenv
load_dotenv()


deepseek_chat_lm = dspy.LM(
    model = "deepseek/deepseek-chat",
    temperature = 0.0,
    max_tokens = 8192,
)

deepseek_reasoner_lm = dspy.LM(
    model = "deepseek/deepseek-reasoner",
    temperature = 0.0,
    max_tokens = 8192,
)


__all__ = [
    "deepseek_chat_lm",
    "deepseek_reasoner_lm"
]
