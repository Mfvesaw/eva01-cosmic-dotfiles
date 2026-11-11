# EVA01 COSMIC desktop

A private snapshot of my Fedora COSMIC desktop, using violet, lavender and lime.
The terminal shows **static, colored ASCII** of the supplied EVA Unit-01 head
beside Fastfetch. Fish and Starship use the normal full-height terminal, with
no animation, background renderer or dedicated tmux pane. Running `clear` or
pressing Ctrl+L clears the terminal and redraws the Fastfetch card above the
prompt. Ctrl+L preserves a partly typed command. The wrapper leaves scripts
and `clear` option/help invocations alone. `EVA01_STARTUP=0` disables the card.

## Restore

Clone this private repository using an authenticated GitHub account:

```sh
gh repo clone Mfvesaw/eva01-cosmic-dotfiles
cd eva01-cosmic-dotfiles
./install.sh --dry-run
./install.sh
```

Close themed apps before restoring their preferences. Open a new terminal after
installation; log out and back in to reload COSMIC's cached cursor and the Qt
environment. The installer backs up every replaced file or theme directory under
`~/.local/state/eva01/backups/<timestamp>/`, then restores the saved preferences.
Unrelated app preferences are merged for VS Code, Vesktop, and Flatpak overrides.
Existing Zen profiles are discovered automatically, and their EVA01 CSS blocks
are replaced while preserving other customization blocks. Websites keep their
own styles; only the browser interface and internal new-tab page are themed.
Launch Zen once and close it before installing its theme on a fresh account.

Optional package and application installation:

```sh
# Fedora: Fish, Fastfetch, Starship, Qt5ct, Qt6ct, Nimbus Mono PS, KiCad.
./install.sh --dependencies
# Restore every Flatpak app listed in metadata/flatpak-apps.tsv, including applets.
./install.sh --apps
# Both, plus the configuration restore:
./install.sh --dependencies --apps
```

The optional Flatpak restore uses the bundled public repository signing keys
for Flathub and COSMIC. It installs the captured app/branch inventory; archived
versions can become unavailable later. VS Code and IntelliJ themselves are not
bundled: install them separately. The installer loads the local VSIX if `code`
is available, and installs the IntelliJ theme into detected IDE configuration
versions. Fedora/COSMIC is the supported target; monitor/output preferences
reflect the source machine and may need adjustment on different hardware.

To test safely in another directory (desktop integration is skipped):

```sh
./install.sh --home /tmp/eva01-test-home
```

## Included

- COSMIC settings: panel/dock layout, applets, borders, workspaces, shortcuts,
  window rules, desktop/terminal/editor theme settings and wallpaper.
- Fish config, bindings and completions; Starship; Fastfetch and static ASCII.
- GTK 3/4, Qt 5/6, KDE color scheme, EVA cursor and purple Colloid icon variants.
- Zen browser chrome, VS Code theme/preferences, IntelliJ appearance/fonts,
  KiCad settings/colors, FreeCAD preferences/theme, Vesktop theme/preferences.
- Environment, autostart, MIME associations, Flatpak appearance overrides.
- Source image, wallpaper, theme files and package/Flatpak/extension inventories.

Home paths are substituted at installation. Session-specific document-portal
paths for the logo-menu image are replaced with a permanent app-private asset.
Source icons/theme assets are compressed with symlinks preserved. Credentials,
browser accounts/history/bookmarks, shell history, project workspaces, caches,
SSH/GPG private keys and unrelated application account data are excluded.
This is a desktop configuration backup, not a full home-directory backup.

## Artwork

```sh
eva01-art                 # static colored artwork
eva01-art --width 64      # larger version
eva01-art --plain         # ordinary uncolored ASCII
fastfetch                 # artwork beside system information
```

`assets/eva-head-source.png` is the supplied reference, preserved unchanged.
`scripts/build-ascii.py` rebuilds the ASCII assets; rebuilding needs Pillow,
while playback needs only Python's standard library. The image's violet armor,
lime accents, blue jaw and amber neck are retained using Fastfetch color codes.
Theme/icon assets retain their upstream license files in the asset archive;
the supplied Evangelion artwork is not an original asset of this repository.

## Update the backup

```sh
./backup.sh
git diff --stat
git add .
git commit -m "Update EVA01 desktop settings"
git push
```

Run `EVA01_REFRESH_ASSETS=1 ./backup.sh` after changing icons, cursor, or GTK
theme assets. The snapshot script uses an explicit allowlist and removes common
credential/history fields from structured preferences. The checker rejects
common credential formats, account databases, unsafe archive entries and files
too large for ordinary GitHub Git. Review new configurations before committing.

To roll back a configuration restore:

```sh
python3 scripts/restore.py ~/.local/state/eva01/backups/<timestamp>
```

Rollback restores files from that installer run. Package installs, extension
installs, GSettings and session environment changes are not reversed by the
file rollback. No repository script closes apps or restarts the desktop.
