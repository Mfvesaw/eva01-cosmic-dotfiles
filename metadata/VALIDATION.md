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

Steam/Obsidian checks: Chromium computed-style fixtures verified purple/lavender
colors, 8 px Steam controls and unchanged image filters. Obsidian appearance
selects EVA01 dark mode. Millennium release SHA-256 was verified against GitHub
release metadata; 32/64-bit native loader dependencies resolve. The running
Steam client was not restarted, so a live Steam visual inspection is pending
the user's normal restart. No claim of a live app screenshot is made.

An isolated full restore discovered a synthetic Obsidian vault, retained its
existing font preference and note, and installed the theme. A synthetic Steam
account file remained unchanged. The portable loader's dry run wrote no runtime
files; its actual isolated install produced the verified native libraries, hook
copies, executable wrapper, Fish function and desktop actions without sudo.
