# ACCESS exercise example repository

This repository teaches you how to write exercises for ACCESS. It also serves
as a mock for testing ACCESS and related tools.

Additionally, it contains a common [test harness](universal/harness.py) for
writing Python exercises. See the separate [README](universal/README.md) for
how that works.

## Overview

ACCESS uses a simple content hierarchy. ACCESS can serve any number of courses
and each course is managed through a Git repository, such as this one. A course
contains assignments and an assignment contains tasks. Courses, assignments and
tasks are configured through `config.toml` files in their respective root
directories.

## Unique identification of assignments and tasks

This is crucially important to understand. Every course, assignment and task
configuration specifies a **slug**. This should be a simple string, not
containing spaces. It will be used to uniquely identify the entity in ACCESS
and in the URL when displaying content in ACCESS.

**Changing the slug of an existing assignment or task will mean that the
this assignment/task will be disabled in ACCESS and a new one created in its
palce! This means all student submissions for the old one will not be visible in
the newly created assignment/task.**

As such, **slugs should not be changed** if at all possible. In principle,
the slug could be changed back to the original one and the old data will be
visible once again, but this kind of confusion should generally be avoided.

Note that the directory names of assignments and tasks play no part in this.
This means that if you wish to re-organize assignments and tasks in the Git
repository, that's no problem. You can move and rename assignment and task
directories with no impact on ACCESS, as long as you update the parent's
references in `config.toml` and as long as you do not change any slugs.

## Configuration files

Three `config.toml` files in this repository contain in-depth commentary on
what is going on.

 * Course [config.toml](config.toml)
 * First assignment [config.toml](01_intro/config.toml)
 * First task of first assignment [config.toml](01_intro/hello_world/config.toml)

## Command execution

Tasks in ACCESS must specify at least a `run_command` and a `grade_command`,
used to run and grade the student's code in ACCESS, respectively.  An optional
`test_command` may be provided if a student may write their own tests.

When ACCESS executes a command, it will copy all visible files specified under
`[files]` into a docker container (and also the `grading` files if running
`grade_command`). ACCESS will also copy any files specified in the course's
`[global_files.grading]` table.

## Grading

Grading in ACCESS is done in three simple steps:

 1) Copy the necessary files into a docker container
 2) Execute the `grade_command` specified by the task author and wait for it to finish
 3) Retrieve the contents from the `grade_results.json` file

Thus, it is entirely up to the task author how to grade solutions. Typically,
the task author will write some script that checks the student's solution,
usually using some kind of unittesting. The only requirement is that at the end
of grading, `grade_result.json` is written to the working directory. The file
needs to conform to the following example, indicating how many points the
student should get, plus a list of hints:

```
{"points": 0.0, "hints": ["The output is not 'Hello, World!'"]}
```

At the moment, ACCESS will only show the first hint provided, but this may
become configurable in the future. For this reason, it's important that the
hints are sorted from highest-to-lowest priority. In other words, the student
will not find it very useful to receive an obscure error message caused by a
test that checks a very specific edge-case of the requirements. Rather, the
student should receive the most general hints first.

## Grading considerations

Grading in ACCESS is note quite the same as regular unit testing for the
following reasons:

 * The student's submission could be literally anything, so we cannot expect that even basic things like importing or parsing the solution will succeed. Thus, it is important to catch all such errors and provide appropriate hints, rather than just crashing.
 * It might make sense to write much more basic tests than one would in normal programming. For example, rather than just checking whether a function returns the correct number, it might make sense to even check whether it returns a number at all, and give the student a corresponding hint if it does not.

## i18n

Information on courses, assignments and tasks can be specified in multiple
languages. English is required (for now).

## Validation

To validate this course or any of its assignments and tasks using `access-cli`, run

```
access-cli -AGs "rm -R task; cp -R solution task" -d ./ -f universal/harness.py -C ./
```

Add `-v` for verbose output.

