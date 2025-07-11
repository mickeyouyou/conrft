import time

import mujoco
import mujoco.viewer
import numpy as np

from franka_sim import envs

from franka_env.spacemouse.spacemouse_expert import SpaceMouseExpert, JoystickExpert, ControllerType
from franka_env.spacemouse.keyboard_expert import KeyboardExpert
from franka_sim.utils.viewer_utils import DualMujocoViewer

env = envs.PandaPickCubeGymEnv(render_mode="human", action_scale=(0.1, 1))
action_spec = env.action_space


def sample():
    a = np.random.uniform(action_spec.low, action_spec.high, action_spec.shape)
    return a.astype(action_spec.dtype)

expert = KeyboardExpert()
def human_sample():
    action, buttons = expert.get_action()
    print(action)
    return action

m = env.model
d = env.data

key_reset = False
KEY_SPACE = 32
HUMAN_SAMPLE = True


def key_callback(keycode):
    if keycode == KEY_SPACE:
        global key_reset
        key_reset = True


env.reset()

# Create the dual viewer
# dual_viewer = DualMujocoViewer(env.unwrapped.model, env.unwrapped.data)

# with dual_viewer as viewer:
with  mujoco.viewer.launch_passive(env.unwrapped.model, env.unwrapped.data, show_left_ui=False, show_right_ui=False) as viewer:
    start = time.time()
    while viewer.is_running():
        if key_reset:
            env.reset()
            key_reset = False
        else:
            step_start = time.time()
            action = sample() if not HUMAN_SAMPLE else human_sample() 
            print(action)
            env.step(action)
            viewer.sync()
            time_until_next_step = env.control_dt - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)
