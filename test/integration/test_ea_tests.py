import unittest
import os
import glob
import numpy as np

from main.algo_ea import evolutionary_algorithm
from main.manufacturing import load_qap_instance, load_opt_values, calculate_cost, load_ea_params

_TESTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'qaplib', 'tests')

_DAT_FILES = glob.glob(os.path.join(_TESTS_DIR, '*.dat'))
if not _DAT_FILES:
    raise RuntimeError("Нет тестовых файлов в папке tests")


class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    BOLD = '\033[1m'




class TestEvolutionaryAlgorithmFull(unittest.TestCase):
    """Интеграционные тесты для эволюционного алгоритма (всегда PASS, только вывод информации)."""

    @classmethod
    def setUpClass(cls):
        """Загружает общие ресурсы и выводит параметры алгоритма."""
        cls.opt_values = load_opt_values()
        cls.params = load_ea_params()
        cls.max_allowed_gap = 0.25  # только для справки, пока проверка не выполняется
        cls.results = []

    def _run_test_for_instance(self, filepath, instance_name):
        n, F, D = load_qap_instance(filepath)
        opt = self.opt_values.get(instance_name)
        if opt is None:
            print(f"[{instance_name}] Оптимальное значение не найдено – пропускаем")
            return

        random_perm = np.random.permutation(n)
        initial_cost = calculate_cost(random_perm, F, D)

        best_perm, best_cost, history = evolutionary_algorithm(F, D, **self.params)

        gap = (best_cost - opt) / opt

        if gap <= 0.1:
            color = Colors.GREEN
        elif gap <= self.max_allowed_gap:
            color = Colors.YELLOW
        else:
            color = Colors.RED

        print(f"\n--- {instance_name} ---")
        print(f"  Оптимальное значение (OPT):       {opt}")
        print(f"  Начальная стоимость:              {initial_cost}")
        print(f"  Лучшее найденное (BEST):          {best_cost}")
        print(f"                                    {" ".join(str(x + 1) for x in best_perm)}")
        print(f"  Отклонение:                       {color}{Colors.BOLD}{gap:.2%}{Colors.RESET}")


        self.__class__.results.append((instance_name, gap, best_cost, opt))

    @classmethod
    def tearDownClass(cls):
        """Выводит сводную таблицу после всех тестов."""
        if not cls.results:
            return
        print("СВОДКА ОТКЛОНЕНИЙ")
        print(f"{'Задача':<12} {'Отклонение':<12} {'Статус':<10}")
        print("-" * 70)
        for inst, gap, best, opt in sorted(cls.results, key=lambda x: x[1], reverse=True):
            if gap <= 0.1:
                status = f"{Colors.GREEN}OK{Colors.RESET}"
            elif gap <= cls.max_allowed_gap:
                status = f"{Colors.YELLOW}WARN{Colors.RESET}"
            else:
                status = f"{Colors.RED}FAIL{Colors.RESET}"
            print(f"{inst:<12} {gap:.2%}           {status}")
        print("=" * 70)

for _path in _DAT_FILES:
    _instance = os.path.splitext(os.path.basename(_path))[0]
    _method_name = f"test_ea_approaches_optimum_{_instance}"

    def _make_test(path, name):
        return lambda self: self._run_test_for_instance(path, name)

    setattr(TestEvolutionaryAlgorithmFull, _method_name, _make_test(_path, _instance))

del _path, _instance, _make_test


if __name__ == '__main__':
    unittest.main()