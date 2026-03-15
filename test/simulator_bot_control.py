from src.simulator import red_bot_controller

print(red_bot_controller.move_forward(distance=1.5))

print(red_bot_controller.strafe_left(distance=0.5))

print(red_bot_controller.get_health())
print(red_bot_controller.set_health(value=50))

print(red_bot_controller.get_ammo())
print(red_bot_controller.set_ammo(value=200))

print(red_bot_controller.fire())
