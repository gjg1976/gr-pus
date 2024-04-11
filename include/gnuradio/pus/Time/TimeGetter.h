/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef ECSS_SERVICES_TIMEGETTER_HPP
#define ECSS_SERVICES_TIMEGETTER_HPP

#include <cstdint>
#include <ctime>
#include <gnuradio/pus/Time/TimeStamp.h>
#include <gnuradio/pus/Time/UTCTimestamp.h>

namespace gr {
  namespace pus {

    /**
    * @brief Get the current time
    */
    class TimeGetter {
      public:
	/**
	 * Returns the current UTC time.
	 * @note
	 * The information needed to compute the UTC time is implementation-specific. This function should
	 * be reimplemented to work for every format of the time-related parameters.
	 */
	static UTCTimestamp getCurrentTimeUTC();

	/**
	 * Converts the current UTC time, to a CUC formatted timestamp.
	 * @note
	 * The original format of the CUC (etl array of bits), is not used here, because it's easier to append
	 * a type uint32_t to a message object, rather than a whole array. Thus, we use the custom CUC format.
	 *
	 * @return CUC timestamp, formatted as elapsed ticks.
	 * @see Time
	 */
	static Time::DefaultCUC getCurrentTimeDefaultCUC();
    };

  } // namespace pus
} // namespace gr
#endif // ECSS_SERVICES_TIMEGETTER_HPP
