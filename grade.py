#!/usr/bin/env python3
"""Grade the storefront's checks against the hidden breaks.

For each patch under breaks/, apply it to a scratch clone of the storefront at the commit under test, start the app
through the harness, run every behavior's check with `vf.py verify`, and record whether any behavior read Failed.
A break nobody catches is a check that passes on broken code. The agent that built the checks never saw these patches.

    grade.py <storefront repo> [--commit HEAD] [--only 03,07]

Prints one line per break and a tally, and writes results/<time>.md with the same plus each run's result lines.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = Path(".agents/skills/verify-storefront")


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check).stdout


def sub_feature_ids(harness):
    ids = []
    for path in sorted((harness / "features").glob("*.md")):
        in_section = False
        for line in path.read_text().splitlines():
            if line.startswith("## "):
                in_section = line.strip() == "## Sub-features"
            elif in_section and (match := re.match(r"^- ([a-z0-9][\w.-]*):", line)):
                ids.append(match.group(1))
    return ids


def vf(clone, *args, timeout=900):
    command = ["python3", str(HARNESS / "scripts" / "framework" / "vf.py"), *args]
    result = subprocess.run(command, cwd=clone, capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--only", help="comma-separated patch number prefixes, such as 03,07")
    args = parser.parse_args()

    patches = sorted((HERE / "breaks").glob("*.patch"))
    if args.only:
        wanted = args.only.split(",")
        patches = [p for p in patches if any(p.name.startswith(w) for w in wanted)]
    scratch = Path(tempfile.mkdtemp(prefix="storefront-grade-"))
    clone = scratch / "storefront"
    subprocess.run(["git", "clone", "-q", str(args.repo), str(clone)], check=True)
    git(clone, "checkout", "-q", args.commit)
    subprocess.run(["uv", "sync", "-q"], cwd=clone, check=True)
    ids = sub_feature_ids(clone / HARNESS)
    if not ids:
        sys.exit("no sub-features with checks in the feature map")

    lines, caught = [], 0
    for patch in patches:
        git(clone, "apply", str(patch))
        try:
            code, output = vf(clone, "verify", "--start", *ids)
            results = [l for l in output.splitlines() if re.match(r"^- [\w.-]+: (Verified|Failed|Not verified|Passed|Stopped)", l) or ": Failed" in l]
            failed = sorted({m.group(1) for l in output.splitlines() if (m := re.match(r"^- ([\w.-]+): Failed", l))})
            if failed:
                caught += 1
                lines.append(f"{patch.stem}: CAUGHT by {', '.join(failed)}")
            else:
                lines.append(f"{patch.stem}: MISSED (verify exit {code})")
            lines.append("    " + "\n    ".join(results[:12]))
        finally:
            vf(clone, "stop")
            git(clone, "apply", "-R", str(patch))
            git(clone, "checkout", "-q", "--", ".")
    tally = f"{caught}/{len(patches)} hidden breaks caught at {git(clone, 'rev-parse', '--short', 'HEAD').strip()}"
    print("\n".join(lines)); print(tally)
    results_dir = HERE / "results"; results_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    (results_dir / f"{stamp}.md").write_text(f"# Grading {stamp}\n\n{tally}\n\n" + "\n".join(lines) + "\n")
    shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
