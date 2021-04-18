import os
import unittest
from typing import NamedTuple, Sequence, Tuple

from src.api import Memory
from src.data import JSONModel, Control
from src.optimisation import model_solve


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.memory = Memory.get_instance()

    @staticmethod
    def test_import_from_file():
        for file in os.listdir("doc/templates/"):
            if not file.endswith(".json"):
                continue

            with open("doc/templates/" + file, "r") as handle:
                JSONModel.create(handle)


class SimulationResult(NamedTuple):
    """A special tuple to list expected results for given parameters."""
    portfolio: Sequence[Tuple[str, int]]
    direct_cost: int
    indirect_cost: int
    max_flow: float


class TemplateTestCase(unittest.TestCase):
    """Tests an included template."""

    # Number of the model in the docs/templates folder.
    model_number: int = None

    # Expected parameters.
    targets: int = None
    edges: int = None
    vertices: int = None
    control_categories: int = None
    control_subcategories: int = None

    # Expected flowing results.
    flowing_tests: Sequence[SimulationResult] = []

    # Tests for which the portfolio is optimal.
    optimal_tests: Sequence[SimulationResult] = []

    @classmethod
    def setUpClass(cls):
        if cls.model_number is None:
            assert False, "Model number has not been set."

    def setUp(self):
        memory = Memory.get_instance()
        self.model = memory.documents[memory.templates[self.model_number]]

    def test_parameters(self):
        self.assertEqual(len(self.model.targets), self.targets)
        self.assertEqual(len(self.model.edges), self.edges)
        self.assertEqual(len(self.model.vertices), self.vertices)
        self.assertEqual(
            len(self.model.control_categories), self.control_categories
        )

        number_of_subcategories = sum(
            len(category)
            for category in self.model.control_subcategories.values()
        )
        self.assertEqual(number_of_subcategories, self.control_subcategories)

    def test_flowing(self):
        """
        Check that for the given portfolios direct costs, indirect costs,
        and resulting max flow matches.
        """

        for i, simulation in enumerate(self.flowing_tests):
            with self.subTest(i):
                portfolio = [
                    self.model.control_subcategories[category][level - 1]
                    for category, level in simulation.portfolio
                ]
                self.model.reflow(portfolio)

                self.assertEqual(self.model.direct_cost, simulation.direct_cost)
                self.assertEqual(
                    self.model.indirect_cost, simulation.indirect_cost
                )
                self.assertAlmostEqual(
                    self.model.max_flow, simulation.max_flow, 5
                )

    def test_optimal(self):
        """Optimise for given costs and check if the same portfolio is given."""

        for i, simulation in enumerate(self.optimal_tests):
            with self.subTest(i):
                solution = model_solve(
                    self.model, simulation.direct_cost, simulation.indirect_cost
                )
                portfolio = [
                    Control(*control) for control in simulation.portfolio
                ]
                self.assertSequenceEqual(solution[2], portfolio)


class FixtureTestCase(TemplateTestCase):
    """
    Test case which is the same as TemplateTestCase, except the model is loaded
    from "doc/fixtures", the directory which contains special models only for testing.
    """
    fixture_name: str = None

    @classmethod
    def setUpClass(cls):
        if cls.fixture_name is None:
            assert False, "Fixture name has not been set."

    def setUp(self):
        with open(f"doc/fixtures/{self.fixture_name}.json", "r") as file:
            self.model = JSONModel.create(file)()


class CustomAdjustmentTestCase(FixtureTestCase):
    """
    A simple fixture for testing custom control adjustment for and edge,
    that is the ability to override the default flow reductions.
    It consists of two vertices and two edges joining them, one with
    default flows and one with overridden.
    """
    fixture_name = "custom_adjustment"

    targets = 1
    edges = 2
    vertices = 2
    control_categories = 1
    control_subcategories = 3

    flowing_tests = [
        SimulationResult([], 0, 0, 1),
        SimulationResult([("C", 1)], 1, 1, 1),
        SimulationResult([("C", 2)], 1, 1, 0.9),
        SimulationResult([("C", 3)], 1, 1, 0.6)
    ]

    optimal_tests = [
        flowing_tests[0],
        flowing_tests[-1]
    ]


class DefaultModelTestCase(TemplateTestCase):
    """Tests on the default model."""

    model_number = 0
    targets = 1
    edges = 15
    vertices = 7
    control_categories = 10
    control_subcategories = 20


class NISTModelTestCase(TemplateTestCase):
    """
    Verify that simulation of Singhal and Ou (2017) returns the same results
     as in Khouzani, etc. (2018).
    """

    model_number = 1
    targets = 1
    edges = 10
    vertices = 7
    control_categories = 6
    control_subcategories = 7

    flowing_tests = [
        SimulationResult([("ScW", 1), ("ScS", 1)], 2, 2, 4.32e-8),
        SimulationResult([("ScW", 1), ("ScS", 1), ("N2", 1)], 3, 3, 4.32e-10),
        SimulationResult([("ScW", 1), ("ScS", 1), ("ScDb", 1)], 3, 7, 4.32e-15),
    ]

    optimal_tests = flowing_tests


# Don't run the template test cases
del TemplateTestCase
del FixtureTestCase

if __name__ == "__main__":
    unittest.main()
