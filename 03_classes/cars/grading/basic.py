#!/usr/bin/env python3

# Scaffolding necessary to set up ACCESS test
import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

# Grading test suite starts here

# instead of doing the usual:
# from task.combustion_car import CombustionCar
# use grading_import which will take care of catching and reporting import errors
CombustionCar = grading_import("task.combustion_car", "CombustionCar")
ElectricCar = grading_import("task.electric_car", "ElectricCar")
HybridCar = grading_import("task.hybrid_car", "HybridCar")

class TestBasics(AccessTestCase):

    def _run_example(self):
        # script
        c = CombustionCar(40.0, 8.0)
        c.get_remaining_range()  # 500
        c.drive(25.0)
        c.get_gas_tank_status()  # (38.0, 40.0)
        with self.assertRaises(Warning):
            c.drive(1000.0)  # fuel is depleted

        e = ElectricCar(25.0, 500.0)
        e.drive(100.0)
        e.charge(2.0)
        e.get_battery_status()  # (22.0, 25)

        h = HybridCar(40.0, 8.0, 25.0, 500.0)
        h.switch_to_combustion()
        h.drive(600.0)  # depletes fuel, auto-switch
        h.get_gas_tank_status()  # (0.0, 40.0)
        h.get_battery_status()  # (20.0, 25.0)

        # test1
        c = CombustionCar(40.0, 8.0)
        self.assertAlmostEqual(500.0, c.get_remaining_range(), delta=0.001)

        # test2
        c = CombustionCar(40.0, 8.0)
        c.drive(25.0)
        self.assertAlmostEqual(38.0, c.get_gas_tank_status()[0], delta=0.001)

    @marks(1)
    def test0_example(self):
        try:
            self._run_example()
        except AssertionError:
            m = "Running examples provided in task.py produce incorrect results. Make sure that " +\
                "the task script and test suite pass, before you attempt any submissions."
            self.fail(m)
        except:
            m = "Failed to run the provided example. Make sure that the task script and test " +\
                "suite passes, before you attempt any submissions."
            self.fail(m)

    @marks(1)
    def test1_repeatability(self):
        try:
            self._run_example()
            self._run_example()
        except:
            m = "Failed to run the provided script and test suite twice in a row. This might be caused by shared " +\
                "class variables that introduce unexpected side effects. We highly encourage you to " +\
                "add your own tests to the task test suite before you attempt any submissions."
            self.fail(m)
