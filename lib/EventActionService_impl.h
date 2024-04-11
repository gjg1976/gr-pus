/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_EVENTACTIONSERVICE_IMPL_H
#define INCLUDED_PUS_EVENTACTIONSERVICE_IMPL_H

#include <gnuradio/pus/EventActionService.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <nlohmann/json.hpp>
#include <fstream>
#include "etl/multimap.h"
#include "etl/vector.h"

#define EVENT_ACTION_NUM_EVENTS_SIZE	1
#define EVENT_ACTION_APID_SIZE	2
#define EVENT_ACTION_EVENT_ID_SIZE	2

namespace gr {
  namespace pus {

    class EventActionService_impl : public EventActionService
    {
     private:
      uint16_t counters[EventActionService::MessageType::end];


	/**
	 * Event-action function status
	 */
	bool eventActionFunctionStatus = false;	    
	
	void parse_json(const std::string& filename);  
   
	bool addEventActionDefinitionsSizeVerification(Message& request);
	
     public:
      EventActionService_impl(const std::string& init_file);
      ~EventActionService_impl();

	struct EventActionDefinition {
		uint16_t applicationID = 0;
		inline static const uint16_t MaxDefinitionID = 65535;
		uint16_t eventDefinitionID = MaxDefinitionID;
		Message request;
		bool enabled = false;

		EventActionDefinition(uint16_t applicationID, uint16_t eventDefinitionID, MessageArray message, bool enabled);
	};

	etl::multimap<uint16_t, EventActionDefinition, ECSSEventActionStructMapSize>
	    eventActionDefinitionMap;

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
        void handle_msg(pmt::pmt_t pdu);
      
        void handle_rid(pmt::pmt_t pdu);  
	/**
	 * TC[19,1] add event-action definitions
	 */
	void addEventActionDefinitions(Message& message);

	/**
	 * TC[19,2] delete event-action definitions
	 */
	void deleteEventActionDefinitions(Message& message);

	/**
	 * TC[19,3] delete all event-action definitions
	 */
	void deleteAllEventActionDefinitions(Message& message);

	/**
	 * TC[19,4] enable event-action definitions
	 */
	void enableEventActionDefinitions(Message& message);

	/**
	 * TC[19,5] disable event-action definitions
	 */
	void disableEventActionDefinitions(Message& message);

	/**
	 * TC[19,6] report the status of each event-action definition
	 */
	void requestEventActionDefinitionStatus(Message& message);

	/**
	 * TM[19,7] event-action status report
	 */
	void eventActionStatusReport();

	/**
	 * TC[19,8] enable the event-action function
	 */
	void enableEventActionFunction(Message& message);

	/**
	 * TC[19,9] disable the event-action function
	 */
	void disableEventActionFunction(Message& message);

	/**
	 * TC[19,10] report the event-action definition
	 */
	void reportEventActionDefinitions(Message& message);

	/**
	 * Setter for event-action function status
	 */
	void setEventActionFunctionStatus(bool status) {
		eventActionFunctionStatus = status;
	}

	/**
	 * Getter for event-action function status
	 * @return eventActionFunctionStatus
	 */
	bool getEventActionFunctionStatus() const {
		return getEventActionFunctionStatus();
	}
	/**
	 * Custom function that is called right after an event takes place, to initiate
	 * the execution of the action
	 */
	void executeAction(uint16_t eventDefinitionID);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_EVENTACTIONSERVICE_IMPL_H */
