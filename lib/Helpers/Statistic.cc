/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/pus/Helpers/Statistic.h>
#include <cmath>
#include <iomanip>
#include <iostream>
namespace gr {
  namespace pus {
    void Statistic::updateStatistics(double value) {
	if (value > max) {
		max = value;
		timeOfMaxValue = TimeGetter::getCurrentTimeDefaultCUC();
	}
	if (value < min) {
		min = value;
		timeOfMinValue = TimeGetter::getCurrentTimeDefaultCUC();
	}
	if (sampleCounter + 1 > 0) {
		mean = (mean * sampleCounter + value) / (sampleCounter + 1);
	}
	sumOfSquares += pow(value, 2);

	sampleCounter++;
    }

    void Statistic::appendStatisticsToMessage(Message& report, uint16_t parameterID)  
    {
	if (!ParameterPool::getInstance()->parameterExists(parameterID))
		return;
	auto parameter = ParameterPool::getInstance()->getParameter(parameterID);
	parameter->get().appendValueAsTypeToMessage(max, report);
	report.appendData(timeOfMaxValue);
	parameter->get().appendValueAsTypeToMessage(min, report);
	report.appendData(timeOfMinValue);
	parameter->get().appendValueAsTypeToMessage(mean, report);

	if constexpr (SupportsStandardDeviation) {
		double standardDeviation = 0;
		if (sampleCounter == 0) {
			standardDeviation = 0;
		} else {
			double meanOfSquares = sumOfSquares / sampleCounter;
			standardDeviation = sqrt(abs(meanOfSquares - pow(mean, 2)));
		}
		parameter->get().appendValueAsTypeToMessage(standardDeviation, report);
	}
    }

    void Statistic::setSelfSamplingInterval(uint32_t samplingInterval) {
	this->selfSamplingInterval = samplingInterval;
    }

    void Statistic::resetStatistics() {
	max = -std::numeric_limits<double>::infinity();
	min = std::numeric_limits<double>::infinity();
	timeOfMaxValue = Time::DefaultCUC(0);
	timeOfMinValue = Time::DefaultCUC(0);
	mean = 0;
	sumOfSquares = 0;
	sampleCounter = 0;
	samplingIntervalCounter = 0;
    }

    bool Statistic::statisticsAreInitialized() 
    {
	return (sampleCounter == 0 and mean == 0 and sumOfSquares == 0 and
	        timeOfMaxValue == Time::DefaultCUC(0) and timeOfMinValue == Time::DefaultCUC(0) and
	        max == -std::numeric_limits<double>::infinity() and min == std::numeric_limits<double>::infinity());
    }
  } // namespace pus
} // namespace gr
