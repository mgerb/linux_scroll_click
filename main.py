import os
from typing import cast
import evdev
import subprocess
from select import select
import threading
import atexit

from evdev.events import KeyEvent

# reverse to grab the fist instance of each device
dd = evdev.list_devices()
dd.reverse()

raw_devices = [evdev.InputDevice(path) for path in dd]

# NOTE: modify these to find your devices
keyboard = next((d for d in raw_devices if "sofle choc" in d.name.lower()), None)
mouse = next((d for d in raw_devices if "mouse" in d.name.lower()), None)


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
    ydotoold_proc.terminate()


atexit.register(cleanup)

ctrl_pressed = False

while True:
    r, w, x = select(devices, [], [])
    for fd in r:
        for event in devices[fd].read():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = cast(KeyEvent, evdev.categorize(event))
                if key_event.keycode == "KEY_LEFTCTRL":
                    ctrl_pressed = key_event.keystate != evdev.KeyEvent.key_up
            if event.type == evdev.ecodes.EV_REL:
                if event.code in [evdev.ecodes.REL_WHEEL, evdev.ecodes.REL_HWHEEL]:
                    if ctrl_pressed:
                        env = os.environ.copy()
                        env["YDOTOOL_SOCKET"] = "/tmp/.ydotool_socket"
                        subprocess.run(
                            [
                                "ydotool",
                                "click",
                                "0xC0",
                            ],
                            env=env,
                        )
