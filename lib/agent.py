#!/usr/bin/python3 -I
"""pramana: the window that asks for your password when an app wants admin
rights the standard way (mounting a disk, changing a system setting,
`pkexec`). Without a polkit agent those requests fail silently.

It registers as the polkit authentication agent of your graphical session
and, for each request, shows what's asking and why, in your desktop's look
(lib/theme.py: Vyom's panels, your varna theme only while everything stays
readable). The password goes to polkit's own helper (polkit-agent-helper-1,
which checks it with PAM), never to anything else. Installed root-owned as
/usr/local/lib/pramana/agent.py (/usr/local/bin/pramana links to it) and
run by the pramana user service.

    pramana              run the agent (the service does this)
    pramana --preview    show the window with a sample request (no polkit)
    pramana --version

Keys:
# keybind: Pramana/password prompt | Enter | Authenticate with the typed password
# keybind: Pramana/password prompt | Esc | Cancel the request (the app is told no)
"""
import importlib.util
import logging
import os
import pwd
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Polkit", "1.0")
gi.require_version("PolkitAgent", "1.0")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango, Polkit, PolkitAgent  # noqa: E402

VERSION = "0.2.0"
APP_ID = "io.github.theyashsawarkar.Pramana"
OBJECT_PATH = "/io/github/theyashsawarkar/pramana/Agent"
log = logging.getLogger("pramana")


