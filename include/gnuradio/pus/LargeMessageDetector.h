/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_LARGEMESSAGEDETECTOR_H
#define INCLUDED_PUS_LARGEMESSAGEDETECTOR_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API LargeMessageDetector : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<LargeMessageDetector> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::LargeMessageDetector.
       *
       * To avoid accidental use of raw pointers, pus::LargeMessageDetector's
       * constructor is in a private implementation
       * class. pus::LargeMessageDetector::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_LARGEMESSAGEDETECTOR_H */
