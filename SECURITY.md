# Security policy

pramana takes your password for admin rights, so security reports matter
more here than anywhere else in the project.

## Supported versions

Only the latest release gets fixes.

## Reporting a vulnerability

Please **don't open a public issue**. Report it privately through
[GitHub's security advisories](https://github.com/Theyashsawarkar/pramana/security/advisories/new):
what an attacker could do (for example, read the password, or make the
window misstate what's asking), from what position (a program running as
the user, a local user, ...), and how to reproduce it. You'll get a reply
within a week; a fix and a release follow as soon as it's confirmed, with
credit to you unless you'd rather not.

Out of scope, as the README explains: a program already running as your
user that is actively malicious (it could draw a lookalike window or stop
the service and register its own agent; true of every polkit agent). In
scope: anything that sends the password anywhere but polkit's helper,
keeps it, logs it, or lets a theme or the environment hide or fake what the
window shows.
