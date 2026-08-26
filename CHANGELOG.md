# Changelog

## Unreleased

## 1.8.0 - 2026-08-25

- pages: `MODULE[Name]` macros in page bodies resolve to the course's module
  by that name at upload (as a markdown link target or href value), so pages
  can link modules without hardcoding course or module ids and stay portable
  across courses; unknown module names warn and leave the macro alone
- pages: template variable values are rendered as inline markdown, so header
  values can use links and emphasis instead of raw html

## 1.7.0 - 2026-08-25

- `rubrics` accepts an optional rubric name and displays that rubric's
  criteria and ratings in an editable text format
- `rubrics COURSE RUBRIC --update-with file` updates the named rubric's
  definition from the file, or creates the rubric if the course doesn't have
  one by that name (which also copies a rubric between courses); without a
  rubric name `--update-with` applies rubric-to-assignment associations as
  before
- new how-to guide: manage rubrics

## 1.6.0 - 2026-08-21

- markdown to html conversion now supports fenced code blocks, tables, sane
  lists (adjacent ordered/unordered lists stay separate), and GFM-style line
  breaks (single newlines become `<br>`)

## 1.5.0 - 2026-08-12

- `list-students --enrollments` shows how each student is enrolled in the class
  (Student/TA/Instructor/etc), added as a tab-separated column with
  comma-separated roles

## 1.4.0 - 2026-08-12

- `list-students --sections` lists the sections each student is in, added as a
  tab-separated column with comma-separated section names

## 1.3.0 - 2026-07-31

- `upload-course-content --pages` now resolves images referenced with relative
  paths in page markdown: the image file is looked up relative to the page's
  `.md` file, uploaded to the course files (reused if it is already there), and
  the img src is rewritten to the canvas file link. external and absolute srcs
  are left alone
- non-`.md` files in the `pages/` directory are no longer parsed as pages, which
  also fixes a `UnicodeDecodeError` crash when an image sat next to a page

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
