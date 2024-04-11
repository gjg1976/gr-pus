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
/* BINDTOOL_HEADER_FILE(RequestSequencingService.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(1dd7723ec07000625497a6606f7a75be)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/pus/RequestSequencingService.h>
// pydoc.h is automatically generated in the build directory
#include <RequestSequencingService_pydoc.h>

void bind_RequestSequencingService(py::module& m)
{

    using RequestSequencingService    = gr::pus::RequestSequencingService;


    py::class_<RequestSequencingService, gr::block, gr::basic_block,
        std::shared_ptr<RequestSequencingService>>(m, "RequestSequencingService", D(RequestSequencingService))

        .def(py::init(&RequestSequencingService::make),
           py::arg("init_file"),
           D(RequestSequencingService,make)
        )
        



        ;




}







