/*
 * Copyright 2020 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include <pybind11/pybind11.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

namespace py = pybind11;

// Headers for binding functions
/**************************************/
// The following comment block is used for
// gr_modtool to insert function prototypes
// Please do not delete
/**************************************/
// BINDING_FUNCTION_PROTOTYPES(
    void bind_ServicesPool(py::module& m);
    void bind_TestService(py::module& m);
    void bind_RequestVerificationService(py::module& m);
    void bind_HousekeepingService(py::module& m);
    void bind_ParameterStatisticsService(py::module& m);
    void bind_EventReportService(py::module& m);
    void bind_MemoryManagementService(py::module& m);
    void bind_FunctionManagementService(py::module& m);
    void bind_TimeBasedSchedulingService(py::module& m);
    void bind_OnBoardMonitoringService(py::module& m);
    void bind_LargePacketTransferService(py::module& m);
    void bind_RealTimeForwardingControlService(py::module& m);
    void bind_StorageAndRetrievalService(py::module& m);
    void bind_EventActionService(py::module& m);
    void bind_ParameterService(py::module& m);
    void bind_TimeConfig(py::module& m);
    void bind_MessageConfig(py::module& m);
    void bind_ParametersInit(py::module& m);
    void bind_EventsInit(py::module& m);
    void bind_setParameter(py::module& m);
    void bind_LargeMessageDetector(py::module& m);
    void bind_FunctionInit(py::module& m);
    void bind_RequestSequencingService(py::module& m);
    void bind_FileManagementService(py::module& m);
    void bind_pdu_vector_source(py::module& m);
// ) END BINDING_FUNCTION_PROTOTYPES


// We need this hack because import_array() returns NULL
// for newer Python versions.
// This function is also necessary because it ensures access to the C API
// and removes a warning.
void* init_numpy()
{
    import_array();
    return NULL;
}

PYBIND11_MODULE(pus_python, m)
{
    // Initialize the numpy C API
    // (otherwise we will see segmentation faults)
    init_numpy();

    // Allow access to base block methods
    py::module::import("gnuradio.gr");

    /**************************************/
    // The following comment block is used for
    // gr_modtool to insert binding function calls
    // Please do not delete
    /**************************************/
    // BINDING_FUNCTION_CALLS(
    bind_ServicesPool(m);
    bind_TestService(m);
    bind_RequestVerificationService(m);
    bind_HousekeepingService(m);
    bind_ParameterStatisticsService(m);
    bind_EventReportService(m);
    bind_MemoryManagementService(m);
    bind_FunctionManagementService(m);
    bind_TimeBasedSchedulingService(m);
    bind_OnBoardMonitoringService(m);
    bind_LargePacketTransferService(m);
    bind_RealTimeForwardingControlService(m);
    bind_StorageAndRetrievalService(m);
    bind_EventActionService(m);
    bind_ParameterService(m);
    bind_TimeConfig(m);
    bind_MessageConfig(m);
    bind_ParametersInit(m);
    bind_EventsInit(m);
    bind_setParameter(m);
    bind_LargeMessageDetector(m);
    bind_FunctionInit(m);
    bind_RequestSequencingService(m);
    bind_FileManagementService(m);
    bind_pdu_vector_source(m);
    // ) END BINDING_FUNCTION_CALLS
}