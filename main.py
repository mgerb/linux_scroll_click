import os
from typing import cast
import evdev
import subprocess
from select import select
import threading
import atexit
import time
import random

from evdev.device import InputDevice
from evdev.events import KeyEvent

# reverse to grab the fist instance of each device
dd = evdev.list_devices()
dd.reverse()

raw_devices = [evdev.InputDevice(path) for path in dd]

for d in raw_devices:
    print(d)

# NOTE: modify these to find your devices
keyboard = next(
    (d for d in raw_devices if "brian low sofle choc" == d.name.lower()), None
)

if not keyboard:
    print("ERROR: keyboard not found")
    exit(1)

mouse = next(
    (
        d
        for d in raw_devices
        if "usb gaming mouse" == d.name.lower() and "input0" in d.phys
    ),
    None,
)

if not mouse:
    print("ERROR: mouse not found")
    exit(1)

# keyboard = InputDevice("/dev/input/event0")
# mouse = InputDevice("/dev/input/event21")
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
    key_codes = [2, 3, 4, 5]
    random.shuffle(key_codes)
    for key_code in key_codes:
        t = 0.2 * random.random()
        time.sleep(t)
        key_press(key_code)


while True:
    r, w, x = select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = cast(KeyEvent, evdev.categorize(event))
                if key_event.keycode == "KEY_LEFTCTRL":
                    ctrl_pressed = key_event.keystate != evdev.KeyEvent.key_up
                    print(f"ctrl_pressed: {ctrl_pressed}")
                if (
                    key_event.keycode == "KEY_F"
                    and key_event.keystate == evdev.KeyEvent.key_up
                ):
                    flask_macro()

            if event.type == evdev.ecodes.EV_REL:
                if event.code in [evdev.ecodes.REL_WHEEL, evdev.ecodes.REL_HWHEEL]:
                    if ctrl_pressed:
                        ydotool(
                            [
                                "click",
                                "0xC0",
                            ]
                        )
