import argparse
import datetime
from typing import Iterable, List, NamedTuple, Optional
import re
import sys


TASK_REGEX = re.compile(r"(^|\r|\n|\r\n)[-*]\s*\[\s*\]\s")
COMPLETION_REGEX = re.compile(r"^[-*]\s*(\[?[xX]\]?)\s")
RE_TAG_REGEX = re.compile(r"\+re:(\S+)")
DUE_TAG_REGEX = re.compile(r"\+due:(\S+)")

MONTH_DAY_YEAR_DATE_FMT = "%b%d_%Y"


def print_next_file(
    redo_file: str,
    days_ago_when_tasks_were_completed: int = 1,
    overwrite: bool = False,
) -> None:
    with open(redo_file) as f:
        text = f.read()

    out_file = open(redo_file, mode="w") if overwrite else sys.stdout

    today = datetime.date.today()
    completed_on = today - datetime.timedelta(days=days_ago_when_tasks_were_completed)

    overdue_header = "# Overdue"
    overdue_tasks = []

    due_header = "# Due"
    due_tasks = []

    upcoming_header = "# Upcoming"
    upcoming_tasks = []

    undated_header = "# Undated"
    undated_tasks = []

    set_of_headers = set([overdue_header, due_header, upcoming_header, undated_header])

    for text_block in each_text_block(text):
        if text_block.is_task:
            task = Task(text_block.text).recurrence(completed_on)

            if task.is_empty():
                continue
            elif task.is_overdue(today):
                overdue_tasks.append(task)
            elif task.is_due(today):
                due_tasks.append(task)
            elif task.is_upcoming(today):
                upcoming_tasks.append(task)
            else:
                undated_tasks.append(task)
            continue
        else:
            for line in text_block.text.splitlines():
                if len(line) > 0 and line not in set_of_headers:
                    print(line, file=out_file)

    print("", file=out_file)
    if len(overdue_tasks) > 0:
        print(overdue_header, file=out_file)
        for task in sorted(overdue_tasks):
            print(task, file=out_file)
        print("", file=out_file)
    if len(due_tasks) > 0:
        print(due_header, file=out_file)
        for task in sorted(due_tasks):
            print(task, file=out_file)
        print("", file=out_file)
    if len(upcoming_tasks) > 0:
        print(upcoming_header, file=out_file)
        for task in sorted(upcoming_tasks):
            print(task, file=out_file)
        print("", file=out_file)
    if len(undated_tasks) > 0:
        print(undated_header, file=out_file)
        for task in sorted(undated_tasks):
            print(task, file=out_file)

    if overwrite:
        out_file.close()


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--redo-file", type=str, help="ReDO file to update.")
    parser.add_argument(
        "--days_ago_when_tasks_were_completed",
        type=int,
        default=1,
        help="The number of days ago when tasks were completed.",
    )
    parser.add_argument(
        "--overwrite",
        default=False,
        action="store_true",
        help="Overwrite input ReDO file.",
    )

    args = parser.parse_args()
    print_next_file(
        redo_file=args.redo_file,
        days_ago_when_tasks_were_completed=args.days_ago_when_tasks_were_completed,
        overwrite=args.overwrite,
    )


class Task:
    lines: List[str]
    has_been_completed: bool = False
    recurs_every: Optional[datetime.timedelta] = None
    due_on: Optional[datetime.date] = None
    completed_on_due_date: bool = False

    def __init__(self, text: str) -> None:
        lines = text.splitlines()
        self.lines = lines
        if len(lines) == 0:
            return

        completion_regex_match = COMPLETION_REGEX.search(lines[0])
        has_been_completed = bool(
            completion_regex_match and completion_regex_match.group(1)
        )
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
        if self.due_on is not None and bool(
            completion_regex_match and completion_regex_match.group(1) == "[X]"
        ):
            self.completed_on_due_date = True

    def is_empty(self) -> bool:
        return len(self.lines) == 0

    def is_upcoming(self, today: datetime.date) -> bool:
        return self.due_on is not None and today < self.due_on

    def is_overdue(self, today: datetime.date) -> bool:
        return self.due_on is not None and today > self.due_on

    def is_due(self, today: datetime.date) -> bool:
        return self.due_on is not None and today == self.due_on

    def copy(self) -> "Task":
        return Task(str(self))

    def recurrence(
        self,
        current_date: Optional[datetime.date] = None,
        skip_old_due_dates: bool = True,
    ) -> "Task":
        if self.has_been_completed:
            if self.due_on is None or self.recurs_every is None:
                return Task("")

            completion_date = (
                self.due_on
                if current_date is None or self.completed_on_due_date
                else current_date
            )
            num_old_due_dates = 0
            if (
                skip_old_due_dates
                and current_date is not None
                and completion_date is not None
            ):
                num_old_due_dates = (
                    current_date - completion_date
                ) // self.recurs_every

            next_due = completion_date + (num_old_due_dates + 1) * self.recurs_every
            next_due_date_str = DUE_TAG_REGEX.sub(
                f"+due:{next_due.strftime(MONTH_DAY_YEAR_DATE_FMT).lower()}",
                "\n".join(self.lines),
            )
            return Task(f"- [ ] {next_due_date_str}")
        else:
            return self.copy()

    def __str__(self) -> str:
        if self.is_empty():
            return ""
        completion_str = "[x]" if self.has_been_completed else "[ ]"
        first_line = f"- {completion_str} " + self.lines[0]
        lines = [first_line] + (self.lines[1:] if len(self.lines) > 1 else [])
        return "\n".join(lines)

    def __lt__(self, other: "Task") -> bool:
        if other.due_on is None:
            if self.due_on is None:
                return self.lines < other.lines
            return True
        elif self.due_on is None or self.due_on == other.due_on:
            return self.lines < other.lines
        else:
            return self.due_on < other.due_on


def each_task(text: str) -> Iterable[Task]:
    for task in TASK_REGEX.split(text):
        task = task.strip()
        if len(task) > 0:
            yield Task(task)


def parse_date(month_day_year_string: str) -> datetime.date:
    return datetime.datetime.strptime(
        month_day_year_string, MONTH_DAY_YEAR_DATE_FMT
    ).date()


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
        if TASK_REGEX.match(line) or COMPLETION_REGEX.match(line):
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
