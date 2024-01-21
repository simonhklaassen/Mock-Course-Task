#!/usr/bin/env python3

# Scaffolding necessary to set up ACCESS test
import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

# Grading test suite starts here

script = grading_import("task", "script")

class GradingTests(AccessTestCase):

    def test_png(self):
        self.hint("PNG not found")
        png_signature = b'\x89PNG\r\n\x1a\n'
        with open("ball.png", 'rb') as file:
            header = file.read(8)
        self.assertEqual(header, png_signature)

    def test_csv(self):
        self.hint("Data not found")
        with open("out/data.csv") as file:
            self.assertEqual(file.read(), "'a','b','cdef'\n1,2,3")

TestRunner().run(AccessTestSuite(1, [GradingTests]))
