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
#include "FunctionInit_impl.h"

namespace gr {
  namespace pus {

    void test_function(std::vector<uint8_t> vec)
    {
    	std::string str(vec.begin(), vec.end());
    	std::cout << "test_function: " << str << "\n";
    }
    
    FunctionInit::sptr
    FunctionInit::make(uint16_t funcNameSize)
    {
      return gnuradio::make_block_sptr<FunctionInit_impl>(
      	funcNameSize );
    }


    /*
     * The private constructor
     */
    FunctionInit_impl::FunctionInit_impl(uint16_t funcNameSize)
      : gr::block("FunctionInit",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
            d_function_pool = FunctionPool::getInstance();
            d_function_pool->setFuncNameSize(funcNameSize);
            d_function_pool->include("test_function", *test_function);
    }

    /*
     * Our virtual destructor.
     */
    FunctionInit_impl::~FunctionInit_impl()
    {
    }


  } /* namespace pus */
} /* namespace gr */
