import email
import os
import subprocess
import sys
import zipfile
from pathlib import Path

WHEELS = Path(__file__).parents[1]


def _source(tmp_path, readme=None):
    source = tmp_path / "src"
    source.mkdir()
    (source / "CMakeLists.txt").write_text("PROJECT(OpenMMCPPForces VERSION 0.2.0)\n")
    if readme is not None:
        (source / "README.md").write_text(readme)
    return source


def _stage(tmp_path):
    stage = tmp_path / "stage"
    (stage / "openmmcppforces").mkdir(parents=True)
    (stage / "openmmcppforces/__init__.py").write_text("")
    (stage / "openmmcppforces/openmmcppforces.py").write_text("")
    return stage


def _build(env, out):
    subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "-w", str(out), str(WHEELS)],
        check=True, env={**os.environ, **env}, capture_output=True)
    (wheel,) = out.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        (metadata,) = [n for n in names if n.endswith(".dist-info/METADATA")]
        return wheel, names, email.message_from_bytes(archive.read(metadata))


def test_wheel_metadata(tmp_path):
    wheel, names, meta = _build({
        "CPF_SOURCE_DIR": str(_source(tmp_path)), "CPF_OPENMM_MINOR": "8.5",
        "CPF_STAGE_DIR": str(_stage(tmp_path))}, tmp_path / "out")
    assert meta["Name"] == "openmm-cpp-forces"
    assert meta["Version"] == "0.2.0.post1"
    assert meta.get_all("Requires-Dist") == ["openmm<8.6,>=8.5.2"]
    assert meta.get_all("Provides-Extra") is None
    assert meta["Requires-Python"] == ">=3.10"
    assert "openmmcppforces/__init__.py" in names
    assert "openmmcppforces/openmmcppforces.py" in names
    # The extension is injected later; the wheel must already be platform-specific
    assert "-none-any" not in wheel.name


def test_description_comes_from_the_built_source(tmp_path):
    # The project page must describe the release being built, not the tooling checkout
    _, _, meta = _build({
        "CPF_SOURCE_DIR": str(_source(tmp_path, readme="Release README\n")), "CPF_OPENMM_MINOR": "8.4",
        "CPF_STAGE_DIR": str(_stage(tmp_path))}, tmp_path / "out")
    assert meta["Version"] == "0.2.0"
    assert meta.get_payload().strip() == "Release README"
