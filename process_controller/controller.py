import time
import psutil
import threading

class ProcessController():
    """
    A class to manage and monitor system processes.
    """

    def __init__(self, pid: int, create_time: float):
        self.pid = pid
        self.create_time = create_time

    @staticmethod
    def from_process(process: psutil.Process):
        """
        Initializes the ProcessController with a given psutil Process object.

        Parameters:
        - process (psutil.Process): The psutil Process object to manage.
        """
        if not isinstance(process, psutil.Process):
            raise TypeError("The process must be an instance of psutil.Process")
        
        # Only PID and create time are stored for memory-efficiency.
        return ProcessController(process.pid, process.create_time())
        
    @staticmethod
    def find_processes(filters=None):
        """
        Finds and returns a list of ProcessController instances matching the provided filters.
        
        Parameters:
        - filters (dict or callable, optional): Filter criteria to match processes. This can be either:
  
        1. A dictionary of exact match filters (key-value pairs).
        2. A callable that takes a `process.info` dictionary and returns True if the process matches.

        In both cases, the following keys are available for filtering via `process.info`:
            - 'pid' (int): Process ID.
            - 'name' (str): Name of the executable (e.g., 'java.exe').
            - 'cwd' (str): Current working directory (e.g., 'D:/server').
            - 'username' (str): Username that owns the process.
            - 'create_time' (float): Time the process was created (in seconds since the epoch).
            - 'cmdline' (list[str]): Full command-line arguments used to launch the process.
        
        Returns:
        - List of Process objects matching the criteria.

        """
        if filters is None:
            filters = lambda _: True
        elif isinstance(filters, dict):
            filter_dict = filters
            def dict_filter(info):
                for key, value in filter_dict.items():
                    if key not in info or info[key] != value:
                        return False
                return True
            filters = dict_filter
        elif not callable(filters):
            raise TypeError("filters must be a dict or a callable")

        processes = []
        for process in psutil.process_iter(['pid', 'name', 'cwd', 'username', 'create_time', 'cmdline']):
            if filters(process.info):
                try:
                    processes.append(ProcessController.from_process(process))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
        return processes
    
    def get_runtime(self):
        """
        Returns the time (in seconds) since the process was created.
        """
        return time.time() - self.create_time
    
    def get_process(self):
        """
        Returns the psutil Process object or None if unavailable.
        """
        try:
            process = psutil.Process(self.pid)
            # Create time is used to verify that another process hasn't reused the PID
            if process.create_time() == self.create_time:
                return process
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            print(f"Access denied to process with PID: {self.pid}")
        return None

    def is_running(self):
        """
        Returns whether the process is running.
        """
        process = self.get_process()
        return process is not None and process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    
    def get_cpu_usage(self, interval=0.1):
        """
        Returns process CPU usage percentage (averaged over `interval`).
        """
        if not isinstance(interval, (float, int)):
            raise TypeError("The interval must be a number (float or int)")

        process = self.get_process()
        return process.cpu_percent(interval=interval) if process else None

    def get_memory_usage_mb(self):
        """
        Returns the process memory usage in MB.
        """
        process = self.get_process()
        return round(process.memory_info().rss / (1024 * 1024), 2) if process else None
    
    def close(self):
        """
        Attempts to terminate the process safely.
        """
        process = self.get_process()
        if process is not None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except psutil.NoSuchProcess:
                return True
            except psutil.TimeoutExpired:
                process.kill()
                # At this point, if the status isnt zombie, we return false. Otherwise, a zombie process is still a stopped process.
                if process.status() != psutil.STATUS_ZOMBIE:
                    return False
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.Error) as e:
                print(f"An error occurred: {e}")
                return False
            
        return True
    
    def terminate(self):
        """
        Wrapper method around close to terminate the process safely.
        """
        return self.close()
    
    def terminate_after(self, delay, daemon=False):
        """
        Schedules the process for termination after a specified delay.

        Parameters:
        - delay (float): The time (in seconds) to wait before terminating the process.
        - daemon (bool): Whether the termination should be executed in a separate thread (default: False).
        """
        if not isinstance(delay, (float, int)):
            raise TypeError("The delay must be a number (float or int)")
        
        if not isinstance(daemon, bool):
            raise TypeError("daemon value must be a boolean.")

        def delayed_termination():
            time.sleep(delay)
            self.terminate()
        
        thread = threading.Thread(target=delayed_termination, daemon=daemon)
        thread.start()

    def restart(self):
        """
        Restarts the process if it is running, terminating and then starting a new instance with the same command line and working directory. Returns the new process or None.
        """
        # If the process stopped before the restart, cancel restart attempt.
        if not self.is_running():
            return None

        process = self.get_process()
        if process:
            try:
                # Store cmdline before termination
                cmdline = process.cmdline()
                cwd = process.cwd()
                
                self.terminate()

                # Start thread
                new_process = psutil.Popen(cmdline, cwd=cwd)
                self.pid = new_process.pid
                self.create_time = new_process.create_time()
                return new_process
            except Exception as e:
                print(f"Error restarting process {self.pid}: {e}")
        
        return None
