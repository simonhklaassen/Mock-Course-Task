import unittest
import json

import script

def calculate(a, b, c, d):
    script.a = a
    script.b = b
    script.c = c
    script.d = d
    return script.calculate()


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

    def _test(self, a, b, c, d, expected):
        actual = calculate(a, b, c, d)
        self.hint = "Calculation not correct for a={}, b={}, c={}, d={}... expected result is {}!".format(a, b, c, d, expected)
        self.assertAlmostEqual(expected, actual, 5)
        self.grade_results['points'] += 1
        self.hint = None

    def test_case1(self):
        self._test(1, 2, 3, 4, 1.444444)

    def test_case2(self):
        self._test(2, 3, 4, 5, 2.428571)

    def test_case3(self):
        self._test(3, 4, 5, 6, 3.432432)

    def test_case4(self):
        self._test(4, 5, 6, 7, 4.438596)

if __name__ == '__main__':
    unittest.main(verbosity=2)
