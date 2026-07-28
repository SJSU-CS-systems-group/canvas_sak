#!/usr/bin/env python3
"""Generate docs/reference/commands.md from the real ``--help`` output.

Hand-written reference docs rot silently: someone adds an option, nobody updates the
page, and six months later the docs describe a tool that no longer exists. This
generates the reference from the CLI itself, and CI re-runs it and fails if the
committed file has drifted (see .github/workflows/ci.yml).

Usage:
    python scripts/gen_command_reference.py            # write the file
    python scripts/gen_command_reference.py --check    # exit 1 if out of date
"""

import argparse
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "docs" / "reference" / "commands.md"

HEADER = """<!-- GENERATED FILE — do not edit by hand.
     Regenerate with: python scripts/gen_command_reference.py
     The text below comes from each command's own --help output. -->

# command reference

every canvas-sak command, straight from its `--help`. this page is generated, so it
cannot drift from the code.

this is the *reference* quadrant — it tells you what the options are, not which command
you want. if you don't know where to start, read the
[getting started tutorial](../tutorial/getting-started.md) or browse the
[how-to guides](../how-to/).

**two things that apply to almost every command:**

- commands that write to canvas default to `--dryrun`. add `--no-dryrun` to actually
  apply the change — see [why everything is a dry run](../explanation/dry-run.md).
- commands take a *partial* course name and require it to match exactly one course.
  see [how courses are found](../explanation/finding-courses.md).

"""


def run_help(*args):
    """Return the --help text for a command path, e.g. run_help("set-due-dates")."""
    result = subprocess.run(
        [sys.executable, "-m", "canvas_sak", *args, "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={"COLUMNS": "88", "PATH": "/usr/bin:/bin", "HOME": "/nonexistent"},
    )
    if result.returncode != 0:
        raise SystemExit(
            f"`canvas-sak {' '.join(args)} --help` failed:\n{result.stderr}"
        )
    return result.stdout.rstrip()


def list_commands():
    """Parse the top-level --help for the command names and their summaries."""
    text = run_help()
    body = text.split("Commands:", 1)[1]
    commands = []
    for line in body.splitlines():
        match = re.match(r"^\s{2}(\S+)\s+(.*)$", line)
        if match:
            commands.append((match.group(1), match.group(2).strip()))
    return commands


def build():
    commands = list_commands()

    parts = [HEADER, "## all commands\n"]
    for name, summary in commands:
        parts.append(f"- [`{name}`](#{name}) — {summary}")
    parts.append("")

    for name, _summary in commands:
        parts.append(f"## {name}\n")
        parts.append("```")
        parts.append(run_help(name))
        parts.append("```\n")

    return "\n".join(parts).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the committed file is out of date instead of rewriting it",
    )
    args = parser.parse_args()

    generated = build()

    if args.check:
        current = OUTPUT.read_text() if OUTPUT.exists() else ""
        if current != generated:
            print(
                f"{OUTPUT.relative_to(REPO_ROOT)} is out of date.\n"
                "run: python scripts/gen_command_reference.py",
                file=sys.stderr,
            )
            return 1
        print(f"{OUTPUT.relative_to(REPO_ROOT)} is up to date")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(generated)
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)} ({len(list_commands())} commands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
