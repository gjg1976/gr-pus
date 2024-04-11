/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_EVENTREPORTSERVICE_H
#define INCLUDED_PUS_EVENTREPORTSERVICE_H

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
    class PUS_API EventReportService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {

	
     public:
	inline static const uint8_t ServiceType = 5;

	enum MessageType : uint8_t {
		InformativeEventReport = 1,
		LowSeverityAnomalyReport = 2,
		MediumSeverityAnomalyReport = 3,
		HighSeverityAnomalyReport = 4,
		EnableReportGenerationOfEvents = 5,
		DisableReportGenerationOfEvents = 6,
		ReportListOfDisabledEvents = 7,
		DisabledListEventReport = 8,
		end = 9
	};
	uint8_t All[8] = {
		InformativeEventReport,
		LowSeverityAnomalyReport,
		MediumSeverityAnomalyReport,
		HighSeverityAnomalyReport,
		EnableReportGenerationOfEvents,
		DisableReportGenerationOfEvents,
		ReportListOfDisabledEvents,
		DisabledListEventReport
	 }; 	

	/**
	 * Type of the information event
	 *
	 * Note: Numbers are kept in code explicitly, so that there is no uncertainty when something
	 * changes.
	 */
	enum Event {
		/**
		 * An unknown event occured
		 */
		InformativeUnknownEvent = 0,
		/**
		 * Watchdogs have reset
		 */
		WWDGReset = 1,
		/**
		 * Assertion has failed
		 */
		AssertionFail = 2,
		/**
		 * Microcontroller has started
		 */
		MCUStart = 3,
		/**
		 * An unknown anomaly of low severity anomalyhas occurred
		 */
		LowSeverityUnknownEvent = 4,
		/**
		 * An unknown anomaly of medium severity has occurred
		 */
		MediumSeverityUnknownEvent = 5,
		/**
		 * An unknown anomaly of high severity has occurred
		 */
		HighSeverityUnknownEvent = 6,
		/**
		 * When an execution of a notification/event fails to start
		 */
		FailedStartOfExecution = 7
	};

      typedef std::shared_ptr<EventReportService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::EventReportService.
       *
       * To avoid accidental use of raw pointers, pus::EventReportService's
       * constructor is in a private implementation
       * class. pus::EventReportService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_EVENTREPORTSERVICE_H */
