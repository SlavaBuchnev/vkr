import unittest
import numpy as np

from main.manufacturing import  calculate_cost

class TestCostFunction(unittest.TestCase):

    def test_identity_permutation(self):
        flow = np.array([[0, 1, 2],
                         [1, 0, 3],
                         [2, 3, 0]])
        dist = np.array([[0, 4, 5],
                         [4, 0, 6],
                         [5, 6, 0]])
        perm = [0, 1, 2]
        expected = (0*0 + 1*4 + 2*5 +
                    1*4 + 0*0 + 3*6 +
                    2*5 + 3*6 + 0*0)
        cost = calculate_cost(perm, flow, dist)
        self.assertEqual(cost, expected)

    def test_swapped_permutation(self):
        flow = np.array([[0, 5],
                         [5, 0]])
        dist = np.array([[0, 3],
                         [3, 0]])
        perm1 = [0, 1]
        perm2 = [1, 0]
        cost1 = calculate_cost(perm1, flow, dist)
        cost2 = calculate_cost(perm2, flow, dist)
        self.assertEqual(cost1, cost2)

if __name__ == '__main__':
    unittest.main()