"""Turn a CMake staging tree into a wheel that installs next to pip's OpenMM.

The library and headers go into site-packages/OpenMM.libs (owned by OpenMM's wheel), next to
libOpenMM, and the Python package goes into site-packages/openmmcppforces. Nothing from OpenMM
may be bundled.
"""

import argparse
import fnmatch
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PACKAGE = "openmmcppforces"
LIBRARY_PREFIX = "libOpenMMCPPForces"
ORIGIN = {"Linux": "$ORIGIN", "Darwin": "@loader_path"}
# Dependencies a macOS binary may have: rpath-relative (OpenMM, our library) or system ones
ALLOWED_MACOS_PREFIXES = ("@rpath/", "@loader_path/", "/usr/lib/", "/System/")
WHEEL_NAME = re.compile(r"^openmm_cpp_forces-(?P<version>[^-]+)-")


def runtime_paths(relpath, system):
    origin = ORIGIN[system]
    parts = Path(relpath).parts
    if parts[0] == "OpenMM.libs":
        # Our library sits next to libOpenMM
        return [origin]
    return [origin + "/" + "../" * (len(parts) - 1) + "OpenMM.libs/lib"]


def _binaries(stage):
    for path in sorted(stage.rglob("*")):
        if path.is_file() and (path.suffix in (".so", ".dylib") or ".so." in path.name):
            yield path


def stage_module(site_packages, stage):
    source = Path(site_packages) / PACKAGE
    missing = [name for name in ("__init__.py", f"{PACKAGE}.py") if not (source / name).is_file()]
    extensions = sorted(path.name for path in source.glob(f"_{PACKAGE}*.so"))
    if missing or len(extensions) != 1:
        raise SystemExit(f"{PACKAGE} package incomplete in {site_packages}: "
                         f"missing {missing}, extensions {extensions}")
    shutil.copytree(source, Path(stage) / PACKAGE, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("tests", "__pycache__"))


def _macos_rpaths(binary):
    output = subprocess.run(["otool", "-l", str(binary)], check=True, capture_output=True, text=True).stdout
    return re.findall(r"cmd LC_RPATH\n\s+cmdsize \d+\n\s+path (\S+)", output)


def fix_runtime_paths(stage):
    system = platform.system()
    for binary in _binaries(Path(stage)):
        wanted = runtime_paths(binary.relative_to(stage).as_posix(), system)
        if system == "Linux":
            subprocess.run(["patchelf", "--set-rpath", ":".join(wanted), str(binary)], check=True)
        else:
            for rpath in _macos_rpaths(binary):
                subprocess.run(["install_name_tool", "-delete_rpath", rpath, str(binary)], check=True)
            for rpath in wanted:
                subprocess.run(["install_name_tool", "-add_rpath", rpath, str(binary)], check=True)
            subprocess.run(["codesign", "--force", "--sign", "-", str(binary)], check=True)


def inject(wheel, stage):
    from delocate.wheeltools import InWheel

    wheel = Path(wheel).resolve()
    # setuptools leaves its egg-info in the staging tree; files already in the wheel are rewritten identically
    files = [
        p for p in sorted(Path(stage).rglob("*"))
        if p.is_file() and not any(part.endswith(".egg-info") for part in p.relative_to(stage).parts)
    ]
    with InWheel(str(wheel), str(wheel)) as unpacked:
        for path in files:
            target = Path(unpacked) / path.relative_to(stage)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def foreign_dependencies(otool_output):
    lines = otool_output.splitlines()[1:]  # the first line names the binary
    dependencies = [line.split(" (")[0].strip() for line in lines if line.strip()]
    return [d for d in dependencies if not d.startswith(ALLOWED_MACOS_PREFIXES)]


def _macos_problems(wheel):
    import tempfile

    problems = []
    with tempfile.TemporaryDirectory() as unpacked:
        zipfile.ZipFile(wheel).extractall(unpacked)
        for binary in _binaries(Path(unpacked)):
            output = subprocess.run(["otool", "-L", str(binary)], check=True, capture_output=True, text=True).stdout
            problems += [f"absolute dependency in {binary.relative_to(unpacked)}: {d}"
                         for d in foreign_dependencies(output)]
    return problems


def check_wheel(wheel, required):
    with zipfile.ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
    problems = _macos_problems(wheel) if platform.system() == "Darwin" else []
    for name in names:
        top = name.split("/")[0]
        if top.endswith(".dylibs") or (top.endswith(".libs") and top != "OpenMM.libs"):
            problems.append(f"bundled library: {name}")
        elif name.startswith("OpenMM.libs/lib/") and not Path(name).name.startswith(LIBRARY_PREFIX):
            problems.append(f"foreign file in OpenMM.libs: {name}")
        elif name.startswith(f"{PACKAGE}/tests/") or "/__pycache__/" in name:
            problems.append(f"file not part of the package: {name}")
    for pattern in required:
        if not any(fnmatch.fnmatch(name, pattern) for name in names):
            problems.append(f"missing file matching {pattern}")
    if problems:
        raise SystemExit(f"{wheel}:\n  " + "\n  ".join(problems))


def arrange(source, destination, expected):
    wheels = sorted(Path(source).rglob("*.whl"))
    if expected is not None and len(wheels) != expected:
        raise SystemExit(f"found {len(wheels)} wheels, expected {expected}")
    for wheel in wheels:
        match = WHEEL_NAME.match(wheel.name)
        if match is None:
            raise SystemExit(f"unexpected wheel {wheel.name}")
        post = re.search(r"\.post(\d+)$", match["version"])
        target = Path(destination) / f"{post.group(1) if post else 0}-base"
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wheel, target / wheel.name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("stage-module")
    command.add_argument("stage", type=Path)
    command = commands.add_parser("fix-runtime-paths")
    command.add_argument("stage", type=Path)
    command = commands.add_parser("inject")
    command.add_argument("wheel", type=Path)
    command.add_argument("stage", type=Path)
    command = commands.add_parser("check")
    command.add_argument("wheel", type=Path)
    command.add_argument("--require", action="append", default=[])
    command = commands.add_parser("arrange")
    command.add_argument("source", type=Path)
    command.add_argument("destination", type=Path)
    command.add_argument("--expected", type=int)
    args = parser.parse_args(argv)

    if args.command == "stage-module":
        import sysconfig
        stage_module(Path(sysconfig.get_paths()["platlib"]), args.stage)
    elif args.command == "fix-runtime-paths":
        fix_runtime_paths(args.stage)
    elif args.command == "inject":
        inject(args.wheel, args.stage)
    elif args.command == "check":
        check_wheel(args.wheel, args.require)
    elif args.command == "arrange":
        arrange(args.source, args.destination, args.expected)


if __name__ == "__main__":
    sys.exit(main())
