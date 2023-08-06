import unittest
import inspect
import json
import task.script as implementation


class PublicTestSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.grade_results = {'points': 0, 'hints': []}
        cls.hint = None

    @classmethod
    def tearDownClass(cls):
        with open('grade_results.json', 'w') as grade_results_file:
            json.dump(cls.grade_results, grade_results_file)

    def tearDown(self):
        if self.hint:
            self.grade_results['hints'].append(self.hint)

    def test_x_is_42(self):
        self.test_x_is_exactly_42()
        source = inspect.getsource(implementation)
        self.hint = "The solution seems to contain x = 42, please assign something slighty more complex"
        self.assertTrue("x=42" not in ''.join(source.split()))
        self.grade_results['points'] += 1
        self.hint = None

    def test_x_is_exactly_42(self):
        self.hint = "x is not exactly 42"
        self.assertEqual(implementation.x, 42)
        self.grade_results['points'] += 1
        self.hint = None


if __name__ == '__main__':
    unittest.main(verbosity=2)
