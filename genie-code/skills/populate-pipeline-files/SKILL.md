---
name: genie-code-populate-pipeline-files
description: Batching pattern for creating and filling in many empty Lakeflow Pipeline files with createAsset/editAsset, including why 60-second timeouts on empty-file edits mean success, not failure. Use whenever Genie Code creates and populates more than a couple of empty pipeline files in one go.
---

# Populating multiple pipeline files

## Pattern

When creating and populating many empty pipeline files:

1. Create all files with `createAsset` first.
2. Use `editAsset` in batches of 3-5 files.
3. For empty files: `old_text=""` and `replace_all=false`.
4. Expect 60-second timeouts: they indicate success, not failure.
5. Spot-check 2-3 files after each batch to verify.
6. Don't retry timeouts, proceed to the next batch.

## Why timeouts happen

The file write succeeds but the acknowledgment is slow, due to backend
workspace filesystem latency, not compute availability.

## Red flags

- `"old_text not found"` means the pattern is wrong or the file already has
  content.
- Use `readAssetById` to inspect the actual current content.
