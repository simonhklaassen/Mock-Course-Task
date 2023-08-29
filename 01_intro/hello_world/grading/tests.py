#!/usr/bin/env python3

# Scaffolding necessary to set up ACCESS test
import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

# Grading test suite starts here
from io import StringIO

class GradingTests(AccessTestCase):

    @marks(1)
    def test_prints_something(self):
        capture = StringIO()
        sys.stdout = capture
        implementation = grading_import("task", "script")
        sys.stdout = sys.__stdout__
        self.assertEqual(
            capture.getvalue(), "Hello, World!\n",
            "The output is not 'Hello, World!'")

TestRunner(verbosity=2, resultclass=AccessResult).run(AccessTestSuite(1, [GradingTests]))
