#!/usr/bin/env python3
import os
import subprocess
import sys
import ast
from shutil import rmtree
from shutil import copyfile

import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

PREFIX_HINT = "# Hint:"

class TestIdentificationVisitor(ast.NodeVisitor):

    def __init__(self):
        self.test_names = []
        self.in_test_class = False
        self.in_test_fun = False
        self.has_test_class = 0
        self.num_tests = 0
        self.num_asserts = 0
        self.error = None

    def visit_ClassDef(self, node):
        bases = [n.id for n in node.bases]
        if "TestCase" in bases:
            self.has_test_class = True
            self.in_test_class = True
            self.generic_visit(node)
            self.in_test_class = False

    def visit_FunctionDef(self, node):
        if self.in_test_class:
            if node.name.startswith("test"):
                if node.name in self.test_names:
                    self.error = f"Multiple definitions of '{node.name}' exist in your test suite, which shadow each other."
                self.test_names.append(node.name)

                self.num_tests += 1
                self.in_test_fun = True
                self.generic_visit(node)
                self.in_test_fun = False

    def visit_Call(self, node):
        if self.in_test_fun:
            if hasattr(node.func, "attr"):
                if node.func.attr.startswith("assert") or node.func.attr.startswith("fail"):
                    self.num_asserts += 1

class Solution:
    def __init__(self, path, hint, should_pass):
        self.path = path
        self.hint = hint
        self.should_pass = should_pass
        self.should_fail = not should_pass

    def __gt__(self, other):
        if isinstance(other, Solution):
            return self.path > other.path
        else:
            return -1

    def get_name(self):
        return os.path.basename(self.path)[:-3]

    def __str__(self):
        return f"""Solution({self.path}, pass:{"OK" if self.should_pass else "FAIL"}, hint:'{self.hint}')"""


class EvalResult:
    def __init__(self, sln, has_crashed, has_ended_successfully, error=None):
        self.sln = sln
        self.has_crashed = has_crashed
        self.has_ended_successfully = has_ended_successfully
        self.error = error

    def __gt__(self, other):
        if isinstance(other, EvalResult):
            return self.sln > other.sln
        else:
            return -1

    def __str__(self):
        return f"EvalResult({self.sln}, crash:{self.has_crashed}, success:{self.has_ended_successfully})"


