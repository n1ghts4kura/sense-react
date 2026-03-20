# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SenseReAct is an agentic robot controlling framework enhanced by LLM and VLM. It has two main layers:

- **Sense Layer (Perception)**: Environment perception using traditional CV + VLM models
- **ReAct Layer (Reasoning/Execution)**: Strategic planning → behavior conversion → robot control指令

Python communicates with a Unity simulator via WebSocket for real robot control.

## Development Commands

```bash
# Install dependencies (uses venv)
pip install -r requirements.txt

# Set environment variables for simulator connection
export SIMULATOR_WS_URL=ws://localhost:8765/ws
export SIMULATOR_WS_ORIGIN=<origin>  # optional
export SIMULATOR_WS_SUBPROTOCOL=<protocol>  # optional
```

## Architecture

```
src/
├── simulator/       # Unity WebSocket communication
│   ├── api.py       # Action/Response Pydantic models + persistent WebSocket client
│   └── bot_controller.py  # TeamBotController (red/blue team)
├── dspy_llm/        # LLM integration via DSPy
│   └── online/deepseek.py  # DeepSeek API wrapper
├── react/           # ReAct execution layer (in development)
└── logger.py        # Singleton colored logging utility
```

## Key Design Decisions

**WebSocket Protocol** (`docs/to_simulator/LongConnectionDesign.md`):
- Persistent connection (not reconnect per request)
- Request/response correlated via `request_id`
- Two independent timeouts: `action.timeout` (Unity execution budget) and `conn_timeout` (Python transport wait)
- Responses arrive out-of-order; matched by `request_id`

**Simulator API** (`src/simulator/api.py`):
- All actions inherit from `Action` base class; responses inherit from `Response`
- `TeamBotController` provides typed methods for chassis/turret/fire/speed/health/ammo control
- Pre-created singletons: `red_bot_controller`, `blue_bot_controller`

**VLM/Perception** (`docs/SenseReAct.md`):
- Traditional perception (YOLO, RNN) produces factual structured output
- VLM (e.g., Qwen) takes traditional output + raw input, produces semantic description
- Degraded mode: if VLM fails, template fills in with traditional output + instability flag

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIMULATOR_WS_URL` | `ws://localhost:8765/ws` | Simulator WebSocket endpoint |
| `SIMULATOR_WS_ORIGIN` | unset | WebSocket origin header |
| `SIMULATOR_WS_SUBPROTOCOL` | unset | WebSocket subprotocol |

## Code Style

- Pydantic v2 for API models
- `src.logger.make_logger(module_name)` for module-level logging
- DSPy `dspy.Tool` for exposing bot controls as LLM-callable tools