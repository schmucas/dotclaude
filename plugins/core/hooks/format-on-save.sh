#!/usr/bin/env bash
# PostToolUse hook for Write|Edit: format the touched file, best-effort.
# Reads the hook JSON payload from stdin. Never fails the tool call -
# unknown extensions and missing formatters are silent no-ops.

input="$(cat)"
file="$(printf '%s' "$input" | jq -r '.tool_response.filePath // .tool_input.file_path // empty' 2>/dev/null)"
[[ -n "$file" && -f "$file" ]] || exit 0

have() { command -v "$1" >/dev/null 2>&1; }

case "${file##*.}" in
  js|jsx|ts|tsx|mjs|cjs|json|css|scss|less|md|mdx|yaml|yml|html|vue)
    if have prettier; then
      prettier --write "$file" >/dev/null 2>&1
    else
      npx --no-install prettier --write "$file" >/dev/null 2>&1
    fi
    ;;
  py)
    have ruff && ruff format "$file" >/dev/null 2>&1
    ;;
  go)
    have gofmt && gofmt -w "$file" >/dev/null 2>&1
    ;;
  rs)
    have rustfmt && rustfmt "$file" >/dev/null 2>&1
    ;;
esac

exit 0
