/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_PARAMETERSTATISTICSSERVICE_H
#define INCLUDED_PUS_PARAMETERSTATISTICSSERVICE_H

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
    class PUS_API ParameterStatisticsService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
     	inline static const uint8_t ServiceType = 4;

	enum MessageType : uint8_t {
		ReportParameterStatistics = 1,
		ParameterStatisticsReport = 2,
		ResetParameterStatistics = 3,
		EnablePeriodicParameterReporting = 4,
		DisablePeriodicParameterReporting = 5,
		AddOrUpdateParameterStatisticsDefinitions = 6,
		DeleteParameterStatisticsDefinitions = 7,
		ReportParameterStatisticsDefinitions = 8,
		ParameterStatisticsDefinitionsReport = 9,
		end = 10
	};
	
	uint8_t All[9] = {
		ReportParameterStatistics,
		ParameterStatisticsReport,
		ResetParameterStatistics,
		EnablePeriodicParameterReporting,
		DisablePeriodicParameterReporting,
		AddOrUpdateParameterStatisticsDefinitions,
		DeleteParameterStatisticsDefinitions,
		ReportParameterStatisticsDefinitions,
		ParameterStatisticsDefinitionsReport
	 };     
	 
      typedef std::shared_ptr<ParameterStatisticsService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::ParameterStatisticsService.
       *
       * To avoid accidental use of raw pointers, pus::ParameterStatisticsService's
       * constructor is in a private implementation
       * class. pus::ParameterStatisticsService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_PARAMETERSTATISTICSSERVICE_H */
