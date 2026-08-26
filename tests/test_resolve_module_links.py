"""Tests for MODULE[Name] macro resolution in upload_canvas_course.py"""

from unittest.mock import MagicMock

from canvas_sak.commands.upload_canvas_course import resolve_module_links


def make_course(modules):
    course = MagicMock()
    course.id = 4242
    mods = []
    for name, mid in modules.items():
        m = MagicMock()
        m.name = name
        m.id = mid
        mods.append(m)
    course.get_modules.return_value = mods
    return course


class TestResolveModuleLinks:
    """MODULE[Name] in a page body becomes a course-relative module link so
    pages stay portable across courses."""

    def test_macro_resolves_to_module_url(self):
        course = make_course({"Course Welcome": 77})
        body = '<a href="MODULE[Course Welcome]">start here</a>'
        out = resolve_module_links(course, body, "p.md")
        assert out == '<a href="/courses/4242/modules/77">start here</a>'

    def test_multiple_macros_resolve(self):
        course = make_course({"Introduction": 1, "C Introduction": 2})
        body = 'a MODULE[Introduction] b MODULE[C Introduction] c'
        out = resolve_module_links(course, body, "p.md")
        assert out == 'a /courses/4242/modules/1 b /courses/4242/modules/2 c'

    def test_unknown_module_left_alone(self):
        course = make_course({"Introduction": 1})
        body = '<a href="MODULE[No Such Module]">x</a>'
        out = resolve_module_links(course, body, "p.md")
        assert out == body

    def test_no_macro_skips_module_fetch(self):
        course = make_course({})
        body = '<p>nothing to resolve</p>'
        out = resolve_module_links(course, body, "p.md")
        assert out == body
        assert course.get_modules.call_count == 0
