/* -------------------------------------------------------------------------- *
 *                              OpenMM CPP Forces                             *
 *                              =================                             *
 *                                                                            *
 *  A plugin for distributing platform-agnostic OpenMM Forces                 *
 *                                                                            *
 *  Copyright (c) 2024 Charlles Abreu                                         *
 *  https://github.com/craabreu/openmm-cpp-forces                             *
 * -------------------------------------------------------------------------- */

#include "CompositeRMSDForce.h"
#include "internal/CompositeRMSDForceImpl.h"

#include "openmm/internal/AssertionUtilities.h"

using namespace OpenMMCPPForces;
using namespace OpenMM;
using namespace std;

CompositeRMSDForce::CompositeRMSDForce(const vector<Vec3>& referencePositions) :
        referencePositions(referencePositions) {
}

void CompositeRMSDForce::setReferencePositions(const std::vector<Vec3>& positions) {
    referencePositions = positions;
}

int CompositeRMSDForce::addGroup(const vector<int>& particles) {
    groups.push_back(particles);
    return groups.size()-1;
}

int CompositeRMSDForce::getNumGroups() const {
    return groups.size();
}

const vector<int>& CompositeRMSDForce::getGroup(int index) const {
    ASSERT_VALID_INDEX(index, groups);
    return groups[index];
}

void CompositeRMSDForce::setGroup(int index, const std::vector<int>& particles) {
    ASSERT_VALID_INDEX(index, groups);
    groups[index] = particles;
}

void CompositeRMSDForce::updateParametersInContext(Context& context) {
    dynamic_cast<CompositeRMSDForceImpl&>(getImplInContext(context)).updateParametersInContext(getContextImpl(context));
}

ForceImpl* CompositeRMSDForce::createImpl() const {
    return new CompositeRMSDForceImpl(*this);
}
