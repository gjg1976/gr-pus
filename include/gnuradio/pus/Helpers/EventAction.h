/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_EVENTACTION_H
#define ECSS_EVENTACTION_H

#include <gnuradio/pus/Helpers/MessageParser.h>
#include <nlohmann/json.hpp>
#include <fstream>

/**
 * Implementation of ST[19] event-action Service
 *
 * ECSS 8.19 && 6.19
 *
 * @ingroup Services
 *
 * @note The application ID was decided to be abolished as an identifier of the event-action
 * definition
 * @attention Every event action definition ID should be different, regardless of the application ID
 */
namespace gr {
 namespace pus {
   class EventAction {

     private:
      static EventAction* inst_eventaction;
      
      EventAction();
      EventAction(const EventAction&);
      
      EventAction& operator=(const EventAction&);
	/**
	 * Event-action function status
	 */
	bool eventActionFunctionStatus = false;
	
        Message none_message = Message();
        
    public:

        static EventAction* getInstance();

	struct EventActionDefinition {
		uint16_t applicationID = 0;
		inline static const uint16_t MaxDefinitionID = 65535;
		uint16_t eventDefinitionID = MaxDefinitionID;
		Message request;
		bool enabled = false;

		EventActionDefinition(uint16_t applicationID, uint16_t eventDefinitionID, MessageArray message, bool enabled);
	};

	std::multimap<uint16_t, EventActionDefinition>
	    eventActionDefinitionMap;

	bool initializeEventAction(const std::string& filename);
	
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
		return eventActionFunctionStatus;
	}

	/**
	 * Custom function that is called right after an event takes place, to initiate
	 * the execution of the action
	 */
	Message& executeAction(uint16_t eventDefinitionID);

   };
  } /* namespace pus */
} /* namespace gr */  

#endif // ECSS_SERVICES_EVENTACTIONSERVICE_HPP
