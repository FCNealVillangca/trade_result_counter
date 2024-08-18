from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="trading_result_counter",
    version='0.1',
    packages=find_packages(),
    long_description=description,
    long_description_content_type="text/markdown",
    install_requires=[
        "pandas == 2.2.2"
    ]
)
