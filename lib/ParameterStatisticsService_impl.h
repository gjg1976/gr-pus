/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_PARAMETERSTATISTICSSERVICE_IMPL_H
#define INCLUDED_PUS_PARAMETERSTATISTICSSERVICE_IMPL_H

#include <gnuradio/pus/ParameterStatisticsService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Helpers/ParameterPool.h>
#include <gnuradio/pus/Helpers/Statistic.h>
#include <atomic>
#include "etl/map.h"
#include "etl/vector.h"

#define PARAM_STATS_RESET_FLAG_SIZE  1
#define PARAM_STATS_RELATIVE_TIME_SIZE 4
#define PARAM_STATS_NUMPARAM_SIZE 2
#define PARAM_STATS_PARAMID_SIZE 2

namespace gr {
  namespace pus {

    class ParameterStatisticsService_impl : public ParameterStatisticsService
    {
     private:
      uint16_t counters[ParameterStatisticsService::MessageType::end];
      TimeProvider* d_time_provider;
      
      ParameterPool* d_parameter_pool;
	/**
	 * Map containing parameters' IDs followed by the statistics that correspond to the specified parameter
	 */
	etl::map<uint16_t, Statistic, ECSSMaxStatisticParameters> statisticsMap;

	/**
	 * The time at which the evaluation of statistics is initialized. It is basically the time when the statistics
	 * are reset.
	 */
	Time::DefaultCUC evaluationStartTime;

	/**
	 * true means that the periodic statistics reporting is enabled
	 */
	bool periodicStatisticsReportingStatus = false;

	/**
	 * The parameter statistics reporting interval
	 */
	uint32_t reportingIntervalMs;
	uint32_t counterIntervalMs = 0;

	void parse_json(const std::string& filename);  
          
     public:
      ParameterStatisticsService_impl(const std::string& init_file);
      ~ParameterStatisticsService_impl();
 
	/**
	 * timer Tick hook, each time is called, it will search for StatisticMap checking if a parameter
	 * shall be update, then, if the periodicStatisticsReportingStatus is enable will check if
	 * parameterStatisticsReport need to be addressed.
	 * @param p TimeProvider singleton
	 * @return void
	 */
	void timerTick(TimeProvider *p) ;    
	  
	/**
	 * If true, after every report reset the parameter statistics.
	 */
	bool hasAutomaticStatisticsReset = false; // todo: do const
	/**
	 * Indicates whether to append/read the sampling interval to/from message
	 */
	const bool supportsSamplingInterval = true;
	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
       void handle_msg(pmt::pmt_t pdu);

	/**
	 * TC[4,1] report the parameter statistics, by calling parameterStatisticsReport()
	 */
	void reportParameterStatistics(Message& request);

	/**
	 * Report the parameter statistics, by calling parameterStatisticsReport()
	 * This is **NOT** the function called by TC. It was created so that this function could be called
	 * from within a Platform (MCU, x86...) without needing to create a fake TC and pass through multiple functions.
	 *
	 * @param reset indicates whether each Statistic should be reset. Simulates the argument contained in the TC[4,1]
	 * that calls reportParameterStatistics(Message& request)
	 */
	void reportParameterStatistics(bool reset);

	/**
	 * Constructs and stores a TM[4,2] packet containing the parameter statistics report.
	 */
	void parameterStatisticsReport();

	/**
	 * TC[4,3] reset parameter statistics, clearing all samples and values. This is the function called by TC from
	 * the GS.
	 */
	void resetParameterStatistics(Message& request);

	/**
	 * This function clears all the samples.
	 */
	void resetParameterStatistics();

	/**
	 * TC[4,4] enable periodic parameter statistics reporting
	 */
	void enablePeriodicStatisticsReporting(Message& request);

	/**
	 * TC[4,5] disable periodic parameter statistics reporting
	 */
	void disablePeriodicStatisticsReporting(Message& request);

	/**
	 * TC[4,6] add or update parameter statistics definitions
	 */
	void addOrUpdateStatisticsDefinitions(Message& request);

	/**
	 * TC[4,7] delete parameter statistics definitions.
	 */
	void deleteStatisticsDefinitions(Message& request);

	/**
	 * TC[4,8] report the parameter statistics definitions, by calling statisticsDefinitionsReport()
	 */
	void reportStatisticsDefinitions(Message& request);
	/**
	 * Constructs and stores a TM[4,9] packet containing the parameter statistics definitions report.
	 */
	void statisticsDefinitionsReport();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_PARAMETERSTATISTICSSERVICE_IMPL_H */
