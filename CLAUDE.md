# pramana -- notes for agents

A polkit authentication agent: the window that asks for your password when
an app wants admin rights. Its own repo, pulled into Vayu
(github.com/Theyashsawarkar/vayu, whose CLAUDE.md "Plugins" rules apply);
it must work on any Linux desktop without its own agent.

- `lib/agent.py` (the agent and its window, GTK 4 / libadwaita, PolkitAgent
  GI), `lib/theme.py` (the look and the palette readability check; the same
  module as anumati's, keep the two in step), `systemd/pramana.service`.
  `install.sh` installs them root-owned into `/usr/local`: never make the
  installed copies user-writable or load code from the user's home.
- Security first: the password goes only to polkit's helper
  (`PolkitAgent.Session.response`); never log, store or pass it elsewhere.
  Read SECURITY.md before changing the flow.
- Not anumati: anumati is the approval window for AI agents' root commands.
  Don't merge the two.
- Keys: `# keybind: Pramana/password prompt | <keys> | <Verb> ...` in
  `lib/agent.py`'s header, and a README row (CI checks).
- Every change: a CHANGELOG.md entry; releases are tags with `VERSION` in
  `lib/agent.py` bumped. `python -m py_compile lib/*.py`,
  `python -m unittest discover -s tests` and `shellcheck install.sh` must pass.
- Test the window with `pramana --preview` in a headless sway
  (WLR_BACKENDS=headless, its own D-Bus session and XDG_RUNTIME_DIR), never
  on the user's screen; a real request: `pkexec true`, which the user answers.
- The website (docs/, GitHub Pages) is generated: after changing README.md, CHANGELOG.md or docs/adr/, run `python3 scripts/build-site.py` and commit docs/ (CI checks it). A significant design decision gets a new ADR in docs/adr/ (next number; supersede, never rewrite).
