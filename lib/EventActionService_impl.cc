/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "EventActionService_impl.h"
#include <gnuradio/pus/EventReportService.h>
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    EventActionService_impl::EventActionDefinition::EventActionDefinition(uint16_t applicationID, uint16_t eventDefinitionID, 
    		MessageArray message, bool enabled)
       : applicationID(applicationID), eventDefinitionID(eventDefinitionID), enabled(enabled)
    {
  
    	message[0] = (message[0] & 0xF8) |((applicationID >> 8U) & 0x07);
	message[1] = applicationID & 0xffU;
	request.setMessageData(message);
    }

    EventActionService::sptr
    EventActionService::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<EventActionService_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    EventActionService_impl::EventActionService_impl(const std::string& init_file)
      : gr::block("EventActionService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        
        serviceType = ServiceType;
        for(size_t i = 0; i < EventActionService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_in(PMT_RID);
        set_msg_handler(PMT_RID,
                    [this](pmt::pmt_t msg) { this->handle_rid(msg); });                    
                    
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);
        message_port_register_out(PMT_ACTION);
        
        parse_json(init_file);

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
    }

    /*
     * Our virtual destructor.
     */
    EventActionService_impl::~EventActionService_impl()
    {
    }
    
    void EventActionService_impl::parse_json(const std::string& filename)
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
		 token = data.substr(0, pos);
                data.erase(0, pos + separator.length());
                action_definition.push_back(std::stoul(token, nullptr, 16));	

                EventActionDefinition temporaryEventActionDefinition(apid, eventid, action_definition, eventEnabled);
                eventActionDefinitionMap.insert(std::make_pair(eventid, temporaryEventActionDefinition));
 			            
            }
        } else {
            return ;
        }
        file.close();
    }
    
    void EventActionService_impl::handle_rid(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);


        if (!pmt::dict_has_key(meta, PMT_EVENT)){
#ifdef _PUS_DEBUG
            	GR_LOG_WARN(d_logger, "No EVENT metadata found");
#endif
		return;
	}else if(!pmt::is_integer(pmt::dict_ref(meta, PMT_EVENT, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
            	GR_LOG_WARN(d_logger, "No valid EVENT metadata found");
#endif
		return;	
	}

        // extract data
        if (pmt::is_u8vector(v_data)) {
                std::vector<uint8_t> in_data = pmt::u8vector_elements(v_data);
                if(in_data.size() < 2){
                	GR_LOG_WARN(d_logger, "Error: the input data size is invalid");
                	return;	
                }
                uint16_t ridLevel = (uint16_t) pmt::to_long(pmt::dict_ref(meta, PMT_EVENT, pmt::PMT_NIL));  
                
                uint16_t eventID = (in_data[0] << 8) | in_data[1];


                switch(ridLevel){
                	case EventReportService::Event::InformativeUnknownEvent:
 				break;      
                	case EventReportService::Event::LowSeverityUnknownEvent:
 				executeAction(eventID);
                		break;                      	
                	case EventReportService::Event::MediumSeverityUnknownEvent:
 				executeAction(eventID);
                 		break;  
                	case EventReportService::Event::HighSeverityUnknownEvent:
 				executeAction(eventID);
                		break;                	
                       default:
			   	d_error_handler->reportInternalError(ErrorHandler::EventReportTypeUnknown);
                }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }
    void EventActionService_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);

        // extract data
        if (pmt::is_u8vector(v_data)) {
                std::vector<uint8_t> inData = pmt::u8vector_elements(v_data);

                MessageArray in_data(inData.data(), inData.data() + inData.size());                
                Message message  = d_message_parser->ParseMessageCommand(in_data);
                if(serviceType == message.getMessageServiceType()){
                    switch (message.getMessageType()) {
                        case AddEventAction:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AddEventAction");
#endif
                           addEventActionDefinitions(message);
                           break;
                        case DeleteEventAction:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeleteEventAction");
#endif
                           deleteEventActionDefinitions(message);
                           break;                                             
                        case DeleteAllEventAction:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "DeleteAllEventAction");
#endif
                           deleteAllEventActionDefinitions(message);
                           break;
                        case EnableEventAction:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "EnableEventAction");
#endif
                           enableEventActionDefinitions(message);
                           break;
                        case DisableEventAction:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "DisableEventAction");
#endif
                           disableEventActionDefinitions(message); 
                           break;
                        case ReportStatusOfEachEventAction:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "ReportStatusOfEachEventAction");
