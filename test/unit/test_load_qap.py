import unittest
import os
import numpy as np

from main.manufacturing import load_qap_instance

class TestLoadQAP(unittest.TestCase):

    def setUp(self):
        self.test_file = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'qaplib', 'tests', 'chr12a.dat')
        self.assertTrue(os.path.exists(self.test_file), f"Файл {self.test_file} не найден")

    def test_load_dimension(self):
        n, F, D = load_qap_instance(self.test_file)
        self.assertEqual(n, 12)

    def test_matrix_shapes(self):
        n, F, D = load_qap_instance(self.test_file)
        self.assertEqual(F.shape, (12, 12))
        self.assertEqual(D.shape, (12, 12))

    def test_matrices_are_non_negative(self):
        n, F, D = load_qap_instance(self.test_file)

        self.assertTrue(np.all(F >= 0))
        self.assertTrue(np.all(D >= 0))

if __name__ == '__main__':
    unittest.main()