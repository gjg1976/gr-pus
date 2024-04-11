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
/* BINDTOOL_GEN_AUTOMATIC(0)                                                       */
/* BINDTOOL_USE_PYGCCXML(0)                                                        */
/* BINDTOOL_HEADER_FILE(EventReportService.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(70cc890b49cce00d5415cfeb48e58730)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/pus/EventReportService.h>
// pydoc.h is automatically generated in the build directory
#include <EventReportService_pydoc.h>

void bind_EventReportService(py::module& m)
{

    using EventReportService    = gr::pus::EventReportService;


    py::class_<EventReportService, gr::block, gr::basic_block,
        std::shared_ptr<EventReportService>>(m, "EventReportService", D(EventReportService))

        .def(py::init(&EventReportService::make),
           py::arg("init_file"),
           D(EventReportService,make)
        )
        



        ;




}








