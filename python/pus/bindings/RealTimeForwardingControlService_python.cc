/*
 * Copyright 2023 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

/***********************************************************************************/
/* This file is automatically generated using bindtool and can be manually edited  */
/* The following lines can be configured to regenerate this file during cmake      */
/* If manual edits are made, the following tags should be modified accordingly.    */
/* BINDTOOL_GEN_AUTOMATIC(0)                                                       */
/* BINDTOOL_USE_PYGCCXML(0)                                                        */
/* BINDTOOL_HEADER_FILE(RealTimeForwardingControlService.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(8fb2c063af13f22f3c9a3a01aa17dcb3)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/pus/RealTimeForwardingControlService.h>
// pydoc.h is automatically generated in the build directory
#include <RealTimeForwardingControlService_pydoc.h>

void bind_RealTimeForwardingControlService(py::module& m)
{

    using RealTimeForwardingControlService    = gr::pus::RealTimeForwardingControlService;


    py::class_<RealTimeForwardingControlService, gr::block, gr::basic_block,
        std::shared_ptr<RealTimeForwardingControlService>>(m, "RealTimeForwardingControlService", D(RealTimeForwardingControlService))

        .def(py::init(&RealTimeForwardingControlService::make),
           py::arg("init_file"),
           D(RealTimeForwardingControlService,make)
        )
        



        ;




}








