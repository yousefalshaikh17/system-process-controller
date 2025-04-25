import unittest
import psutil
import time
import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from process_controller import ProcessController

data_folder = os.path.join(os.path.dirname(__file__), 'data')


def is_process_running(pid):
        """
        Check if the process with the given PID is running.
        """
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False

def yield_until_process_running(pid: int, timeout=10):
    """
    Yield until a process runs.
    """
    max_time = time.time() + timeout
    while not is_process_running(pid):
        if max_time < time.time():
            raise TimeoutError("Testing process 'test_script.py' did not start in time.")
        time.sleep(0.1)
        

class TestProcessController(unittest.TestCase):

    def setUp(self):
        """
        Before each test, we start a real process (test_script.py).
        This ensures we have a process to test against.
        """
        self.cmdline = ['python', 'test_script.py']

        # Clean up any remaining processes. (Extra measure)
        for process in psutil.process_iter(['cwd']):
            if process.cwd == data_folder:
                process.kill()


        self.process = subprocess.Popen(
            self.cmdline,
            cwd=data_folder,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            )
        yield_until_process_running(self.process.pid)
    
        # Create a ProcessController instance for the new process
        process = psutil.Process(self.process.pid)
        self.controller = ProcessController.from_process(process)

    def tearDown(self):
        """
        Terminate the process after each test.
        """
        self.controller.terminate()
        self.process.terminate()
        while self.controller.is_running():
            time.sleep(0.1)
                

    def test_find_process_1(self):
        """
        Test to verify that the ProcessController can correctly find the running process based on filter parameters.
        """
        filter = {
            'name': 'python.exe',
            'cmdline': self.cmdline 
        }

        process_controllers = ProcessController.find_processes(filter)
        self.assertTrue(
            any([process.pid == self.process.pid for process in process_controllers]),
            msg="test_process_controller.test_find_process_1: Process was not found with the filter name='python.exe' and cmdline."
        )

    def test_find_process_2(self):
        """
        Test to verify that the ProcessController can correctly find the running process based on filter parameters.
        """
        filter = {
            'pid': self.process.pid
        }

        process_controllers = ProcessController.find_processes(filter)
        self.assertTrue(
            len(process_controllers) > 0,
            msg="test_process_controller.test_find_process_2: Process with given PID was not found."
        )


    def test_get_runtime(self):
        """
        Test get_runtime() to ensure it correctly calculates the elapsed time.
        """
        expected_runtime = time.time() - self.controller.create_time
        self.assertAlmostEqual(
            self.controller.get_runtime(), 
            expected_runtime, 
            delta=1,
            msg="test_process_controller.test_get_runtime: Runtime mismatch between expected and actual."
        )

    def test_get_cpu_usage(self):
        """
        Test get_cpu_usage() to ensure it returns the correct value.
        """
        cpu_usage = self.controller.get_cpu_usage()
        self.assertIsInstance(
            cpu_usage, 
            float, 
            msg="test_process_controller.test_get_cpu_usage: CPU usage is not of type float."
        )

    def test_get_memory_usage_mb(self):
        """
        Test get_memory_usage_mb() to ensure it returns the correct memory usage in MB.
        """
        memory_usage = self.controller.get_memory_usage_mb()
        self.assertIsInstance(
            memory_usage, 
            float, 
            msg="test_process_controller.test_get_memory_usage_mb: Memory usage is not of type float."
        )

    def test_is_running(self):
        """
        Test is_running() method to ensure it correctly determines if the process is running.
        """
        self.assertTrue(
            self.controller.is_running(), 
            msg="test_process_controller.test_is_running: Process is not running when it should be."
        )

    def test_terminate(self):
        """
        Test terminate() to ensure the process is properly terminated.
        """
        self.assertTrue(
            self.controller.terminate(),
            msg="test_process_controller.test_terminate: Process could not be terminated."
        )
        deadline = time.time() + 10
        while self.controller.is_running() and time.time() < deadline:
            time.sleep(0.1)
        self.assertFalse(
            self.controller.is_running(),
            msg="test_process_controller.test_terminate: Process still running after termination."
        )

    def test_restart(self):
        """
        Test restart() method to ensure the process is correctly restarted.
        """
        initial_pid = self.controller.pid
        initial_create_time = self.controller.create_time
        
        # Restart the process
        self.assertTrue(
            self.controller.restart(),
            msg="test_process_controller.test_restart: Process could not be restarted."
        )

        # After restart, the PID and create_time should have changed
        self.assertNotEqual(
            self.controller.pid, initial_pid,
            msg="test_process_controller.test_restart: Process PID did not change after restart."
        )
        self.assertNotEqual(
            self.controller.create_time, initial_create_time,
            msg="test_process_controller.test_restart: Process create_time did not change after restart."
        )
