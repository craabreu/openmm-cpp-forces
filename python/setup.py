from setuptools import setup, Extension
import os
import platform
import numpy as np

openmm_dir = '@OPENMM_DIR@'
header_dir = '@PLUGIN_HEADER_DIR@'
library_dir = '@PLUGIN_LIBRARY_DIR@'
module_dir = '@MODULE_NAME@'

# setup extra compile and link arguments on Mac
extra_compile_args = ['-std=c++17']
extra_link_args = []

if platform.system() == 'Darwin':
    extra_compile_args += ['-stdlib=libc++']
    extra_link_args += ['-stdlib=libc++', '-Wl,-rpath,' + os.path.join(openmm_dir, 'lib')]

os.environ['CC'] = '@CMAKE_C_COMPILER@'
os.environ['CXX'] = '@CMAKE_CXX_COMPILER@'

setup(
    ext_modules=[
        Extension(
            name='@MODULE_NAME@._@MODULE_NAME@',
            sources=[os.path.join(module_dir, '@WRAP_FILE@')],
            libraries=['OpenMM', '@PLUGIN_LIBRARY_NAME@'],
            include_dirs=[os.path.join(openmm_dir, 'include'), header_dir, np.get_include()],
            library_dirs=[os.path.join(openmm_dir, 'lib'), library_dir],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )
    ],
)
