#!/usr/bin/env python3

# Scaffolding necessary to set up ACCESS test
import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

# Grading test suite starts here
implementation = grading_import("task", "script")

def calculate(a, b, c, d):
    implementation.a = a
    implementation.b = b
    implementation.c = c
    implementation.d = d
    return implementation.calculate()


class GradingTests(AccessTestCase):

    def _test(self, a, b, c, d, expected):
        actual = calculate(a, b, c, d)
        hint = "Calculation not correct for a={}, b={}, c={}, d={}... expected result is {}!".format(a, b, c, d, expected)
        self.assertAlmostEqual(expected, actual, 5, hint)

    @marks(0.25)
    def test_case1(self):
        self._test(1, 2, 3, 4, 1.444444)

    @marks(0.25)
    def test_case2(self):
        self._test(2, 3, 4, 5, 2.428571)

    @marks(0.25)
    def test_case3(self):
        self._test(3, 4, 5, 6, 3.432432)

    @marks(0.25)
    def test_case4(self):
        self._test(4, 5, 6, 7, 4.438596)

TestRunner().run(AccessTestSuite(1, [GradingTests]))
