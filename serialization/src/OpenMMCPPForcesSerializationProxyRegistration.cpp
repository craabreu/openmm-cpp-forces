/* -------------------------------------------------------------------------- *
 *                              OpenMM CPP Forces                             *
 *                              =================                             *
 *                                                                            *
 *  A plugin for distributing platform-agnostic OpenMM Forces                 *
 *                                                                            *
 *  Copyright (c) 2024 Charlles Abreu                                         *
 *  https://github.com/craabreu/openmm-cpp-forces                             *
 * -------------------------------------------------------------------------- */

#ifdef WIN32
#include <windows.h>
#include <sstream>
#else
#include <dlfcn.h>
#include <dirent.h>
#include <cstdlib>
#endif

#include "CompositeRMSDForce.h"
#include "CompositeRMSDForceProxy.h"
#include "openmm/serialization/SerializationProxy.h"

#if defined(WIN32)
    #include <windows.h>
    extern "C" CUSTOM_CPP_FORCES_EXPORT void registerOpenMMCPPForcesSerializationProxies();
    BOOL WINAPI DllMain(HANDLE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
        if (ul_reason_for_call == DLL_PROCESS_ATTACH)
            registerOpenMMCPPForcesSerializationProxies();
        return TRUE;
    }
#else
    extern "C" void __attribute__((constructor)) registerOpenMMCPPForcesSerializationProxies();
#endif

using namespace OpenMMCPPForces;
using namespace OpenMM;

extern "C" CUSTOM_CPP_FORCES_EXPORT void registerOpenMMCPPForcesSerializationProxies() {
    SerializationProxy::registerProxy(typeid(CompositeRMSDForce), new CompositeRMSDForceProxy());
}
