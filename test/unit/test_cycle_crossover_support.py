import unittest
import itertools
from main.cycle_crossover_support import (
    mul, reverse, solve, decompose_cycles,
    find_subset_sum, build_ans_from_cycles, cycle_crossover_optimal
)

class TestMul(unittest.TestCase):
    def test_mul(self):
        a = [1, 0, 2]
        b = [2, 1, 0]
        # mul(a, b) = [b[a[0]], b[a[1]], b[a[2]]] = [b[1], b[0], b[2]] = [1, 2, 0]
        self.assertEqual(mul(a, b), [1, 2, 0])
        # тождественная
        e = [0, 1, 2, 3]
        self.assertEqual(mul(e, e), e)
        # умножение на обратную даёт тождественную
        p = [2, 0, 3, 1]
        rev = reverse(p)  # [1, 3, 0, 2]
        self.assertEqual(mul(p, rev), [0, 1, 2, 3])

class TestReverse(unittest.TestCase):
    def test_reverse(self):
        p = [2, 0, 3, 1]
        rev = reverse(p)
        self.assertEqual(rev, [1, 3, 0, 2])
        # проверка: p[rev[i]] == i
        for i in range(len(p)):
            self.assertEqual(p[rev[i]], i)
        # обратная от обратной = исходная
        self.assertEqual(reverse(rev), p)

class TestSolve(unittest.TestCase):
    def test_solve_example(self):
        p = [2, 0, 4, 3, 1]
        k = 2
        ans = solve(p, k)
        expected = [2, 1, 4, 3, 0]
        self.assertEqual(ans, expected)

    def test_solve_k0(self):
        self.assertEqual(solve([1, 0, 2], 0), [0, 1, 2])

    def test_solve_full_cycle(self):
        p3 = [1, 2, 0]
        ans3 = solve(p3, 3)
        self.assertEqual(ans3, [1, 2, 0])

    def test_solve_preserves_permutation(self):
        for n in range(1, 5):
            for perm in itertools.permutations(range(n)):
                for k in range(n + 1):
                    ans = solve(list(perm), k)
                    self.assertEqual(sorted(ans), list(range(n)))

class TestDecomposeCycles(unittest.TestCase):
    def test_decompose_cycles(self):
        p = [2, 0, 4, 3, 1]
        cycles = decompose_cycles(p)
        cycles_sets = [set(c) for c in cycles]
        self.assertIn({0, 2, 4, 1}, cycles_sets)
        self.assertIn({3}, cycles_sets)
        self.assertEqual(len(cycles), 2)

    def test_identity(self):
        e = list(range(5))
        cycles_e = decompose_cycles(e)
        self.assertEqual(len(cycles_e), 5)
        for c in cycles_e:
            self.assertEqual(len(c), 1)

class TestFindSubsetSum(unittest.TestCase):
    def test_no_subset(self):
        cycles = [[0, 2, 4, 1], [3]]  # длины 4 и 1
        self.assertIsNone(find_subset_sum(cycles, 2))

    def test_single_cycle(self):
        cycles = [[0, 2, 4, 1], [3]]
        selected = find_subset_sum(cycles, 4)
        self.assertEqual(selected, [0])

    def test_two_cycles(self):
        cycles = [[0, 2, 4, 1], [3]]
        selected = find_subset_sum(cycles, 5)
        self.assertEqual(set(selected), {0, 1})

    def test_multiple_cycles(self):
        cycles2 = [[0, 1, 2], [3, 4, 5], [6, 7], [8]]  # длины 3,3,2,1
        selected = find_subset_sum(cycles2, 7)
        # ожидаем 3+3+1 = 7 (индексы 0,1,3)
        self.assertEqual(sorted(selected), [0, 1, 3])

    def test_target_zero(self):
        cycles2 = [[0, 1, 2], [3, 4, 5]]
        selected = find_subset_sum(cycles2, 0)
        self.assertEqual(selected, [])

class TestBuildAnsFromCycles(unittest.TestCase):
    def test_first_cycle(self):
        p = [2, 0, 4, 3, 1]
        cycles = decompose_cycles(p)  # [[0,2,4,1], [3]]
        ans = build_ans_from_cycles(p, cycles, [0])
        expected = [2, 0, 4, 3, 1]
        self.assertEqual(ans, expected)

    def test_second_cycle(self):
        p = [2, 0, 4, 3, 1]
        cycles = decompose_cycles(p)
        ans = build_ans_from_cycles(p, cycles, [1])
        expected = [0, 1, 2, 3, 4]
        self.assertEqual(ans, expected)

    def test_is_permutation(self):
        p = [2, 0, 4, 3, 1]
        cycles = decompose_cycles(p)
        for sel in [[0], [1], [0, 1]]:
            ans = build_ans_from_cycles(p, cycles, sel)
            self.assertEqual(sorted(ans), list(range(len(p))))

class TestCycleCrossoverOptimal(unittest.TestCase):
    def test_odd_n(self):
        a = [0, 1, 2, 3, 4]
        b = [2, 0, 4, 3, 1]
        c = cycle_crossover_optimal(a, b)
        ra = sum(1 for i in range(5) if a[i] == c[i])
        rb = sum(1 for i in range(5) if b[i] == c[i])
        self.assertEqual(min(ra, rb), 2)
        self.assertEqual(sorted(c), [0, 1, 2, 3, 4])

    def test_even_n_perfect_split(self):
        a = [0, 1, 2, 3]
        b = [1, 0, 3, 2]   # p = [1,0,3,2] -> циклы (0,1) и (2,3)
        c = cycle_crossover_optimal(a, b)
        ra = sum(1 for i in range(4) if a[i] == c[i])
        rb = sum(1 for i in range(4) if b[i] == c[i])
        self.assertEqual(min(ra, rb), 2)
        self.assertEqual(ra, 2)
        self.assertEqual(rb, 2)

    def test_even_n_single_cycle(self):
        a = [0, 1, 2, 3]
        b = [1, 2, 3, 0]   # один цикл длины 4
        c = cycle_crossover_optimal(a, b)
        ra = sum(1 for i in range(4) if a[i] == c[i])
        rb = sum(1 for i in range(4) if b[i] == c[i])
        self.assertEqual(min(ra, rb), 1)

    def test_n2(self):
        a = [0, 1]
        b = [1, 0]
        c = cycle_crossover_optimal(a, b)
        ra = sum(1 for i in range(2) if a[i] == c[i])
        rb = sum(1 for i in range(2) if b[i] == c[i])
        self.assertEqual(min(ra, rb), 0)

    def test_always_permutation(self):
        for n in range(1, 5):
            for a_perm in itertools.permutations(range(n)):
                for b_perm in itertools.permutations(range(n)):
                    a = list(a_perm)
                    b = list(b_perm)
                    c = cycle_crossover_optimal(a, b)
                    self.assertEqual(sorted(c), list(range(n)))

if __name__ == '__main__':
    unittest.main()