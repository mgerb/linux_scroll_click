Linux utility to bind control+scroll wheel to left click. Works with Wayland.
Can be used to spam click items in games such as Path of Exile.

Also supports flask macros

- Press one button to use all flasks
- Use life flask on timer

Currently taylored to my setup, but can be easily modified. See comments in `main.py`.

- [evdev](https://github.com/gvalkov/python-evdev)
- [ydotool](https://github.com/ReimuNotMoe/ydotool)
- [xdotool](https://github.com/jordansissel/xdotool)

```sh
# run with the flake (recommended)
sudo nix develop
python main.py

# or without the flake
sudo nix-shell -p python312 python312Packages.evdev ydotool xdotool --run "python main.py"
```
