# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT pus_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT pus_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################
list(APPEND pus_python_files
    ServicesPool_python.cc
    TestService_python.cc
    RequestVerificationService_python.cc
    HousekeepingService_python.cc
    ParameterStatisticsService_python.cc
    EventReportService_python.cc
    MemoryManagementService_python.cc
    FunctionManagementService_python.cc
    TimeBasedSchedulingService_python.cc
    OnBoardMonitoringService_python.cc
    LargePacketTransferService_python.cc
    RealTimeForwardingControlService_python.cc
    StorageAndRetrievalService_python.cc
    EventActionService_python.cc
    ParameterService_python.cc
    TimeConfig_python.cc
    MessageConfig_python.cc
    ParametersInit_python.cc
    EventsInit_python.cc
    setParameter_python.cc
    LargeMessageDetector_python.cc
    FunctionInit_python.cc
    RequestSequencingService_python.cc
    FileManagementService_python.cc
    pdu_vector_source_python.cc python_bindings.cc)

GR_PYBIND_MAKE_OOT(pus
   ../../..
   gr::pus
   "${pus_python_files}")

# copy bindings extension for use in QA test module
add_custom_command(TARGET pus_python POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:pus_python>
    ${CMAKE_BINARY_DIR}/test_modules/gnuradio/pus/
)

install(TARGETS pus_python DESTINATION ${GR_PYTHON_DIR}/gnuradio/pus COMPONENT pythonapi)
