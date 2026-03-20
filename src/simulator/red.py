# simulator/red.py
# RED Robot controlling TOOLS
#
# @author n1ghts4kura
# @date 2026-03-20
# 

import dspy

from src.simulator.bot_controller import red_bot_controller


move_forward = dspy.Tool(
    func = red_bot_controller.move_forward,
    name = "机器人前进",
    desc = "操控机器人向前进若干米的距离",
    arg_desc = {
        "distance": "前进的距离；单位为米"
    }
)

move_backward = dspy.Tool(
    func = red_bot_controller.move_backward,
    name = "机器人后退",
    desc = "操控机器人向后退若干米的距离",
    arg_desc = {
        "distance": "后退的距离；单位为米"
    }
)

strafe_left = dspy.Tool(
    func = red_bot_controller.strafe_left,
    name = "机器人向左平移",
    desc = "操控机器人向左平移若干米的距离",
    arg_desc = {
        "distance": "向左平移的距离；单位为米"
    }
)

strafe_right = dspy.Tool(
    func = red_bot_controller.strafe_right,
    name = "机器人向右平移",
    desc = "操控机器人向右平移若干米的距离",
    arg_desc = {
        "distance": "向右平移的距离；单位为米"
    }
)

chassis_rotate_clockwise = dspy.Tool(
    func = red_bot_controller.chassis_rotate_clockwise,
    name = "机器人底盘顺时针旋转",
    desc = "操控机器人底盘顺时针旋转若干度",
    arg_desc = {
        "angle": "旋转的角度；单位为度"
    }
)

chassis_rotate_counter_clockwise = dspy.Tool(
    func = red_bot_controller.chassis_rotate_counter_clockwise,
    name = "机器人底盘逆时针旋转",
    desc = "操控机器人底盘逆时针旋转若干度",
    arg_desc = {
        "angle": "旋转的角度；单位为度"
    }
)

turret_rotate_clockwise = dspy.Tool(
    func = red_bot_controller.turret_rotate_clockwise,
    name = "炮塔顺时针旋转",
    desc = "操控炮塔顺时针旋转若干度",
    arg_desc = {
        "angle": "旋转的角度；单位为度"
    }
)

turret_rotate_counter_clockwise = dspy.Tool(
    func = red_bot_controller.turret_rotate_counter_clockwise,
    name = "炮塔逆时针旋转",
    desc = "操控炮塔逆时针旋转若干度",
    arg_desc = {
        "angle": "旋转的角度；单位为度"
    }
)

turret_rotate_pitch = dspy.Tool(
    func = red_bot_controller.turret_rotate_pitch,
    name = "炮塔俯仰角调整",
    desc = "操控炮塔俯仰角调整若干度",
    arg_desc = {
        "angle": "俯仰的角度；单位为度"
    }
)

set_chassis_linear_speed = dspy.Tool(
    func = red_bot_controller.set_chassis_linear_speed,
    name = "设置底盘线速度",
    desc = "设置底盘线速度",
    arg_desc = {
        "speed": "线速度；单位为米每秒"
    }
)

get_chassis_linear_velocity = dspy.Tool(
    func = red_bot_controller.get_chassis_linear_velocity,
    name = "获取底盘线速度",
    desc = "获取当前底盘线速度",
    arg_desc = {}
)

set_chassis_angular_speed = dspy.Tool(
    func = red_bot_controller.set_chassis_angular_speed,
    name = "设置底盘角速度",
    desc = "设置底盘角速度",
    arg_desc = {
        "speed": "角速度；单位为度每秒"
    }
)

get_chassis_angular_velocity = dspy.Tool(
    func = red_bot_controller.get_chassis_angular_velocity,
    name = "获取底盘角速度",
    desc = "获取当前底盘角速度",
    arg_desc = {}
)

set_turret_pitch_limit = dspy.Tool(
    func = red_bot_controller.set_turret_pitch_limit,
    name = "设置炮塔俯仰限制",
    desc = "设置炮塔俯仰角度限制",
    arg_desc = {
        "value": "俯仰限制角度；单位为度，正负值分别代表向上和向下的最大俯仰角"
    }
)

get_turret_pitch_limit = dspy.Tool(
    func = red_bot_controller.get_turret_pitch_limit,
    name = "获取炮塔俯仰限制",
    desc = "获取当前炮塔俯仰角度限制",
    arg_desc = {}
)

get_health = dspy.Tool(
    func = red_bot_controller.get_health,
    name = "获取生命值",
    desc = "获取机器人当前生命值",
    arg_desc = {}
)

set_health = dspy.Tool(
    func = red_bot_controller.set_health,
    name = "设置生命值",
    desc = "设置机器人生命值",
    arg_desc = {
        "value": "目标生命值"
    }
)

get_ammo = dspy.Tool(
    func = red_bot_controller.get_ammo,
    name = "获取弹药数",
    desc = "获取机器人当前弹药数量",
    arg_desc = {}
)

set_ammo = dspy.Tool(
    func = red_bot_controller.set_ammo,
    name = "设置弹药数",
    desc = "设置机器人弹药数量",
    arg_desc = {
        "value": "目标弹药数量"
    }
)

fire = dspy.Tool(
    func = red_bot_controller.fire,
    name = "开火",
    desc = "操控机器人开火",
    arg_desc = {}
)

set_control_mode = dspy.Tool(
    func = red_bot_controller.set_control_mode,
    name = "设置控制模式",
    desc = "设置机器人控制模式，可选模式有：independent（底盘和炮塔独立控制）、chassis_follow_turret（底盘跟随炮塔方向）、turret_follow_chassis（炮塔跟随底盘方向）",
    arg_desc = {
        "mode": "控制模式：independent、chassis_follow_turret 或 turret_follow_chassis"
    }
)

get_control_mode = dspy.Tool(
    func = red_bot_controller.get_control_mode,
    name = "获取控制模式",
    desc = "获取机器人当前控制模式",
    arg_desc = {}
)

tool_list = [
    move_forward,
    move_backward,
    strafe_left,
    strafe_right,
    chassis_rotate_clockwise,
    chassis_rotate_counter_clockwise,
    turret_rotate_clockwise,
    turret_rotate_counter_clockwise,
    turret_rotate_pitch,
    set_chassis_linear_speed,
    get_chassis_linear_velocity,
    set_chassis_angular_speed,
    get_chassis_angular_velocity,
    set_turret_pitch_limit,
    get_turret_pitch_limit,
    get_health,
    set_health,
    get_ammo,
    set_ammo,
    fire,
    set_control_mode,
    get_control_mode,
]

__all__ = [
    "move_forward",
    "move_backward",
    "strafe_left",
    "strafe_right",
    "chassis_rotate_clockwise",
    "chassis_rotate_counter_clockwise",
    "turret_rotate_clockwise",
    "turret_rotate_counter_clockwise",
    "turret_rotate_pitch",
    "set_chassis_linear_speed",
    "get_chassis_linear_velocity",
    "set_chassis_angular_speed",
    "get_chassis_angular_velocity",
    "set_turret_pitch_limit",
    "get_turret_pitch_limit",
    "get_health",
    "set_health",
    "get_ammo",
    "set_ammo",
    "fire",
    "set_control_mode",
    "get_control_mode",
    "tool_list",
]