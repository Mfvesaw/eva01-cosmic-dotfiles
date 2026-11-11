# Verification

- Fish syntax checked and a real PTY session started, accepted input, and exited.
- Fastfetch parsed the config and printed the static colored ASCII logo.
- Noninteractive Fish produced only the command output.
- A controlling PTY test answered terminal capability probes and verified `clear`
  and Ctrl+L redraw Fastfetch. A partly typed command survived Ctrl+L and executed
  successfully. Scripted `clear` and option/help output stayed unmodified.
- Installer dry run verified checksums and wrote no files.
- Installed into an isolated temporary home containing existing Fish settings,
  Zen profile/CSS, VS Code JSONC settings, Vesktop settings and a GTK CSS symlink.
- Verified profile discovery, existing setting preservation, home path substitution,
  static Fastfetch setup, theme/cursor extraction and safe symlink replacement.
- Rolled back that installation and confirmed old files/settings were restored.
- Checked 82,617 archive members for unsafe paths/link targets.
- Backup scanner checked common credential formats and excluded account databases.

The optional Fedora package and Flatpak reinstall modes were not run: the apps
are already installed on this machine. Different hardware/output settings and
future app versions may need adjustment.
