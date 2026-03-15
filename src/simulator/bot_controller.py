# Generic Team Bot Controlling Module
#
# @author n1ghts4kura
# @date 2026-3-15
#

import json
from typing import Type
from pydantic import ValidationError

from src.simulator.api import *


class TeamBotController:
    """Controller that provides the same command set for a specific team bot."""

    def __init__(self, team: str):
        self.team = team

    def _send_action(self, action: Action, response_model: Type[Response] = Response) -> Response:
        """Send one action and parse the response into a typed model."""

        result = request(action)

        if result == "timeout" or result.startswith("error:"):
            return StringResponse(
                request_id=action.request_id,
                success=False,
                value=result,
            )

        try:
            payload = json.loads(result)
        except json.JSONDecodeError as e:
            return StringResponse(
                request_id=action.request_id,
                success=False,
                value=f"error: invalid json response: {str(e)}",
            )

        try:
            base_resp = Response.model_validate(payload)
        except ValidationError as e:
            return StringResponse(
                request_id=action.request_id,
                success=False,
                value=f"error: invalid response schema: {str(e)}",
            )

        if base_resp.request_id != action.request_id:
            return StringResponse(
                request_id=action.request_id,
                success=False,
                value=(
                    "error: mismatched request_id in response. "
                    f"expected={action.request_id}, got={base_resp.request_id}"
                ),
            )

        if not base_resp.success:
            return StringResponse(
                request_id=base_resp.request_id,
                success=False,
                value=str(payload.get("value", payload)),
            )

        try:
            return response_model.model_validate(payload)
        except ValidationError as e:
            return StringResponse(
                request_id=action.request_id,
                success=False,
                value=f"error: unexpected response payload: {str(e)}",
            )

    def move_forward(self, distance: float):
        action = ChassisForwardAction(team=self.team, distance=distance)
        return self._send_action(action, Response)

    def move_backward(self, distance: float):
        action = ChassisBackwardAction(team=self.team, distance=distance)
        return self._send_action(action, Response)

    def strafe_left(self, distance: float):
        action = ChassisStrafeLeftAction(team=self.team, distance=distance)
        return self._send_action(action, Response)

    def strafe_right(self, distance: float):
        action = ChassisStrafeRightAction(team=self.team, distance=distance)
        return self._send_action(action, Response)

    def chassis_rotate_clockwise(self, angle: float):
        action = ChassisRotateClockwiseAction(team=self.team, angle=angle)
        return self._send_action(action, Response)

    def chassis_rotate_counter_clockwise(self, angle: float):
        action = ChassisRotateCounterClockwiseAction(team=self.team, angle=angle)
        return self._send_action(action, Response)

    def turret_rotate_clockwise(self, angle: float):
        action = TurretRotateClockwiseAction(team=self.team, angle=angle)
        return self._send_action(action, Response)

    def turret_rotate_counter_clockwise(self, angle: float):
        action = TurretRotateCounterClockwiseAction(team=self.team, angle=angle)
        return self._send_action(action, Response)

    def turret_rotate_pitch(self, angle: float):
        action = TurretRotatePitchAction(team=self.team, angle=angle)
        return self._send_action(action, Response)

    def set_chassis_linear_speed(self, speed: float):
        action = ChassisLinearSpeedSetAction(team=self.team, speed=speed)
        return self._send_action(action, FloatResponse)

    def get_chassis_linear_velocity(self):
        action = ChassisLinearSpeedGetAction(team=self.team)
        return self._send_action(action, FloatResponse)

    def set_chassis_angular_speed(self, speed: float):
        action = ChassisAngularSpeedSetAction(team=self.team, speed=speed)
        return self._send_action(action, FloatResponse)

    def get_chassis_angular_velocity(self):
        action = ChassisAngularSpeedGetAction(team=self.team)
        return self._send_action(action, FloatResponse)

    def set_turret_pitch_limit(self, value: float):
        action = TurretPitchLimitSetAction(team=self.team, value=value)
        return self._send_action(action, Response)

    def get_turret_pitch_limit(self):
        action = TurretPitchLimitGetAction(team=self.team)
        return self._send_action(action, FloatResponse)

    def get_health(self):
        action = BotHealthGetAction(team=self.team)
        return self._send_action(action, IntResponse)

    def set_health(self, value: int):
        action = BotHealthSetAction(team=self.team, value=value)
        return self._send_action(action, IntResponse)

    def get_ammo(self):
        action = BotAmmoGetAction(team=self.team)
        return self._send_action(action, IntResponse)

    def set_ammo(self, value: int):
        action = BotAmmoSetAction(team=self.team, value=value)
        return self._send_action(action, IntResponse)

    def fire(self):
        action = TurretFireAction(team=self.team)
        return self._send_action(action, IntResponse)

    def set_control_mode(self, mode: BotControlMode):
        action = BotControlModeSetAction(team=self.team, mode=mode)
        return self._send_action(action, Response)

    def get_control_mode(self):
        action = BotControlModeGetAction(team=self.team)
        return self._send_action(action, StringResponse)


red_bot_controller = TeamBotController("red")
blue_bot_controller = TeamBotController("blue")


__all__ = [
    "TeamBotController",
    "red_bot_controller",
    "blue_bot_controller",
]