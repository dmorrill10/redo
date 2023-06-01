import argparse
import datetime
from typing import Iterable, List, NamedTuple, Optional
import re


TASK_REGEX = re.compile(r"(^|\r|\n|\r\n)[-*]\s")
COMPLETION_REGEX = re.compile(r"^[-*]\s*(\[?x\]?)\s")
RE_TAG_REGEX = re.compile(r"\+re:(\S+)")
DUE_TAG_REGEX = re.compile(r"\+due:(\S+)")

MONTH_DAY_YEAR_DATE_FMT = "%b%d_%Y"


def update_file(redo_file: str, days_ago_when_tasks_were_completed: int = 1) -> None:
    with open(redo_file) as f:
        text = f.read()

    completed_on = datetime.datetime.today() - datetime.timedelta(
        days=days_ago_when_tasks_were_completed
    )
    # TODO: update overdue, due, upcoming sections
    for text_block in each_text_block(text):
        if text_block.is_task:
            task = Task(text_block.text).recurrence(completed_on)
            if not task.is_empty():
                print("\n".join(task.lines))
        else:
            print(text_block.text)


def run_cli():
    parser = argparse.ArgumentParser(description="Say hi.")
    parser.add_argument("--redo-file", type=str, help="ReDO file to update.")
    parser.add_argument(
        "--days_ago_when_tasks_were_completed",
        type=int,
        default=1,
        help="The number of days ago when tasks were completed.",
    )

    args = parser.parse_args()
    update_file(
        redo_file=args.redo_file,
        days_ago_when_tasks_were_completed=args.days_ago_when_tasks_were_completed,
    )


class Task:
    lines: List[str]
    has_been_completed: bool = False
    recurs_every: Optional[datetime.timedelta] = None
    due_on: Optional[datetime.datetime] = None

    def __init__(self, text: str) -> None:
        lines = text.splitlines()
        self.lines = lines
        if len(lines) == 0:
            return

        match = COMPLETION_REGEX.search(lines[0])
        has_been_completed = bool(match and match.group(1))
        self.has_been_completed = has_been_completed

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

    def is_empty(self) -> bool:
        return len(self.lines) == 0

    def copy(self) -> "Task":
        return Task("- " + "\n".join(self.lines))

    def recurrence(self, current_date: Optional[datetime.datetime] = None) -> "Task":
        if self.has_been_completed:
            if self.due_on is None or self.recurs_every is None:
                return Task("")
            completion_date = self.due_on if current_date is None else current_date
            next_due = completion_date + self.recurs_every
            next_due_date_str = DUE_TAG_REGEX.sub(
                f"+due:{next_due.strftime(MONTH_DAY_YEAR_DATE_FMT).lower()}",
                "\n".join(self.lines),
            )
            return Task(f"- {next_due_date_str}")
        else:
            return self.copy()


def each_task(text: str) -> Iterable[Task]:
    for task in TASK_REGEX.split(text):
        task = task.strip()
        if len(task) > 0:
            yield Task(task)


def parse_date(month_day_year_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(month_day_year_string, MONTH_DAY_YEAR_DATE_FMT)


def parse_duration(duration_string: str) -> datetime.timedelta:
    amount_str, units = duration_string.strip().split("_")
    if not units.endswith("s"):
        units += "s"
    return datetime.timedelta(**{units.lower(): float(amount_str)})


class TextBlock(NamedTuple):
    text: str
    is_task: bool


def each_text_block(text: str) -> Iterable[TextBlock]:
    s = ""
    is_task = False
    for line in text.splitlines(keepends=True):
        if TASK_REGEX.match(line):
            if len(s) > 0:
                yield TextBlock(s, is_task)
            s = line
            is_task = True
        elif is_task and len(line.strip()) == 0:
            if len(s) > 0:
                yield TextBlock(s, is_task)
            s = line
            is_task = False
        else:
            s += line
    if len(s) > 0:
        yield TextBlock(s, is_task)
