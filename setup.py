from setuptools import setup, find_packages

def read_version():
    with open("process_controller/version.txt", "r") as f:
        return f.read().strip()

setup(
    name="process-controller",
    version=read_version(),
    install_requires=[
        "psutil"
    ],
    py_modules=['process_controller']
)
