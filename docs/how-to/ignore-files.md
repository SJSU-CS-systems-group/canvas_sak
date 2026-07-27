# exclude files from processing

when canvas-sak walks a directory — downloading submissions, uploading course content,
bundling code for a similarity check — you usually don't want everything in it.
`node_modules/`, `.git/`, build output, and `.DS_Store` are noise at best and, in a moss
submission, actively harmful: they swamp the real code and slow the comparison down.

ignore patterns use the same syntax as `.gitignore`, so you already know it.

## two places to put patterns

### per directory: `canvas-sak-ignore.lst`

drop a file named `canvas-sak-ignore.lst` in the directory you're working in. one
pattern per line; blank lines and lines starting with `#` are ignored:

```
# build output
build/
dist/
*.o

# editor and os cruft
.DS_Store
.idea/

# dependencies — never useful in a similarity check
node_modules/
venv/
```

this is the right place for anything specific to one assignment or one course.

### everywhere: the `[IGNORE]` section of your config

for patterns you always want, add an `[IGNORE]` section to your canvas-sak config file
(`canvas-sak help-me-setup` prints its location):

```ini
[IGNORE]
ds_store=.DS_Store
pycache=__pycache__/
node=node_modules/
```

each entry is `name=pattern`. the name on the left is just a label so you can tell them
apart — only the pattern on the right is used.

patterns from both sources are combined; neither replaces the other.

## pattern syntax

| pattern | matches |
|---|---|
| `*.log` | any `.log` file — `*` does not cross directory separators |
| `**/tmp` | `tmp` at any depth |
| `?` | exactly one character |
| `build/` | the directory `build` and its contents — trailing `/` means directories only |
| `!keep.log` | **un**-ignores something an earlier pattern matched |

negation with `!` is evaluated in order, so put the exception after the rule it
excepts:

```
*.log
!important.log
```

## checking it works

ignore patterns apply to the commands that walk the filesystem — `code-similarity`,
`download-submissions`, and the course-content commands. all of them default to a dry
run, so you can see exactly which files would be included before anything happens:

```bash
canvas-sak code-similarity "CS 146" "Homework 1"
```

if a file you expected to be skipped shows up in that list, the pattern didn't match —
check for a stray leading `/`, or a missing trailing `/` on a directory pattern.
