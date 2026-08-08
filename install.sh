#!/usr/bin/env bash
# Symlink the one global file this repo owns into ~/.claude.
#
# Everything else here ships as a plugin, and Claude Code installs a plugin at
# whatever scope you ask for, so none of it needs a link. Only CLAUDE.md does: a
# plugin cannot deliver always-on user instructions, and you cannot check a git
# repo out into ~/.claude, which Claude Code owns.
#
# Never link settings.json. Claude Code writes to that file, so a link would let
# it edit this repo behind your back. See the README.
#
#   ./install.sh          link
#   ./install.sh --dry    show what would happen
#   ./install.sh --unlink remove the link

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HOME/.claude"
MODE="${1:-link}"

case "$MODE" in
  link | --dry | --unlink) ;;
  *)
    printf 'unknown mode: %s\n' "$MODE" >&2
    exit 1
    ;;
esac

# Each entry: <path inside repo/home>  ->  <path inside ~/.claude>
LINKS=(
  "CLAUDE.md"
)

# Links earlier versions of this script created, back when the repo shipped a
# global half. Pruned on every run so an old install is not left pointing at
# paths this repo no longer has.
RETIRED=(
  "settings.json"
  "skills"
  "hooks"
  "modules"
)

log() { printf '%s\n' "$*"; }

# True only for a symlink pointing back inside this repo, which is the one thing
# this script could have created. A real file, or a link somewhere else, is not
# ours to remove. If the repo has moved since the link was made the prefix stops
# matching and we leave the link alone, which is the safe way to be wrong.
ours() {
  local path="$1" dest
  [[ -L "$path" ]] || return 1
  dest="$(readlink "$path")"
  [[ "$dest" == "$REPO"/* ]]
}

prune_one() {
  local dst="$TARGET/$1"
  ours "$dst" || return 0
  if [[ "$MODE" == "--dry" ]]; then
    log "would unlink $dst (retired)"
  else
    rm "$dst"
    log "unlink $dst (retired)"
  fi
}

link_one() {
  local src="$1" dst="$2"
  if [[ ! -e "$src" ]]; then
    log "skip   $dst (no $src)"
    return
  fi
  case "$MODE" in
    --dry)
      log "would  $dst -> $src"
      ;;
    --unlink)
      if [[ -L "$dst" ]]; then
        rm "$dst"
        log "unlink $dst"
      else
        log "skip   $dst (not a symlink)"
      fi
      ;;
    link)
      # Back up a real file or directory that is in the way, never clobber it.
      if [[ -e "$dst" && ! -L "$dst" ]]; then
        mv "$dst" "$dst.bak.$(date +%Y%m%d%H%M%S)"
        log "backup $dst -> $dst.bak.*"
      fi
      ln -sfn "$src" "$dst"
      log "link   $dst -> $src"
      ;;
  esac
}

mkdir -p "$TARGET"

for name in "${RETIRED[@]}"; do
  prune_one "$name"
done

for name in "${LINKS[@]}"; do
  link_one "$REPO/home/$name" "$TARGET/$name"
done

log ""
log "done. verify with: ls -la $TARGET"
