#!/usr/bin/env python3
"""PreToolUse guard that blocks writes violating this repo's Databricks conventions.

Reads the Claude Code hook payload on stdin. Exits 2 with an explanation on
stderr when a banned pattern appears in the content being written, which blocks
the tool call and hands the reason back to Claude. Exits 0 otherwise.
"""

import json
import re
import sys

# (compiled pattern, human readable reason)
BANNED = [
    (re.compile(r"dbfs:/|/dbfs/"), "DBFS path. Use a Unity Catalog table or /Volumes/<cat>/<schema>/<vol>/."),
    (re.compile(r"/mnt/"), "Legacy mount path. Use /Volumes/<cat>/<schema>/<vol>/."),
    (re.compile(r"dbutils\.fs\."), "dbutils.fs is DBFS era. Use Unity Catalog Volumes."),
    (re.compile(r"^\s*import\s+dlt\b|@dlt\.", re.M), "Legacy DLT spelling. Use `from pyspark import pipelines as dp` and @dp.table."),
]

# Files where a mention is documentation, not usage.
DOC_SUFFIXES = (".md", ".mdx", ".txt", ".rst")

# Directories whose whole purpose is to contain violations. Without this, the
# guard blocks the eval fixtures that exist to prove reviews still catch them.
EXEMPT_DIRS = ("/evals/fixtures/", "/tests/fixtures/", "/fixtures/")


def extract(payload: dict) -> tuple[str, str]:
    """Return (file_path, text) for the content this tool call would write.

    Args:
        payload: Decoded hook payload from stdin.

    Returns:
        Tuple of the target file path and the concatenated new content.
    """
    tool_input = payload.get("tool_input", {}) or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""

    parts = [
        tool_input.get("content"),
        tool_input.get("new_string"),
        tool_input.get("new_source"),
    ]
    for edit in tool_input.get("edits", []) or []:
        parts.append(edit.get("new_string"))

    return path, "\n".join(p for p in parts if isinstance(p, str))


def main() -> int:
    """Run the guard. Returns the process exit code."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never block on a payload we cannot parse

    path, text = extract(payload)
    normalised = path.replace("\\", "/")
    if not text or path.endswith(DOC_SUFFIXES):
        return 0
    if any(exempt in normalised for exempt in EXEMPT_DIRS):
        return 0

    hits = [reason for pattern, reason in BANNED if pattern.search(text)]
    if not hits:
        return 0

    print(
        "Blocked by the databricks plugin convention guard.\n"
        f"File: {path or '(unknown)'}\n"
        + "\n".join(f"  - {h}" for h in hits)
        + "\nRewrite the content to satisfy these before retrying.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
