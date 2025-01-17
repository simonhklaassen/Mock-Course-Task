# Grading harness for Python exercises

`harness.py` is essentially a shim to go between Python's `unittest` and the
grading tests written by the task author. It transparently takes care of some
of the more common errors that would occur during grading, but it also requires
the grading tests to be written slightly differently.

## General approach

See [this grading test suite](../02_basics/variable_assignment/grading/tests.py) for a
simple example and see the following sections for more details.

### Boilerplate

To write a new grading test suite, add the boilerplate needed to use the test
harness:

```
#!/usr/bin/env python3

# Boilerplate necessary to set up ACCESS test
import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

# Grading test suite starts here
```

What happens in detail is not important for writing tests, but to explain: this
code will attempt to import the harness from two different locations:

 * A local module `universal.harness`. This is for when the test suite is executed on ACCESS or via access-cli, as it will copy the global `universal` folder into the docker container before grading.
 * A relatively referenced module `../../universal/`. This is for when you execute a test suite locally on your machine using the `grade_command`. Of course, it requires that you use a directory structure where courses contain assignments and assignments contain tasks. If not, adjust the relative import as needed.

### Imports

Next, we typically want to import the student's submission or parts of it.
But rather than importing the student's submission directly...

```
import task.script as implementation
```

we use the `grading_import` function:

```
implementation = grading_import("task", "script")
```

Or to, for example, import a class from the implementation, instead of doing

```
from task.script import TheClass
```

we do:

```
TheClass = grading_import("task.script", "TheClass")
```

The `grading_import` function will ensure that if the student's submission
suffers from any kind of problem during the import, all tests will be skipped
and an appropriate solution hint generated.

### Test Cases

Make sure you inherit from `AccessTestCase` rather than `unittest.TestCase`.
Then, write tests as usual (remember Python tests should start with the 
character sequence `test`).

```
class GradingTests(AccessTestCase):

    def test_x_is_42(self):
        self.hint("x is not 42")
        self.assertEqual(implementation.x, 42)
```

**Important**: Before any action that could fail or error the test, you must
call `self.hint(...)` to provide a solution hint. Whenever a test fails or
errors, the latest hint supplied will be used to explain the failure.

### Test Runner

Do not use Python unittest's auto-discovery, but instead use `TestRunner` to
execute the grading test suite explicitely. The `AccessTestSuite` always takes
two parameters. The first is the maximum number of points that this task should
award, and the second is a list of `AccessTestCase`s:

```
TestRunner().run(AccessTestSuite(2, [GradingTests]))
```

So to run your grading test suite locally, execute

```
python -m grading.tests
```

Correspondingly, the `grade_command` in `config.toml` should always be

```
grade_command = "python -m grading.tests"
```

Note that an AccessTestSuite can contain multiple TestCases, and the order of
hints provided corresponds to the order of TestCases.

Or, instead of running the grading locally in your environment, use access-cli
as explained in the main README.

### Weights and points

By default, each unit test has the same weight. For example, if there are 3 unit
tests, and the task awards a maximum of 6 points, then each test will contribute
2 points. If you wish to change the weight of a test, add a `@weight(x)` 
annotation, where `x` is the weight that will be given to this unittest. Typical
use cases for this are

 * If a test will pass even for the template, it should not award any points,
   so `@weight(0)` can be used. This can be useful to do basic validation that
   warns the student if they messed with the template.
 * If you want to give students an additional challenge that does not need to be
   completed to achieve full points, you can also set a weight of 0.
 * If a test is more important, it could have a higher weight than 1.

When all tests have been executed (via TestRunner), the harness will calculate
the correct number of points to award based on the `max_points` defined in
`config.toml` (i.e. `(weights_awarded / weights_achievable) * max_points)`)

### Order of failure hints

Since the order of failure hints is important (see
[course README.md](../README.md)), the harness implicitely controls how hints
will be sorted based on test method and test case order. Within an
`AccessTestCase`, the order of test method definitions determines hint priority
(earlier tests have higher priority). Within an `AccessTestSuite`, earlier test
cases have higher priority.

Finally, any hint caused by a test *error* rather than a test *failure* will receive
lower overall priority.

As much as possible, we want to write grading tests that result in a test
**failure** rather than an error. If your grading test errors given a student
solution, the test should be augmented with additional checks to result in a
failure instead.

## Input function

The harness will replace builtins.input with an implementation that always
fails. If a student uses `input()`, they will receive a hint that this is
forbidden.

