from setuptools import setup, find_packages

from process_controller import __version__

setup(
    name="process-controller",
    version=__version__,
    install_requires=[
        "psutil"
    ],
    py_modules=['process_controller']
)
