import unittest
import json
import sys
from io import StringIO


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

    def test_prints_something(self):
        capture = StringIO()
        sys.stdout = capture
        import script
        sys.stdout = sys.__stdout__
        m = "@@The output is not 'Hello, World!'@@"
        self.assertEqual(capture.getvalue(), "Hello, World!\n", m)

if __name__ == '__main__':
    unittest.main(verbosity=2)
