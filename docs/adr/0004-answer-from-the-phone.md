# 4. Answering from the phone, through ekatva, by the same path as typing

**Status:** Accepted  
**Date:** 2026-10-26

## Context

[ekatva](https://github.com/Theyashsawarkar/ekatva) links your phone and laptop end to end, and [anumati](https://github.com/Theyashsawarkar/anumati) (v1.3.0, its ADR 7) already takes root approvals from the phone. polkit prompts (mounting a disk, a settings change, `pkexec`) are the same need: you're away, something waits for your password.

## Decision

When ekatva runs, each password window also hands its request to ekatva's socket, `/run/user/<uid>/ekatva-root.sock`: polkit's message, the action, and the program or command line, exactly as the window shows them. An answer from the phone is applied as if typed: the password goes into the field and the same `submit` follows, to `PolkitAgent.Session` and polkit's own helper; "deny" is Esc. A wrong password is reported back so the phone can retry; completion or cancellation clears it on the phone.

`lib/remote.py` is the same module as anumati's (keep the two in step): only answers come in, nothing secret goes out, the socket is found by uid (never the environment), and answers are validated strictly.

## Consequences

- The guarantee holds: the password goes to polkit only (now possibly typed on the phone, carried over ekatva's end-to-end encrypted link into this window).
- Which phone may answer, with which confirmation, and the logs on both devices, are ekatva's (the "root" capability, off by default, fingerprint each time).
- Without ekatva nothing changes.
