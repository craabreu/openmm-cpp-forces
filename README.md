OpenMM-CPP-Forces Plugin
========================

[![Linux](
    https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Linux.yml/badge.svg
)](
    https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Linux.yml
)
[![MacOS](
    https://github.com/craabreu/openmm-cpp-forces/actions/workflows/MacOS.yml/badge.svg
)](
    https://github.com/craabreu/openmm-cpp-forces/actions/workflows/MacOS.yml
)
[![Docs](
    https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Docs.yml/badge.svg
)](
    https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Docs.yml
)
[![License: MIT](
    https://img.shields.io/badge/License-MIT-green.svg
)](
    https://opensource.org/licenses/MIT
)

[![Conda version](
    https://img.shields.io/conda/v/mdtools/openmm-cpp-forces.svg
)](
    https://anaconda.org/mdtools/openmm-cpp-forces
)
[![Conda platforms](
    https://img.shields.io/conda/pn/mdtools/openmm-cpp-forces.svg
)](
    https://anaconda.org/mdtools/openmm-cpp-forces
)
[![Conda downloads](
    https://img.shields.io/conda/dn/mdtools/openmm-cpp-forces.svg
)](
    https://anaconda.org/mdtools/openmm-cpp-forces
)

This [OpenMM] plugin provides Platform-agnostic Force classes.


### Available Forces

The Force classes implemented in OpenMM-CPP-Forces are listed in the table below.

| Force / CV             | Description                                                             |
|------------------------|-------------------------------------------------------------------------|
| [CompositeRMSDForce]   | Deviation of multiple corotating bodies from their reference structures |

### Documentation

Documentation for this plugin is available at [Github Pages].


### Installation and Usage

OpenMM-CPP-Forces is available as a conda package on the [mdtools] channel. To install it, run:

```bash
    conda install -c conda-forge -c mdtools openmm-cpp-forces
```

Or:

```bash
    mamba install -c mdtools openmm-cpp-forces
```

To use OpenMM-CPP-Forces in your own Python script or Jupyter notebook, simply import it as follows:

```python
    import openmmcppforces
```

### Copyright

Copyright (c) 2024, [Redesign Science](https://www.redesignscience.com)


[CompositeRMSDForce]:
    https://craabreu.github.io/openmm-cpp-forces/pythonapi/CompositeRMSDForce.html
[Github Pages]:
    https://craabreu.github.io/openmm-cpp-forces
[mdtools]:
    https://anaconda.org/mdtools/openmm-cpp-forces
[OpenMM]:
    https://openmm.org
