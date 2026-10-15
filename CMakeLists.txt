#---------------------------------------------------
# OpenMM OpenMMCPPForces Plugin
#----------------------------------------------------

CMAKE_MINIMUM_REQUIRED(VERSION 3.17)

PROJECT(OpenMMCPPForces VERSION 0.1.1)

IF(NOT DEFINED OPENMM_DIR)
    IF(DEFINED ENV{CONDA_PREFIX})
        SET(OPENMM_DIR $ENV{CONDA_PREFIX} CACHE PATH "Where OpenMM is installed")
    ELSE()
        MESSAGE(FATAL_ERROR "Set OPENMM_DIR to the directory where OpenMM is installed.")
    ENDIF()
ENDIF()

FIND_PROGRAM(PYTHON_EXECUTABLE python REQUIRED)
IF(NOT DEFINED OPENMM_VERSION)
    EXECUTE_PROCESS(
        COMMAND ${PYTHON_EXECUTABLE} -c "import openmm; print(openmm.__version__)"
        OUTPUT_VARIABLE DETECTED_OPENMM_VERSION
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE OPENMM_IMPORT_RESULT
    )
    IF(NOT OPENMM_IMPORT_RESULT EQUAL 0)
        MESSAGE(FATAL_ERROR "Could not import openmm with ${PYTHON_EXECUTABLE}. Set OPENMM_VERSION explicitly.")
    ENDIF()
    SET(OPENMM_VERSION ${DETECTED_OPENMM_VERSION} CACHE STRING "OpenMM version")
ENDIF()
MESSAGE(STATUS "OpenMM version: ${OPENMM_VERSION}")
IF(OPENMM_VERSION VERSION_LESS 8.4)
    MESSAGE(FATAL_ERROR "OpenMM version must be at least 8.4")
ENDIF()

INCLUDE_DIRECTORIES("${OPENMM_DIR}/include")
LINK_DIRECTORIES("${OPENMM_DIR}/lib" "${OPENMM_DIR}/lib/plugins")

# Specify the C++ version we are building for.
SET (CMAKE_CXX_STANDARD 11)

SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake_modules")

# Set flags for linking on mac
IF(APPLE)
    SET(CMAKE_INSTALL_NAME_DIR "@rpath")
    SET(EXTRA_COMPILE_FLAGS "-stdlib=libc++")
ENDIF(APPLE)

# Select where to install
IF(${CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT})
    IF(WIN32)
        SET(CMAKE_INSTALL_PREFIX "$ENV{ProgramFiles}/OpenMM" CACHE PATH "Where to install the plugin" FORCE)
    ELSE(WIN32)
        SET(CMAKE_INSTALL_PREFIX ${OPENMM_DIR} CACHE PATH "Where to install the plugin" FORCE)
    ENDIF(WIN32)
ENDIF(${CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT})

# The source is organized into subdirectories, but we handle them all from
# this CMakeLists file rather than letting CMake visit them as SUBDIRS.
SET(PLUGIN_SOURCE_SUBDIRS openmmcppforces serialization)

# Set the library name
SET(PLUGIN_LIBRARY_NAME OpenMMCPPForces)
SET(SHARED_CUSTOM_CPP_FORCES_TARGET ${PLUGIN_LIBRARY_NAME})

# These are all the places to search for header files which are to be part of the API.
SET(API_INCLUDE_DIRS "openmmcppforces/include")

# Locate header files.
SET(API_INCLUDE_FILES)
FOREACH(dir ${API_INCLUDE_DIRS})
    FILE(GLOB fullpaths ${dir}/*.h)
    SET(API_INCLUDE_FILES ${API_INCLUDE_FILES} ${fullpaths})
ENDFOREACH(dir)

# Collect up source files
SET(SOURCE_FILES) # empty
SET(SOURCE_INCLUDE_FILES)
FOREACH(subdir ${PLUGIN_SOURCE_SUBDIRS})
    FILE(GLOB src_files  ${CMAKE_CURRENT_SOURCE_DIR}/${subdir}/src/*.cpp)
    FILE(GLOB incl_files ${CMAKE_CURRENT_SOURCE_DIR}/${subdir}/src/*.h)
    SET(SOURCE_FILES         ${SOURCE_FILES}         ${src_files})   #append
    SET(SOURCE_INCLUDE_FILES ${SOURCE_INCLUDE_FILES} ${incl_files})

    ## Make sure we find these locally before looking in OpenMM/include if
    ## OpenMM was previously installed there.
    INCLUDE_DIRECTORIES(BEFORE ${CMAKE_CURRENT_SOURCE_DIR}/${subdir}/include)
ENDFOREACH(subdir)

# Create the library.

ADD_LIBRARY(${SHARED_CUSTOM_CPP_FORCES_TARGET} SHARED ${SOURCE_FILES} ${SOURCE_INCLUDE_FILES} ${API_INCLUDE_FILES})
SET_TARGET_PROPERTIES(${SHARED_CUSTOM_CPP_FORCES_TARGET}
    PROPERTIES COMPILE_FLAGS "-DPLUGIN_BUILDING_SHARED_LIBRARY ${EXTRA_COMPILE_FLAGS}"
    LINK_FLAGS "${EXTRA_COMPILE_FLAGS}")
TARGET_LINK_LIBRARIES(${SHARED_CUSTOM_CPP_FORCES_TARGET} OpenMM)
INSTALL_TARGETS(/lib RUNTIME_DIRECTORY /lib ${SHARED_CUSTOM_CPP_FORCES_TARGET})

# install headers
FILE(GLOB API_ONLY_INCLUDE_FILES "openmmcppforces/include/*.h")
INSTALL (FILES ${API_ONLY_INCLUDE_FILES} DESTINATION include)

# Enable testing

ENABLE_TESTING()
ADD_SUBDIRECTORY(tests)
ADD_SUBDIRECTORY(serialization/tests)
INCLUDE(CTest)

# Build the implementations for different platforms

SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}")

# Build the Python API

FIND_PROGRAM(PYTHON_EXECUTABLE python REQUIRED)
FIND_PROGRAM(SWIG_EXECUTABLE swig REQUIRED)
SET(PLUGIN_BUILD_PYTHON_WRAPPERS ON CACHE BOOL "Build wrappers for Python")
IF(PLUGIN_BUILD_PYTHON_WRAPPERS)
    ADD_SUBDIRECTORY(python)
ENDIF(PLUGIN_BUILD_PYTHON_WRAPPERS)

# Build the documentation

ADD_SUBDIRECTORY(docs)

# Find required packages

SET(CMAKE_THREAD_PREFER_PTHREAD ON CACHE BOOL "Prefer pthread lib")
SET(THREADS_PREFER_PTHREAD_FLAG ON CACHE BOOL "Prefer pthread flag")
FIND_PACKAGE(Threads REQUIRED)
