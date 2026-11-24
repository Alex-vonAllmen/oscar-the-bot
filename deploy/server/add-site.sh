#!/usr/bin/env bash
# Prepare one static site on the server: web root, upload user, locked-down deploy key.
# Run as root:  sudo ./add-site.sh <name> ['ssh-ed25519 AAAA... comment']
# Creates /srv/sites/<name> owned by <name>-deploy. The key may only rsync into that folder.
# Safe to run again, for example to replace the key.
set -euo pipefail

site="${1:-}"
key="${2:-}"
if [[ ! "$site" =~ ^[a-z0-9-]+$ ]]; then
  echo "usage: sudo $0 <name> ['ssh-ed25519 AAAA...']   (name: lowercase letters, digits, hyphens)" >&2
  exit 1
fi
[[ $EUID -eq 0 ]] || { echo "run as root" >&2; exit 1; }

user="${site}-deploy"
root="/srv/sites/${site}"
rrsync="$(command -v rrsync || true)"
[[ -n "$rrsync" ]] || { echo "rrsync not found: apt install rsync" >&2; exit 1; }

install -d -m 755 -o root -g root /srv/sites /srv/sites/caddy
id "$user" >/dev/null 2>&1 || adduser --disabled-password --gecos "" "$user"
install -d -m 755 -o "$user" -g "$user" "$root"

if [[ -n "$key" ]]; then
  [[ "$key" =~ ^ssh-(ed25519|rsa)\ [A-Za-z0-9+/=]+ ]] || { echo "that does not look like a public key" >&2; exit 1; }
  install -d -m 700 -o "$user" -g "$user" "/home/${user}/.ssh"
  printf 'command="%s %s",restrict %s\n' "$rrsync" "$root" "$key" > "/home/${user}/.ssh/authorized_keys"
  chown "$user:$user" "/home/${user}/.ssh/authorized_keys"
  chmod 600 "/home/${user}/.ssh/authorized_keys"
fi

echo "ready: ${root}, upload user ${user}${key:+, key installed}"
echo "the user is not in the docker group, and must not be"
