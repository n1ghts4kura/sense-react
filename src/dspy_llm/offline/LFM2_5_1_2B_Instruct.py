# dspy_llm/offline/LFM2_5_1_2B_Instruct.py
# Start an LLaMA Server for the LFM 2.5 1.2B Instruct model.
#
# @author n1ghts4kura
# @date 2026-03-22
#

from pathlib import Path
from subprocess import Popen

from .llama_server import (
    LLaMAServerSettings,
    LLaMAModelSettings,
    run_model as _run_model,
)


# Path to the model file (resolved relative to this file's directory)
_MODEL_DIR = Path(__file__).parent.parent.parent.parent / "model"
_MODEL_PATH = str(_MODEL_DIR / "LFM2.5-1.2B-Instruct-Q4_K_M.gguf")


def run_lfm25(
    server_settings: LLaMAServerSettings | None = None,
) -> Popen:
    """
    Run an LLaMA Server for the LFM 2.5 1.2B Instruct model.

    Args:
        server_settings: Server settings. Uses defaults if not provided.

    Returns:
        A Popen object representing the running server process.
    """
    if server_settings is None:
        server_settings = LLaMAServerSettings()

    model_settings = LLaMAModelSettings(
        model_path=_MODEL_PATH,
        alias="default",
    )

    return _run_model(model_settings, server_settings)
