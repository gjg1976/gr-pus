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
/* BINDTOOL_HEADER_FILE(RequestVerificationService.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(c9264b6d224da9c07e9fb84887aafcfc)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/pus/RequestVerificationService.h>
// pydoc.h is automatically generated in the build directory
#include <RequestVerificationService_pydoc.h>

void bind_RequestVerificationService(py::module& m)
{

    using RequestVerificationService    = gr::pus::RequestVerificationService;


    py::class_<RequestVerificationService, gr::block, gr::basic_block,
        std::shared_ptr<RequestVerificationService>>(m, "RequestVerificationService", D(RequestVerificationService))

        .def(py::init(&RequestVerificationService::make),
           D(RequestVerificationService,make)
        )
        



        ;




}








