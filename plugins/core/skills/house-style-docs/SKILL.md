---
name: house-style-docs
description: Write or review a README, architecture doc or Mermaid diagram in Luca's house style. Use whenever authoring or editing documentation in a repo of his, especially a public one, and whenever adding a diagram to a README. Covers prose rules, structure, badges, tables and the GitHub Mermaid rendering limits.
---

# Docs house style

## Prose rules

- **No em-dashes.** They read as AI-generated. Use a comma, a colon, parentheses,
  or two sentences.
- **No emoji** in headings, badges or body text. A single one in a centered header
  block is the most that is ever acceptable.
- Short declarative sentences. State the thing, then the reason, then stop.
- Explain the design decision, not just the mechanism. A reader who understands why
  a choice was made can extend it. A reader who only knows what the code does
  cannot.
- No marketing adjectives: powerful, seamless, blazing, robust, cutting-edge.
- Second person for instructions, first person for opinions and decisions.

## README structure

Public repos follow this order. Skip a section rather than padding it.

1. Centered header: title, one sentence describing the whole thing, a row of badges.
2. **The idea.** The design question the repo answers, and the answer. This is the
   section that decides whether anyone reads further.
3. **What is in here.** Linked list of the actual artifacts, grouped by kind.
4. **Repo map.** A tree block with an inline comment per entry.
5. **Setup.** Copy-pasteable commands, split by how often they are run.
6. **Design notes.** The tradeoffs taken and why.
7. **Gotchas worth knowing.** Things learned the hard way. Often the most useful
   section in the file.
8. **Reference.** Links out to official docs.

Badges are flat and monochrome apart from one accent. They link to real
documentation, not to a build that does not exist.

Comparison of two approaches goes in a table with the criteria as rows, not as two
bullet lists.

## Mermaid on GitHub

GitHub renders Mermaid but does not support styling on every diagram type.

- **`erDiagram` cannot be styled.** `classDef` and the `:::` operator produce a
  lexer error. To colour-code facts against dimensions, use a `flowchart` with
  node labels that look like entities, and apply `classDef` there.
- Keep `classDef` colours consistent across every diagram in the repo, and pick
  values that survive both light and dark theme.
- Prefer `flowchart LR` for pipelines and `flowchart TB` for layered architecture.
- Use `subgraph` for grouping rather than drawing boxes with unicode.
- Label every edge that is not self-explanatory.
- Verify a diagram renders on GitHub itself. The local preview is more permissive.

## Review mode

When reviewing rather than writing, report `[FIX] <file>:<line> - <issue>` with a
one line replacement suggestion. Flag em-dashes, emoji, marketing language,
aspirational tense, unstyleable `erDiagram` styling, and any section that exists
but is empty.
