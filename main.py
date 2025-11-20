import traceback
import os
from typing import cast
import evdev
import subprocess
from select import select
import threading
import atexit
import time
import random

# The name of your mouse and keyboard to search for.
KEYBOARD_IDENTIFIER = "brian low sofle choc"
MOUSE_IDENTIFIER = "usb gaming mouse"

FLASK_MACRO_ENABLED = False
# Key that will active FLASK_BINDINGS.
FLASK_KEY = "KEY_F"
# These are the flask keys that will be pressed when the FLASK_KEY is pressed.
FLASK_BINDINGS = [2, 3, 4, 5]

LIFE_FLASK_TOGGLE_KEY = "KEY_F3"
# The duration of the life flask in the game tooltip.
LIFE_FLASK_DURATION = 6.44
# In game life flask binding.
LIFE_FLASK_BINDING_KEY_CODE = evdev.ecodes.KEY_F2

SCROLL_CLICK_ENABLED = True


from evdev.device import InputDevice
from evdev.events import KeyEvent

WINDOW_NAME = "Path of Exile"


def window_is_active():
    try:
        out = subprocess.check_output(["xdotool", "getactivewindow", "getwindowname"])
        active_window = out.decode().lower().strip()
        return active_window == WINDOW_NAME.lower()
    except Exception as e:
        traceback.print_exc()
        return False


# reverse to grab the fist instance of each device
dd = evdev.list_devices()
dd.reverse()

raw_devices = [evdev.InputDevice(path) for path in dd]

for d in raw_devices:
    print(d)

keyboard = next((d for d in raw_devices if KEYBOARD_IDENTIFIER == d.name.lower()), None)

if not keyboard:
    print("ERROR: keyboard not found")
    exit(1)

mouse = next(
    (
        d
        for d in raw_devices
        if MOUSE_IDENTIFIER == d.name.lower() and "input0" in d.phys
    ),
    None,
)

if not mouse:
    print("ERROR: mouse not found")
    exit(1)

devices = [keyboard, mouse]
devices = {dev.fd: dev for dev in devices}


ydotoold_proc = None

if keyboard and mouse:

    def run_ydotoold():
        env = os.environ.copy()
        global ydotoold_proc
        ydotoold_proc = subprocess.Popen(["ydotoold"], env=env)
        ydotoold_proc.wait()

    thread = threading.Thread(
        target=run_ydotoold,
        daemon=True,
    )
    thread.start()


def cleanup():
    if ydotoold_proc:
        ydotoold_proc.terminate()


atexit.register(cleanup)

ctrl_pressed = False


def ydotool(args: list[str]):
    env = os.environ.copy()
    env["YDOTOOL_SOCKET"] = "/tmp/.ydotool_socket"
    subprocess.run(
        ["ydotool", *args],
        env=env,
    )


def key_press(key_code: int):
    ydotool(["key", f"{key_code}:1", f"{key_code}:0"])


def flask_macro():
    random.shuffle(FLASK_BINDINGS)
    for key_code in FLASK_BINDINGS:
        t = 0.2 * random.random()
        time.sleep(t)
        key_press(key_code + 1)
        print(f"key press: {key_code}")


LIFE_FLACK_LOCK = threading.Lock()
LIFE_FLASK_MACRO_RUNNING = False


def life_flask_loop():
    random_delay = 0.5
    while True:
        with LIFE_FLACK_LOCK:
            flask_active = LIFE_FLASK_MACRO_RUNNING

        if not flask_active:
            time.sleep(0.001)
            continue

        time.sleep(LIFE_FLASK_DURATION - random_delay)

        with LIFE_FLACK_LOCK:
            should_fire = LIFE_FLASK_MACRO_RUNNING and window_is_active()

        if not should_fire:
            continue

        time.sleep(random.uniform(0, 0.2))

        with LIFE_FLACK_LOCK:
            if LIFE_FLASK_MACRO_RUNNING and window_is_active():
                print("activating life flask")
                key_press(LIFE_FLASK_BINDING_KEY_CODE)


def main_loop():
    while True:
        global devices
        global ctrl_pressed
        global LIFE_FLASK_MACRO_RUNNING
        r, w, x = select(devices, [], [])
        for fd in r:
            for event in devices[fd].read():
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = cast(KeyEvent, evdev.categorize(event))
                    if (
                        key_event.keycode == LIFE_FLASK_TOGGLE_KEY
                        and key_event.keystate == evdev.KeyEvent.key_up
                    ):
                        with LIFE_FLACK_LOCK:
                            LIFE_FLASK_MACRO_RUNNING = not LIFE_FLASK_MACRO_RUNNING
                            state = "on" if LIFE_FLASK_MACRO_RUNNING else "off"
                        print(f"life flask macro toggled {state}")

                    if key_event.keycode == "KEY_LEFTCTRL":
                        ctrl_pressed = key_event.keystate != evdev.KeyEvent.key_up
                        print(f"ctrl_pressed: {ctrl_pressed}")
                    if (
                        key_event.keycode == FLASK_KEY
                        and key_event.keystate == evdev.KeyEvent.key_up
                        and FLASK_MACRO_ENABLED
                        and window_is_active()
                    ):
                        flask_macro()

                if SCROLL_CLICK_ENABLED and event.type == evdev.ecodes.EV_REL:
                    if event.code in [evdev.ecodes.REL_WHEEL, evdev.ecodes.REL_HWHEEL]:
                        if ctrl_pressed:
                            ydotool(
                                [
                                    "click",
                                    "0xC0",
                                ]
                            )


if __name__ == "__main__":
    main_loop_thread = threading.Thread(target=main_loop)
    main_loop_thread.start()

    life_flask_loop_thread = threading.Thread(target=life_flask_loop)
    life_flask_loop_thread.start()

    main_loop_thread.join()
    life_flask_loop_thread.join()
