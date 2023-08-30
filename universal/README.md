# Grading harness for Python exercises

`harness.py` is essentially a shim to go between Python's `unittest` and the
grading tests written by the task author. It transparently takes care of some
of the more common errors that would occur during grading, but it also requires
the grading tests to be written slightly differently.

## General approach

See [this grading test suite](../02_basics/variable_assignment/grading/tests.py) for a
simple but complete example and see the following sections for more details.

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

 * A local module `universal.harness`. This is for when the test suite is executed on ACCESS, as it will copy the global `universal` folder into the docker container before grading.
 * A relatively referenced module `../../universal/`. This is for when you execute a test suite locally on your machine. Of course, it requires that you use a directory structure where courses contain assignments and assignments contain tasks, rather than additional levels.

### Imports

Next, we typically want to import the student's submission. But rather than
importing the student's submission directly...

```
import task.script as implementation
```

we use the `grading_import` function:

```
implementation = grading_import("task", "script")
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

    @marks(1)
    def test_x_is_42(self):
        self.assertEqual(implementation.x, 42, "x is not 42")
```

The solution hint provided to the student should be passed as a message to the
unittest assertion (use the `msg=` keyword argument where appropriate).

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

### Marks and points

Each unit test should be annotated with a `@marks(x)` annotation, where `x` is
essentially the weight that will be given to this unittest. Typically, one
might use `@marks(1)` for every test, but if one test should count for more
towards the total number of points, one might use a higher value.

When all tests have been executed (via TestRunner), the harness will calculate
the correct number of points to award based on the `max_points` defined in
`config.toml` (i.e. `(marks_awarded / marks_achievable) * max_points)`)

### Order of failure hints

Since the order of failure hints is important (see
[course README.md](../README.md)), the harness implicitely controls how hints
will be sorted based on test method and test case order. Within an
`AccessTestCase`, the order of test method definitions determines hint priority
(earlier tests have higher priority). Within an `AccessTestSuite`, earlier test
cases have higher priority.

Finally, any hint caused by a test error rather than a test failure will receive
lower overall priority.

## Avoiding test errors

As much as possible, we want to write grading tests that result in a test
**failure** rather than an error. This is because failure hints are provided
as assertion messages, and if the assertion itself fails due to an exception,
then the assertion message is lost. Consider the following assertion:

```
self.assertAlmostEqual(42, implementation.x, delta=0.01, "x should be roughly 42")
```

Now if the student's implementation's `x` is not a number, then the assertion
itself will fail with a TypeError,
[trying to subtract](https://github.com/python/cpython/blob/d0160c7c22c8dff0a61c49b5304244df6e36465e/Lib/unittest/case.py#L916C1-L916C35)
`x` from 42.

For this reason, it's important to try as much as possible to write
comprehensive tests (e.g., in this case, checking if `x` is even a number).
Another approach is to just not use the specialized assertion methods and just
use `assertTrue` and `assertFalse`, although this loses some fidelity.

With that said, the test harness is designed such that failure hints from
test errors will all have a lower priority than failure hints from test
failures. This ensures that the student is more likely to receive a useful hint.

## Input function

The harness will replace builtins.input with an implementation that always
fails. If a student uses `input()`, they will receive a hint that this is
forbidden.

