/* -------------------------------------------------------------------------- *
 *                          OpenMM Custom CPP Forces                          *
 *                          ========================                          *
 *                                                                            *
 *  A plugin for distributing OpenMM CustomCPPForce instances                 *
 *                                                                            *
 *  Copyright (c) 2024 Charlles Abreu                                         *
 *  https://github.com/craabreu/customcppforces                               *
 * -------------------------------------------------------------------------- */

#include "ConcertedRMSDForce.h"
#include "internal/ConcertedRMSDForceImpl.h"

using namespace CustomCPPForces;
using namespace OpenMM;
using namespace std;

ConcertedRMSDForce::ConcertedRMSDForce(const vector<Vec3>& referencePositions, const vector<int>& particles) :
        referencePositions(referencePositions), particles(particles) {
}

void ConcertedRMSDForce::setReferencePositions(const std::vector<Vec3>& positions) {
    referencePositions = positions;
}

void ConcertedRMSDForce::setParticles(const std::vector<int>& particles) {
    this->particles = particles;
}

void ConcertedRMSDForce::updateParametersInContext(Context& context) {
    dynamic_cast<ConcertedRMSDForceImpl&>(getImplInContext(context)).updateParametersInContext(getContextImpl(context));
}

ForceImpl* ConcertedRMSDForce::createImpl() const {
    return new ConcertedRMSDForceImpl(*this);
}