/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_ONBOARDMONITORINGSERVICE_H
#define INCLUDED_PUS_ONBOARDMONITORINGSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API OnBoardMonitoringService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 12;
	enum MessageType : uint8_t {
		EnableParameterMonitoringDefinitions = 1,
		DisableParameterMonitoringDefinitions = 2,
		ChangeMaximumTransitionReportingDelay = 3,
		DeleteAllParameterMonitoringDefinitions = 4,
		AddParameterMonitoringDefinitions = 5,
		DeleteParameterMonitoringDefinitions = 6,
		ModifyParameterMonitoringDefinitions = 7,
		ReportParameterMonitoringDefinitions = 8,
		ParameterMonitoringDefinitionReport = 9,
		ReportOutOfLimits = 10,
		OutOfLimitsReport = 11,
		CheckTransitionReport = 12,
		ReportStatusOfParameterMonitoringDefinition = 13,
		ParameterMonitoringDefinitionStatusReport = 14,
		EnableParameterMonitoringFunction = 15,
		DisableParameterMonitoringFunction = 16,		
		end = 17
	};

	uint8_t All[16] = {
		EnableParameterMonitoringDefinitions,
		DisableParameterMonitoringDefinitions,
		ChangeMaximumTransitionReportingDelay,
		DeleteAllParameterMonitoringDefinitions,
		AddParameterMonitoringDefinitions,
		DeleteParameterMonitoringDefinitions,
		ModifyParameterMonitoringDefinitions,
		ReportParameterMonitoringDefinitions,
		ParameterMonitoringDefinitionReport,
		ReportOutOfLimits,
		OutOfLimitsReport,
		CheckTransitionReport,
		ReportStatusOfParameterMonitoringDefinition,
		ParameterMonitoringDefinitionStatusReport,
		EnableParameterMonitoringDefinitions,
		DisableParameterMonitoringDefinitions
	 };     

      typedef std::shared_ptr<OnBoardMonitoringService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::OnBoardMonitoringService.
       *
       * To avoid accidental use of raw pointers, pus::OnBoardMonitoringService's
       * constructor is in a private implementation
       * class. pus::OnBoardMonitoringService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_ONBOARDMONITORINGSERVICE_H */
