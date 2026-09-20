import unittest
import random
from optimizer import *


class OptimizerTests(unittest.TestCase):
    def assert_valid(self, result, packages):
        self.assertEqual(
            sorted(p.id for v in result for p in v.route),
            sorted(p.id for p in packages),
        )
        for v in result:
            self.assertAlmostEqual(v.total_weight, sum(p.weight for p in v.route))
            self.assertLessEqual(v.total_weight, v.capacity)
            self.assertEqual(
                [p.priority for p in v.route], sorted(p.priority for p in v.route)
            )

    def test_capacity_and_no_dropped_or_duplicate_packages(self):
        packages = [Package(i, i * 2, i % 3, 1 + i % 4, 1 + i % 5) for i in range(10)]
        for seed in range(10):
            random.seed(seed)
            for result in [
                simulated_annealing(
                    packages,
                    [Vehicle(i, 12) for i in range(3)],
                    T_init=10,
                    T_min=1,
                    cooling=0.5,
                    iterations=10,
                ),
                genetic_algorithm(
                    packages,
                    [Vehicle(i, 12) for i in range(3)],
                    population_size=10,
                    generations=10,
                ),
            ]:
                self.assert_valid(result, packages)

    def test_single_vehicle(self):
        packages = [Package(1, 1, 0, 2, 1), Package(2, 2, 0, 3, 2)]
        self.assert_valid(
            simulated_annealing(
                packages, [Vehicle(0, 5)], T_init=2, T_min=1, cooling=0.5
            ),
            packages,
        )
        self.assert_valid(
            genetic_algorithm(
                packages, [Vehicle(0, 5)], population_size=2, generations=2
            ),
            packages,
        )

    def test_rejects_incomplete_assignment(self):
        with self.assertRaises(ValueError):
            initial_solution([Package(1, 0, 0, 6, 1)], [Vehicle(1, 5)])
        with self.assertRaises(ValueError):
            initial_solution(
                [Package(i, 0, 0, 4, 1) for i in range(3)],
                [Vehicle(1, 5), Vehicle(2, 5)],
            )

    def test_known_distance_and_input_unchanged(self):
        p = Package(1, 3, 4, 1, 1)
        v = Vehicle(0, 10)
        v.add_package(p)
        self.assertEqual(total_distance(v), 10)
        original = [Vehicle(0, 10)]
        simulated_annealing([p], original, T_init=2, T_min=1, cooling=0.5)
        self.assertEqual(original[0].route, [])


if __name__ == "__main__":
    unittest.main()
