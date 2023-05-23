import datetime
from typing import Iterator, List
import re


TASK_REGEX = re.compile(r"(^|\r|\n|\r\n)[-*]\s*")
COMPLETION_REGEX = re.compile(r"^[-*]\s*(\[?x\]?)\s")


def run_cli() -> None:
    pass


class Task:
    lines: List[str]
    has_been_completed: bool

    def __init__(self, text: str) -> None:
        lines = text.splitlines()
        assert len(lines) > 0
        match = COMPLETION_REGEX.match(lines[0])
        self.has_been_completed = bool(match and match.group(1))
        lines[0] = (COMPLETION_REGEX if self.has_been_completed else TASK_REGEX).sub(
            "", lines[0]
        )
        self.lines = lines

    def has_been_completed(self) -> bool:
        return False


def each_task(text: str) -> Iterator[Task]:
    for task in TASK_REGEX.split(text):
        task = task.strip()
        if len(task) > 0:
            yield Task(task)


def parse_date(month_day_year_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(month_day_year_string, "%b%d_%Y")


def parse_duration(duration_string: str) -> datetime.timedelta:
    amount_str, units = duration_string.strip().split("_")
    if not units.endswith("s"):
        units += "s"
    return datetime.timedelta(**{units.lower(): float(amount_str)})
