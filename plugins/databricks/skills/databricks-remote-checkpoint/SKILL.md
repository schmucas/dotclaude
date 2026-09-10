---
name: databricks-remote-checkpoint
description: "Pause-and-confirm gate between local Databricks development and the real workspace. Use whenever Databricks code (job, pipeline, notebook, app, or anything else shipped to Databricks) has passed local checks - written, locally tested, ruff clean - and the next step would be putting it on the real workspace: validating, deploying to dev, running it, and checking the result there, whatever mechanism the project uses (Asset Bundles, `databricks apps deploy`, workspace import, CLI, MCP, ...). Does not apply if the user's own request already explicitly asked for deploy/run. For how to actually validate, deploy or run, defer to the matching vendor skill (databricks-dabs, databricks-jobs, databricks-apps, ...); this skill only decides whether to ask first."
---

# Local-to-remote checkpoint

Databricks projects have two phases: local development (writing the code, local
tests, `ruff check`/`ruff format`) and the real workspace (validate, deploy to dev,
run, check the result there). Do not slide from one into the other on your own
initiative, no matter which tooling the project deploys with.

## When to stop and ask

Once the code is written and passes local checks (tests green, ruff clean, any other
local check the project defines), stop before touching Databricks itself. Ask the
user, in one message, whether to proceed with the whole remote phase: validate,
deploy to dev, run it, and check the result there. Use whichever mechanism this
project actually deploys with, for example:

- Asset Bundles: `databricks bundle validate` -> `bundle deploy` (dev target) -> run
  the job/pipeline -> check the result
- A Databricks App: `databricks apps deploy` -> hit the running app -> check it
  behaves
- Anything else the project uses to get code onto the workspace and exercise it

Checking the result itself can go through any tool that answers the question: the
`databricks` CLI, the Databricks SQL MCP, job run output, the app's own logs, and so
on. This skill does not care which; it only cares that the user was asked first.

Ask once, covering the whole phase, e.g.:

> Local dev is done: tests pass, ruff is clean. Want me to validate, deploy to dev,
> run it, and check the result on Databricks?

If they say yes, run the whole remote phase without re-asking at each step. If a step
fails, or the remote run surfaces a bug, treat the fix as new local work: make the
change, re-run local checks, and open a fresh checkpoint before going back to remote.

## When this does not apply

If the user's own instruction already asked for the remote steps explicitly ("build
X, deploy it to dev, and check it's working"), this gate does not apply - proceed.
It exists only for the case where Claude would otherwise decide, unprompted, to move
from local code to the live workspace.

## Mechanics

For how validate/deploy/run actually work, defer to whichever vendor skill matches
the project: `databricks-dabs` and `databricks-jobs` for Asset Bundles, `databricks-apps`
for Apps, and so on. For checking results, defer similarly (`databricks-dbsql`,
`databricks-data-discovery`, or plain CLI usage). This skill does not own any of that
mechanics, and it does not narrow which tool is used for any step; it only governs
whether to ask before the remote phase starts.
