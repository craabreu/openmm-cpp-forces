#ifndef OPENMM_COMPOSITERMSDFORCE_H_
#define OPENMM_COMPOSITERMSDFORCE_H_

/* -------------------------------------------------------------------------- *
 *                              OpenMM CPP Forces                             *
 *                              =================                             *
 *                                                                            *
 *  A plugin for distributing platform-agnostic OpenMM Forces                 *
 *                                                                            *
 *  Copyright (c) 2024 Charlles Abreu                                         *
  *  https://github.com/craabreu/openmm-cpp-forces                             *
 * -------------------------------------------------------------------------- */

#include "internal/windowsExportOpenMMCPPForces.h"

#include "openmm/Force.h"
#include "openmm/Vec3.h"
#include "openmm/internal/AssertionUtilities.h"
#include <vector>

using namespace OpenMM;
using namespace std;

namespace OpenMMCPPForces {

/**
 * This is a force whose energy equals a special type of root mean squared deviation
 * (RMSD) between the current coordinates and a reference structure.  It is intended for
 * use with CustomCVForce.  You will not normally want a force that exactly equals
 * the RMSD, but there are many situations where it is useful to have a restraining
 * or biasing force that depends on the RMSD in some way.
 *
 * The force is computed by first aligning the particle positions to the reference
 * structure, then computing the RMSD between the aligned positions and the reference.
 * The computation can optionally be done based on only a subset of the particles
 * in the system.
 */

class CUSTOM_CPP_FORCES_EXPORT CompositeRMSDForce : public Force {
public:
    /**
     * Create an CompositeRMSDForce.
     *
     * @param referencePositions  the reference positions to compute the deviation from.
     *                            The length of this vector must equal the number of
     *                            particles in the system, even if not all particles are
     *                            used in computing the Composite RMSD.
     */
    explicit CompositeRMSDForce(const vector<Vec3>& referencePositions);
    /**
     * Get the reference positions to compute the deviation from.
     */
    const vector<Vec3>& getReferencePositions() const {
        return referencePositions;
    }
    /**
     * Set the reference positions to compute the deviation from.
     *
     * @param positions    the reference positions to compute the deviation from.
     *                     The length of this vector must equal the number of
     *                     particles in the system, even if not all particles are
     *                     used in computing the composite RMSD.
     */
    void setReferencePositions(const vector<Vec3>& positions);
    /**
     * Add a group of particles to be included in the composite RMSD calculation.
     *
     * @param particles    the indices of the particles to include
     *
     * @return the index of the group that was added
     */
    int addGroup(const vector<int>& particles);
    /**
     * Get the number of particle groups included in the composite RMSD calculation.
     */
    int getNumGroups() const;
    /**
     * Get the particles of a group included in the composite RMSD calculation.
     *
     * @param index    the index of the group whose particles are to be retrieved
     */
    const vector<int>& getGroup(int index) const;
    /**
     * Set the particles of a group included in the composite RMSD calculation.
     */
    void setGroup(int index, const vector<int>& particles);
    /**
     * Update the reference positions and particle groups in a Context to match those stored
     * in this Force object.  This method provides an efficient way to update these parameters
     * in an existing Context without needing to reinitialize it.  Simply call setReferencePositions()
     * and setGroup() to modify this object's parameters, then call updateParametersInContext()
     * to copy them over to the Context.
     */
    void updateParametersInContext(Context& context);
    /**
     * Returns whether or not this force makes use of periodic boundary
     * conditions.
     *
     * @returns true if force uses PBC and false otherwise
     */
    bool usesPeriodicBoundaryConditions() const {
        return false;
    }
protected:
    ForceImpl* createImpl() const;
private:
    vector<Vec3> referencePositions;
    vector<vector<int>> groups;
};

} // namespace OpenMMCPPForces

#endif /*OPENMM_COMPOSITERMSDFORCE_H_*/
