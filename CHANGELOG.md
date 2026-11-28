# Changelog

Newest first. Releases are tags (`vX.Y.Z`) with `VERSION` in `lib/agent.py`.

## Unreleased

- Website: pranali joins the family list in the footer; the site builder passes ruff.
- The website, closer to Vayu's own: the tool's screenshot blurred behind the page, a centred hero with the logo and the verse, the page you're on as the white pill, glass "On this page" and footer panels, releases as cards. No glow behind the logo, no coloured line beside the verse.
- **Spatial look**: the password window's buttons, mode and badges are pills, its cards rounder; without varna, Vayu's Spatial colours.
- The website has Vayu's Spatial look: graphite glass, a floating navigation bar, near-white for links and the main button, and the tool's own colour only as its signature (the logo's glow, the shloka's line, the release dots). No more all-caps labels.

## v0.3.0 -- 2026-11-09

- Every corner is rounded: the website's callouts.
- A logo and a shloka at the top of the README and the website: every Vayu tool has them now.

- `Ctrl+j` / `Ctrl+k` change who you authenticate as (when polkit offers
  several) without leaving the password field: the identity menu used to
  need Tab and the arrow keys. The same keys move a list from a search box
  in every Vayu tool.
- The footer shows the mode (INSERT: the prompt only types).
- The keys are data, resolved by Vyom's keys module (`lib/keys.py`,
  vendored, installed root-owned with the rest); `scripts/keybinds.py`
  writes the `# keybind:` lines and the README table, and CI checks them.

## v0.2.1 -- 2026-10-28

- `lib/remote.py` in step with anumati 1.4.0's copy: `parse_answer` and
  `Remote.start` take an optional `root` (the requests that need the
  password; anumati's commands that run as you don't). pramana doesn't
  pass it, so every answer still needs the password: no change here.

## v0.2.0 -- 2026-10-26

- Answer from your phone: when [ekatva](https://github.com/Theyashsawarkar/ekatva)
  runs, each password window also hands its request (polkit's message,
  the action, the program) to ekatva, which shows it on your paired phone.
  Your password typed there fills the field here and goes to polkit the
  same way; denying there cancels. Wrong passwords are reported back; the
  window sends nothing secret out and finds ekatva by uid. Without ekatva
  nothing changes. `lib/remote.py` (the same module as anumati's), ADR 4.

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
