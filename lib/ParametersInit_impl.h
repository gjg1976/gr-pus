/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_PARAMETERSINIT_IMPL_H
#define INCLUDED_PUS_PARAMETERSINIT_IMPL_H

#include <gnuradio/pus/ParametersInit.h>
#include <gnuradio/pus/Helpers/ParameterPool.h>

namespace gr {
  namespace pus {

    class ParametersInit_impl : public ParametersInit
    {
     private:
       ParameterPool* d_parameter_pool;

     
     public:
      ParametersInit_impl(const std::string& init_file);
      ~ParametersInit_impl();

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_PARAMETERSINIT_IMPL_H */
