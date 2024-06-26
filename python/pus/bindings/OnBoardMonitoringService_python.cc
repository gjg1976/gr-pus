/*
 * Copyright 2024 Free Software Foundation, Inc.
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
/* BINDTOOL_GEN_AUTOMATIC(1)                                                       */
/* BINDTOOL_USE_PYGCCXML(0)                                                        */
/* BINDTOOL_HEADER_FILE(OnBoardMonitoringService.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(a7643e084a09a7629b9ca96c7b2c244e)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/pus/OnBoardMonitoringService.h>
// pydoc.h is automatically generated in the build directory
#include <OnBoardMonitoringService_pydoc.h>

void bind_OnBoardMonitoringService(py::module& m)
{

    using OnBoardMonitoringService    = gr::pus::OnBoardMonitoringService;


    py::class_<OnBoardMonitoringService, gr::block, gr::basic_block,
        std::shared_ptr<OnBoardMonitoringService>>(m, "OnBoardMonitoringService", D(OnBoardMonitoringService))

        .def(py::init(&OnBoardMonitoringService::make),
           py::arg("init_file"),
           D(OnBoardMonitoringService,make)
        )
        



        ;




}








