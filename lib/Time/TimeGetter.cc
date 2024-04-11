/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 
#include <gnuradio/pus/Time/TimeGetter.h>


namespace gr {
  namespace pus {
  
    UTCTimestamp TimeGetter::getCurrentTimeUTC() {
	time_t timeInSeconds = static_cast<time_t>(time(nullptr));
	tm* UTCTimeStruct = gmtime(&timeInSeconds);
	UTCTimestamp currentTime(UTCTimeStruct->tm_year, UTCTimeStruct->tm_mon,
	                         UTCTimeStruct->tm_mday, UTCTimeStruct->tm_hour,
	                         UTCTimeStruct->tm_min, UTCTimeStruct->tm_sec);
	return currentTime;
    }

    Time::DefaultCUC TimeGetter::getCurrentTimeDefaultCUC() {
	UTCTimestamp timeUTC = getCurrentTimeUTC();
	return Time::DefaultCUC(timeUTC);
    }

  } // namespace pus
} // namespace gr    
