# Changelog

Newest first. Releases are tags (`vX.Y.Z`) with `VERSION` in `lib/agent.py`.

## v0.1.0 -- 2026-10-24

- First release: a polkit authentication agent for desktops that don't
  bring one (sway, Hyprland, river…). When an app asks for admin rights the
  standard way (mounting a disk, a settings change, `pkexec`), a window
  shows what's asking (the message, the polkit action, the program) and
  takes your password; it goes to polkit's own helper, never anywhere else.
- Vyom's look in your varna theme, through the same readability checks as
  anumati's window: a theme can change tints, never hide anything.
- Choose who to authenticate as when polkit offers several admins (you
  first). A wrong password keeps the window open to try again; Esc cancels
  and the app is told no.
- Runs as the `pramana` user service in the graphical session, restarting
  on failure, and steps aside (exit 3, no restart) when another agent
  already serves the session. Logs to the journal (`journalctl --user -u pramana`).
- `install.sh` installs it root-owned into `/usr/local` and enables the service.
- It started inside anumati and became its own tool before release:
  anumati stays the approval window for AI agents' root commands.
