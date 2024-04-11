/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_STATISTIC_H
#define ECSS_STATISTIC_H

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Time/TimeGetter.h>
#include <gnuradio/pus/Helpers/ParameterPool.h>

namespace gr {
  namespace pus {
/**
 * Class containing all the statistics for every parameter. Includes functions that calculate and append the
 * statistics to messages
 */
    class Statistic {
     public:
	uint32_t selfSamplingInterval = 0;
	uint32_t samplingIntervalCounter = 0;
	uint16_t sampleCounter = 0;
	Time::DefaultCUC timeOfMaxValue;
	Time::DefaultCUC timeOfMinValue;
	double max = -std::numeric_limits<double>::infinity();
	double min = std::numeric_limits<double>::infinity();
	double sumOfSquares = 0;
	double mean = 0;

	Statistic() = default;

	/**
	 * Gets the value from the sensor as argument and updates the statistics without storing it
	 * @param value returned value from "getValue()" of Parameter.hpp, i.e. the last sampled value from a parameter
	 */
	void updateStatistics(double value);

	/**
	 * Resets all statistics calculated to default values
	 */
	void resetStatistics();

	/**
	 * Appends itself to the received Message
	 * message.
	 */
	void appendStatisticsToMessage(Message& report, uint16_t parameterID);

	/**
	 * Setter function
	 */
	void setSelfSamplingInterval(uint32_t samplingInterval);

	/**
	 * Check if all the statistics are initialized
	 */
	bool statisticsAreInitialized();
    };
  } // namespace pus
} // namespace gr
#endif
