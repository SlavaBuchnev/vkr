import unittest

from main.algo_ea import order_crossover

class TestCrossover(unittest.TestCase):

    def test_child_is_valid_permutation(self):
        p1 = [0, 1, 2, 3, 4, 5, 6, 7]
        p2 = [7, 6, 5, 4, 3, 2, 1, 0]
        child = order_crossover(p1, p2)
        self.assertEqual(len(child), 8)
        self.assertEqual(sorted(child), list(range(8)))

    def test_child_inherits_segment(self):
        p1 = [0, 1, 2, 3, 4, 5]
        p2 = [5, 4, 3, 2, 1, 0]
        for _ in range(20):
            child = order_crossover(p1, p2)

            self.assertEqual(sorted(child), list(range(6)))

if __name__ == '__main__':
    unittest.main()