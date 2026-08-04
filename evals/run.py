#!/usr/bin/env python3
"""Measure whether the right skill or agent loads for a given prompt.

Triggering is stochastic, so a single run tells you very little. Every case runs
`--runs` times and the result is a rate. A case that fires 7 times in 10 is a
description problem that one green run would have hidden.

    python3 evals/run.py                 # every case, 5 runs each
    python3 evals/run.py --runs 10
    python3 evals/run.py --filter lakeflow
    python3 evals/run.py --json report.json

Needs the `claude` CLI on PATH and working auth. Costs tokens, so this is not
wired into pull request CI.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
CASES = Path(__file__).resolve().parent / "triggers.yaml"

# Below this, a case is treated as a real defect rather than noise.
PASS_THRESHOLD = 0.8


def invoke(prompt: str, timeout: int) -> set[str]:
    """Run one prompt headlessly and return the skills and agents that loaded.

    Args:
        prompt: The user turn to send.
        timeout: Seconds before giving up on the run.

    Returns:
        Set of skill names and subagent types observed in the tool calls. Empty
        when nothing from this repo loaded, which is the expected result for a
        negative case.
    """
    try:
        proc = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--output-format",
                "stream-json",
                "--verbose",
                "--max-turns",
                "1",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {f"<error: {type(exc).__name__}>"}

    loaded: set[str] = set()
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        for block in (event.get("message") or {}).get("content", []) or []:
            if block.get("type") != "tool_use":
                continue
            args = block.get("input") or {}
            if block.get("name") == "Skill" and args.get("skill"):
                loaded.add(str(args["skill"]).split(":")[-1])
            elif block.get("name") == "Task" and args.get("subagent_type"):
                loaded.add(str(args["subagent_type"]))
    return loaded


def evaluate(case: dict, runs: int, timeout: int, workers: int) -> dict:
    """Run one case `runs` times and summarise the outcome."""
    expected = case.get("expect")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        observations = list(pool.map(lambda _: invoke(case["prompt"], timeout), range(runs)))

    if expected is None:
        hits = sum(1 for obs in observations if not obs)
    else:
        hits = sum(1 for obs in observations if expected in obs)

    # What loaded instead, ranked, so a failure names its competitor.
    confusions: dict[str, int] = {}
    for obs in observations:
        for name in obs:
            if name != expected:
                confusions[name] = confusions.get(name, 0) + 1

    return {
        "prompt": case["prompt"],
        "expected": expected or "(nothing)",
        "why": case.get("why", ""),
        "rate": hits / runs,
        "hits": hits,
        "runs": runs,
        "confused_with": dict(sorted(confusions.items(), key=lambda kv: -kv[1])),
    }


def main() -> int:
    """Run the suite and print a report. Returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5, help="repeats per case, default 5")
    parser.add_argument("--filter", default="", help="only cases whose prompt or expectation matches")
    parser.add_argument("--timeout", type=int, default=120, help="seconds per run")
    parser.add_argument("--workers", type=int, default=3, help="concurrent runs")
    parser.add_argument("--json", type=Path, help="also write the full report here")
    args = parser.parse_args()

    cases = yaml.safe_load(CASES.read_text())["cases"]
    if args.filter:
        needle = args.filter.lower()
        cases = [
            c for c in cases
            if needle in c["prompt"].lower() or needle in str(c.get("expect", "")).lower()
        ]
    if not cases:
        sys.exit("no cases matched the filter")

    print(f"{len(cases)} cases, {args.runs} runs each\n")

    results = []
    for case in cases:
        result = evaluate(case, args.runs, args.timeout, args.workers)
        results.append(result)

        rate = result["rate"]
        mark = "PASS" if rate >= PASS_THRESHOLD else "FAIL"
        print(f"[{mark}] {rate:>5.0%}  {result['expected']:<24} {result['prompt'][:60]}")
        if rate < PASS_THRESHOLD and result["confused_with"]:
            instead = ", ".join(f"{k} x{v}" for k, v in result["confused_with"].items())
            print(f"         loaded instead: {instead}")
            if result["why"]:
                print(f"         expected because: {result['why']}")

    failed = [r for r in results if r["rate"] < PASS_THRESHOLD]
    mean = sum(r["rate"] for r in results) / len(results)

    print(f"\n{len(results) - len(failed)}/{len(results)} cases above {PASS_THRESHOLD:.0%}, "
          f"mean trigger rate {mean:.0%}")

    if args.json:
        args.json.write_text(json.dumps({"mean_rate": mean, "cases": results}, indent=2))
        print(f"report written to {args.json}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
