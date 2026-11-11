# EVA01 Steam

Millennium loads the custom library, dialog, navigation, friends and Big Picture
colors. The CSS retains Steam's layout, game artwork and status colors. No
custom theme JavaScript, third-party plugin or store/website CSS is added.

The verified upstream Millennium 3.6.2 Linux release is installed per user under
`~/.local/lib/millennium/3.6.2`. Its documented-in-source bootstrap environment
override, `MILLENNIUM_RUNTIME_PATH`, is exported by `~/.local/bin/steam`. A user
desktop entry forwards Steam and its desktop actions through this wrapper.
The hooks are copied into the existing Steam client directories; x64 files are
copied instead of linked so Steam's web-helper container can see them.

```sh
python3 install-millennium.py --dry-run
python3 install-millennium.py
```

The archive is SHA-256 verified before installation. Existing files are backed
up under `~/.local/state/eva01/steam-backups/`. No administrator rights are
needed. No running Steam process or game is stopped by the installer. Fully
exit Steam, including its tray icon, and reopen it after installation. Native
x86_64 Linux Steam is required; this setup does not target Flatpak Steam.

Upstream source and MIT license:
https://github.com/SteamClientHomebrew/Millennium/tree/v3.6.2
https://docs.steambrew.app/themes/basics/config

This user-local layout uses upstream binaries and the upstream runtime-path
override; it differs from the upstream system-wide `/usr/lib` installer.
