/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_FUNCTIONINIT_H
#define INCLUDED_PUS_FUNCTIONINIT_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API FunctionInit : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<FunctionInit> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::FunctionInit.
       *
       * To avoid accidental use of raw pointers, pus::FunctionInit's
       * constructor is in a private implementation
       * class. pus::FunctionInit::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint16_t funcNameSize);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_FUNCTIONINIT_H */
