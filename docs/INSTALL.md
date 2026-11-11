# Installation guide

## Requirements

- A Linux desktop already running COSMIC. Fedora with COSMIC is the supported
  target; this repository does not install a desktop environment or an OS.
- Git, Bash, Python **3.12 or newer**, and enough free space for the assets and
  a backup of the files already on your machine.
- Fish, Fastfetch and Starship for the terminal setup; Qt5ct and Qt6ct for Qt apps.

The configuration was prepared on Fedora 44 / COSMIC 1.11. Monitor names, display
scaling, panel placement and installed app versions may differ on your machine.

## 1. Download

The repository is public. GitHub CLI authentication is not required:

```sh
git clone https://github.com/Mfvesaw/eva01-cosmic-dotfiles.git
cd eva01-cosmic-dotfiles
```

## 2. Preview the changes

```sh
./install.sh --help
./install.sh --dry-run
```

The dry run verifies file checksums and validates the icon/theme archive. It
prints planned desktop integration commands and changes no files or packages.
The restore writes the saved COSMIC layout and application preferences. Close
themed apps before running it so they cannot overwrite the restored preferences.

## 3. Install

With the required programs already installed:

```sh
./install.sh
```

For Fedora package installation as well:

```sh
./install.sh --dependencies
```

This optional mode runs `sudo dnf install` for Fish, Fastfetch, Starship, Qt5ct,
Qt6ct, Nimbus Mono PS fonts and KiCad. It needs administrator authentication.
The configuration restore itself runs as your normal user: do not run the entire
installer with sudo.

To select the second wallpaper:

```sh
./install.sh --wallpaper purple-nebula
```

Both original wallpapers are copied to `~/.local/share/backgrounds/EVA01/`.
The default selection is `eva01`. You can switch them in COSMIC Settings later.

To reinstall the captured Flatpak app inventory, including COSMIC applets:

```sh
./install.sh --apps
# Or combine all options:
./install.sh --dependencies --apps --wallpaper purple-nebula
```

`--apps` installs **every app** listed in
[metadata/flatpak-apps.tsv](../metadata/flatpak-apps.tsv), not just themed apps.
Review that list first. Signed Flathub/COSMIC remote definitions are bundled.
The installer does not install VS Code or IntelliJ themselves;
install those applications separately if you want their themes.

## 4. Reload the desktop and apps

1. Log out and back in to refresh COSMIC's cached cursor and Qt environment.
2. Open a new terminal. If your login shell is not Fish, run `fish` to try the
   prompt, completions and Fastfetch artwork. To make Fish your login shell,
   optionally run `chsh -s /usr/bin/fish`, then log in again.
3. Open the applications you themed. Adjust monitor settings and panel placement
   in COSMIC Settings if your hardware differs.

For Zen and Obsidian on a fresh account, launch the app once first to create a
profile or vault, then close it and rerun the installer. Existing profiles/vaults
are discovered locally; the source machine's browser/vault registry is not copied.
Zen websites keep their normal appearance. Obsidian notes are never replaced.

## Test in a separate directory

```sh
./install.sh --home /tmp/eva01-test-home --wallpaper purple-nebula
```

This restores files into that folder and skips desktop integration. It does not
change your real desktop. Do not combine `--home` with package/app install flags.

## Backups and rollback

Replaced configuration files and asset directories are saved automatically:

```text
~/.local/state/eva01/backups/<timestamp>/
```

To restore the files from one run:

```sh
python3 scripts/restore.py ~/.local/state/eva01/backups/<timestamp>
```

The file rollback does not uninstall packages/extensions or undo GSettings and
session-environment changes.

Older COSMIC applets use a synchronized legacy theme copy. Its user path unit
is `eva01-legacy-theme.path`. To stop automatic synchronization:

```sh
systemctl --user disable --now eva01-legacy-theme.path
```

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Cursor or Qt colors are still old | Log out and back in; reopen the app. |
| Missing terminal colors/art | Install Fish, Fastfetch and Starship, then open Fish. |
| Lime panel/dock borders disappeared | Run `python3 scripts/match-panel-borders.py`. |
| Older applet still has default colors | Run `python3 ~/.local/bin/eva01-sync-legacy-theme`. |
| Zen or Obsidian theme was skipped | Create a profile/vault, close the app and rerun the installer. |
| Checksum mismatch | Restore the modified repository file or review your edits and run `python3 scripts/check-backup.py --write-checksums`. |

Package installation modes were not exercised on a clean OS. Configuration
restores, rollback, native theme parsing and isolated app-theme checks are
recorded in [metadata/VALIDATION.md](../metadata/VALIDATION.md).

## Zen and MYNT new-tab layout

The browser CSS and extension setup are separate. See the
[Zen + MYNT replication guide](ZEN-MYNT.md) to reproduce the nebula screenshot.
Steam themes and Steam loader installation are not included in this installer.
