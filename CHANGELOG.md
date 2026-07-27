# Changelog

## Unreleased

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
