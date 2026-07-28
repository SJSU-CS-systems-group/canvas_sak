# what

<!-- what does this change? one or two sentences. -->

# why

<!-- REQUIRED. what problem does this solve, and why this approach?

     this is the field reviewers care about most. the diff shows what changed; only
     you can explain why it should. if this closes an issue, link it — but still say
     why, because the issue may describe a symptom rather than a cause. -->

Closes #

# how to verify

<!-- how should a reviewer convince themselves this works?
     the exact commands to run, and what they should see. -->

# checklist

- [ ] tests added or updated — a bug fix should come with a test that fails without it
- [ ] `pytest -q` passes locally
- [ ] `CHANGELOG.md` updated under `## Unreleased`, saying *why* the change exists
- [ ] docs updated, if this changes what a command does
- [ ] anything that writes to canvas still defaults to a dry run (`--no-dryrun` to apply)

## breaking changes

<!-- none, or: what breaks and exactly what a user has to do differently. -->

none.

---

## ai assistance

<!-- ai-assisted contributions are welcome — please just tell us, so review can focus
     in the right place. see CONTRIBUTING.md for the full policy. -->

- [ ] this pr was written or substantially assisted by an llm

if checked, please confirm:

- [ ] i can explain the rationale behind every change here, and i'm not proposing a
      redesign i don't understand
- [ ] the diff is scoped to the change — no whole-file rewrites, reformatting, or
      unrelated refactoring bundled in
- [ ] i ran the tests and read the output myself
