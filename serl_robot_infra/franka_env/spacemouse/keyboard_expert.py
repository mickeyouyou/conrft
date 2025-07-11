import numpy as np
import multiprocessing
from pynput import keyboard

class KeyboardExpert:
    """
    Keyboard teleoperation using pynput.
    Outputs 7D action: [dx, dy, dz, droll, dpitch, dyaw, gripper_delta]
    Arrow keys: dx/dy
    PageUp/PageDown: dz
    I/K J/L U/O: rpy
    Left Ctrl: close gripper
    Left Shift: open gripper
    """

    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.latest_data = self.manager.dict()
        self.latest_data["action"] = [0.0] * 7
        self.key_state = self.manager.dict()
        self.process = multiprocessing.Process(target=self._keyboard_loop)
        self.process.daemon = True
        self.process.start()

    def _keyboard_loop(self):
        import time

        key_map = {
            'up': (0, +1), 'down': (0, -1),
            'left': (1, +1), 'right': (1, -1),
            'page_up': (2, +1), 'page_down': (2, -1),
            'i': (3, +1), 'k': (3, -1),
            'j': (4, +1), 'l': (4, -1),
            'u': (5, +1), 'o': (5, -1),
        }

        scale = [0.05, 0.05, 0.05, 0.1, 0.1, 0.1, 0.5]

        def on_press(key):
            try:
                k = key.char.lower()
            except AttributeError:
                k = key.name
            self.key_state[k] = True

        def on_release(key):
            try:
                k = key.char.lower()
            except AttributeError:
                k = key.name
            self.key_state[k] = False
            if k == 'esc':
                return False  # stop listener

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        while True:
            action = [0.0] * 7
            buttons = [False, False]

            for k, (idx, sign) in key_map.items():
                if self.key_state.get(k, False):
                    action[idx] += scale[idx] * sign

            # Gripper control
            if self.key_state.get('shift_r', False):
                action[6] = -scale[6]  # close
                buttons[0] = True
            elif self.key_state.get('shift', False) or self.key_state.get('shift_l', False):
                action[6] = scale[6]   # open
                buttons[1] = True

            self.latest_data["action"] = action
            self.latest_data["button"] = buttons
            time.sleep(0.05)

    def get_action(self):
        action = self.latest_data["action"]
        buttons = self.latest_data["button"] 
        return np.array(self.latest_data["action"]), buttons

    def close(self):
        self.process.terminate()
