<!--
Release announcement template for canvas-sak.

A tag is not a release announcement, and a list of commit subjects is not one either.
This document answers "should I upgrade, and what will it cost me?" — which a diff
can never answer.

Worth remembering who reads this: teachers, often mid-semester, with a live gradebook.
The question behind every release is "will this change what my commands do to my
course?" Answer it explicitly, even when the answer is "no".

Copy this into the GitHub release body, fill it in, delete this comment.
-->

# canvas-sak {{VERSION}}

{{One short paragraph: what this release is about and why it exists. Not a list.
If it's a bugfix release, say what class of bug and who was hit by it. If it's a
feature release, say what's now possible that wasn't before.}}

## Highlights

### {{HEADLINE_1}}

{{What it is, why it matters, and the actual command showing it:}}

```bash
canvas-sak {{...}}
```

{{Link to the relevant page under docs/.}}

### {{HEADLINE_2}}

<!-- Three at most. If everything is a highlight, nothing is. -->

## ⚠️ Breaking changes

<!-- Mark these unmistakably and ALWAYS pair each with its migration step. If there
     are none, write "None." explicitly — an absent section reads as an oversight,
     and for a tool that writes to live courses that ambiguity is expensive. -->

None.

### {{WHAT_BROKE}}

**Why:** {{rationale — people forgive breakage they understand}}

**Migrate:**

```diff
- canvas-sak {{old usage}}
+ canvas-sak {{new usage}}
```

## Does this change what any command does to my course?

<!-- Specific to this project, and the thing a teacher most needs to know. Call out
     any change to what gets written to canvas, to a --dryrun default, or to how a
     data file (due dates, assignment groups, ignore patterns) is parsed. "No" is a
     perfectly good answer — but say it. -->

{{No / yes, and exactly what.}}

## Other changes

{{Everything else, grouped: Added / Fixed / Changed. GitHub's auto-generated
"what's changed" list is fine HERE, below the hand-written sections — never
instead of them.}}

## Thanks

<!-- Name everyone who contributed to this release and say what they did. A bare
     username list isn't creditable on a CV; "fixed the qti import for courses whose
     term hadn't started" is. Use GitHub handles so the mention notifies them.

     Thank the people who filed good bug reports too — they did real work and are
     almost never named. -->

Thanks to @{{HANDLE}} for {{contribution}}.

## Upgrading

```bash
pip install --upgrade canvas-sak
```

Full changelog: https://github.com/SJSU-CS-systems-group/canvas_sak/compare/{{PREV_TAG}}...{{TAG}}

---

<!--
Release checklist (matches the project's existing flow):

  1. bump version in pyproject.toml
  2. move CHANGELOG.md "## Unreleased" entries under the new version + date
  3. commit, tag, push
  4. build and publish to PyPI
  5. install the published version in a clean venv and run `canvas-sak --version`
  6. create the GitHub release using this template  <-- the step that keeps getting skipped
  7. post it to Discussions -> Announcements

Step 6 matters more than it looks: the GitHub releases page is the first thing a
prospective user sees, and it is currently the staleest thing in the project.
-->
