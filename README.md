# **Process Controller**

A Python tool to manage and monitor system processes using `psutil`.

## **Overview**
The **Process Controller** provides an easy way to interact with and manage system processes. It allows you to:
- Find processes by various filters (PID, name, command line, etc.)
- Monitor process details like CPU usage, memory usage, and runtime
- Gracefully terminate, force kill, or restart processes
- Schedule process termination after a delay

This tool uses the `psutil` library to interface with system processes and provides a `ProcessController` class that wraps around `psutil.Process` objects for convenient process management.

## **Features**
- Find processes using filters like PID, name, and command line arguments
- Get CPU and memory usage statistics for processes
- Gracefully terminate or force kill processes
- Restart processes while keeping the same command line arguments
- Schedule delayed termination of processes

## **Requirements**
- Python 3.6 or higher
- `psutil` library for process management

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/yousefalshaikh17/system-process-controller.git
   cd system-process-controller
   ```

2. Install dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

## **Usage**

### **ProcessController Class**

The `ProcessController` class is used to manage and monitor processes. It allows you to:
- Find processes
- Monitor runtime, CPU usage, and memory usage
- Gracefully terminate or force kill processes
- Restart processes

### **Basic Example**

```python
import psutil
from process_controller import ProcessController

# Example usage to find a process and manage it
process = psutil.Process(1234)  # Replace with an actual PID
controller = ProcessController(process)

# Get the process runtime
print("Runtime:", controller.get_runtime())

# Get CPU usage
print("CPU Usage:", controller.get_cpu_usage())

# Terminate the process
controller.terminate()
```

### **Find Processes by Filters**

You can filter processes by various criteria using the `find_processes` static method:

```python
filters = {'name': 'python.exe'}
process_controllers = ProcessController.find_processes(filters)

for process_controller in process_controllers:
    print(process_controller.pid)
```

### **Methods Available:**
- **`get_runtime()`**: Returns the time since the process was created (in seconds).
- **`get_cpu_usage(interval)`**: Returns the CPU usage of the process (in percentage).
- **`get_memory_usage_mb()`**: Returns the memory usage of the process (in MB).
- **`terminate()`**: Gracefully terminates the process.
- **`terminate_after(delay)`**: Schedules the termination of the process after a delay (in seconds).
- **`restart()`**: Restarts the process (by terminating it and starting a new instance with the same command line). (Not recommended)
- **`find_processes(filters)`**: Finds processes matching the filters (`pid`, `name`, `cmdline`, etc.).

## **Testing**

The project includes unit tests to verify the functionality of the `ProcessController` class.

### **Running Tests Locally**

1. Run the tests using `unittest`:

   ```bash
   python -m unittest discover -s tests
   ```

### **Test Methods**

The tests cover the following methods:
- **`test_find_process_1`**: Tests the ability to find a process by name and command line filter.
- **`test_find_process_2`**: Tests the ability to find a process by PID.
- **`test_get_runtime`**: Verifies the calculation of the process runtime.
- **`test_get_cpu_usage`**: Verifies the CPU usage calculation.
- **`test_get_memory_usage_mb`**: Verifies the memory usage calculation.
- **`test_is_running`**: Verifies if a process is running.
- **`test_terminate`**: Verifies the termination of a process.
- **`test_restart`**: Verifies the restarting of a process.

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
