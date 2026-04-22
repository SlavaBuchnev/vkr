import unittest

from main.algo_ea import mutate_swap

class TestMutation(unittest.TestCase):

    def test_mutation_rate_1(self):
        ind = [0, 1, 2, 3, 4]
        original = ind[:]
        mutated = mutate_swap(ind, 1.0)
        self.assertEqual(sorted(mutated), sorted(original))
        diff_count = sum(1 for i in range(len(ind)) if mutated[i] != original[i])
        self.assertEqual(diff_count, 2)

    def test_mutation_rate_0(self):
        ind = [0, 1, 2, 3, 4]
        original = ind[:]
        mutated = mutate_swap(ind, 0.0)
        self.assertEqual(mutated, original)

    def test_no_side_effects_outside_function(self):
        ind = [0, 1, 2, 3]
        original = ind[:]
        _ = mutate_swap(ind, 1.0)

        self.assertNotEqual(ind, original)

if __name__ == '__main__':
    unittest.main()