/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_EVENTREPORTSERVICE_IMPL_H
#define INCLUDED_PUS_EVENTREPORTSERVICE_IMPL_H

#include <gnuradio/pus/EventReportService.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"

#define EVENTS_NUM_EVENTS_SIZE  2
#define EVENTS_ID_SIZE  2

namespace gr {
  namespace pus {

    class EventReportService_impl : public EventReportService
    {
     private:
        uint16_t counters[EventReportService::MessageType::end];
      
	// Variables that count the event reports per severity level
	uint16_t lowSeverityReportCount = 0;
	uint16_t mediumSeverityReportCount = 0;
	uint16_t highSeverityReportCount = 0;

	// Variables that count the event occurences per severity level
	uint16_t lowSeverityEventCount = 0;
	uint16_t mediumSeverityEventCount = 0;
	uint16_t highSeverityEventCount = 0;

	uint16_t disabledEventsCount = 0;

	uint16_t lastLowSeverityReportID = 65535;
	uint16_t lastMediumSeverityReportID = 65535;
	uint16_t lastHighSeverityReportID = 65535;

	static const uint16_t numberOfEvents = 7;
	std::bitset<numberOfEvents> stateOfEvents;
	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);
      
      void handle_rid(pmt::pmt_t pdu);

	
	void parse_json(const std::string& filename);   
	      	
     public:
      EventReportService_impl(const std::string& init_file);
      ~EventReportService_impl();


      
	/**
	 * TM[5,1] informative event report
	 * Send report to inform the respective recipients about an event
	 *
	 * Note: The parameters are defined by the standard
	 *
	 * @param eventID event definition ID
	 * @param data the data of the report
	 */
	void informativeEventReport(Event eventID, MessageArray& data);

	/**
	 * TM[5,2] low severiity anomaly report
	 * Send report when there is an anomaly event of low severity to the respective recipients
	 *
	 * Note: The parameters are defined by the standard
	 *
	 * @param eventID event definition ID
	 * @param data the data of the report
	 */
	void lowSeverityAnomalyReport(Event eventID, MessageArray& data);

	/**
	 * TM[5,3] medium severity anomaly report
	 * Send report when there is an anomaly event of medium severity to the respective recipients
	 *
	 * Note: The parameters are defined by the standard
	 *
	 * @param eventID event definition ID
	 * @param data the data of the report
	 */
	void mediumSeverityAnomalyReport(Event eventID, MessageArray& data);

	/**
	 * TM[5,4] high severity anomaly report
	 * Send report when there is an anomaly event of high severity to the respective recipients
	 *
	 * Note: The parameters are defined by the standard
	 *
	 * @param eventID event definition ID
	 * @param data the data of the report
	 */
	void highSeverityAnomalyReport(Event eventID, MessageArray& data);

	/**
	 * TC[5,5] request to enable report generation
	 * Telecommand to enable the report generation of event definitions
	 */
	void enableReportGeneration(Message message);

	/**
	 * TC[5,6] request to disable report generation
	 * Telecommand to disable the report generation of event definitions
	 * @param message
	 */
	void disableReportGeneration(Message message);
	/**
	 * TC[5,7] request to report the disabled event definitions
	 * Note: No arguments, according to the standard.
	 * @param message
	 */
	void requestListOfDisabledEvents(Message message);

	/**
	 * TM[5,8] disabled event definitions report
	 * Telemetry package of a report of the disabled event definitions
	 */
	void listOfDisabledEventsReport();
	
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_EVENTREPORTSERVICE_IMPL_H */
