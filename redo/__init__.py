import datetime
from typing import Iterator, List, Optional
import re


TASK_REGEX = re.compile(r"(^|\r|\n|\r\n)[-*]\s*")
COMPLETION_REGEX = re.compile(r"^[-*]\s*(\[?x\]?)\s")
RE_TAG_REGEX = re.compile(r"\+re\:(\S+)")
DUE_TAG_REGEX = re.compile(r"\+due\:(\S+)")


def run_cli() -> None:
    pass


class Task:
    lines: List[str]
    has_been_completed: bool
    recurs_every: Optional[datetime.timedelta] = None
    due_on: Optional[datetime.datetime] = None

    def __init__(self, text: str) -> None:
        lines = text.splitlines()
        assert len(lines) > 0

        match = COMPLETION_REGEX.search(lines[0])
        has_been_completed = bool(match and match.group(1))

        # Remove extra stuff from task text
        task_marker_regex = COMPLETION_REGEX if has_been_completed else TASK_REGEX
        lines[0] = task_marker_regex.sub("", lines[0])

        # Find re and due tags
        match = RE_TAG_REGEX.search(text)
        if match and match.group(1):
            self.recurs_every = parse_duration(match.group(1))
        match = DUE_TAG_REGEX.search(text)
        if match and match.group(1):
            self.due_on = parse_date(match.group(1))

        # Save data to properties
        self.lines = lines
        self.has_been_completed = has_been_completed


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