def _load_theme_module():
    # By path from this root-owned directory: python -I puts no script
    # directory on sys.path, and nothing is ever loaded from the user's home.
    spec = importlib.util.spec_from_file_location(
        "pramana_theme", os.path.join(os.path.dirname(os.path.realpath(__file__)), "theme.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


THEME = _load_theme_module()


def _load_remote_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("pramana_remote", os.path.join(os.path.dirname(os.path.realpath(__file__)), "remote.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REMOTE = _load_remote_module()

EXTRA_CSS = """
.elevate .mode.auth { background-color: alpha(@warn, 0.15); color: @warn; }
.elevate .message { font-size: 14px; font-weight: 600; color: @text; }
.elevate .kv-key { color: @muted; font-size: 12px; }
.elevate .kv-val { font-family: "JetBrainsMono Nerd Font", monospace; font-size: 12px; color: @subtext; }
"""


def keycap(keys, t):
    return (f"<span background='{t['crust']}' foreground='{t['subtext']}' font_family='JetBrainsMono Nerd Font'> "
            + GLib.markup_escape_text(keys) + " </span>")


def who(identity):
    """A polkit identity as a name ("yash", or "root")."""
    if isinstance(identity, Polkit.UnixUser):
        try:
            return pwd.getpwuid(identity.get_uid()).pw_name
        except KeyError:
            return f"uid {identity.get_uid()}"
    return identity.to_string()


class PromptWindow(Adw.ApplicationWindow):
    """One request: what's asking, the password field, Authenticate / Cancel."""

    def __init__(self, app, t, message, action_id, details, identities, on_password, on_cancel):
        super().__init__(application=app, title="Password needed")
        self.t, self.on_password, self.on_cancel = t, on_password, on_cancel
        self.identities = identities
        self.remote = None          # the request's line to ekatva (lib/remote.py), if it runs
        self.attempts = 0
        self.add_css_class("elevate")
        self.set_default_size(560, -1)
        self.connect("close-request", lambda *_: (self.cancel(), True)[1])
        keys = Gtk.EventControllerKey()
        keys.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        keys.connect("key-pressed", self.on_key)
        self.add_controller(keys)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top = Gtk.Box(spacing=12)
        top.add_css_class("topbar")
        pill = Gtk.Box(spacing=7, valign=Gtk.Align.CENTER)
        pill.add_css_class("mode")
        pill.add_css_class("auth")
        glyph = Gtk.Label(label="\U000f033e")   # nf-md-lock
        glyph.add_css_class("glyph")
        pill.append(glyph)
        pill.append(Gtk.Label(label="Password needed"))
        top.append(pill)
        title = Gtk.Label(label="an app wants admin rights", xalign=0, hexpand=True)
        title.add_css_class("title")
        top.append(title)
        outer.append(top)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.add_css_class("body")
        msg = Gtk.Label(label=message or "Authentication is required.", xalign=0, wrap=True)
        msg.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        msg.add_css_class("message")
        body.append(msg)

        # What's asking: the action and, when polkit says, the program.
        facts = [("Action", action_id)]
        program = details.get("program", "")
        if details.get("command_line"):
            facts.append(("Command", details["command_line"]))
        elif program:
            facts.append(("Program", program))
        grid = Gtk.Grid(column_spacing=14, row_spacing=6)
        for i, (k, v) in enumerate(facts):
            kl = Gtk.Label(label=k, xalign=0, valign=Gtk.Align.START)
            kl.add_css_class("kv-key")
            vl = Gtk.Label(label=v, xalign=0, wrap=True, selectable=True)
            vl.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            vl.add_css_class("kv-val")
            grid.attach(kl, 0, i, 1, 1)
            grid.attach(vl, 1, i, 1, 1)
        body.append(grid)

        # As whom: you when you're an admin, else the first admin polkit offers.
        self.who = Gtk.DropDown.new_from_strings([who(i) for i in identities])
        if len(identities) > 1:
            row = Gtk.Box(spacing=10)
            lab = Gtk.Label(label="As", xalign=0)
            lab.add_css_class("kv-key")
            row.append(lab)
            row.append(self.who)
            body.append(row)

        self.error = Gtk.Label(xalign=0, visible=False, wrap=True)
        self.error.add_css_class("error")
        body.append(self.error)

        bottom = Gtk.Box(spacing=8, margin_bottom=8)
        self.password = Gtk.PasswordEntry(show_peek_icon=True, hexpand=True, placeholder_text="Your password")
        self.password.connect("activate", lambda *_: self.submit())
        bottom.append(self.password)
        cancel = Gtk.Button(label="Cancel")
        cancel.add_css_class("btn")
        cancel.add_css_class("deny")
        cancel.connect("clicked", lambda *_: self.cancel())
        bottom.append(cancel)
        self.ok = Gtk.Button(label="Authenticate")
        self.ok.add_css_class("btn")
        self.ok.add_css_class("run")
        self.ok.connect("clicked", lambda *_: self.submit())
        bottom.append(self.ok)
        body.append(bottom)
        outer.append(body)

        foot = Gtk.Box(spacing=16)
        foot.add_css_class("foot")
        for k, what in (("Enter", "authenticate"), ("Esc", "cancel")):
            h = Gtk.Label(use_markup=True)
            h.set_markup(f"{keycap(k, t)} {GLib.markup_escape_text(what)}")
            h.add_css_class("hint")
            foot.append(h)
        outer.append(foot)
        self.set_content(outer)
        self.password.grab_focus()

    def identity(self):
        return self.identities[self.who.get_selected()] if self.identities else None

    def on_key(self, _c, keyval, _code, _state):
        if keyval == Gdk.KEY_Escape:
            self.cancel()
            return True
        return False

    def busy(self, on):
        for w in (self.password, self.ok, self.who):
            w.set_sensitive(not on)

    def submit(self):
        if not self.password.get_sensitive():
            return
        pw = self.password.get_text()
        self.password.set_text("")
        self.busy(True)
        self.error.set_visible(False)
        self.on_password(self.identity(), pw)

    def failed(self, text):
        self.attempts += 1
        if self.remote:
            self.remote.send({"t": "wrong", "attempts": self.attempts})
        self.busy(False)
        self.error.set_label(text)
        self.error.set_visible(True)
        self.password.grab_focus()

    def cancel(self):
        cb, self.on_cancel = self.on_cancel, None
        if cb:
            cb()
        self.destroy()

    def remote_answer(self, answer):
        """An answer from the phone: the same as typing it here."""
        if not self.password.get_sensitive():
            return False
        if not answer["approve"]:
            self.cancel()
            return False
        self.password.set_text(answer["password"])
        answer["password"] = None
        self.submit()
        return False

    def done(self, status):
        if self.remote:
            self.remote.send({"t": "done", "status": status})
            self.remote.close()
            self.remote = None


class Agent(PolkitAgent.Listener):
    """polkit calls initiate_authentication for each request in this session."""

    def __init__(self, app):
        super().__init__()
        self.app = app

    def do_initiate_authentication(self, action_id, message, icon_name, details, cookie, identities,
                                   cancellable, callback, user_data):
        task = Gio.Task.new(self, cancellable, callback, user_data)
        info = {k: details.lookup(k) for k in details.get_keys()} if details else {}
        log.info("request %s from %s", action_id, info.get("program") or info.get("polkit.caller-pid") or "?")
        # You first, when you're one of the identities polkit accepts.
        me = os.getuid()
        identities = sorted(identities, key=lambda i: not (isinstance(i, Polkit.UnixUser) and i.get_uid() == me))
        state = {"session": None, "done": False, "win": None}

        def finish(ok, why=""):
            if state["done"]:
                return
            state["done"] = True
            if state["win"] is not None:
                state["win"].done("completed" if ok else "denied")
                state["win"].on_cancel = None
                state["win"].destroy()
            if ok:
                task.return_boolean(True)
            else:
                task.return_error(GLib.Error.new_literal(Gio.io_error_quark(), why or "Cancelled",
                                                         Gio.IOErrorEnum.CANCELLED))

        def on_password(identity, password):
            session = PolkitAgent.Session.new(identity, cookie)
            state["session"] = session

            def request(_s, _prompt, _echo_on):
                session.response(password)

            def completed(_s, gained):
                state["session"] = None
                if gained:
                    log.info("granted %s", action_id)
                    finish(True)
                elif not state["done"] and state["win"] is not None:
                    state["win"].failed("That password didn't work. Try again, or Esc to cancel.")

            session.connect("request", request)
            session.connect("show-error", lambda _s, text: log.warning("polkit: %s", text))
            session.connect("completed", completed)
            session.initiate()

        def on_cancel():
            if state["session"] is not None:
                state["session"].cancel()
            log.info("cancelled %s", action_id)
            finish(False, "The user cancelled")

        if cancellable is not None:   # polkit gave up (the app went away)
            cancellable.connect(lambda *_: GLib.idle_add(lambda: (finish(False, "Cancelled by polkit"), False)[1]))

        win = PromptWindow(self.app, self.app.theme, message, action_id, info, identities, on_password, on_cancel)
        state["win"] = win
        # Answerable from the phone too, when ekatva runs.
        what = info.get("command_line") or info.get("program") or action_id
        win.remote = REMOTE.Remote.start(
            {"id": action_id, "via": "polkit", "requester": info.get("program") or action_id,
             "reason": message or "", "commands": [{"cmd": what, "why": action_id}]},
            lambda answer: GLib.idle_add(win.remote_answer, answer))
        win.present()

    def do_initiate_authentication_finish(self, result):
        return result.propagate_boolean()


def session_subject():
    """This user's graphical session. The service runs in the user manager,
    outside any session, so not by our own pid: by XDG_SESSION_ID (the
    desktop exports it to the user manager), else logind's display session."""
    sid = os.environ.get("XDG_SESSION_ID")
    if not sid:
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            user = bus.call_sync("org.freedesktop.login1", "/org/freedesktop/login1",
                                 "org.freedesktop.login1.Manager", "GetUser", GLib.Variant("(u)", (os.getuid(),)),
                                 GLib.VariantType("(o)"), Gio.DBusCallFlags.NONE, -1, None).unpack()[0]
            sid = bus.call_sync("org.freedesktop.login1", user, "org.freedesktop.DBus.Properties", "Get",
                                GLib.Variant("(ss)", ("org.freedesktop.login1.User", "Display")),
                                GLib.VariantType("(v)"), Gio.DBusCallFlags.NONE, -1, None).unpack()[0][0]
        except GLib.Error as e:
            log.warning("logind: %s", e.message)
    if sid:
        return Polkit.UnixSession.new(sid)
    return Polkit.UnixSession.new_for_process_sync(os.getpid(), None)


class App(Adw.Application):
    def __init__(self, preview=False):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.preview = preview
        self.theme = THEME.FALLBACK
        self.agent = None
        self.handle = None
        self.connect("activate", self.on_activate)

    def on_activate(self, _app):
        self.theme = THEME.theme(pwd.getpwuid(os.getuid()).pw_dir)
        Adw.StyleManager.get_default().set_color_scheme(
            Adw.ColorScheme.FORCE_DARK if self.theme["dark"] else Adw.ColorScheme.FORCE_LIGHT)
        provider = Gtk.CssProvider()
        provider.load_from_string(THEME.theme_css(self.theme) + EXTRA_CSS)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
        self.hold()   # resident: no window most of the time
        if self.preview:
            win = PromptWindow(self, self.theme, "Authentication is required to mount Kingston DataTraveler (/dev/sdb1)",
                               "org.freedesktop.udisks2.filesystem-mount", {"program": "/usr/bin/udisksctl mount -b /dev/sdb1"},
                               [Polkit.UnixUser.new(os.getuid()), Polkit.UnixUser.new(0)],
                               lambda *_: None, self.quit)
            win.present()
            return
        self.agent = Agent(self)
        try:
            self.handle = PolkitAgent.register_listener(self.agent, session_subject(), OBJECT_PATH)
        except GLib.Error as e:
            # Another agent already serves this session (a desktop's own): step aside.
            log.error("can't register as the session's polkit agent: %s", e.message)
            self.quit()
            sys.exit(3)   # the service doesn't restart on 3
        log.info("registered as the polkit agent for session %s", os.environ.get("XDG_SESSION_ID", "?"))


def main():
    if "--version" in sys.argv:
        print(f"pramana {VERSION}")
        return 0
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__.split("Keys:")[0].strip())
        return 0
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(name)s: %(message)s")
    return App(preview="--preview" in sys.argv).run([])


if __name__ == "__main__":
    sys.exit(main())
