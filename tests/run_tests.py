"""
File, that runs all tests
It goes through all project directories and search for files named tests.py
Then it runs all unit tests stored in all tests.py files
"""

import unittest

if __name__ == "__main__":
    # Searching for all tests in tests.py files
    tests = unittest.TestLoader().discover(".", pattern="tests.py")

    # Run all found tests
    # verbosity indicates how much details of tests output would be showed
    # 2 - the most amount of details
    unittest.TextTestRunner(verbosity=2).run(tests)
