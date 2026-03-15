# Unity-Python WebSocket Long Connection Design

## 1. Purpose

This document defines a production-oriented long-connection design for simulator control between Python and Unity.
Both coding agents (Python side and Unity side) must implement based on this document.

Primary goal:

- Keep one persistent WebSocket connection per Python process instead of reconnecting for every action.

Expected benefit:

- Lower latency for frequent commands.
- Fewer handshake failures under high request frequency.
- Better control over reconnect, timeout, and observability.

## 2. Scope and Compatibility

In scope:

- Transport-layer redesign from short connection to long connection.
- Request/response correlation using `request_id`.
- Reconnect, heartbeat, and graceful shutdown behavior.

Out of scope:

- Business command schema changes.
- New action command types.

Compatibility rule:

- Message packet format remains the same as in `docs/to_simulator/Format.md`.
- Existing fields are preserved: `request_id`, `timeout`, `team`, `command`, `value`.

## 3. Shared Protocol Contract for Long Connection

## 3.1 One request, one response

For each request packet sent by Python:

1. Unity must return exactly one JSON response.
2. Response `request_id` must exactly match request `request_id`.
3. Responses can arrive out of order across requests.

Implication:

- Python must dispatch responses by `request_id` (not by send order).

## 3.2 Timeout semantics (unchanged)

- `action.timeout` (packet field `timeout`): Unity-side execution budget in ms.
  - `-1` means no execution deadline.
  - `> 0` means bounded execution.
- `conn_timeout` (Python local): transport wait timeout in ms.

These two timeouts are independent and must not be merged.

## 3.3 Error response format

When request handling fails, Unity should still return a response with same `request_id`:

```json
{
  "request_id": "<same-as-request>",
  "success": false,
  "value": "error: <reason>"
}
```

## 4. Python Detailed Design

## 4.1 New transport component

Add a dedicated component, recommended file:

- `src/simulator/ws_persistent_client.py`

Core class:

- `PersistentWsClient`

Responsibilities:

1. Maintain one live WebSocket connection.
2. Provide synchronous `request(action)` API for upper layer.
3. Run background receive loop and route responses by `request_id`.
4. Handle reconnect and heartbeat.

## 4.2 Public API contract

Suggested class interface:

```python
class PersistentWsClient:
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def request(self, action: Action, conn_timeout: int) -> str: ...
    def is_connected(self) -> bool: ...
```

Integration rule:

- Existing `src/simulator/api.py::request(...)` becomes a thin wrapper to singleton `PersistentWsClient.request(...)`.
- Upper-layer controller code keeps current calling style.

## 4.3 Internal data structures

Minimum required structures:

1. `self._ws`: active WebSocket object or `None`.
2. `self._state`: `DISCONNECTED | CONNECTING | CONNECTED | STOPPING`.
3. `self._send_lock`: mutex for `ws.send(...)` serialization.
4. `self._pending`: map `{request_id: PendingItem}`.
   - `PendingItem` includes wait primitive and response string slot.
5. `self._recv_thread`: background thread reading `ws.recv()`.
6. `self._heartbeat_thread` (optional but recommended).

Pending wait primitive options:

- `threading.Event` + shared response slot (recommended).
- or `queue.Queue(maxsize=1)`.

## 4.4 Request flow

On `request(action, conn_timeout)`:

1. Ensure connected (`_ensure_connected`).
2. Build packet via existing `action.to_datapacket_str()`.
3. Register pending waiter by `action.request_id`.
4. Acquire `self._send_lock`, send packet.
5. Block waiting for pending result up to `conn_timeout`.
6. On timeout:
   - remove pending entry,
   - return local transport timeout error JSON.
7. On response:
   - return response text as-is.

No retry rule (default):

- Do not auto-resend an action after send timeout/connection loss, to avoid duplicate side effects.

## 4.5 Receive loop behavior

Background loop (`_recv_loop`) must:

1. Continuously `recv()` while connected.
2. Parse JSON safely.
3. Extract `request_id`.
4. Match pending entry.
5. Store response and wake waiting requester.

If receive loop exits unexpectedly:

1. Transition to `DISCONNECTED`.
2. Fail all pending requests immediately with local transport exception error.
3. Trigger reconnect for future requests.

## 4.6 Reconnect strategy

Recommended reconnect policy:

- Lazy reconnect on next request.
- Retry up to `N=3` attempts per ensure-connect call.
- Backoff schedule: 0.2s, 0.5s, 1.0s.
- If all fail, return local transport exception response.

Reconnect safety:

- Only one thread may execute connect/reconnect path at a time (`self._connect_lock`).

## 4.7 Heartbeat and liveness

Recommended env vars:

- `SIMULATOR_WS_HEARTBEAT_MS` (default `10000`)
- `SIMULATOR_WS_IDLE_CLOSE_MS` (optional, informational)

Heartbeat behavior:

1. If no outgoing/incoming traffic for heartbeat interval, send WebSocket ping (or protocol heartbeat message if Unity stack requires it).
2. If ping/pong or heartbeat ack is absent for 2 intervals, mark disconnected and reconnect lazily.

## 4.8 Thread safety rules

