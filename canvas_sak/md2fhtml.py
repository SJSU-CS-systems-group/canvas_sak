import re

import markdownify
import markdown


def html2mdstr(html_str: str):
    """Converts html in string form to markdown"""
    md_str = markdownify.markdownify(html_str)
    return md_str


def html2mdlist(html_list: list):
    """Converts html as a list of strings to markdown"""
    html_str = '\n'.join(html_list)
    return html2mdstr(html_str)


def md2htmlstr(md_str: str):
    """Converts markdown in string form to html"""
    html_str = markdown.markdown(
        md_str,
        extensions=['fenced_code', 'tables', 'sane_lists', 'nl2br', 'smarty'],
        # only dashes: -- becomes an en dash and --- an em dash. quotes and
        # ellipses stay ascii so commands and values quoted in prose survive
        extension_configs={'smarty': {
            'smart_quotes': False,
            'smart_angled_quotes': False,
            'smart_ellipses': False,
        }},
    )
    return html_str


def md2htmllist(md_list: list):
    """Converts markdown as a list of strings to html"""
    md_str = '\n'.join(md_list)
    return md2htmlstr(md_str)


_P_WRAP_RE = re.compile(r'\A<p>(.*)</p>\Z', re.S)


def md2inlinehtmlstr(md_str: str):
    """Converts a single line of markdown to html without the enclosing <p>
    tag, for values substituted into an inline context (template variables)."""
    html_str = md2htmlstr(md_str)
    m = _P_WRAP_RE.match(html_str)
    return m.group(1) if m else html_str
