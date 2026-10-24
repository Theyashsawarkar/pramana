#!/usr/bin/env bash
# Installs pramana root-owned, so no program running as your user can edit
# the window that takes your password. Run it as your user from a clone of
# this repo; it calls sudo.
#
#   ./install.sh            install whatever differs, enable the user service
#   ./install.sh --check    list what differs, exit 1 if anything does
#   ./install.sh --uninstall
#
# Installs:
#   /usr/local/lib/pramana/agent.py               the polkit agent (GTK 4)
#   /usr/local/lib/pramana/theme.py               its look and the theme readability check
#   /usr/local/bin/pramana                        -> agent.py
#   /usr/local/lib/systemd/user/pramana.service   runs it in your graphical session
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
lib=/usr/local/lib/pramana
unit=/usr/local/lib/systemd/user/pramana.service
mode=${1:-install}

if [ "$mode" = "--uninstall" ]; then
  systemctl --user disable --now pramana.service 2>/dev/null || true
  sudo rm -rf "$lib" "$unit"
  [ -L /usr/local/bin/pramana ] && sudo rm -f /usr/local/bin/pramana
  systemctl --user daemon-reload 2>/dev/null || true
  echo "pramana removed"
  exit 0
fi
check=false
[ "$mode" = "--check" ] && check=true

n=0
differs() { n=$((n + 1)); if $check; then echo "differs: $1"; fi; }

# Dependencies: Arch package names; other distributions, see the README.
if command -v pacman >/dev/null; then
  missing=()
  for p in python python-gobject gtk4 libadwaita polkit; do
    pacman -Q "$p" >/dev/null 2>&1 || missing+=("$p")
  done
  if [ "${#missing[@]}" -gt 0 ]; then
    differs "packages not installed: ${missing[*]}"
    $check || sudo pacman -S --needed --noconfirm "${missing[@]}"
  fi
fi

if [ -d "$lib" ] && [ "$(stat -c '%U %a' "$lib")" = "root 755" ]; then :; else
  differs "$lib (root-owned directory)"
  $check || sudo install -d -m755 -o root -g root "$lib"
fi
files=(
  "lib/agent.py:$lib/agent.py:755"
  "lib/theme.py:$lib/theme.py:755"
  "systemd/pramana.service:$unit:644"
)
for entry in "${files[@]}"; do
  IFS=: read -r src dst perm <<<"$entry"
  src=$here/$src
  if cmp -s "$src" "$dst" 2>/dev/null && [ "$(stat -c '%U %a' "$dst")" = "root $perm" ]; then continue; fi
  differs "$dst"
  $check || sudo install -Dm"$perm" -o root -g root "$src" "$dst"
done
if [ "$(readlink /usr/local/bin/pramana 2>/dev/null)" != "$lib/agent.py" ]; then
  differs "/usr/local/bin/pramana (link to agent.py)"
  $check || sudo ln -sfn "$lib/agent.py" /usr/local/bin/pramana
fi
if ! systemctl --user is-enabled -q pramana.service 2>/dev/null; then
  differs "pramana.service (user service, not enabled)"
  $check || { systemctl --user daemon-reload; systemctl --user enable pramana.service; }
fi

if $check; then
  [ "$n" -eq 0 ] && echo "pramana is installed and matches this repo"
  [ "$n" -eq 0 ]
  exit
fi
[ "$n" -eq 0 ] && { echo "pramana already up to date"; exit 0; }
systemctl --user daemon-reload
systemctl --user restart pramana.service 2>/dev/null || true
echo "pramana installed: $n change(s). Try: pkexec true"
