# Changelog

## 1.0.30 - 2026-07-07

- relax all remaining exact dependency pins to `>=` floors so future python
  upgrades don't break installation
- fix tests for click >= 8.2 (CliRunner no longer takes mix_stderr; stderr is
  captured separately by default)

## 1.0.29 - 2026-07-07

- relax lxml pin to `>=4.9.3` so installation works on Python 3.13/3.14
  (lxml 4.9.3 has no wheels for those versions and fails to build from source)
