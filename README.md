# dotclaude

My Claude Code configuration, in one repo, in two halves.

**Global half** (`home/`, `modules/`) gets symlinked into `~/.claude` and applies to
every project on the machine.

**Per project half** (`plugins/`, `.claude-plugin/`) is a plugin marketplace. A
project opts into the plugins it wants by committing one small settings file.

Same repo, two delivery mechanisms. That distinction is the whole design.

## Layout

```
dotclaude/
├── .claude-plugin/marketplace.json   catalog of the plugins below
├── home/                             symlinked into ~/.claude, always on
│   ├── CLAUDE.md                     global instructions
│   ├── settings.json                 global settings
│   └── skills/                       skills available in every project
├── modules/                          CLAUDE.md fragments, imported on demand
│   └── databricks-conventions.md
├── plugins/                          installed per project
│   ├── core/
│   └── databricks/
│       └── skills/lakeflow-review/
├── templates/
│   └── project-settings.json         copy into a new project
└── install.sh
```

## Global setup, once per machine

```bash
git clone git@github.com:schmucas/dotclaude.git ~/git-repos/dotclaude
cd ~/git-repos/dotclaude
./install.sh
```

That creates:

```
~/.claude/CLAUDE.md     -> ~/git-repos/dotclaude/home/CLAUDE.md
~/.claude/settings.json -> ~/git-repos/dotclaude/home/settings.json
~/.claude/skills        -> ~/git-repos/dotclaude/home/skills
~/.claude/modules       -> ~/git-repos/dotclaude/modules
```

Symlinks are live. Edit a file here, or `git pull`, and every project sees the
change on the next Claude Code launch. Nothing to reinstall.

Run `./install.sh --dry` first if you want to see what it would touch. Any real
file already sitting at one of those paths gets backed up, not overwritten.

## Per project setup

Register the marketplace once:

```
/plugin marketplace add schmucas/dotclaude
```

Then in any project, either install interactively:

```
/plugin install databricks@luca
```

or commit `templates/project-settings.json` to `<project>/.claude/settings.json`.
Claude Code then offers to install the listed plugins when the folder is trusted,
so a fresh clone of that project is configured with no manual step.

Update installed plugins with `/plugin marketplace update luca`. Unlike the
symlinks, plugins are cached copies, so they update on demand rather than live.

## Which half does a thing belong in?

| What | Where | Why |
| --- | --- | --- |
| Instructions for every project | `home/CLAUDE.md` | loads automatically, no per project wiring |
| A skill you want everywhere | `home/skills/<name>/SKILL.md` | always available |
| A skill for some projects only | `plugins/<plugin>/skills/<name>/SKILL.md` | opt in per repo, keeps unrelated projects clean |
| Prose reused by several projects | `modules/<name>.md` | imported with `@~/.claude/modules/<name>.md` |
| Anything specific to one project | that project's own `CLAUDE.md` | does not belong here |

## Gotchas

Installing a plugin copies its directory into a cache, so a plugin cannot reference
paths outside itself such as `../shared`. Shared content has to be duplicated or
symlinked inside the plugin directory.

`@path` imports in a `CLAUDE.md` do not save context. The imported file expands at
launch, exactly as if pasted. Imports buy organization and reuse, not a smaller
prompt. Imports resolve up to four hops deep.

Nothing secret goes in this repo. It is public. Tokens belong in a secret manager,
machine specific overrides belong in `settings.local.json`, which is gitignored.
