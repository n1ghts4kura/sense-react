# react/executor.py
# The action executor in ReAct Layer.
#
# @author n1ghts4kura
# @date 2026-03-20
#

import dspy
from typing import Literal

from src.dspy_llm.online import deepseek_chat_lm
from src.simulator import red_tool_list, blue_tool_list


class ExecutorSignature(dspy.Signature):

    tasks: str = dspy.InputField(
        description = "你需要完成的宏观任务"
    )

    success: bool = dspy.OutputField(
        description = "是否成功完成**所有宏观任务**"
    )

    what_is_done: str = dspy.OutputField(
        description = "你已经完成了的任务"
    )

    what_is_not_done: str = dspy.OutputField(
        description = "你还没有完成的任务"
    )


def build_executor(team: Literal["red", "blue"]) -> dspy.ReAct:
    """
    Build the Executor Agent.
    
    Args:
        team(Literal["red", "blue"]): which robot to control.
    
    Return:
        dspy.ReAct: The Executor Agent.
    """

    agent = dspy.ReAct(
        signature = ExecutorSignature,
        tools = red_tool_list if team == "red" else blue_tool_list,
        max_iters = 500, # actually can't reach i think.
    )

    agent.set_lm(deepseek_chat_lm) # currently use deepseek for tests.

    return agent


__all__ = [
    "build_executor"
]
