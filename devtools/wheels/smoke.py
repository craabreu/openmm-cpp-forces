"""Checks run in a clean venv after installing the wheel."""

import argparse
import copy
from importlib.metadata import version


def check(expected):
    # Import the plugin before OpenMM: its extension must find libOpenMM by itself
    import openmmcppforces as mmcpp
    import numpy as np
    import openmm as mm

    failures = [f for f in mm.Platform.getPluginLoadFailures() if "OpenMMCPPForces" in f]
    assert not failures, f"plugin load failures: {failures}"
    assert version("openmm-cpp-forces") == expected, version("openmm-cpp-forces")
    assert mmcpp.__version__ == expected.split(".post")[0], mmcpp.__version__

    rng = np.random.default_rng(1234)
    num_particles = 20
    reference = [mm.Vec3(*x) for x in rng.normal(size=(num_particles, 3))]
    positions = [mm.Vec3(*x) for x in rng.normal(size=(num_particles, 3))]
    force = mmcpp.CompositeRMSDForce(reference)
    force.addGroup(list(range(10)))
    force.addGroup(list(range(10, 20)))

    results = {}
    for name in ("Reference", "CPU"):
        system = mm.System()
        for _ in range(num_particles):
            system.addParticle(1.0)
        # copy.copy goes through XmlSerializer::clone, so it needs the serialization proxy
        system.addForce(copy.copy(force))
        context = mm.Context(system, mm.VerletIntegrator(0.001), mm.Platform.getPlatformByName(name))
        context.setPositions(positions)
        state = context.getState(getEnergy=True, getForces=True)
        energy = state.getPotentialEnergy()._value
        forces = np.array(state.getForces(asNumpy=True)._value)
        print(f"{name} energy: {energy}")
        results[name] = (energy, forces)

    (e_ref, f_ref), (e_cpu, f_cpu) = results["Reference"], results["CPU"]
    assert e_ref > 0, e_ref
    assert abs(e_cpu - e_ref) <= 1e-6 * abs(e_ref), (e_cpu, e_ref)
    assert np.abs(f_cpu - f_ref).max() <= 1e-5 * max(1.0, np.abs(f_ref).max())

    xml = mm.XmlSerializer.serialize(force)
    assert mmcpp.CompositeRMSDForce.isinstance(mm.XmlSerializer.deserialize(xml)), xml[:200]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", help="expected version of the installed openmm-cpp-forces distribution")
    args = parser.parse_args()
    check(args.expected)
    print("OK")


if __name__ == "__main__":
    main()
