import builtins
import inspect
from collections import defaultdict
from dataclasses import dataclass, astuple
from unittest import TestCase, TestSuite, TextTestResult, TextTestRunner, defaultTestLoader
import json
import sys

class GradingException(Exception): pass

# Input should never be used in ACCESS
class YouCannotUseInputInACCESSException(Exception): pass
def crashing_input(prompt=""):
    raise GradingException("You cannot use input() on ACCESS!")
builtins.input_orig = builtins.input
builtins.input = crashing_input

# This exception basically shouldn't occur, if it does, report an issue
class MissingHintException(Exception): pass
MISSING_HINT = "No solution hint (report this as an issue)"

import_errors = []
def grading_import(module, name=None):
    try:
        if name is not None:
            result = __import__(module, fromlist=[name])
            return getattr(result, name)
        else:
            return __import__(module)
    except ImportError as e:
        import_errors.append((module, name, e))
        return None
    except BaseException as e:
        import_errors.append((module, name, e))
        return None


class AccessTestSuite(TestSuite):
    def __init__(self, max_points, test_classes):
        super().__init__()
        self.test_classes = test_classes
        self.max_points = max_points
        self.test_names = []
        for test_class in self.test_classes:
            tests = defaultTestLoader.loadTestsFromTestCase(test_class)
            self.addTests(tests)
            self.test_names.extend(test_class._test_names())

    def run(self, result, debug=False):
        # run the tests in the suite
        super().run(result, debug)
        max_weight = 0
        awarded_weight = 0
        # We prioritize failure hints, because they are more useful.
        failure_hints = []
        error_hints = []
        missing = []
        for test_name in self.test_names:
            test_name, weight, hint, isError, isSuccess = astuple(result.grade_results[test_name])
            if hint == MISSING_HINT:
                missing.append(test_name)
            max_weight += weight
            if isSuccess:
                awarded_weight += weight
            if isError:
                error_hints.append(hint)
            else:
                failure_hints.append(hint)
        if len(missing) > 0:
            print(f"ERROR: grade_results not written; missing hints for: {', '.join(missing)}")
            sys.exit(1)
        awarded_points = (awarded_weight / max_weight) * self.max_points
        grading_results = {"points": awarded_points,
                           "hints": failure_hints + error_hints}
        with open('grade_results.json', 'w') as grade_results_file:
            json.dump(grading_results, grade_results_file)


        return result

class AccessResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.grade_results = {} # Map of test_name: GradeResult
        self.grade_errors = {} # Map of test_name: GradeResult

    def stopTest(self, test):
        super().stopTest(test)
        if test.grade_result != None:
            self.grade_results[test.grade_result.test_name] = test.grade_result

    def addSuccess(self, test):
        super().addSuccess(test)

    def addError(self, test, err):
        super().addError(test, err)

    def addFailure(self, test, err):
        super().addFailure(test, err)


@dataclass
class GradeResult:
    test_name: str
    weight: int
    hint: str
    isError: bool = False
    success: bool = False

def weight(weight):
    """Supply the awarded weight for a given test method"""
    def decorator(func):
        test_name = func.__name__
        def wrapper(*args, **kwargs):
            instance = args[0]
            instance.weight[test_name] = weight
            return func(*args, **kwargs)
        return wrapper
    return decorator

class AccessTestCase(TestCase):
    longMessage = False

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.grade_result = None

    @classmethod
    def _test_names(cls):
        return [f"{cls.__name__}>{name}" for name, value in cls.__dict__.items()
                if callable(value) and name.startswith("test")]

    @classmethod
    def setUpClass(cls):
        # If there are imports problems, skip all tests
        cls.skip_all_tests = False
        global import_errors
        if import_errors:
            module, name, e = import_errors[0]
            cls.skip_all_tests = True
            if name is None:
                cls.skip_reason = f"Failed to import {module}: {e}. Make sure your code runs before submitting."
            else:
                cls.skip_reason = f"Failed to import {name} from {module}: {e}. Make sure your code runs before submitting."
        # weight for each test method, as provided using the @weight annotation
        cls.weight = defaultdict(lambda: 1)
        cls._hint = {}

    def setUp(self):
        # If we're skipping all tests, do nothing
        #if self.skip_all_tests:
        #    self.skipTest('Skipping all tests')
        # Snapshot current overall test results so we'll be able
        # to compare with after the test runs
        self.addCleanup(self.postprocess)
        self._initial_errors = len(self._outcome.result.errors)
        self._initial_failures = len(self._outcome.result.failures)
        self._hint = {}

    def hint(self, msg=None, lang="en"):
        if msg == None:
            raise ValueError
        self._hint[lang] = msg

    def postprocess(self):
            test_name = self._testMethodName
            full_test_name = f"{self.__class__.__name__}>{test_name}"
            # If we're skipping all tests, give the reason and 0 weight
            if self.skip_all_tests:
                self.grade_result = GradeResult(full_test_name, self.weight[test_name], self.skip_reason)
            else:
                global import_errors
                if import_errors:
                    module, name, e = import_errors[0]
                    if name is None:
                        self.hint(f"Failed to {module}: {e}. Make sure your code runs before submitting.")
                    else:
                        self.hint(f"Failed to import {name} from {module}: {e}. Make sure your code runs before submitting.")
                if "en" not in self._hint or self._hint["en"] == None:
                    hint = MISSING_HINT
                else:
                    hint = self._hint["en"]
                # If the test resulted in an error, the assertion message is lost,
                # so we give a generic hint
                if len(self._outcome.result.errors) > self._initial_errors:
                    error = self._outcome.result.errors[0]
                    error_type = "Error"
                    # Attempt to parse the exception type
                    try:
                        error_type = list(reversed(error[1].splitlines()))[0].split(":")[0]
                    except: pass
                    error_hint = hint + f" (This was caused by an error of type {error_type})."
                    self.grade_result = GradeResult(full_test_name, self.weight[test_name], error_hint, True)
                # If the test failed properly, we should have a failure hint
                elif len(self._outcome.result.failures) > self._initial_failures:
                    self.grade_result = GradeResult(full_test_name, self.weight[test_name], hint)
                else:
                    # Overriding as a success is always OK
                    self.grade_result = GradeResult(full_test_name, self.weight[test_name], None, False, True)
            self._hint = None

    def reject_template(self, snippet, min_ast_nodes=20,
            hint="You must implement more of the solution before resubmitting"):
        self.hint(hint)
        import inspect
        import ast
        def visit(root):
            return 1 + sum(map(visit, ast.iter_child_nodes(root)))
        tree = ast.parse(inspect.getsource(snippet))
        node_count = visit(tree)
        if node_count < min_ast_nodes:
            self.fail()

class TestRunner(TextTestRunner):
    def __init__(self):
        super().__init__(verbosity=2, resultclass=AccessResult)
