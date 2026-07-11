"""Tests for the settings-navigation command."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from canvas_sak.commands.settings_navigation import (
    list_navigation,
    update_navigation,
)


class FakeTab:
    def __init__(self, id, label, hidden=False, position=0):
        self.id = id
        self.label = label
        self.position = position
        if hidden:
            self.hidden = True
        self.updates = []

    def update(self, **kwargs):
        self.updates.append(kwargs)
        if "hidden" in kwargs:
            self.hidden = kwargs["hidden"]
        return self


def make_course(tabs):
    course = MagicMock()
    course.name = "My Course"
    course.get_tabs.return_value = tabs
    return course


def run(command, args, tabs, input=None):
    course = make_course(tabs)
    with patch("canvas_sak.commands.settings_navigation.get_canvas_object", MagicMock()), \
         patch("canvas_sak.commands.settings_navigation.get_course", return_value=course):
        result = CliRunner().invoke(command, args, input=input)
    return result, course


def default_tabs():
    return [
        FakeTab("home", "Home", position=1),
        FakeTab("modules", "Modules", position=2),
        FakeTab("grades", "Grades", position=3),
        FakeTab("files", "Files", hidden=True, position=4),
        FakeTab("settings", "Settings", position=5),
    ]


def test_list_shows_visible_and_hidden():
    result, _ = run(list_navigation, ["My Course"], default_tabs())
    assert result.exit_code == 0
    out = result.output
    visible_section = out.split("hidden:")[0]
    hidden_section = out.split("hidden:")[1]
    assert "Modules" in visible_section
    assert "Grades" in visible_section
    assert "Files" in hidden_section
    # Files is the only hidden item
    assert "Files" not in visible_section


def test_update_dryrun_does_not_call_update():
    tabs = default_tabs()
    result, _ = run(update_navigation, ["My Course", "Modules"], tabs)
    assert result.exit_code == 0
    assert all(t.updates == [] for t in tabs)
    assert "This was a dryrun" in result.output


def test_update_hides_unlisted_and_shows_listed():
    tabs = default_tabs()
    # Keep only Files visible: Modules and Grades should be hidden, Files shown.
    result, _ = run(update_navigation, ["My Course", "Files", "--no-dryrun"], tabs)
    assert result.exit_code == 0

    by_id = {t.id: t for t in tabs}
    assert by_id["files"].hidden is False        # was hidden, now shown
    assert by_id["modules"].hidden is True       # unlisted, now hidden
    assert by_id["grades"].hidden is True        # unlisted, now hidden


def test_update_never_hides_home_or_settings():
    tabs = default_tabs()
    # Request only Modules; Home and Settings are unlisted but unhideable.
    result, _ = run(update_navigation, ["My Course", "Modules", "--no-dryrun"], tabs)
    assert result.exit_code == 0

    by_id = {t.id: t for t in tabs}
    assert by_id["home"].updates == []
    assert by_id["settings"].updates == []
    assert getattr(by_id["home"], "hidden", False) is False


def test_update_unknown_item_errors():
    tabs = default_tabs()
    result, _ = run(update_navigation, ["My Course", "Nonexistent", "--no-dryrun"], tabs)
    assert result.exit_code == 2
    assert all(t.updates == [] for t in tabs)


def test_update_reads_items_from_stdin():
    tabs = default_tabs()
    # Items piped on stdin (one per line, indented like NAVIGATION_ITEMS.lst)
    # should be made visible, and unlisted items hidden.
    stdin = "    Modules\n    Grades\n"
    result, _ = run(update_navigation, ["My Course", "--no-dryrun"], tabs, input=stdin)
    assert result.exit_code == 0

    by_id = {t.id: t for t in tabs}
    assert getattr(by_id["modules"], "hidden", False) is False   # listed, stays visible
    assert getattr(by_id["grades"], "hidden", False) is False    # listed, stays visible
    # Files is not listed, so it stays hidden (already hidden -> no change)
    assert by_id["files"].hidden is True
    assert by_id["files"].updates == []


def test_update_combines_stdin_and_args():
    tabs = default_tabs()
    result, _ = run(update_navigation, ["My Course", "Files", "--no-dryrun"], tabs,
                    input="    Modules\n")
    assert result.exit_code == 0
    by_id = {t.id: t for t in tabs}
    assert getattr(by_id["modules"], "hidden", False) is False   # from stdin
    assert by_id["files"].hidden is False                        # from args, was hidden -> shown
    assert by_id["grades"].hidden is True                        # unlisted -> hidden


def test_update_no_items_errors_without_hiding():
    tabs = default_tabs()
    # No positional items and empty stdin: must not hide everything.
    result, _ = run(update_navigation, ["My Course", "--no-dryrun"], tabs, input="")
    assert result.exit_code == 2
    assert all(t.updates == [] for t in tabs)


def test_update_matches_by_substring():
    tabs = default_tabs()
    result, _ = run(update_navigation, ["My Course", "mod", "--no-dryrun"], tabs)
    assert result.exit_code == 0
    by_id = {t.id: t for t in tabs}
    # "mod" resolves to Modules, which stays visible; Grades gets hidden.
    assert getattr(by_id["modules"], "hidden", False) is False
    assert by_id["modules"].updates == []
    assert by_id["grades"].hidden is True
