# Change Report (2026-03-15): WebSocket Handshake 400 Fix Alignment

## Background

Python client previously received:

- `Handshake status 400 Bad Request`
- Server header showed `Mono-HTTPAPI/1.0`

This indicates TCP connection reached Unity HTTP server, but WebSocket handshake was rejected.

## Root Cause (Most Likely)

1. Endpoint path mismatch (Python using root path while Unity expects a specific path).
2. Handshake policy mismatch (Origin and/or Subprotocol constraints on Unity side).

## Python-Side Changes Completed

Files changed:

- `src/simulator/api.py`
- `docs/to_simulator/Format.md`

Code changes in `src/simulator/api.py`:

1. Default WS URL changed to:
   - `ws://localhost:8765/ws`
2. Added environment-driven handshake configuration:
   - `SIMULATOR_WS_URL` (full URL override)
   - `SIMULATOR_WS_ORIGIN` (optional)
   - `SIMULATOR_WS_SUBPROTOCOL` (optional)
3. `create_connection` now passes optional `origin` and `subprotocols` when configured.

Protocol doc updates in `docs/to_simulator/Format.md`:

1. Default endpoint updated to `/ws`.
2. Added handshake requirements and 400 troubleshooting.
3. Added explicit Unity implementation notes for endpoint, origin, subprotocol, and logging.

## Required Unity-Side Behavior

Unity server must implement these rules:

1. Expose a WebSocket endpoint path (recommended `/ws`).
2. Accept WebSocket upgrade requests on that exact path and return HTTP 101.
3. Return one JSON response per request message (`request_id` preserved).
4. If using Origin/Subprotocol validation, define and document accepted values.
5. Log rejection reasons for handshake failures (path mismatch, origin mismatch, protocol mismatch).

## Interface Contract Reminder

Request format (already aligned):

```json
{
  "request_id": "<uuid>",
  "timeout": -1,
  "team": "red",
  "command": "ChassisForwardAction",
  "value": {
    "distance": 1.0
  }
}
```

- `timeout = -1`: no Unity-side execution deadline.
- `timeout > 0`: enforce Unity-side execution timeout (milliseconds).

## Joint Debug Checklist

1. Confirm Unity actually listens at `ws://localhost:8765/ws`.
2. If Unity uses another path, set `SIMULATOR_WS_URL` accordingly.
3. If Unity checks Origin, set `SIMULATOR_WS_ORIGIN` to accepted value.
4. If Unity checks Subprotocol, set `SIMULATOR_WS_SUBPROTOCOL` to accepted value.
5. Re-test and ensure handshake returns HTTP 101 instead of 400.

## Suggested Environment Setup Example (PowerShell)

```powershell
$env:SIMULATOR_WS_URL = "ws://localhost:8765/ws"
$env:SIMULATOR_WS_ORIGIN = "http://localhost"
$env:SIMULATOR_WS_SUBPROTOCOL = "sense-react-v1"
python -m test.simulator_bot_control
```

Use `SIMULATOR_WS_ORIGIN` and `SIMULATOR_WS_SUBPROTOCOL` only if Unity requires them.
