# dspy_llm/offline/llama_server.py
# Start an LLaMA Server for a single model.
#
# @author n1ghts4kura
# @date 2026-03-22
#

from time import sleep
from typing import Literal
from pydantic import BaseModel, Field
from subprocess import DEVNULL, Popen


_current_port = 9000


class LLaMAServerSettings(BaseModel):
    """
    Settings for an LLaMA Server.
    """

    # Number of CPU threads to use during generation
    threads: int = Field(default=4)

    # The thread/process priority of the server
    priority: Literal[-1, 0, 1, 2, 3] = Field(default=0)

    # Size of the prompt context
    ctx_size: int = Field(default=0, le=8192)

    # Set Flash Attention use
    flash_attn: Literal["on", "off", "auto"] = Field(default="on")

    # KV cache offloading (default: enabled)
    kv_offload: bool = Field(default=True)

    # Logging
    logging: bool = Field(default=False)


class LLaMAModelSettings(BaseModel):
    """
    Settings for an model.
    """

    # Where to storage the model
    model_path: str = Field()

    # Seed
    seed: str = Field(default="-1")

    # Temperature
    temperature: float = Field(default=0.0) 

    # Top-k
    top_k: int = Field(default=40)

    # Top-p
    top_p: float = Field(default=0.95)

    # Model name (using for import)
    alias: str = Field(default="default")

    # Host
    host: str = Field(default="0.0.0.0")

    # Port 
    port: str = Field(default_factory=lambda: str(_current_port))


def _get_next_port() -> int:
    """
    Get the next available port and increment the counter.
    """
    global _current_port
    port = _current_port
    _current_port += 1
    return port


def run_model(
    model_settings: LLaMAModelSettings,
    server_settings: LLaMAServerSettings
) -> Popen:
    """
    Run an LLaMA Server for a single model.

    Args:
        model_settings: The settings for the model.
        server_settings: The settings for the server.

    Returns:
        A Popen object representing the running server process.
    """

    global _current_port

    cmd = [
        "llama-server",
        "--model", model_settings.model_path,
        "--host", model_settings.host,
        "--port", model_settings.port,
        "--threads", str(server_settings.threads),
        "--prio", str(server_settings.priority),
        "--ctx-size", str(server_settings.ctx_size),
        "--flash-attn", server_settings.flash_attn,
        "--kv-offload" if server_settings.kv_offload else "--no-kv-offload",
        "--log-disable" if not server_settings.logging else None,
        "--seed", model_settings.seed,
        "--temp", str(model_settings.temperature),
        "--top-k", str(model_settings.top_k),
        "--top-p", str(model_settings.top_p),
        "--alias", model_settings.alias
    ]
    cmd = [c for c in cmd if c is not None]

    process = Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # Wait 15 seconds for the server to start
    sleep(15)

    if process.poll() is not None:
        # The process has already exited, which means it failed to start
        raise RuntimeError(f"Failed to start LLaMA Server for model {model_settings.alias}")

    return process
