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
        'flake8==7.0.0',
        'pytest==8.0.0',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'folium==0.15.1',
        'tqdm==4.66.2',
        'matplotlib==3.8.3',
        'coverage==7.4.2',
        'pandas==2.2.0',
    ],
)
