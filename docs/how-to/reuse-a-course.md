# reuse a course from a previous semester

canvas's own course copy gives you an opaque duplicate: to change the wording on one
page you click into canvas, find the page, and edit it in a rich-text box. that's fine
for one page and miserable for forty.

`download-course-content` and `upload-course-content` turn a course into markdown files
on disk. once it's text, you can edit it in your editor, search and replace across the
whole course, and keep it in git — then push it into next semester's shell.

## the workflow

```bash
# 1. pull last semester's course down (it has ended, so --inactive)
mkdir cs146-fall && cd cs146-fall
canvas-sak download-course-content "CS 146 Fall 2025" --all --inactive --no-dryrun

# 2. edit the files. change dates, fix typos, update the syllabus.

# 3. see what would be pushed into the new shell
canvas-sak upload-course-content "CS 146 Spring 2026" --all --inactive

# 4. push it
canvas-sak upload-course-content "CS 146 Spring 2026" --all --inactive --no-dryrun
```

both commands default to `--dryrun`, including the download — so step 1 needs
`--no-dryrun` to actually write files to disk.

`--inactive` appears throughout because both the finished course and the not-yet-started
one are invisible by default. see [how courses are
found](../explanation/finding-courses.md).

## choosing what to transfer

`--all` covers everything. you can also pick individual kinds of content, each of which
maps to a subdirectory:

| flag | directory |
|---|---|
| `--pages` | `pages/` |
| `--assignments` | `assignments/` |
| `--discussions` | `discussions/` |
| `--announcements` | `announcements/` |
| `--files` | `files/` |
| `--modules` | `modules/` |

use `--target` (download) or `--source` (upload) to work somewhere other than the
current directory.

## page headers

each page file starts with optional header lines — `key: value`, one per line, before
the markdown body:

```markdown
title: Week 1 — Introduction
published: true
front_page: false

the actual content of the page starts here, in ordinary markdown.
```

recognised keys are `title`, `published`, `publish_at`, and `front_page`. parsing stops
at the first line that isn't a recognised key, and that line onward is treated as
content — so a document that happens to begin with `Note: something` won't lose it.

## discussion headers

discussion files work the same way: optional `key: value` header lines, then the
discussion description in markdown. discussions are always created threaded.

```markdown
title: Discussion: Week 3: Compute
points: 1
assignment_group: Study Discussion
available: 2026-08-24-13:00
due: 2026-08-31-13:00
until: 2026-08-31-13:00
allow_rating: true
only_graders_can_rate: true

reply with your own study question about this week's topic.
```

`title`, `published`, and `publish_at` work as for pages. the graded headers —
`points`, `assignment_group`, `available`, `due`, and `until` — make the discussion
a graded discussion: `points` is the score it is graded out of, `assignment_group`
names an assignment group that must already exist in the course, and the dates use
the due-dates file format (`YYYY-MM-DD-hh:mm`, local time) with the same meanings
as `set-due-dates`. `allow_rating` lets replies be liked, and
`only_graders_can_rate` restricts liking to graders.

## sharing one style across pages

markdown gives you a page canvas will render plainly. if you want a consistent visual
wrapper without hand-writing html in every file, add a `template:` header naming an html
file relative to your `--source` directory:

```markdown
title: Week 1 — Introduction
template: templates/week.html
week_number: 1

content in markdown, as usual.
```

in `templates/week.html`, `$body` receives the rendered markdown, and any other
`$variable` becomes an additional header key you can set per page:

```html
<div class="week">
  <h1>Week $week_number</h1>
  $body
</div>
```

variables you don't set come out empty. template variables must appear *after* the
`template:` line in the page's headers.

## keeping it in git

the point of having your course as text is that you can version it:

```bash
git init && git add . && git commit -m "cs146 fall 2025 as taught"
```

next year you diff instead of remembering.

## a caveat worth knowing

`upload-course-content` skips content that already exists unless you pass `--force`. if
you edit a page locally and re-upload without `--force`, nothing happens and the command
reports success — which reads as a silent failure. use `--force` when you mean to
overwrite.
