/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_REALTIMEFORWARDINGCONTROLSERVICE_H
#define INCLUDED_PUS_REALTIMEFORWARDINGCONTROLSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"
#include <nlohmann/json.hpp>
#include <fstream>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API RealTimeForwardingControlService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 14;

	enum MessageType : uint8_t {
		AddReportTypesToAppProcessConfiguration = 1,
		DeleteReportTypesFromAppProcessConfiguration = 2,
		ReportEnabledTelemetrySourcePackets = 3,
		EnabledTelemetrySourcePacketsReport = 4,
		EventReportConfigurationContentReport = 16,
		end = 17
	};	

	uint8_t All[5] = {
		AddReportTypesToAppProcessConfiguration,
		DeleteReportTypesFromAppProcessConfiguration,
		ReportEnabledTelemetrySourcePackets,
		EnabledTelemetrySourcePacketsReport,
		EventReportConfigurationContentReport
	 };
      typedef std::shared_ptr<RealTimeForwardingControlService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::RealTimeForwardingControlService.
       *
       * To avoid accidental use of raw pointers, pus::RealTimeForwardingControlService's
       * constructor is in a private implementation
       * class. pus::RealTimeForwardingControlService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_REALTIMEFORWARDINGCONTROLSERVICE_H */
