from setuptools import setup, find_packages

setup(
    name="process-controller",
    version="0.4",
    packages=find_packages(),
    install_requires=[
        "psutil"
    ],
)