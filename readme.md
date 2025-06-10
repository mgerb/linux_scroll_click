Linux utility to bind control+scroll wheel to left click. Works with Wayland.
Can be used to spam click items in games such as Path of Exile.

Currently taylored to my setup, but can be easily modified. See comments in `main.py`.

- [evdev](https://github.com/gvalkov/python-evdev)
- [ydotool](https://github.com/ReimuNotMoe/ydotool)

```sh
sudo nix-shell -p python312 python312Packages.evdev ydotool --run "python main.py"
```
