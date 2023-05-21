# ReDO: Recurrent TODO

This repository defines the ReDO (recurrent TODO) Markdown file format and includes a script to automatically update ReDO files.

The ReDO format is a mix of TODO.txt and GitHub TODO formats, with additional important aspects.
- Tasks are bullet points that begin at the very start of a line (no whitespace allowed). As in typical markdown, such items can start with a `-` or `*`. All lines following the start of a task are expected to be part of that task until another task or a blank line.
- Tasks are marked as completed with `[x]` before the start of any description text, *e.g.*, "- [x] completed task".
- The tag `re` is the key aspect of this format and the one that that gives it its name. The value of `re` denotes how often this task should repeat after it is completed. A `:` is used to separate tag keys from values. Durations are specified in days, weeks, months, or years, with the amount first and then the unit. Underscores in tags are interpreted as spaces. Only one duration value and unit, *e.g.*, `2_weeks`, is currently accepted since that is the main expected use case. Instead of writing `2_weeks_1_day`, for example, write `15_days`.
- Due dates are specified in my personal favorite format, three letter month, one or two number day, underscore four number year.


# License

MIT license, copyright (c) 2023 Dustin Morrill. See [LICENSE](LICENSE) for details.
