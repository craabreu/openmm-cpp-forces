"""Wheel of openmm-cpp-forces: the Python package, its extension, and libOpenMMCPPForces."""

import os
import sys
from pathlib import Path

from setuptools import setup
from setuptools.dist import Distribution

sys.path.insert(0, str(Path(__file__).resolve().parent))
from versions import load_versions, release_version, requirement, source_version  # noqa: E402

minor = os.environ["CPF_OPENMM_MINOR"]
entry = load_versions()[minor]
version = release_version(source_version(os.environ["CPF_SOURCE_DIR"]), entry["post"])
readme = Path(os.environ["CPF_SOURCE_DIR"]) / "README.md"


class BinaryDistribution(Distribution):
    # The extension and library are injected after the build; this makes the wheel platform-specific
    def has_ext_modules(self):
        return True


setup(
    name="openmm-cpp-forces",
    version=version,
    description="Platform-agnostic OpenMM forces",
    long_description=readme.read_text() if readme.exists() else "",
    long_description_content_type="text/markdown",
    author="Charlles Abreu",
    url="https://github.com/craabreu/openmm-cpp-forces",
    license="MIT",
    python_requires=">=3.10",
    package_dir={"": os.environ["CPF_STAGE_DIR"]},
    packages=["openmmcppforces"],
    install_requires=[requirement(minor, entry)],
    distclass=BinaryDistribution,
)