#endif
                           requestEventActionDefinitionStatus(message);
                           break;
                        case EnableEventActionFunction:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "EnableEventActionFunction");
#endif
                           enableEventActionFunction(message);
                           break;
                        case DisableEventActionFunction:  
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "DisableEventActionFunction");
#endif
                           disableEventActionFunction(message);
                           break;
                        case ReportEventActionDefinitions:  
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "ReportEventActionDefinitions");
#endif
                           reportEventActionDefinitions(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Event Action Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Event Action Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    bool EventActionService_impl::addEventActionDefinitionsSizeVerification(Message& request) {  
 	uint16_t currentPosition = request.getMessageReadPosition();
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < EVENT_ACTION_NUM_EVENTS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return false;
	}
	uint8_t numOfEventActions = request.readUint8();
	
	tcSize -= EVENT_ACTION_NUM_EVENTS_SIZE;

	for(uint16_t i = 0; i < numOfEventActions; i++){
		if(tcSize < (EVENT_ACTION_APID_SIZE + EVENT_ACTION_EVENT_ID_SIZE + 
				CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize)){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return false;
		}	
		request.readUint16();
		request.readUint16();	
		
		MessageArray action_definition = d_message_parser->parseTCfromMessage(request);
		if(tcSize < action_definition.size()){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return false;
		}
		tcSize -= (EVENT_ACTION_APID_SIZE + EVENT_ACTION_EVENT_ID_SIZE + action_definition.size());

	}	
		
 	if(tcSize > 0){     
		reportAcceptanceError(request,ErrorHandler::InvalidLength);	
		return false;
	}

	request.setMessageReadPosition(currentPosition);	
	return true;    
    }         
