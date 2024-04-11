/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_MESSAGECONFIG_H
#define INCLUDED_PUS_MESSAGECONFIG_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API MessageConfig : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<MessageConfig> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::MessageConfig.
       *
       * To avoid accidental use of raw pointers, pus::MessageConfig's
       * constructor is in a private implementation
       * class. pus::MessageConfig::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint16_t apid, bool crc_enable);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_MESSAGECONFIG_H */
