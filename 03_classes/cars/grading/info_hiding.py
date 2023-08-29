#!/usr/bin/env python3

# Scaffolding necessary to set up ACCESS test
import sys
try: from universal.harness import *
except: sys.path.append("../../universal/"); from harness import *

# Grading test suite starts here

from abc import ABC
import ast, types

Car = grading_import("task.combustion_car", "Car")
CombustionCar = grading_import("task.combustion_car", "CombustionCar")
ElectricCar = grading_import("task.electric_car", "ElectricCar")
HybridCar = grading_import("task.hybrid_car", "HybridCar")

INSTANCES = [
    CombustionCar(1.0, 2.0),
    ElectricCar(3.0, 4.0),
    HybridCar(5.0, 6.0, 7.0, 8.0),
]
TYPES = {
    Car: "task/car.py",
    CombustionCar: "task/combustion_car.py",
    ElectricCar: "task/electric_car.py",
    HybridCar: "task/hybrid_car.py",
}


# utility
def get_non_method_members(ts):
    if type(ts) != list:
        ts = [ts]
    class_members = []
    for t in ts:
        for attr_name in dir(t):
            attr = getattr(t, attr_name)
            if isinstance(attr, types.MethodType) or isinstance(attr, types.FunctionType):
                continue
            class_members.append(attr_name)
    return class_members


class TestInformationHiding(AccessTestCase):

    # ensures 0 marks are awarded for an empty submission
    def _check_implementation(self):
        import inspect

        for t in TYPES:
            if t != Car:
                source = inspect.getsource(t.drive)
                # Throw fail if the source contains pass
                if "pass" in source:
                    m = "The implementation of {} is not complete.".format(
                        TYPES[t]
                    )
                    self.fail(m)

    @marks(1)
    def test_instance_variables(self):
        self._check_implementation()
        for instance in INSTANCES:
            static = get_non_method_members(type(instance))
            for attr_name in dir(instance):
                if attr_name.startswith("_"):
                    continue
                if type(getattr(instance, attr_name)) == types.MethodType:
                    continue
                if attr_name in static:
                    continue
                m = "Classes should hide implementation details. The variable '{}' in type '{}' " \
                    "does not need to be task."
                m = m.format(attr_name, type(instance).__name__)
                self.fail(m)

    @marks(1)
    def test_global_state(self):
        self._check_implementation()
        for t in TYPES:
            path = TYPES[t]
            with open(path) as f:
                tree = ast.parse(f.read())
                v = SolutionVisitor()
                v.visit(tree)

                m = "Class state should be self-contained, yet, at least " +\
                    "one variable in '{}' is defined in the global scope."
                m = m.format(t.__name__)
                self.assertFalse(v.hasAssignInGlobalScope, m)

    @marks(0.2)
    def test_static_variables(self):
        self._check_implementation()
        predef = get_non_method_members([object, AccessTestCase, ABC]) # built-int type + imported type + ABC
        for t in TYPES:
            for attr_name in get_non_method_members(t): # attributes of the _class_
                if attr_name in predef:
                    continue
                m = "Object instances should be independent, yet, the variable " \
                    "'{}' in '{}' is defined as a shared class variable."
                m = m.format(attr_name, t.__name__)
                self.fail(m)


class SolutionVisitor(ast.NodeVisitor):

    def __init__(self):
        self.hasAssignInGlobalScope = False

    def visit_If(self, node):
        try:
            if node.test.left.id == "__name__":
                return
        except:
            self.generic_visit(node)

    def visit_Assign(self, node):
        self.hasAssignInGlobalScope = True

    def visit_FunctionDef(self, node):
        return

    def visit_ClassDef(self, node):
        return
