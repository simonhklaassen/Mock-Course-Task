#!/usr/bin/env python3

from unittest import TestCase
from task.combustion_car import CombustionCar
from task.electric_car import ElectricCar
from task.hybrid_car import HybridCar


class TestCars(TestCase):

    def test_comb_instantiates(self):
        c = CombustionCar(40.0, 8.0)
        self.assertTrue(isinstance(c, CombustionCar))

    # The following tests will fail until you implement the necessary features
#    def test_comb_remaining_range(self):
#        c = CombustionCar(40.0, 8.0)
#        self.assertAlmostEqual(500.0, c.get_remaining_range(), delta=0.001)
#
#    def test_comb_drive(self):
#        c = CombustionCar(40.0, 8.0)
#        c.drive(25.0)
#        self.assertAlmostEqual(38.0, c.get_gas_tank_status()[0], delta=0.001)
