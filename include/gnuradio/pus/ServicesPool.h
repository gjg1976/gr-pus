/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_SERVICESPOOL_H
#define INCLUDED_PUS_SERVICESPOOL_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API ServicesPool : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<ServicesPool> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::ServicesPool.
       *
       * To avoid accidental use of raw pointers, pus::ServicesPool's
       * constructor is in a private implementation
       * class. pus::ServicesPool::make is the public interface for
       * creating new instances.
       */
      static sptr make(std::vector<uint16_t> services_list);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_SERVICESPOOL_H */
