import unittest
import os
import json

from main.manufacturing import _common_load_json


class TestLoadJson(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'json_tests')

        os.makedirs(self.test_dir, exist_ok=True)

        self.test_file1 = os.path.join(self.test_dir, 'test_data1.json')
        self.data1 = {"a": 10, "b": 20, "c": 30}
        with open(self.test_file1, 'w', encoding='utf-8') as f:
            json.dump(self.data1, f)

        self.test_file2 = os.path.join(self.test_dir, 'test_data2.json')
        self.data2 = {"param": 0.5, "flag": True, "list": [1, 2, 3]}
        with open(self.test_file2, 'w', encoding='utf-8') as f:
            json.dump(self.data2, f)

        self.assertTrue(os.path.exists(self.test_file1))
        self.assertTrue(os.path.exists(self.test_file2))

    def tearDown(self):
        if os.path.exists(self.test_file1):
            os.remove(self.test_file1)
        if os.path.exists(self.test_file2):
            os.remove(self.test_file2)
        if os.path.exists(self.test_dir) and not os.listdir(self.test_dir):
            os.rmdir(self.test_dir)

    def test_load_json_returns_dict(self):
        """Проверяет, что _common_load_json возвращает словарь"""
        result = _common_load_json(self.test_file1)
        self.assertIsInstance(result, dict)

    def test_load_json_content_matches(self):
        """Проверяет, что загруженные данные совпадают с исходными"""
        result = _common_load_json(self.test_file1)
        self.assertEqual(result, self.data1)

    def test_load_json_another_file(self):
        """Проверяет загрузку второго файла"""
        result = _common_load_json(self.test_file2)
        self.assertEqual(result, self.data2)
        self.assertEqual(result["param"], 0.5)
        self.assertEqual(result["list"], [1, 2, 3])

    def test_load_json_raises_file_not_found(self):
        """Проверяет, что при отсутствии файла выбрасывается исключение"""
        with self.assertRaises(FileNotFoundError):
            _common_load_json("nonexistent_file.json")

    def test_load_json_raises_json_decode_error(self):
        """Проверяет, что при битом JSON выбрасывается исключение"""
        bad_file = os.path.join(self.test_dir, 'bad.json')
        with open(bad_file, 'w', encoding='utf-8') as f:
            f.write("{не валидный json}")
        with self.assertRaises(json.JSONDecodeError):
            _common_load_json(bad_file)
        os.remove(bad_file)


if __name__ == '__main__':
    unittest.main()