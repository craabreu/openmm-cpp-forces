import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
import package  # noqa: E402


def test_linux_runtime_paths():
    assert package.runtime_paths("openmmcppforces/_openmmcppforces.cpython-312-x86_64-linux-gnu.so", "Linux") == [
        "$ORIGIN/../OpenMM.libs/lib"]
    assert package.runtime_paths("OpenMM.libs/lib/libOpenMMCPPForces.so", "Linux") == ["$ORIGIN"]


def test_macos_runtime_paths():
    assert package.runtime_paths("openmmcppforces/_openmmcppforces.cpython-312-darwin.so", "Darwin") == [
        "@loader_path/../OpenMM.libs/lib"]
    assert package.runtime_paths("OpenMM.libs/lib/libOpenMMCPPForces.dylib", "Darwin") == ["@loader_path"]


def _site_packages(tmp_path, files):
    site = tmp_path / "site"
    for name in files:
        path = site / "openmmcppforces" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    return site


INSTALLED = ["__init__.py", "openmmcppforces.py", "_openmmcppforces.cpython-312-x86_64-linux-gnu.so",
             "tests/__init__.py", "tests/test_concerted_rmsd_force.py", "__pycache__/__init__.cpython-312.pyc"]


def test_stage_module_copies_package_without_tests(tmp_path):
    stage = tmp_path / "stage"
    package.stage_module(_site_packages(tmp_path, INSTALLED), stage)
    staged = sorted(p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file())
    assert staged == ["openmmcppforces/__init__.py", "openmmcppforces/_openmmcppforces.cpython-312-x86_64-linux-gnu.so",
                      "openmmcppforces/openmmcppforces.py"]


def test_stage_module_requires_complete_package(tmp_path):
    site = _site_packages(tmp_path, ["__init__.py", "openmmcppforces.py"])
    with pytest.raises(SystemExit, match="incomplete"):
        package.stage_module(site, tmp_path / "stage")


def _wheel(path, names):
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, b"")
    return path


BASE = [
    "openmmcppforces/__init__.py",
    "openmmcppforces/openmmcppforces.py",
    "openmmcppforces/_openmmcppforces.cpython-312-x86_64-linux-gnu.so",
    "OpenMM.libs/lib/libOpenMMCPPForces.so",
    "OpenMM.libs/include/CompositeRMSDForce.h",
]
REQUIRED = ["openmmcppforces/__init__.py", "openmmcppforces/_openmmcppforces*",
            "OpenMM.libs/lib/libOpenMMCPPForces.*", "OpenMM.libs/include/CompositeRMSDForce.h"]


def test_check_wheel_accepts_our_files(tmp_path):
    package.check_wheel(_wheel(tmp_path / "ok.whl", BASE), REQUIRED)


def test_check_wheel_rejects_grafted_libraries(tmp_path):
    wheel = _wheel(tmp_path / "bad.whl", BASE + ["openmm_cpp_forces.libs/libOpenMM-1a2b.so"])
    with pytest.raises(SystemExit, match="bundled"):
        package.check_wheel(wheel, REQUIRED)


def test_check_wheel_rejects_foreign_openmm_files(tmp_path):
    wheel = _wheel(tmp_path / "bad.whl", BASE + ["OpenMM.libs/lib/libOpenMM.so"])
    with pytest.raises(SystemExit, match="foreign"):
        package.check_wheel(wheel, REQUIRED)


def test_check_wheel_rejects_tests_and_caches(tmp_path):
    wheel = _wheel(tmp_path / "bad.whl", BASE + ["openmmcppforces/tests/test_concerted_rmsd_force.py",
                                                 "openmmcppforces/__pycache__/__init__.cpython-312.pyc"])
    with pytest.raises(SystemExit, match="not part of the package") as error:
        package.check_wheel(wheel, REQUIRED)
    assert "tests/test_concerted_rmsd_force.py" in str(error.value)
    assert "__pycache__" in str(error.value)


def test_check_wheel_requires_extension(tmp_path):
    wheel = _wheel(tmp_path / "noext.whl", [n for n in BASE if "_openmmcppforces" not in n])
    with pytest.raises(SystemExit, match="missing"):
        package.check_wheel(wheel, REQUIRED)


