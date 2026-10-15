#!/bin/bash

set -euxo pipefail

rm -rf build || true

CMAKE_FLAGS="-DOPENMM_DIR=${PREFIX} -DPYTHON_EXECUTABLE=${PYTHON}"
if [[ "$target_platform" == osx* ]]; then
    CMAKE_FLAGS+=" -DCMAKE_OSX_SYSROOT=${CONDA_BUILD_SYSROOT}"
    CMAKE_FLAGS+=" -DCMAKE_OSX_DEPLOYMENT_TARGET=${MACOSX_DEPLOYMENT_TARGET}"
fi

# Build in subdirectory and install.
mkdir -p build
cd build
cmake ${CMAKE_ARGS} ${CMAKE_FLAGS} ${SRC_DIR}
make -j$CPU_COUNT install
make -j$CPU_COUNT PythonWrapper
${PREFIX}/bin/python -m pip install --no-deps --ignore-installed python/
