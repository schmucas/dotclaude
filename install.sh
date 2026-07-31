#!/usr/bin/env bash
# Symlink the global (user level) parts of this repo into ~/.claude.
# Run once per machine. Re-run any time you add something to home/.
#
#   ./install.sh          link
#   ./install.sh --dry    show what would happen
#   ./install.sh --unlink remove the links

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HOME/.claude"
MODE="${1:-link}"

# Each entry: <path inside repo/home>  ->  <path inside ~/.claude>
LINKS=(
  "CLAUDE.md"
  "settings.json"
  "skills"
  "hooks"
)
# modules/ lives at repo root, not under home/, but is linked into ~/.claude too
# so that CLAUDE.md files can import it as @~/.claude/modules/<name>.md

log() { printf '%s\n' "$*"; }

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
    *)
      log "unknown mode: $MODE" >&2
      exit 1
      ;;
  esac
}

mkdir -p "$TARGET"

for name in "${LINKS[@]}"; do
  link_one "$REPO/home/$name" "$TARGET/$name"
done

link_one "$REPO/modules" "$TARGET/modules"

log ""
log "done. verify with: ls -la $TARGET"
