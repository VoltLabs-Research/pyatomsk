from pathlib import Path

from setuptools import find_packages, setup

_README = Path(__file__).resolve().parent / "README.md"
_LONG_DESCRIPTION = _README.read_text(encoding="utf-8") if _README.is_file() else ""


setup(
    name="pyatomsk",
    version="0.3.0",
    description="Pythonic builders for Atomsk structures/dislocations, with local VOLT plugin compute and viewing.",
    long_description=_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "voltsdk>=3.0.0,<4",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
