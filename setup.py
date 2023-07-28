"""
standard setup.py for the project
"""
from setuptools import setup, find_packages

setup(
    name='rNotecards',
    version='1.1.1',
    packages=find_packages(),
    description='A study tool, like with notecards when I was a kid.',
    long_description=open('README.md').read(),
    install_requires=[line.strip() for line in open('requirements.txt')],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='==3.10.*',
)