def test_inject_adds_staged_files(tmp_path):
    stage = tmp_path / "stage"
    (stage / "OpenMM.libs/lib").mkdir(parents=True)
    (stage / "openmmcppforces").mkdir()
    (stage / "openmmcppforces/__init__.py").write_text("")
    (stage / "openmmcppforces/_openmmcppforces.so").write_bytes(b"ext")
    (stage / "OpenMM.libs/lib/libOpenMMCPPForces.so").write_bytes(b"lib")
    wheel = tmp_path / "x-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("openmmcppforces/__init__.py", "")
        archive.writestr("x-1.0.dist-info/RECORD", "openmmcppforces/__init__.py,,\nx-1.0.dist-info/RECORD,,\n")
    package.inject(wheel, stage)
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        record = archive.read("x-1.0.dist-info/RECORD").decode()
    assert "OpenMM.libs/lib/libOpenMMCPPForces.so" in names
    assert "openmmcppforces/_openmmcppforces.so" in names
    assert names.count("openmmcppforces/__init__.py") == 1
    assert "OpenMM.libs/lib/libOpenMMCPPForces.so,sha256=" in record


def test_inject_skips_build_metadata(tmp_path):
    # setuptools writes its egg-info into the staging tree, which is the wheel's package root
    stage = tmp_path / "stage"
    (stage / "pkg.egg-info").mkdir(parents=True)
    (stage / "pkg.egg-info/PKG-INFO").write_text("")
    wheel = tmp_path / "x-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("x-1.0.dist-info/RECORD", "x-1.0.dist-info/RECORD,,\n")
    package.inject(wheel, stage)
    with zipfile.ZipFile(wheel) as archive:
        assert not [n for n in archive.namelist() if ".egg-info" in n]


def test_arrange_orders_by_post(tmp_path):
    source, destination = tmp_path / "in", tmp_path / "out"
    (source / "a").mkdir(parents=True)
    names = [
        "openmm_cpp_forces-0.2.0-cp312-cp312-manylinux_2_34_x86_64.whl",
        "openmm_cpp_forces-0.2.0.post2-cp312-cp312-manylinux_2_34_x86_64.whl",
        "openmm_cpp_forces-0.2.0.post2-cp310-cp310-macosx_10_13_x86_64.whl",
    ]
    for name in names:
        (source / "a" / name).write_bytes(b"")
    package.arrange(source, destination, expected=3)
    assert sorted(p.name for p in (destination / "0-base").iterdir()) == [names[0]]
    assert sorted(p.name for p in (destination / "2-base").iterdir()) == sorted(names[1:])


def test_arrange_checks_count(tmp_path):
    (tmp_path / "in").mkdir()
    (tmp_path / "in" / "openmm_cpp_forces-0.2.0-cp312-cp312-manylinux_2_34_x86_64.whl").write_bytes(b"")
    with pytest.raises(SystemExit, match="expected 2"):
        package.arrange(tmp_path / "in", tmp_path / "out", expected=2)


def test_arrange_rejects_unknown_wheels(tmp_path):
    (tmp_path / "in").mkdir()
    (tmp_path / "in" / "something_else-1.0-py3-none-any.whl").write_bytes(b"")
    with pytest.raises(SystemExit, match="unexpected"):
        package.arrange(tmp_path / "in", tmp_path / "out", expected=None)


OTOOL = """/tmp/x/openmmcppforces/_openmmcppforces.cpython-312-darwin.so:
\t@rpath/libOpenMMCPPForces.dylib (compatibility version 0.0.0, current version 0.0.0)
\t@rpath/libOpenMM.dylib (compatibility version 0.0.0, current version 0.0.0)
\t/usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 1800.101.0)
\t/Users/runner/work/_temp/build-env/lib/python3.12/site-packages/OpenMM.libs/lib/libOpenMM.dylib (x)
\t/opt/homebrew/lib/libfoo.dylib (compatibility version 1.0.0)
"""


def test_foreign_macos_dependencies():
    # Anything not resolved through rpaths or the system would break on users' machines
    assert package.foreign_dependencies(OTOOL) == [
        "/Users/runner/work/_temp/build-env/lib/python3.12/site-packages/OpenMM.libs/lib/libOpenMM.dylib",
        "/opt/homebrew/lib/libfoo.dylib",
    ]
