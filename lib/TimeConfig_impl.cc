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
#include "TimeConfig_impl.h"

namespace gr {
  namespace pus {

    TimeConfig::sptr
    TimeConfig::make(float resolution, uint8_t mode, bool p_field, uint16_t epoch_year, uint8_t epoch_month, uint8_t epoch_day)
    {
      return gnuradio::make_block_sptr<TimeConfig_impl>(
        resolution, mode, p_field, epoch_year, epoch_month, epoch_day);
    }


    /*
     * The private constructor
     */
    TimeConfig_impl::TimeConfig_impl(float resolution, uint8_t mode, bool p_field, uint16_t epoch_year, uint8_t epoch_month, uint8_t epoch_day)
      : gr::block("TimeConfig",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
    	d_time_provider = TimeProvider::getInstance();

    	if(!d_time_provider->config(resolution, mode, p_field, epoch_year, --epoch_month, epoch_day)){
    	   GR_LOG_ERROR(this->d_logger, "Invalid Epoch date, usign default one");
    	}
    	//d_time_provider->start();
    }

    /*
     * Our virtual destructor.
     */
    TimeConfig_impl::~TimeConfig_impl()
    {

    }

     std::vector<uint8_t> TimeConfig_impl::getCurrentTimeStampAsVector()
    {
    	etl::vector<uint8_t, ECSSMaxTimeField> timeStamp = d_time_provider->getCurrentTimeStamp();
    	std::vector<uint8_t> stamp;
    	for(auto b: timeStamp)
    		stamp.push_back(b);
    	return stamp;
    }

    etl::vector<uint8_t, ECSSMaxTimeField> TimeConfig_impl::getCurrentTimeStamp()
    {
    	return d_time_provider->getCurrentTimeStamp();
    }
    
    UTCTimestamp TimeConfig_impl::getCurrentTimeUTC()
    {
    	return d_time_provider->getCurrentTimeUTC();
    } 

    uint32_t  TimeConfig_impl::getCurrentTimeDefaultCUC()
    {
    	return d_time_provider->getCurrentTimeDefaultCUC();
    }   
  } /* namespace pus */
} /* namespace gr */
