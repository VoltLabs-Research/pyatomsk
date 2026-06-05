from setuptools import find_packages, setup


setup(
    name="pyatomsk",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "voltsdk>=3.1.0",
    ],
    python_requires=">=3.10",
)
