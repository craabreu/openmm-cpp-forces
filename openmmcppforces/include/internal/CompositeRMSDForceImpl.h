#ifndef OPENMM_COMPOSITERMSDFORCEIMPL_H_
#define OPENMM_COMPOSITERMSDFORCEIMPL_H_

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

#include "openmm/internal/CustomCPPForceImpl.h"
#include "openmm/internal/ContextImpl.h"
#include <vector>

using namespace OpenMM;
using namespace std;

namespace OpenMMCPPForces {

/**
 * This is the internal implementation of CompositeRMSDForce.
 */

class CompositeRMSDForceImpl : public CustomCPPForceImpl {
public:
    CompositeRMSDForceImpl(const CompositeRMSDForce& owner) :
      CustomCPPForceImpl(owner), owner(owner), resetForces(true) {}
    void initialize(ContextImpl& context);
    double computeForce(ContextImpl& context, const vector<Vec3>& positions, vector<Vec3>& forces);
    const CompositeRMSDForce& getOwner() const {
        return owner;
    }
    void updateParametersInContext(ContextImpl& context);
private:
    void updateParameters(int systemSize);
    const CompositeRMSDForce& owner;
    vector<vector<int>> groups;
    vector<Vec3> referencePos;
    double sumRefPosSq;
    bool resetForces;
};

} // namespace OpenMMCPPForces

#endif /*OPENMM_COMPOSITERMSDFORCEIMPL_H_*/
