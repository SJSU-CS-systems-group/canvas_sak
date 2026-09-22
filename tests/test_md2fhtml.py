from canvas_sak.md2fhtml import md2htmlstr, md2htmllist


def test_fenced_code_block():
    md = "```python\nprint('hi')\n```"
    html = md2htmlstr(md)
    assert '<pre>' in html
    assert 'language-python' in html
    assert "print('hi')" in html
    # without the fenced_code extension the backticks leak into the output
    assert '```' not in html


def test_table():
    md = '\n'.join([
        '| name | score |',
        '| ---- | ----- |',
        '| alice | 90 |',
        '| bob | 85 |',
    ])
    html = md2htmlstr(md)
    assert '<table>' in html
    assert '<th>name</th>' in html
    assert '<td>alice</td>' in html


def test_nl2br_single_newline_breaks_line():
    md = 'line one\nline two'
    html = md2htmlstr(md)
    assert '<br' in html


def test_sane_lists_keeps_list_types_separate():
    md = '1. ordered item\n\n* unordered item'
    html = md2htmlstr(md)
    assert '<ol>' in html
    assert '<ul>' in html


def test_md2htmllist_table():
    md_lines = [
        '| a | b |',
        '| - | - |',
        '| 1 | 2 |',
    ]
    html = md2htmllist(md_lines)
    assert '<table>' in html
    assert '<td>1</td>' in html


def test_smart_dashes_in_prose():
    html = md2htmlstr('a --- b and c -- d')
    assert '&mdash;' in html
    assert '&ndash;' in html
    assert '---' not in html


def test_smart_dashes_leave_code_alone():
    html = md2htmlstr('run `a --- b`\n\n```\nx --- y\n```')
    assert '&mdash;' not in html
    assert html.count('---') == 2


def test_smarty_does_not_educate_quotes_or_ellipses():
    html = md2htmlstr('it\'s "quoted" ... done')
    assert '&rsquo;' not in html
    assert '&ldquo;' not in html
    assert '&hellip;' not in html
    assert '"quoted"' in html
    assert '...' in html
