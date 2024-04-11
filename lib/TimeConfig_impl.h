/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_TIMECONFIG_IMPL_H
#define INCLUDED_PUS_TIMECONFIG_IMPL_H

#include <gnuradio/pus/TimeConfig.h>


namespace gr {
  namespace pus {

    class TimeConfig_impl : public TimeConfig
    {
     private:
      TimeProvider* d_time_provider;

     public:
      TimeConfig_impl(float resolution, uint8_t mode, bool p_field, uint16_t epoch_year, uint8_t epoch_month, uint8_t epoch_day);
      ~TimeConfig_impl();

      etl::vector<uint8_t, ECSSMaxTimeField> getCurrentTimeStamp();

      std::vector<uint8_t> getCurrentTimeStampAsVector() override;
      
      UTCTimestamp getCurrentTimeUTC() override; 

      uint32_t  getCurrentTimeDefaultCUC() override;
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_TIMECONFIG_IMPL_H */
