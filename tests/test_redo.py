import pytest
import redo


TASK_MARKERS = ["- ", "* "]


@pytest.mark.parametrize("task_marker", TASK_MARKERS)
def test_create_task_that_has_not_been_completed(task_marker: str) -> None:
    first_line = "first line of task"
    second_line = "second line of task"
    task_that_has_not_been_completed = redo.Task(
        f"{task_marker}{first_line}\n{second_line}"
    )

    assert not task_that_has_not_been_completed.has_been_completed
    assert task_that_has_not_been_completed.lines == [first_line, second_line]


@pytest.mark.parametrize("task_marker", TASK_MARKERS)
@pytest.mark.parametrize("completion_marker", ["x ", "[x] "])
def test_create_completed_task(task_marker: str, completion_marker: str) -> None:
    first_line = "first line of task"
    second_line = "second line of task"
    completed_task = redo.Task(
        f"{task_marker}{completion_marker}{first_line}\n{second_line}"
    )

    assert completed_task.has_been_completed
    assert completed_task.lines == [first_line, second_line]


@pytest.mark.parametrize("task_marker", TASK_MARKERS)
def test_create_two_tasks(task_marker: str) -> None:
    first_line = "first line of task"
    second_line = "second line of task"
    third_line = "first line of second task"
    tasks = list(
        redo.each_task(
            f"{task_marker}{first_line}\n{second_line}\n{task_marker}{third_line}"
        )
    )

    assert len(tasks) == 2
    assert not tasks[0].has_been_completed
    assert tasks[0].lines == [first_line, second_line]
    assert tasks[1].lines == [third_line]


@pytest.mark.parametrize("date_string", ["may22_2023", "May22_2023"])
def test_parse_date_in_may(date_string: str) -> None:
    date = redo.parse_date(date_string)
    assert date.month == 5
    assert date.day == 22
    assert date.year == 2023


@pytest.mark.parametrize("date_string", ["feb22_2023", "Feb22_2023"])
def test_parse_date_in_february(date_string: str) -> None:
    date = redo.parse_date(date_string)
    assert date.month == 2
    assert date.day == 22
    assert date.year == 2023


def test_parse_duration() -> None:
    assert redo.parse_duration("1_day").days == 1
    assert redo.parse_duration("7_days").days == 7
    assert redo.parse_duration("1_week").days == 7
    assert redo.parse_duration("2_weeks").days == 14


def test_create_task_with_re_and_due_tags() -> None:
    task = redo.Task("- task +re:1_day +due:mar22_2023")
    assert not task.has_been_completed
    assert task.recurs_every is not None
    assert task.recurs_every.days == 1
    assert task.due_on is not None
    assert task.due_on.timetuple()[:3] == (2023, 3, 22)


def test_identify_task_text() -> None:
    text = """
---
This is a block comment in a mock markdown file.
---

# Upcoming
- task 1
* task 2
    additional information

# About
This text is in the recurrent TODO (reDO) format.
"""
    parsed = list(redo.each_text_block(text))
    assert len(parsed) == 4
    assert not parsed[0].is_task
    assert (
        parsed[0].text
        == """
---
This is a block comment in a mock markdown file.
---

# Upcoming
"""
    )
    assert parsed[1].text == "- task 1\n"
    assert parsed[1].is_task
    assert parsed[2].text == "* task 2\n    additional information\n"
    assert not parsed[3].is_task
    assert (
        parsed[3].text
        == """
# About
This text is in the recurrent TODO (reDO) format.
"""
    )