/****************************************************************************************************************/    
    void EventActionService_impl::addEventActionDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::AddEventAction)) {
		return;
	}
	if(!addEventActionDefinitionsSizeVerification(request))
		return;
		
	reportSuccessAcceptanceVerification(request);

	uint8_t numberOfEventActionDefinitions = request.readUint8();

	bool bFaultStartExecution = false;
		
	while (numberOfEventActionDefinitions-- != 0) {
		bool bAddAction = true;
		uint16_t applicationID = request.readUint16();
		
		uint16_t eventDefinitionID = request.readUint16();

		for (auto& element: eventActionDefinitionMap) {
			if (element.first == eventDefinitionID) {
				if (element.second.enabled) {
					reportExecutionStartError(request, ErrorHandler::EventActionEnabledError);
					bFaultStartExecution = true;
					bAddAction = false;
				} else{
					eventActionDefinitionMap.erase(eventDefinitionID);
				}
				break;
			}
		}
		if (eventActionDefinitionMap.size() == ECSSEventActionStructMapSize) {
				reportExecutionStartError(request, ErrorHandler::EventActionDefinitionsMapIsFull);
				bFaultStartExecution = true;
				bAddAction = false;
		}
		MessageArray action_definition = d_message_parser->parseTCfromMessage(request);

		if(bAddAction){
			EventActionDefinition temporaryEventActionDefinition(applicationID, 
								eventDefinitionID, action_definition, false);
			eventActionDefinitionMap.insert(std::make_pair(eventDefinitionID, temporaryEventActionDefinition));
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void EventActionService_impl::deleteEventActionDefinitions(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::DeleteEventAction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < EVENT_ACTION_NUM_EVENTS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}
	
 	tcSize -= EVENT_ACTION_NUM_EVENTS_SIZE;   
	
	uint8_t numberOfEventActionDefinitions = request.readUint8();

 	if(tcSize != numberOfEventActionDefinitions * (EVENT_ACTION_APID_SIZE + EVENT_ACTION_EVENT_ID_SIZE)){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);			
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;

	while (numberOfEventActionDefinitions-- != 0) {
		uint16_t applicationID = request.readUint16();
		uint16_t eventDefinitionID = request.readUint16();
		
		bool actionDefinitionExists = false;

		for (auto& element: eventActionDefinitionMap) {
			if (element.first == eventDefinitionID) {
				actionDefinitionExists = true;
				if (element.second.applicationID != applicationID) {
					reportExecutionStartError(request, ErrorHandler::EventActionUnknownEventActionDefinitionError);
					bFaultStartExecution = true;
				} else if (element.second.enabled) {
					reportExecutionStartError(request, ErrorHandler::EventActionDeleteEnabledDefinitionError);
					bFaultStartExecution = true;
				} else {
					eventActionDefinitionMap.erase(
							eventActionDefinitionMap.find(eventDefinitionID));
				}
				break;
			}
		}
		if (not actionDefinitionExists) {
			reportExecutionStartError(request, ErrorHandler::EventActionUnknownEventActionDefinitionError);
			bFaultStartExecution = true;
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void EventActionService_impl::deleteAllEventActionDefinitions(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::DeleteAllEventAction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize > 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}

	reportSuccessAcceptanceVerification(request);	
		
	reportSuccessStartExecutionVerification(request);
		
	setEventActionFunctionStatus(false);
	
	eventActionDefinitionMap.clear();

	reportSuccessCompletionExecutionVerification(request);
    }

    void EventActionService_impl::enableEventActionDefinitions(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::EnableEventAction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < EVENT_ACTION_NUM_EVENTS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}
	
 	tcSize -= EVENT_ACTION_NUM_EVENTS_SIZE;   
	
	uint8_t numberOfEventActionDefinitions = request.readUint8();

 	if(tcSize != numberOfEventActionDefinitions * (EVENT_ACTION_APID_SIZE + EVENT_ACTION_EVENT_ID_SIZE)){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);			
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	bool bFaultStartExecution = false;

	if (numberOfEventActionDefinitions != 0U) {
		while (numberOfEventActionDefinitions-- != 0) {
			uint16_t applicationID = request.readUint16();
			uint16_t eventDefinitionID = request.readUint16();

			bool actionDefinitionExists = false;
			
			for (auto& element: eventActionDefinitionMap) {
				if (element.first == eventDefinitionID) {
					actionDefinitionExists = true;
					if (element.second.applicationID != applicationID) {
						reportExecutionStartError(request, 
							ErrorHandler::EventActionUnknownEventActionDefinitionError);
						bFaultStartExecution = true;
					} else {
						element.second.enabled = true;
					}
					break;
				}
			}
			if (not actionDefinitionExists) {
				reportExecutionStartError(request, 
					ErrorHandler::EventActionUnknownEventActionDefinitionError);
				bFaultStartExecution = true;
			}
		}
	} else {
		for (auto& element: eventActionDefinitionMap) {
			element.second.enabled = true;
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void EventActionService_impl::disableEventActionDefinitions(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::DisableEventAction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < EVENT_ACTION_NUM_EVENTS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}
	
 	tcSize -= EVENT_ACTION_NUM_EVENTS_SIZE;   
	
	uint8_t numberOfEventActionDefinitions = request.readUint8();

 	if(tcSize != numberOfEventActionDefinitions * (EVENT_ACTION_APID_SIZE + EVENT_ACTION_EVENT_ID_SIZE)){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);			
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;

	if (numberOfEventActionDefinitions != 0U) {

		while (numberOfEventActionDefinitions-- != 0) {
			uint16_t applicationID = request.readUint16();
			uint16_t eventDefinitionID = request.readUint16();

			bool actionDefinitionExists = false;

			for (auto& element: eventActionDefinitionMap) {
				if (element.first == eventDefinitionID) {
					actionDefinitionExists = true;
					if (element.second.applicationID != applicationID) {
						reportExecutionStartError(request, 
							ErrorHandler::EventActionUnknownEventActionDefinitionError);
						bFaultStartExecution = true;
					} else {
						element.second.enabled = false;
					}
					break;
				}
			}
			if (not actionDefinitionExists) {
				reportExecutionStartError(request, 
					ErrorHandler::EventActionUnknownEventActionDefinitionError);
				bFaultStartExecution = true;
			}
		}
	} else {
		for (auto& element: eventActionDefinitionMap) {
			element.second.enabled = false;
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void EventActionService_impl::requestEventActionDefinitionStatus(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::ReportStatusOfEachEventAction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize > 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}

	reportSuccessAcceptanceVerification(request);	
		
	reportSuccessStartExecutionVerification(request);
	
	eventActionStatusReport();

	reportSuccessCompletionExecutionVerification(request);
    }

    void EventActionService_impl::eventActionStatusReport() {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			EventActionService::MessageType::EventActionStatusReport, 
			counters[EventActionService::MessageType::EventActionStatusReport], 0);

	uint16_t count = eventActionDefinitionMap.size();
        report.appendUint16(count);
	for (const auto& element:  eventActionDefinitionMap) {
		report.appendUint16(element.second.applicationID);
		report.appendUint16(element.second.eventDefinitionID);
		report.appendBoolean(element.second.enabled);                		
	}
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

	counters[EventActionService::MessageType::EventActionStatusReport]++;
    }

    void EventActionService_impl::enableEventActionFunction(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::EnableEventActionFunction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize > 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	
		
	reportSuccessStartExecutionVerification(request);
	
	setEventActionFunctionStatus(true);
	
	reportSuccessCompletionExecutionVerification(request);	
    }

    void EventActionService_impl::disableEventActionFunction(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::DisableEventActionFunction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize > 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	
		
	reportSuccessStartExecutionVerification(request);
	
	setEventActionFunctionStatus(false);
	
	reportSuccessCompletionExecutionVerification(request);	
    }

    void EventActionService_impl::reportEventActionDefinitions(Message& request) 
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			EventActionService::MessageType::ReportEventActionDefinitions)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < EVENT_ACTION_NUM_EVENTS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}
	
 	tcSize -= EVENT_ACTION_NUM_EVENTS_SIZE;   

	uint8_t numberOfEventActionDefinitions = request.readUint8();

 	if(tcSize != numberOfEventActionDefinitions * (EVENT_ACTION_APID_SIZE + EVENT_ACTION_EVENT_ID_SIZE)){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);			
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			EventActionService::MessageType::EventActionDefinitionsReport, 
			counters[EventActionService::MessageType::EventActionDefinitionsReport], 0);

	uint16_t currentPosition = request.getMessageReadPosition();
	
	uint8_t numberOfValidEvents = 0;
	for (uint8_t i = 0; i < numberOfEventActionDefinitions; i++) {
		uint16_t applicationID = request.readUint16();
		uint16_t eventDefinitionID = request.readUint16();

		for (auto& element: eventActionDefinitionMap) {
			if (element.first == eventDefinitionID) {
				if (element.second.applicationID == applicationID) {
					numberOfValidEvents++;
				}
				break;
			}
		}
	}
	
	report.appendUint8(numberOfValidEvents);   	
	
	request.setMessageReadPosition(currentPosition);

	bool bFaultStartExecution = false;
		
	while (numberOfEventActionDefinitions-- != 0) {
		uint16_t applicationID = request.readUint16();
		uint16_t eventDefinitionID = request.readUint16();

		bool actionDefinitionExists = false;
		
		for (auto& element: eventActionDefinitionMap) {
			if (element.first == eventDefinitionID) {
				actionDefinitionExists = true;
				if (element.second.applicationID != applicationID) {
					reportExecutionStartError(request, ErrorHandler::EventActionUnknownEventActionDefinitionError);
					bFaultStartExecution = true;
				}else{
					report.appendUint16(element.second.applicationID);
					report.appendUint16(element.second.eventDefinitionID);
					report.appendBoolean(element.second.enabled);  
					report.appendUint8Array(element.second.request.getMessageData());
				}
				break; 							

			}
		}
		if (not actionDefinitionExists) {
			reportExecutionStartError(request, ErrorHandler::EventActionUnknownEventActionDefinitionError);
			bFaultStartExecution = true;
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[EventActionService::MessageType::EventActionDefinitionsReport]++;

	reportSuccessCompletionExecutionVerification(request);
    }
    
    void EventActionService_impl::executeAction(uint16_t eventDefinitionID) 
    {
	// Custom function
	if (eventActionFunctionStatus) {
		auto range = eventActionDefinitionMap.equal_range(eventDefinitionID);
		for (auto& element = range.first; element != range.second; ++element) {
			if (element->second.enabled) {
				Message message(element->second.request);
				message_port_pub(PMT_ACTION, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));
			}
		}
	}
    }

  } /* namespace pus */
} /* namespace gr */
