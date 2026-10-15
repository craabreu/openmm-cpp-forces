OpenMM CPP Forces Plugin
========================

[![Linux](https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Linux.yml/badge.svg)](https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Linux.yml)
[![MacOS](https://github.com/craabreu/openmm-cpp-forces/actions/workflows/MacOS.yml/badge.svg)](https://github.com/craabreu/openmm-cpp-forces/actions/workflows/MacOS.yml)
[![Docs](https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Docs.yml/badge.svg)](https://github.com/craabreu/openmm-cpp-forces/actions/workflows/Docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

This [OpenMM] plugin contains platform-agnostic forces. They are computed in C++ on the
host through OpenMM's `CustomCPPForceImpl`, and OpenMM's own platforms (Reference, CPU, CUDA,
and OpenCL) move positions and forces to and from the device. The plugin therefore has no GPU
kernels, and the same build works on every platform.

| Force                | Description                                                             |
|----------------------|-------------------------------------------------------------------------|
| [CompositeRMSDForce] | Deviation of multiple corotating bodies from their reference structures |

### Composite RMSD

The **CompositeRMSDForce** class computes the root-mean-square deviation (RMSD) of a set of
particle groups from a reference structure, where each group can translate independently but all
groups rotate together. For $`m`$ groups $`\mathbf{g}_j`$ with $`n_j`$ particles each and centroids
$`\mathbf{c}_j`$, the composite RMSD is

```math
d_{\rm crms}(\mathbf{r}) = \sqrt{
    \frac{1}{n} \min_{\mathbf{q} \in \mathbb{R}^4,\ \|\mathbf{q}\| = 1}
    \sum_{j=1}^{m} \sum_{i \in \mathbf{g}_j} \left\|
        \mathbf{A}(\mathbf{q})\left(\mathbf{r}_i - \mathbf{c}_j\right)
        - \mathbf{r}_i^{\rm ref} + \mathbf{c}_j^{\rm ref}
    \right\|^2
}
```

where $`n = \sum_{j=1}^{m} n_j`$, $`\mathbf{r}_i^{\rm ref}`$ and $`\mathbf{c}_j^{\rm ref}`$ are reference
positions and centroids, and $`\mathbf{A}(\mathbf{q})`$ is the rotation matrix of the unit quaternion
$`\mathbf{q}`$. A single rotation aligns all groups, so their relative orientations matter but their
relative positions do not. The energy of the force equals $`d_{\rm crms}`$, which makes it a
collective variable for a [CustomCVForce].

Documentation
=============

Documentation for this plugin is available at [GitHub Pages], including its Python API.

Installation
============

The plugin requires OpenMM 8.4 or later. It is distributed on the [mdtools] conda channel:

```bash
mamba install -c conda-forge -c mdtools openmm-cpp-forces
```

and on [PyPI], for Linux x86_64 and macOS (Apple Silicon and Intel) with Python 3.10–3.14:

```bash
pip install openmm-cpp-forces
```

Each PyPI release is published once per supported OpenMM version. pip installs the newest one,
upgrading OpenMM if needed; to keep an older OpenMM, pin it in the same command, for example
`pip install "openmm==8.5.*" openmm-cpp-forces`:

| PyPI release  | OpenMM |
|---------------|--------|
| `X.Y.Z`       | 8.4    |
| `X.Y.Z.post1` | 8.5    |
| `X.Y.Z.post2` | 8.6    |

On Intel Macs, OpenMM 8.6 from PyPI only works with Python 3.10, so pip installs the OpenMM 8.5
release there for Python 3.11 and later.

The PyPI wheels work with every OpenMM platform. To run on NVIDIA GPUs, also install the OpenMM
CUDA add-on that matches your driver, `openmm-cuda-12` or `openmm-cuda-13`.

To build from source, install OpenMM, CMake, SWIG, numpy, and a C++ compiler, then run:

```bash
mkdir build && cd build
cmake .. -DOPENMM_DIR=/path/to/openmm   # defaults to $CONDA_PREFIX
make install
make PythonInstall
```

Usage
=====

The example below restrains the composite RMSD of two groups of particles with a harmonic
potential:

```py
import numpy as np
import openmm as mm
import openmmcppforces as mmcpp

# A toy system: 10 particles split into two groups
num_particles = 10
system = mm.System()
for _ in range(num_particles):
    system.addParticle(1.0)
reference = np.random.default_rng(1234).normal(size=(num_particles, 3))

rmsd = mmcpp.CompositeRMSDForce(reference)
rmsd.addGroup(list(range(5)))
rmsd.addGroup(list(range(5, 10)))

restraint = mm.CustomCVForce("0.5*k*rmsd^2")
restraint.addGlobalParameter("k", 1000.0)  # kJ/mol/nm^2
restraint.addCollectiveVariable("rmsd", rmsd)
system.addForce(restraint)
context = mm.Context(system, mm.VerletIntegrator(0.001))

# Translating each group as a whole leaves the composite RMSD at zero
shift = np.array([[1.0, 0.0, 0.0]] * 5 + [[0.0, 2.0, 0.0]] * 5)
context.setPositions(reference + shift)
print(f"{restraint.getCollectiveVariableValues(context)[0]:.4f} nm")  # 0.0000 nm

# A deformation does not
noise = np.random.default_rng(5678).normal(scale=0.1, size=(num_particles, 3))
context.setPositions(reference + noise)
print(f"{restraint.getCollectiveVariableValues(context)[0]:.4f} nm")  # 0.1326 nm
```

Copyright
=========

Copyright (c) 2024, [Redesign Science](https://www.redesignscience.com)


[CompositeRMSDForce]: https://craabreu.github.io/openmm-cpp-forces/latest/pythonapi/CompositeRMSDForce.html
[CustomCVForce]:      http://docs.openmm.org/latest/api-python/generated/openmm.openmm.CustomCVForce.html
[GitHub Pages]:       https://craabreu.github.io/openmm-cpp-forces
[mdtools]:            https://anaconda.org/mdtools/openmm-cpp-forces
[OpenMM]:             https://openmm.org
[PyPI]:               https://pypi.org/project/openmm-cpp-forces
