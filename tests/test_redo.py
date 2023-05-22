import pytest
import redo


@pytest.mark.parametrize('task_marker', ['-', '- ', '*', '* '])
def test_create_incomplete_task(task_marker: str) -> None:
    first_line = 'first line of task'
    second_line = 'second line of task'
    incomplete_task = redo.Task(f"{task_marker}{first_line}\n{second_line}")

    assert not incomplete_task.is_completed()
    assert incomplete_task.lines() == [first_line, second_line]

@pytest.mark.parametrize('task_marker', ['-', '- ', '*', '* '])
@pytest.mark.parametrize('completion_marker', ['x ', '[x] '])
def test_create_completed_task(task_marker: str, completion_marker: str) -> None:
    first_line = 'first line of task'
    second_line = 'second line of task'
    completed_task = redo.Task(f"{task_marker}{completion_marker}{first_line}\n{second_line}")

    assert completed_task.is_completed()
    assert completed_task.lines() == [first_line, second_line]

@pytest.mark.parametrize('task_marker', ['-', '- ', '*', '* '])
def test_create_two_tasks(task_marker: str) -> None:
    first_line = 'first line of task'
    second_line = 'second line of task'
    third_line = 'first line of second task'
    tasks = redo.parse(f"{task_marker}{first_line}\n{second_line}\n{task_marker}{third_line}")

    assert len(tasks) == 2

    assert not tasks[0].is_completed()
    assert tasks[0].lines() == [first_line, second_line]
    assert tasks[1].lines() == [third_line]
