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

COSMIC Pomodoro compatibility: the installed 0.1.0 release pins libcosmic
03d0171, whose Theme config version is 1. Converted v2 colors were deserialized
by a native Rust checker with the 29-field legacy theme layout and matching
component/container/palette field definitions. Background and accent values
matched EVA01. The systemd user path unit is enabled for automatic synchronization.
The running applet PID was retained; timer preferences and process were not reset.

Public release checks: all reachable Git history was scanned for common credential
patterns before changing repository visibility. Both supplied wallpaper JPEGs
were copied byte-for-byte and contain no EXIF metadata. The public installer's
isolated dry run made no changes; an isolated install selected the nebula,
installed both original images, exposed both COSMIC wallpaper choices, and
rolled back the prior wallpaper configuration successfully. Documentation links
were checked against the repository files.
