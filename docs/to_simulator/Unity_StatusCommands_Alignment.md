# Unity Alignment Spec: Robot Status Commands and Fire Return

## 1. Purpose

This document is a focused alignment contract for Unity implementation.
It covers only:

1. New commands:
   - BotHealthGetAction
   - BotHealthSetAction
   - BotAmmoGetAction
   - BotAmmoSetAction
2. Updated command behavior:
   - TurretFireAction returns remaining ammo on success

Use this document together with docs/to_simulator/Format.md.

## 2. Transport Baseline

Common request fields:

1. request_id: string, required
2. timeout: int, required (-1 or positive)
3. team: string, required (red or blue)
4. command: string, required
5. value: object, optional for parameterless commands

Common response fields:

1. request_id: same as request
2. success: bool
3. value: command result on success, error string on failure

Hard requirements:

1. One request -> one response.
2. Response request_id must match request request_id.
3. Response must be valid JSON text.

## 3. Command Contracts

## 3.1 BotHealthGetAction

Description:

- Return current health of target team robot.

Request:

```json
{
  "request_id": "hp-get-001",
  "timeout": 3000,
  "team": "blue",
  "command": "BotHealthGetAction"
}
```

Response on success:

```json
{
  "request_id": "hp-get-001",
  "success": true,
  "value": 85
}
```

Response rules:

1. success=true, value is integer.

## 3.2 BotHealthSetAction

Description:

- Set health to input integer.
- Clamp to [0, 100].

Request:

```json
{
  "request_id": "hp-set-001",
  "timeout": 3000,
  "team": "red",
  "command": "BotHealthSetAction",
  "value": { "value": 50 }
}
```

Response on success:

```json
{
  "request_id": "hp-set-001",
  "success": true,
  "value": 50
}
```

Response on missing/invalid parameter:

```json
{
  "request_id": "hp-set-001",
  "success": false,
  "value": "error: invalid request: missing integer parameter 'value'"
}
```

Response rules:

1. success=true, value is clamped integer.
2. success=false, value is error string.

## 3.3 BotAmmoGetAction

Description:

- Return current ammo of target team robot.

Request:

```json
{
  "request_id": "ammo-get-001",
  "timeout": 3000,
  "team": "blue",
  "command": "BotAmmoGetAction"
}
```

Response on success:

```json
{
  "request_id": "ammo-get-001",
  "success": true,
  "value": 157
}
```

Response rules:

1. success=true, value is integer.

## 3.4 BotAmmoSetAction

Description:

- Set ammo to input integer.
- Minimum is 0, no upper bound.

Request:

```json
{
  "request_id": "ammo-set-001",
  "timeout": 3000,
  "team": "blue",
  "command": "BotAmmoSetAction",
  "value": { "value": 200 }
}
```

Response on success:

```json
{
  "request_id": "ammo-set-001",
  "success": true,
  "value": 200
}
```

Response on missing/invalid parameter:

```json
{
  "request_id": "ammo-set-001",
  "success": false,
  "value": "error: invalid request: missing integer parameter 'value'"
}
```

Response rules:

1. success=true, value is resulting integer ammo.
2. success=false, value is error string.

## 3.5 TurretFireAction (Behavior Update)

Description:

- Fire once.
- If ammo is zero, return dedicated no-ammo error.
- If fire succeeds, return remaining ammo.

Request:

```json
{
  "request_id": "fire-001",
  "timeout": 3000,
  "team": "red",
  "command": "TurretFireAction"
}
```

Response on success:

```json
{
  "request_id": "fire-001",
  "success": true,
  "value": 199
}
```

Response when no ammo:

```json
{
  "request_id": "fire-002",
  "success": false,
  "value": "error: no ammo"
}
```

Response rules:

1. success=true, value must be integer remaining ammo.
2. no-ammo failure must return exact error string: error: no ammo.

## 4. Unity Router Mapping Checklist

Unity command router must include handlers for:

1. BotHealthGetAction
2. BotHealthSetAction
3. BotAmmoGetAction
4. BotAmmoSetAction
5. TurretFireAction (updated return payload)

If any command is missing, Unity currently returns:

- error: invalid request: unknown command '<CommandName>'

This must disappear after mapping is complete.

## 5. Team and Controller Resolution

Server must resolve team to runtime controller:

1. red -> red robot controller
2. blue -> blue robot controller

If team is unknown or controller missing, return:

```json
{
  "request_id": "<same-as-request>",
  "success": false,
  "value": "error: invalid request: no controller for team '<team>'"
}
```

## 6. Validation Rules

1. command is required and must be known.
2. team is required and must be red or blue.
3. timeout is required and must be -1 or positive integer.
4. For set commands, value.value must be integer.
5. For BotAmmoSetAction, value.value must be >= 0.
6. For BotHealthSetAction, clamp value.value to [0, 100].

## 7. Initial State Reference

1. health default: 100
2. ammo default: 200

## 8. Acceptance Test Cases

A Unity implementation is aligned only when all pass:

1. BotHealthGetAction returns success=true with integer value.
2. BotHealthSetAction returns clamped integer value.
3. BotAmmoGetAction returns success=true with integer value.
4. BotAmmoSetAction returns success=true with integer value.
5. TurretFireAction success returns remaining ammo integer.
6. TurretFireAction with zero ammo returns success=false and value=error: no ammo.
7. No unknown command errors for the four new status commands.
