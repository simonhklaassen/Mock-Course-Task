import builtins
import inspect
from dataclasses import dataclass, astuple
from unittest import TestCase, TestSuite, TextTestResult, TextTestRunner, defaultTestLoader
import json
import sys

failure_hint = None
class GradingException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global failure_hint
        failure_hint = args[0]

# Input should never be used in ACCESS
class YouCannotUseInputInACCESSException(Exception): pass
def crashing_input(prompt=""):
    raise GradingException("You cannot use input() on ACCESS!")
builtins.input_orig = builtins.input
builtins.input = crashing_input

# This exception basically shouldn't occur, if it does, report an issue
class MissingHintException(Exception): pass

import_errors = []
def grading_import(module, name):
    try:
        result = __import__(module, fromlist=[name])
        return getattr(result, name)
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
        max_marks = 0
        awarded_marks = 0
        # We prioritize failure hints, because they are more useful.
        failure_hints = []
        error_hints = []
        for test_name in self.test_names:
            test_name, marks, hint, isError, isSuccess = astuple(result.grade_results[test_name])
            max_marks += marks
            if isSuccess:
                awarded_marks += marks
            if isError:
                error_hints.append(hint)
            else:
                failure_hints.append(hint)
        awarded_points = (awarded_marks / max_marks) * self.max_points
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
    marks: int
    hint: str
    isError: bool = False
    success: bool = False

def marks(marks):
    """Supply the awarded marks for a given test method"""
    def decorator(func):
        test_name = func.__name__
        def wrapper(*args, **kwargs):
            instance = args[0]
            instance.marks[test_name] = marks
            return func(*args, **kwargs)
        return wrapper
    return decorator

class AccessTestCase(TestCase):
    failureException = GradingException
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
            cls.skip_reason = f"Failed to import {name} from {module}: {e}. Make sure your code runs with the provided command."
        # marks for each test method, as provided using the @marks annotation
        cls.marks = {}

    def setUp(self):
        # If we're skipping all tests, do nothing
        if self.skip_all_tests:
            self.skipTest('Skipping all tests')
        # Snapshot current overall test results so we'll be able
        # to compare with after the test runs
        self._initial_errors = len(self._outcome.result.errors)
        self._initial_failures = len(self._outcome.result.failures)

    def tearDown(self):
        test_name = self._testMethodName
        full_test_name = f"{self.__class__.__name__}>{test_name}"
        # If we're skipping all tests, give the reason and 0 marks
        if self.skip_all_tests:
            self.grade_result = GradeResult(None, self.marks[test_name], self.skip_reason)
        # If the test resulted in an error, the assertion message is lost,
        # so we give a generic hint
        if len(self._outcome.result.errors) > self._initial_errors:
            error = self._outcome.result.errors[0]
            error_type = "Error"
            # Attempt to parse the exception type
            try:
                error_type = list(reversed(error[1].splitlines()))[0].split(":")[0]
            except: pass
            error_hint = f"An error occured during grading ({error_type}). This usually means that a variable or attribute has an unexpected type. Make sure your implementation works with a wide range of possible inputs and write tests to confirm correct behavior"
            self.grade_result = GradeResult(full_test_name, self.marks[test_name], error_hint, True)
        # If the test failed properly, we should have a failure hint
        elif len(self._outcome.result.failures) > self._initial_failures:
            # Get failure hint
            global failure_hint
            # If there's no hint, the test suite is faulty and we don't want
            # to use it for grading at all and crash instead
            if failure_hint == None:
                raise MissingHintException(test_name, error)
            self.grade_result = GradeResult(full_test_name, self.marks[test_name], failure_hint)
        else:
            # Overriding as a success is always OK
            self.grade_result = GradeResult(full_test_name, self.marks[test_name], None, False, True)
        failure_hint = None

class TestRunner(TextTestRunner):
    def __init__(self):
        super().__init__(verbosity=2, resultclass=AccessResult)
