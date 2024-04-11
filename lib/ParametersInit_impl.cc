/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "ParametersInit_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    ParametersInit::sptr
    ParametersInit::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<ParametersInit_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    ParametersInit_impl::ParametersInit_impl(const std::string& init_file)
      : gr::block("ParametersInit",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_parameter_pool = ParameterPool::getInstance();
       
        if (!d_parameter_pool->initializeParameterMap(init_file)){
        	GR_LOG_WARN(d_logger, "No Parameters init file found");
        }
    }

    /*
     * Our virtual destructor.
     */
    ParametersInit_impl::~ParametersInit_impl()
    {
    }
  } /* namespace pus */
} /* namespace gr */
