---
name: pipeline-comment-style
description: Load whenever writing or editing a notebook, pipeline source file, or other data-engineering code in this project, any time a comment would document a caveat, gotcha, decision, or other non-obvious detail. Enforces short bullet-point comments instead of long prose paragraphs.
---

# Pipeline comment style

Rule: when code needs a comment for a caveat, decision, or non-obvious
detail, write it as short bullet points, not a prose paragraph.

## When this applies

- Any notebook or pipeline source file in this project.
- Only for comments that explain a caveat, gotcha, decision, or other
  non-obvious detail, never for comments that restate what the code does.

## How to write it

- One bullet per fact or decision, one short line each.
- Lead with the fact, skip the backstory.
- Drop filler ("note that", "it's important to understand that").
- A single one-line caveat stays a single line: bullets are for 2+ points,
  not padding for one.

## Example

Don't:

```python
# This value is calculated using population_stddev_samp instead of
# population_stddev_pop because we are treating these 6 years of data
# as a sample of the full population of years rather than the complete
# population, which is the more statistically appropriate choice here.
```

Do:

```python
# population_stddev_samp: 6 years are a sample, not the full population.
```

Multiple points, still bullets:

```python
# - BLS pads header/values with spaces; trim before use as key or number.
# - Q05 is the annual average, not a fifth quarter (exclude from sums).
```
