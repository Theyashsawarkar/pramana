# Contributing to pramana

Thanks for helping. Bug reports, ideas and pull requests are welcome.
Because this window takes the password for admin rights, changes are
reviewed for security first: keep them small and explain the reasoning.

## Development setup

```sh
git clone https://github.com/Theyashsawarkar/pramana ~/code/pramana
cd ~/code/pramana
python -m py_compile lib/*.py
python -m unittest discover -s tests -v
shellcheck install.sh
python3 lib/agent.py --preview     # the window with a sample request, no polkit
```

The installed copy is root-owned in `/usr/local`; test a change by running
`./install.sh` from your clone (it restarts the service), then a harmless
request: `pkexec true`.

## How it fits together

- `lib/agent.py`: registers with polkit as the session's authentication
  agent (`PolkitAgent.register_listener`); for each request opens the
  window, and hands the typed password to a `PolkitAgent.Session`, which
  passes it to polkit's setuid helper.
- `lib/theme.py`: the look, and the check that a varna palette keeps
  everything readable (shared with anumati).
- `systemd/pramana.service`: runs the agent in the graphical session.
- `install.sh`: installs them root-owned.

## Rules

- **The password goes only to polkit.** Never log it, keep it after the
  attempt, or pass it to anything but `Session.response`.
- **Show what polkit says.** The message, action and program come from
  polkit; never reword them into something friendlier but less exact.
- **Keys are discoverable**: a `# keybind: Pramana/<scope> | <keys> | <Verb> <object>`
  line in `lib/agent.py`'s header and a row in the README (CI checks).
- Every change gets a `CHANGELOG.md` entry; releases are tags `vX.Y.Z` with
  `VERSION` in `lib/agent.py` bumped.

## Pull requests

Describe what and why, and tick the template's checklist. By contributing
you agree your work is released under the [MIT License](LICENSE).
