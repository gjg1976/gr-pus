/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 
#include <gnuradio/pus/Helpers/EventAction.h>

namespace gr {
 namespace pus {
    EventAction::EventActionDefinition::EventActionDefinition(uint16_t applicationID, uint16_t eventDefinitionID, 
    		MessageArray message, bool enabled)
       : applicationID(applicationID), eventDefinitionID(eventDefinitionID), enabled(enabled)
    {
    	message[0] = (message[0] & 0xF8) |((applicationID >> 8U) & 0x07);
	message[1] = applicationID & 0xffU;
	request.setMessageData(message);
    }

    EventAction* EventAction::inst_eventaction = NULL;
    
    EventAction::EventAction() 
    {
    }
    
    EventAction* EventAction::getInstance()
    {
       if(inst_eventaction == NULL)
           inst_eventaction = new EventAction();
       
       return inst_eventaction;
    }
    
    Message& EventAction::executeAction(uint16_t eventDefinitionID) {
	// Custom function
	if (eventActionFunctionStatus) {
		auto range = eventActionDefinitionMap.equal_range(eventDefinitionID);
		for (auto& element = range.first; element != range.second; ++element) {
			if (element->second.enabled) {
				return element->second.request;
			}
		}
	} 

	return none_message;
    }

    bool EventAction::initializeEventAction(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;
            bool eventActionEnabled = json["enabled"];
            setEventActionFunctionStatus(eventActionEnabled);
            for (auto& elem : json["events"]){
                size_t pos = 0;
                
                uint16_t apid = elem["apid"];
                uint16_t eventid = elem["id"];
                bool eventEnabled = elem["enabled"];
                std::string data = elem["data"];
                std::string separator = ",";
                std::string token;

                MessageArray action_definition;
               
                while((pos = data.find(separator)) != std::string::npos){
                	token = data.substr(0, pos);
                	data.erase(0, pos + separator.length());
                	action_definition.push_back(std::stoul(token, nullptr, 16));	
                }

                EventActionDefinition temporaryEventActionDefinition(apid, eventid, action_definition, eventEnabled);
                eventActionDefinitionMap.insert(std::make_pair(eventid, temporaryEventActionDefinition));
            }
        } else {
            return false;
        }
        file.close();
        return true;
    }

  } /* namespace pus */
} /* namespace gr */


