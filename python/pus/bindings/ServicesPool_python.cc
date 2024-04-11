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
/* BINDTOOL_HEADER_FILE(ServicesPool.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(a87d70422be64addb781689e02444e61)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/pus/ServicesPool.h>
// pydoc.h is automatically generated in the build directory
#include <ServicesPool_pydoc.h>

void bind_ServicesPool(py::module& m)
{

    using ServicesPool    = gr::pus::ServicesPool;


    py::class_<ServicesPool, gr::block, gr::basic_block,
        std::shared_ptr<ServicesPool>>(m, "ServicesPool", D(ServicesPool))

        .def(py::init(&ServicesPool::make),
           py::arg("services_list"),
           D(ServicesPool,make)
        )
        



        ;




}








