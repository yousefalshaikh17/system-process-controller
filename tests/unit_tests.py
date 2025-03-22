import unittest

from test_process_controller import TestProcessController

def make_suite():
    """
    make a unittest TestSuite object
        Returns
            (unittest.TestSuite)
    """
    suite = unittest.TestSuite()


    suite.addTest(TestProcessController('test_find_process_1'))
    suite.addTest(TestProcessController('test_find_process_2'))
    suite.addTest(TestProcessController('test_get_runtime'))
    suite.addTest(TestProcessController('test_get_cpu_usage'))
    suite.addTest(TestProcessController('test_get_memory_usage_mb'))
    suite.addTest(TestProcessController('test_is_running'))
    suite.addTest(TestProcessController('test_terminate'))
    suite.addTest(TestProcessController('test_restart'))

    return suite

def run_all_tests():
    """
    run all tests in the TestSuite
    """
    runner = unittest.TextTestRunner()
    runner.run(make_suite())

if __name__ == '__main__':
    run_all_tests()