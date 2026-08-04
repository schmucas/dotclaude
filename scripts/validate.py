#!/usr/bin/env python3
"""Validate this repo's Claude Code configuration.

Deterministic checks only. Anything requiring judgement (is a description
distinctive, is a skill too long) belongs to the docs-drift-checker agent or the
eval suite under evals/, not here.

Run locally with `python3 scripts/validate.py`, or `--quiet` to print failures
only. Exits 1 if any check fails.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FAILURES: list[str] = []
CHECKS = 0

# House style. Kept here rather than in a skill because it must be enforceable,
# not merely requested.
BANNED_CHARS = {"—": "em-dash", "–": "en-dash"}

MIN_DESCRIPTION_CHARS = 60


def check(condition: bool, message: str) -> bool:
    """Record the outcome of one check.

    Args:
        condition: True when the check passes.
        message: What is wrong, shown only on failure.

    Returns:
        The condition, so callers can short-circuit follow-up checks.
    """
    global CHECKS
    CHECKS += 1
    if not condition:
        FAILURES.append(message)
    return condition


def rel(path: Path) -> str:
    """Return a path relative to the repo root, for readable messages."""
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict | None:
    """Parse a JSON file, recording a failure instead of raising."""
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        check(False, f"{rel(path)}: invalid JSON, {exc}")
        return None


def frontmatter(path: Path) -> dict[str, str] | None:
    """Extract YAML frontmatter keys from a markdown file.

    Only top level `key: value` pairs are read, which is all the agent and skill
    formats use. Returns None when the file has no frontmatter block.
    """
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    return dict(re.findall(r"^([A-Za-z_]+):\s*(.*)$", match.group(1), re.M))


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def check_markdown_units() -> None:
    """Every agent and skill has valid frontmatter whose name matches its path."""
    units = sorted(ROOT.glob("plugins/*/agents/*.md")) + sorted(
        ROOT.glob("plugins/*/skills/*/SKILL.md")
    ) + sorted(ROOT.glob("home/skills/*/SKILL.md"))

    check(bool(units), "no agents or skills found, is the layout what this script expects")

    for unit in units:
        keys = frontmatter(unit)
        if not check(keys is not None, f"{rel(unit)}: missing frontmatter block"):
            continue

        expected = unit.parent.name if unit.name == "SKILL.md" else unit.stem
        name = keys.get("name", "")
        check(bool(name), f"{rel(unit)}: frontmatter has no name")
        check(
            name == expected,
            f"{rel(unit)}: name '{name}' does not match its directory '{expected}'",
        )

        description = keys.get("description", "")
        check(bool(description), f"{rel(unit)}: frontmatter has no description")
        check(
            len(description) >= MIN_DESCRIPTION_CHARS,
            f"{rel(unit)}: description is {len(description)} chars, too thin to "
            f"trigger reliably (want {MIN_DESCRIPTION_CHARS}+)",
        )


def check_json_parses() -> None:
    """Every JSON file in the repo parses."""
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        load_json(path)


def check_marketplace() -> None:
    """Every marketplace entry resolves to a real plugin whose name agrees."""
    manifest = ROOT / ".claude-plugin" / "marketplace.json"
    if not check(manifest.exists(), "missing .claude-plugin/marketplace.json"):
        return

    data = load_json(manifest)
    if data is None:
        return

    listed = set()
    for entry in data.get("plugins", []):
        source = ROOT / entry["source"].lstrip("./")
        plugin_json = source / ".claude-plugin" / "plugin.json"
        if not check(
            plugin_json.exists(),
            f"marketplace lists '{entry['name']}' at {entry['source']}, "
            "but no .claude-plugin/plugin.json is there",
        ):
            continue
        listed.add(source.name)
        plugin = load_json(plugin_json)
        if plugin:
            check(
                plugin.get("name") == entry["name"],
                f"{rel(plugin_json)}: name '{plugin.get('name')}' does not match "
                f"marketplace entry '{entry['name']}'",
            )

    on_disk = {p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()}
    for orphan in sorted(on_disk - listed):
        check(False, f"plugins/{orphan} exists but is not listed in marketplace.json")


def check_hook_targets() -> None:
    """Every command a hook config points at exists, is executable, has a shebang."""
    configs = sorted(ROOT.glob("plugins/*/hooks/hooks.json")) + [ROOT / "home" / "settings.json"]

    for config in configs:
        if not config.exists():
            continue
        data = load_json(config)
        if data is None:
            continue

        plugin_root = config.parent.parent if "plugins" in config.parts else ROOT

        for event, matchers in (data.get("hooks") or {}).items():
            for matcher in matchers:
                for hook in matcher.get("hooks", []):
                    command = hook.get("command", "")
                    if "${CLAUDE_PLUGIN_ROOT}" in command:
                        target = Path(command.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root)))
                    elif command.startswith("~/.claude/"):
                        # Symlinked from home/, so resolve against the repo instead.
                        target = ROOT / command.replace("~/.claude/", "home/", 1)
                    else:
                        continue

                    label = f"{rel(config)} [{event}]"
                    if not check(target.exists(), f"{label}: hook command not found, {command}"):
                        continue
                    check(
                        os.access(target, os.X_OK),
                        f"{label}: {rel(target)} is not executable, run chmod +x",
                    )
                    check(
                        target.read_bytes().startswith(b"#!"),
                        f"{label}: {rel(target)} has no shebang",
                    )


def check_mcp_config() -> None:
    """Bundled MCP configs parse and commit no workspace specific values."""
    for path in sorted(ROOT.glob("plugins/*/.mcp.json")):
        data = load_json(path)
        if data is None:
            continue
        blob = json.dumps(data)
        check(
            "mcpServers" in data,
            f"{rel(path)}: no mcpServers key",
        )
        check(
            not re.search(r"https://(?!\$)[\w.-]+\.(databricks|azuredatabricks|cloud)\b", blob),
            f"{rel(path)}: a literal workspace host is committed, use ${{DATABRICKS_HOST}}",
        )
        check(
            not re.search(r"\b(dapi[0-9a-f]{32}|Bearer\s+(?!\$)[A-Za-z0-9._-]{20,})", blob),
            f"{rel(path)}: looks like a literal token is committed",
        )


def check_eval_expectations() -> None:
    """Every skill or agent named in the eval suite still exists.

    This is the check that catches the most common drift in a repo like this:
    a skill gets renamed or deleted and the eval suite quietly starts measuring
    a thing that is not there.
    """
    cases_file = ROOT / "evals" / "triggers.yaml"
    if not cases_file.exists():
        return

    try:
        import yaml  # noqa: PLC0415, imported lazily so the rest runs without it
    except ImportError:
        print("note: pyyaml not installed, skipping eval expectation check", file=sys.stderr)
        return

    known = {p.parent.name for p in ROOT.glob("plugins/*/skills/*/SKILL.md")}
    known |= {p.parent.name for p in ROOT.glob("home/skills/*/SKILL.md")}
    known |= {p.stem for p in ROOT.glob("plugins/*/agents/*.md")}

    cases = yaml.safe_load(cases_file.read_text()).get("cases", [])
    check(bool(cases), "evals/triggers.yaml has no cases")

    for case in cases:
        check(bool(case.get("prompt")), "evals/triggers.yaml: a case has no prompt")
        expected = case.get("expect")
        if expected is None:
            continue  # a negative case, nothing to resolve
        check(
            expected in known,
            f"evals/triggers.yaml expects '{expected}', which is not a skill or "
            "agent in this repo",
        )

    covered = {c.get("expect") for c in cases if c.get("expect")}
    for orphan in sorted(known - covered):
        check(False, f"{orphan} has no eval case, add one to evals/triggers.yaml")


def check_house_style() -> None:
    """No em-dashes or en-dashes in prose the repo ships."""
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for line_no, line in enumerate(path.read_text().splitlines(), start=1):
            for char, label in BANNED_CHARS.items():
                if char in line:
                    check(False, f"{rel(path)}:{line_no}: {label}, use a comma, colon or parentheses")


def check_readme_links() -> None:
    """Every relative link in the README points at something that exists."""
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    for target in re.findall(r"\]\((?!https?:|#)([^)]+)\)", readme.read_text()):
        path = ROOT / target.split("#", 1)[0]
        check(path.exists(), f"README.md: dead relative link, {target}")


def main() -> int:
    """Run every check and report. Returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="print failures only")
    args = parser.parse_args()

    for fn in (
        check_markdown_units,
        check_json_parses,
        check_marketplace,
        check_eval_expectations,
        check_hook_targets,
        check_mcp_config,
        check_house_style,
        check_readme_links,
    ):
        fn()

    if FAILURES:
        print(f"{len(FAILURES)} of {CHECKS} checks failed:\n", file=sys.stderr)
        for failure in FAILURES:
            print(f"  {failure}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"{CHECKS} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
