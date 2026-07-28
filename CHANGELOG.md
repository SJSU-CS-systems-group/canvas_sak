# Changelog

## Unreleased

## 1.2.0 - 2026-07-28

- fix `todo --remove` failing to import on python 3.10 and 3.11: two f-strings in
  `todo.py` had a backslash inside the expression, which is only legal from 3.12
  (pep 701). the whole package failed to import on those versions, so every
  command was affected, not just `todo`
- raise `requires-python` to `>=3.10` (was `>=3.7`): click 8.2+ requires 3.10 and
  the test suite already targets its `CliRunner` api, so the old floor advertised
  support that pip could not actually resolve
- add package metadata that was missing from every release so far: project urls
  (source, changelog, issues), trove classifiers, keywords, and an spdx license
  field, so the pypi page links back to the repository
- add github actions ci: tests on python 3.10-3.14, plus a job that builds the
  wheel and installs it into a clean interpreter — the check that would have
  caught the 1.0.29 and 1.0.30 install failures before release
- add `CONTRIBUTING.md` and `CONTRIBUTORS.md`
- add `docs/`: a getting-started tutorial, how-to guides for due dates, assignment
  groups, course reuse, quiz settings and ignore patterns, explanations of the
  dry-run convention and of how courses are matched, and a command reference
  generated from `--help` and checked in ci so it cannot drift
- move the reference material that was in `README.md` into `docs/`, and rewrite the
  readme as a pitch with a runnable example above the install instructions
- add issue and pull request templates, including one asking people how they use
  canvas-sak — five years with zero issues tells us nothing about who depends on it
- add a dev container so contributors get a working environment in one click, built
  and tested in ci so it cannot rot
- fix `upload-course-content --pages --force` silently not updating existing
  pages: the canvas pages API ignores attributes not wrapped in `wiki_page`,
  so page edits now send `wiki_page=...`
- add styling support to `upload-course-content` pages: a `template:` header
  names an html template file (relative to `--source`) whose `$body`
  placeholder receives the rendered markdown; other `$variables` in the
  template become additional page header keys (empty if unset), so pages can
  share a hand-styled wrapper while keeping plain markdown sources

## 1.1.0 - 2026-07-10

- add `settings-navigation` command with `list` and `update` subcommands to
  view and manage a course's navigation menu; `update` makes the given items
  visible (passed as arguments and/or piped on stdin) and hides the rest
- add `--active/--inactive` flag to `upload-qti-quiz` (defaults to active) so
  courses whose term has not started can be targeted with `--inactive`

## 1.0.30 - 2026-07-07

- relax all remaining exact dependency pins to `>=` floors so future python
  upgrades don't break installation
- fix tests for click >= 8.2 (CliRunner no longer takes mix_stderr; stderr is
  captured separately by default)

## 1.0.29 - 2026-07-07

- relax lxml pin to `>=4.9.3` so installation works on Python 3.13/3.14
  (lxml 4.9.3 has no wheels for those versions and fails to build from source)
