#!/usr/bin/env python3

# Scaffolding necessary to set up ACCESS test
import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

from grading.basic import TestBasics
from grading.inheritance import TestInheritance
from grading.combustion_car import TestCombustionCar
from grading.electric_car import TestElectricCar
from grading.hybrid_car import TestHybridCar
from grading.info_hiding import TestInformationHiding

import unittest

test_suite = AccessTestSuite(4.5, [
    TestBasics,
    TestCombustionCar,
    TestElectricCar,
    TestHybridCar,
    TestInheritance,
    TestInformationHiding
])

TestRunner(verbosity=2, resultclass=AccessResult).run(test_suite)

