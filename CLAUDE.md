# dotclaude project notes

Context specific to working in this repo. Global instructions (branch and PR discipline,
docstrings, writing style) live in `~/.claude/CLAUDE.md`, symlinked from `home/CLAUDE.md`
in this repo, and apply here too.

## Keep README.md in sync with genie-code/skills/

`genie-code/skills/` has been renamed and extended more than once (skills added, moved,
or dropped the `genie-code-` prefix on their directory) without README.md's genie-code
table and repo map being updated to match. That leaves `scripts/validate.py`'s dead-link
check failing in CI, on PRs unrelated to genie-code.

Whenever a directory under `genie-code/skills/` is added, renamed or removed:

- Update the genie-code table and the repo map in README.md to match.
- Run `python3 scripts/validate.py` before pushing, and fix anything it flags rather than
  leaving it for the next PR to trip over.
