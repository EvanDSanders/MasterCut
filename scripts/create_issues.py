#!/usr/bin/env python3
"""Create a GitHub issue per annotated .py file listed in structure.md.

Dry run by default. Pass --run to create issues and add them to the project.
"""
import argparse
import re
import subprocess
from pathlib import Path

REPO = "EvanDSanders/MasterCut"
PROJECT_NUMBER = "1"
PROJECT_OWNER = "EvanDSanders"


def parse(path):
    stack = []  # (indent, dirname)
    entries = []  # [path, [desc lines]]
    for raw in Path(path).read_text().splitlines():
        if "Video File Structure" in raw:
            break
        stripped = raw.strip()
        if not stripped or stripped.startswith("- - -"):
            continue
        indent = len(raw) - len(raw.lstrip())
        if stripped.startswith(">"):
            if entries:
                text = stripped[1:].strip()
                if text:
                    entries[-1][1].append(text)
            continue
        if not stripped.startswith("- "):
            continue
        name = re.split(r"\s{2,}|\s\(", stripped[2:].strip())[0].strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if name.endswith(".py"):
            full = "/".join([d for _, d in stack] + [name])
            entries.append([full, []])
        else:
            stack.append((indent, name.rstrip("/")))
            # directory descriptions must not attach to the previous file
            entries.append([None, []])
    return [(p, "\n".join(d)) for p, d in entries if p and d]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="structure.md")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    items = parse(args.file)
    for title, body in items:
        print(f"[{title}]\n  {body}\n")
        if not args.run:
            continue
        url = subprocess.run(
            ["gh", "issue", "create", "-R", REPO, "--title", title, "--body", body],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        subprocess.run(
            ["gh", "project", "item-add", PROJECT_NUMBER,
             "--owner", PROJECT_OWNER, "--url", url],
            check=True,
        )
        print(f"  created {url}")
    print(f"{len(items)} issue(s) {'created' if args.run else 'would be created (dry run)'}")


if __name__ == "__main__":
    main()