class TestingTaskHarness:

    def __init__(self,
            test_sources,
            dir_correct = "grading/correct",
            dir_buggy = "grading/buggy",
                ):
        self.dir_correct = dir_correct
        self.dir_buggy = dir_buggy

        self.test_sources = test_sources[0]           # TODO: should support more than one file
        self.test_dst = "tmp/" + self.test_sources    # TODO: should be a path where all the multiple test files go

        self.cwd = os.getcwd()


        assert os.path.isdir("task")
        assert os.path.isfile(self.test_sources)
        assert os.path.isdir("grading")
        assert os.path.isdir(self.dir_correct)
        assert os.path.isdir(self.dir_buggy)

        self.generated_tests = []
        self.run()

    def create_test_class(self, name, message, success):
        def test_method(self):
            self.hint(message)
            if not success:
                self.fail(message)
        return type(name, (AccessTestCase, ), {
            "test_method": test_method
        })

    def run(self):

        print("Searching for solutions...")
        neg = self.find_solutions(self.dir_buggy, False)
        pos_unweighted = self.find_solutions(self.dir_correct, True)
        # number of sample solutions is multiplied by the number of neg solutions to ensure that 
        # a simple self.fail() does not get more than half of the points
        pos = [pos_unweighted[0] for i in range(len(neg))]

        print("Found solutions:")
        for s in pos + neg:
            print("- " + str(s))

        err = self.submission_has_tests()
        if err == None:
            res = self.execute(pos + neg)
        else:
            res = [EvalResult(None, False, False, err)] * (len(pos) + len(neg))

        os.chdir(self.cwd)
        self.gen_results(res)

    def gen_results(self, res):
        test_num = 0 # each generated class get's a unique name
        for eval_result in res:
            sln = eval_result.sln

            test_num += 1
            test_name = f"GeneratedTest_{test_num}"


            if eval_result.error is not None:
                self.generated_tests.append(self.create_test_class(
                    test_name,
                    eval_result.error,
                    False))
                continue

            test_name += f"_{sln.get_name()}"

            if eval_result.has_crashed:
                m = eval_result.error if eval_result.error else sln.hint
                self.generated_tests.append(self.create_test_class(
                    test_name,
                    f"Execution crashed: {m}",
                    False))
                continue

            if sln.should_pass == eval_result.has_ended_successfully:
                state = "Worked" if sln.should_pass else "Failed"
                self.generated_tests.append(self.create_test_class(
                    test_name,
                    f"{state} as expected: {sln.hint}",
                    True))
                continue

            if sln.should_pass:
                m = f"A correct solution did not pass your test suite: {sln.hint}"
            else:
                m = f"Your test suite did not detect an issue in a hidden implementation: {sln.hint}"
            self.generated_tests.append(self.create_test_class(
                    test_name,
                    m,
                    False))

    def execute(self, solutions):
        res = []
        for sln in solutions:
            print("-------------")
            print(f"Executing {sln}...")

            os.chdir(self.cwd)
            if os.path.exists("tmp"):
                rmtree("tmp")
            os.makedirs("tmp/task")

            print(f"Copying {self.test_sources} to {self.test_dst}...")
            copyfile(self.test_sources, self.test_dst)
            SCRIPT_DEST = "tmp/task/script.py"
            print(f"Copying {sln.path} to {SCRIPT_DEST}...")
            copyfile(sln.path, SCRIPT_DEST)

            os.chdir("tmp")
            print("now in: " + os.getcwd())

            #cmd = "/usr/bin/python --version"
            cmd = "python -m unittest task/tests.py"
            print(f"executing '{cmd}'...")
            out = subprocess.Popen(cmd,
                                   cwd=os.getcwd(),
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

            stdout, stderr = out.communicate()

            if stdout:
                stdout = stdout.decode("UTF-8")
            if stderr:
                stderr = stderr.decode("UTF-8")

            last_line = stdout.split("\n")[-2]
            has_crashed = not (last_line == "OK" or last_line.startswith(
                "FAILED")) # fail vs. error
            has_ended_successfully = not out.returncode

            # handle cases, in which the execution crashed unexpectedly
            error = self.parse_error(stdout)
            if sln.should_pass and error:
                if error == "AssertionError":
                    m = f"Your test suite contains a test that fails for a correct implementation ({sln.hint})."
                elif error == "UserWarning":
                    uw_hint = None
                    for l in stdout.split("\n"):
                        if l.startswith("UserWarning"):
                            idx1 = l.find("@@")
                            if idx1 != -1:
                                idx2 = l.find("@@", idx1 + 2)
                                if idx2 != -1:
                                    uw_hint = l[idx1 + 2 : idx2]
                    if uw_hint:
                        m = f"Your test suite failed for a correct implementation. Hint: {uw_hint}"
                    else:
                        m = f"Your test suite failed for a correct implementation: {sln.hint}"
                else:
                    m = f"Running your test suite on a correct implementation failed due to a '{error}'."
                res.append(EvalResult(sln, True, False, m))
            else:
                res.append(EvalResult(sln, has_crashed, has_ended_successfully))

        os.chdir(self.cwd)
        if os.path.exists("tmp"):
            rmtree("tmp")
        return sorted(res)


    def parse_error(self, stdout):
        if "Traceback" in stdout:
            lines = stdout.split("\n")
            lines = [l for l in lines if l] # filter empty lines

            # At this point lines might look like this if printed line by line:
            """
.F
======================================================================
FAIL: test_move_up (task.tests.MoveTestSuite.test_move_up)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/shapeshifter/stuff/info1/course-info1-hs23-staging/06_testing/white_box_testing_game/tmp/task/tests.py", line 57, in test_move_up
    self.assertEqual(actual, expected)
AssertionError: Tuples differ: (('#####   ', '### o  #', '#     ##', '   #####'), ('down', 'left', 'right')) != (('#####   ', '### o  #', '#     ##', '   #####'), ('left', 'right'))
First differing element 1:
('down', 'left', 'right')
('left', 'right')
- (('#####   ', '### o  #', '#     ##', '   #####'), ('down', 'left', 'right'))
?                                                     --------
+ (('#####   ', '### o  #', '#     ##', '   #####'), ('left', 'right'))
----------------------------------------------------------------------
Ran 2 tests in 0.001s
FAILED (failures=1)
"""

            idx_trace = 0
            for l in lines: # find segment that contains crash
                if l.startswith("Traceback"):
                    break
                idx_trace += 1
            if idx_trace < len(lines):
                lines = lines[idx_trace:]
                idx_splitter = 0
                for l in lines: # find end of segment
                    if l.startswith("-----") or l.startswith("====="):
                        break
                    idx_splitter += 1
                error = "UnknownError"
                for l in lines[
                    idx_splitter - 1 : 0 : -1
                ]:  # travel back up to find error line
                    if (
                        len(l) > 0
                        and l[0].isalpha()
                        and not (  # skip lines that don't start with alpha
                            l.startswith("FAIL:") or l.startswith("OK:") or l.startswith("First diff")
                        )
                    ):  # skip own error reporting
                        error = l
                        break
                return error
            return "Unknown Error"
        return None


    def find_solutions(self, base, should_pass):
        solutions = []
        for root, dirs, files in os.walk(base):
            for f in files:
                if f.endswith(".py") and not f == "__init__.py":
                    with open(root + "/" + f, "r") as f2:
                        hint = f2.readlines()[1]
                        if len(hint) < len(PREFIX_HINT) or not hint.startswith(PREFIX_HINT):
                            raise Exception(f"Error in solution file '{f}': (In-) Correct Solutions must start with a solution hint!")
                        hint = hint[len(PREFIX_HINT):].strip()
                        s = Solution(root + "/" + f, hint, should_pass)
                        solutions.append(s)
        return solutions


    def submission_has_tests(self):
        try:
            with open(self.test_sources) as f:
                tree = ast.parse(f.read())
                #print(ast.dump(tree))

                v = TestIdentificationVisitor()
                v.visit(tree)

                if v.error:
                    return v.error
                elif not v.has_test_class:
                    return "Could not find a test suite that inherits from TestCase."
                elif v.num_tests == 0:
                    return "The test suite did not define any tests."
                elif v.num_asserts == 0:
                    return "No assertions like self.assertEqual or self.fail found in any of the tests."
            return None
        except Exception as e:
            return f"The test suite cannot be parsed due to a '{type(e).__name__}'."


