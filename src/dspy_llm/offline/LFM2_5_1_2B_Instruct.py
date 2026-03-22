# dspy_llm/offline/LFM2_5_1_2B_Instruct.py
# Manage multiple LFM 2.5 1.2B Instruct model instances.
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
    _get_next_port,
)


# Path to the model file (resolved relative to this file's directory)
_MODEL_DIR = Path(__file__).parent.parent.parent.parent / "model"
_MODEL_PATH = str(_MODEL_DIR / "LFM2.5-1.2B-Instruct-Q4_K_M.gguf")

# Running instances: name -> Popen
_instances: dict[str, Popen] = {}


def new(
    name: str,
    server_settings: LLaMAServerSettings | None = None,
) -> int:
    """
    Start a new LFM 2.5 1.2B Instruct model instance.

    Args:
        name: Unique name for this instance.
        server_settings: Server settings. Uses defaults if not provided.

    Returns:
        The port number the instance is listening on.

    Raises:
        ValueError: If an instance with the given name already exists.
    """
    if name in _instances:
        raise ValueError(f"Instance '{name}' already exists")

    port = _get_next_port()

    if server_settings is None:
        server_settings = LLaMAServerSettings()

    model_settings = LLaMAModelSettings(
        model_path=_MODEL_PATH,
        alias="default",
        port=str(port),
    )

    process = _run_model(model_settings, server_settings)
    _instances[name] = (process, port)

    return port


def stop(name: str) -> None:
    """
    Stop a running LFM 2.5 1.2B Instruct model instance.

    Args:
        name: Name of the instance to stop.

    Raises:
        ValueError: If no instance with the given name is found.
    """
    if name not in _instances:
        raise ValueError(f"Instance '{name}' not found")

    process, _ = _instances.pop(name)
    process.terminate()
    process.wait(timeout=10)
