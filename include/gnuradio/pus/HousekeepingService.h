/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_HOUSEKEEPINGSERVICE_H
#define INCLUDED_PUS_HOUSEKEEPINGSERVICE_H

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
    class PUS_API HousekeepingService : virtual public gr::pus::Service
    {
     public:

	inline static const uint8_t ServiceType = 3;

	enum MessageType : uint8_t {
		CreateHousekeepingReportStructure = 1,
		DeleteHousekeepingReportStructure = 3,
		EnablePeriodicHousekeepingParametersReport = 5,
		DisablePeriodicHousekeepingParametersReport = 6,
		ReportHousekeepingStructures = 9,
		HousekeepingStructuresReport = 10,
		HousekeepingParametersReport = 25,
		GenerateOneShotHousekeepingReport = 27,
		AppendParametersToHousekeepingStructure = 29,
		ModifyCollectionIntervalOfStructures = 31,
		ReportHousekeepingPeriodicProperties = 33,
		HousekeepingPeriodicPropertiesReport = 35,
		end = 36
	};
	uint8_t All[12] = {
		CreateHousekeepingReportStructure,
		DeleteHousekeepingReportStructure,
		EnablePeriodicHousekeepingParametersReport,
		DisablePeriodicHousekeepingParametersReport,
		ReportHousekeepingStructures,
		HousekeepingStructuresReport,
		HousekeepingParametersReport,
		GenerateOneShotHousekeepingReport,
		AppendParametersToHousekeepingStructure,
		ModifyCollectionIntervalOfStructures,
		ReportHousekeepingPeriodicProperties,
		HousekeepingPeriodicPropertiesReport
	 }; 
      typedef std::shared_ptr<HousekeepingService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::HousekeepingService.
       *
       * To avoid accidental use of raw pointers, pus::HousekeepingService's
       * constructor is in a private implementation
       * class. pus::HousekeepingService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_HOUSEKEEPINGSERVICE_H */
