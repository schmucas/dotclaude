---
name: databricks-remote-checkpoint
description: "Pause-and-confirm gate between local Databricks development and the real workspace. Use whenever Databricks code (job, pipeline, notebook, app) has passed local checks - written, locally tested, ruff clean - and the next step would be `databricks bundle validate`, `bundle deploy`, running a job/pipeline, or checking results on the workspace (CLI, SQL MCP, or any other means). Does not apply if the user's own request already explicitly asked for deploy/run. For how to actually validate, deploy or run, defer to the vendor databricks-dabs and databricks-jobs skills; this skill only decides whether to ask first."
---

# Local-to-remote checkpoint

Local development (writing the code, local tests, `ruff check`/`ruff format`) and
touching the real Databricks workspace (`bundle validate`, `bundle deploy`, running a
job or pipeline, checking results on the workspace) are two separate phases. Do not
slide from one into the other on your own initiative.

## When to stop and ask

Once the code is written and passes local checks (tests green, ruff clean, any other
local check the project defines), stop before running anything against Databricks.
Ask the user, in one message, whether to proceed with the full remote sequence:

1. `databricks bundle validate`
2. `databricks bundle deploy` (dev target)
3. Run the job / pipeline / app
4. Check the result on the workspace, by whatever means fits best: the `databricks`
   CLI, the Databricks SQL MCP, job run output, or anything else that answers the
   question

Ask once, covering the whole sequence, e.g.:

> Local dev is done: tests pass, ruff is clean. Want me to validate the bundle,
> deploy to dev, run it, and check the result on Databricks?

If they say yes, run all four steps without re-asking at each one. If a step fails,
or the remote run surfaces a bug, treat the fix as new local work: make the change,
re-run local checks, and open a fresh checkpoint before going back to remote.

## When this does not apply

If the user's own instruction already asked for the remote steps explicitly ("build
X, deploy it to dev, and check it's working"), this gate does not apply - proceed.
It exists only for the case where Claude would otherwise decide, unprompted, to move
from local code to the live workspace.

## Mechanics

For how `bundle validate`/`deploy`/`run` actually work, defer to the vendor
`databricks-dabs` and `databricks-jobs` skills. For checking results, use whatever
tool fits: the `databricks` CLI, the Databricks SQL MCP (`databricks-dbsql`,
`databricks-data-discovery`), or any other available means. This skill only governs
whether to ask first, not which tool validates the result.
