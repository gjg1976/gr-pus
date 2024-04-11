/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_TIMECONFIG_H
#define INCLUDED_PUS_TIMECONFIG_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Time/TimeProvider.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API TimeConfig : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<TimeConfig> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::TimeConfig.
       *
       * To avoid accidental use of raw pointers, pus::TimeConfig's
       * constructor is in a private implementation
       * class. pus::TimeConfig::make is the public interface for
       * creating new instances.
       */
      static sptr make(float resolution, uint8_t mode, bool p_field, uint16_t epoch_year, uint8_t epoch_month, uint8_t epoch_day);

      virtual std::vector<uint8_t> getCurrentTimeStampAsVector() = 0;

      virtual UTCTimestamp getCurrentTimeUTC() = 0; 

      virtual uint32_t  getCurrentTimeDefaultCUC() = 0;
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_TIMECONFIG_H */
