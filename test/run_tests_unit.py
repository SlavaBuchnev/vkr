import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.discover('unit', pattern='test_*.py'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)