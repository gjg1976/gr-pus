/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_FUNCTIONINIT_IMPL_H
#define INCLUDED_PUS_FUNCTIONINIT_IMPL_H

#include <gnuradio/pus/FunctionInit.h>
#include <gnuradio/pus/Helpers/FunctionPool.h>

namespace gr {
  namespace pus {

    class FunctionInit_impl : public FunctionInit
    {
     private:
      FunctionPool* d_function_pool;

     public:
      FunctionInit_impl(uint16_t funcNameSize);
      ~FunctionInit_impl();

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_FUNCTIONINIT_IMPL_H */