1. `send` must be serialized.
2. `pending` map mutations must be under lock.
3. `stop()` must be idempotent.
4. `stop()` must unblock all waiting requests with deterministic local error.

## 4.9 Logging and observability

Python logs must include:

- connect success/failure with URL and attempt count,
- disconnect reason,
- request lifecycle (`request_id`, send timestamp, receive timestamp, latency),
- pending map size high-water mark.

## 5. Unity Detailed Design

## 5.1 Server architecture

Unity side must provide:

1. WebSocket endpoint (default `/ws`).
2. Per-session connection object.
3. Receive loop for each connected Python client.
4. Request dispatcher by `command`.
5. Main-thread executor for scene/game-object operations.

Recommended logical components:

- `WsServerHost`: start/stop listener.
- `WsSession`: holds one client connection state.
- `RequestRouter`: maps `command` to handler.
- `MainThreadActionExecutor`: executes Unity API calls on main thread.
- `ResponseWriter`: serializes and sends response JSON.

## 5.2 Session lifecycle

For each accepted connection:

1. Create `WsSession` with unique session id.
2. Start receive loop.
3. Keep connection open until client closes or transport failure.
4. On close, cancel all session pending jobs and cleanup resources.

## 5.3 Request handling flow

On each incoming packet:

1. Validate JSON and required fields.
2. Extract `request_id`, `timeout`, `team`, `command`, `value`.
3. Build execution context.
4. Dispatch to corresponding command handler.
5. Execute Unity object-changing code on main thread.
6. Send exactly one response with same `request_id`.

If validation fails:

- Send `success=false` error response with original `request_id` if available.

## 5.4 Timeout implementation

Execution timeout uses request field `timeout`:

1. `timeout == -1`: no cancellation deadline.
2. `timeout > 0`: enforce cancellation/deadline in handler pipeline.

Implementation suggestion:

- Use cancellation token or deadline timestamp propagated through handler chain.
- On deadline exceed, return `success=false` with `error: timeout`.

## 5.5 Main-thread execution rule

Any Unity API or scene object mutation must run on main thread.

Required mechanism:

1. Worker receive thread enqueues executable task to main-thread queue.
2. Main thread ticks queue and executes task.
3. Completion result is sent back via session writer.

## 5.6 Heartbeat and idle policy

Unity server should support one of:

1. Native WebSocket ping/pong handling from server library, or
2. Custom heartbeat request type if library lacks ping/pong visibility.

Recommended idle policy:

- Do not proactively close active session within 60s of idle by default.
- If server closes idle session, log reason and close code explicitly.

## 5.7 Concurrency and ordering

Per-session ordering policy (recommended):

- Accept concurrent requests, but process command handlers in arrival order per team if game logic requires deterministic behavior.

If strict sequential semantics are required:

- Use session-level command queue with single consumer.

Document chosen policy in Unity implementation readme.

## 5.8 Unity logging requirements

Must log at least:

- handshake accepted/rejected + reason,
- session open/close with close code,
- request received and response sent with `request_id`,
- command execution duration and timeout cases.

## 6. Handshake Alignment Checklist

Both sides must agree on:

1. URL and path (default `ws://localhost:8765/ws`).
2. Whether Origin is required and accepted value.
3. Whether Subprotocol is required and accepted value.
4. Compression/permessage-deflate compatibility if enabled.

Python env vars already reserved:

- `SIMULATOR_WS_URL`
- `SIMULATOR_WS_ORIGIN`
- `SIMULATOR_WS_SUBPROTOCOL`

## 7. Failure Matrix (Transport Level)

Required behavior:

1. Connect refused:
   - Python returns local error JSON (`success=false`) with transport exception text.
2. Handshake 400:
   - Unity logs rejection reason.
   - Python surfaces local error JSON with original handshake error text.
3. Connection lost while waiting response:
   - Python fails all pending with deterministic local transport error.
4. Unity internal handler exception:
   - Unity returns `success=false` with error message, same `request_id`.

## 8. Minimal Sequence

```text
Python process start
  -> PersistentWsClient.start()
  -> CONNECTED

request(action)
  -> register pending(request_id)
  -> send packet
  -> wait

Unity recv loop
  -> parse + dispatch
  -> execute on main thread
  -> send response(request_id)

Python recv loop
  -> match request_id
  -> wake waiter
  -> return response
```

## 9. Implementation Plan (Coding Order)

1. Python: add persistent client class and unit-level tests with mocked socket.
2. Python: refactor `api.py::request` to delegate to singleton persistent client.
3. Unity: add session lifecycle + receive loop + response writer.
4. Unity: add main-thread execution queue integration.
5. Joint: run end-to-end test from `python -m test.simulator_bot_control`.
6. Joint: verify reconnect by killing Unity server during requests and recovering.

## 10. Acceptance Criteria

Long connection is considered complete only if all are true:

1. First request establishes connection; subsequent requests do not re-handshake.
2. At least 100 consecutive requests run without reconnect under stable server.
3. Request/response correlation is correct under concurrent requests.
4. Disconnection is detected and next request triggers reconnect automatically.
5. No request hangs forever on Python side when `conn_timeout` is set.
6. Unity always returns at most one response per request and preserves `request_id`.
