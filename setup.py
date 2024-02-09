from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='bus_project',
    version='0.1',
    author='Jakub Dziura',
    author_email='jd439956@students.mimuw.edu.pl',
    description='Final assignment for Python Course',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jdziura/kurs-pythona",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        # TODO
    ],
)