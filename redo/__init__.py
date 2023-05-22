import datetime
from typing import Iterator, List
import re


def run_cli() -> None:
    pass


task_regex = re.compile(r"(^|\r|\n|\r\n)[-*]\s*")
completion_regex = re.compile(r"^[-*]\s*(\[?x\]?)\s")


class Task:
    lines: List[str]
    has_been_completed: bool

    def __init__(self, text: str) -> None:
        lines = text.splitlines()
        assert len(lines) > 0
        match = completion_regex.match(lines[0])
        self.has_been_completed = bool(match and match.group(1))
        lines[0] = (completion_regex if self.has_been_completed else task_regex).sub(
            "", lines[0]
        )
        self.lines = lines

    def has_been_completed(self) -> bool:
        return False


def each_task(text: str) -> Iterator[Task]:
    for task in task_regex.split(text):
        task = task.strip()
        if len(task) > 0:
            yield Task(task)


def parse_date(month_day_year_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(month_day_year_string, "%b%d_%Y")
