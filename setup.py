from setuptools import find_packages, setup


setup(
    name="pyatomsk",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "voltsdk>=3.0.0",
    ],
    python_requires=">=3.10",
)
