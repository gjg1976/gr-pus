/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_EVENTSINIT_H
#define INCLUDED_PUS_EVENTSINIT_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API EventsInit : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<EventsInit> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::EventsInit.
       *
       * To avoid accidental use of raw pointers, pus::EventsInit's
       * constructor is in a private implementation
       * class. pus::EventsInit::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_EVENTSINIT_H */
