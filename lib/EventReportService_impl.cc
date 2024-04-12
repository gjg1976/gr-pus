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
#include "EventReportService_impl.h"
#include <gnuradio/pus/Helpers/EventAction.h>
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    EventReportService::sptr
    EventReportService::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<EventReportService_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    EventReportService_impl::EventReportService_impl(const std::string& init_file)
      : gr::block("EventReportService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        
        stateOfEvents.set();
        		
        serviceType = ServiceType;
        for(size_t i = 0; i < EventReportService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_in(PMT_RID);
        set_msg_handler(PMT_RID,
                    [this](pmt::pmt_t msg) { this->handle_rid(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);

        parse_json(init_file);
 
        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
    }

    /*
     * Our virtual destructor.
     */
    EventReportService_impl::~EventReportService_impl()
    {
    }

    void EventReportService_impl::parse_json(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;
            for (auto& elem : json["events"]){
             	 uint16_t enum16 = elem["id"];
             	 bool enabled = elem["enabled"];
                 if(enabled)
			stateOfEvents[enum16] = true;
		 else
			stateOfEvents[enum16] = false;
            }
        } else {
            GR_LOG_WARN(d_logger, "No event report init file found");
        }
        file.close();
    }  
    
    void EventReportService_impl::handle_rid(pmt::pmt_t pdu)
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
                std::vector<uint8_t> inData = pmt::u8vector_elements(v_data);

                MessageArray in_data(inData.data(), inData.data() + inData.size()); 
                if(in_data.size() < 2){
                	 GR_LOG_WARN(d_logger, "Error: input data size smaller than expected one");
                	return;
                }
                uint16_t ridLevel = (uint16_t) pmt::to_long(pmt::dict_ref(meta, PMT_EVENT, pmt::PMT_NIL));  

                switch(ridLevel){
                	case Event::InformativeUnknownEvent:
 				informativeEventReport(Event::InformativeUnknownEvent, in_data);
                		break;      
                	case Event::LowSeverityUnknownEvent:
 				lowSeverityAnomalyReport(Event::LowSeverityUnknownEvent, in_data);
                		break;                      	
                	case Event::MediumSeverityUnknownEvent:
 				mediumSeverityAnomalyReport(Event::MediumSeverityUnknownEvent, in_data);
                 		break;  
                	case Event::HighSeverityUnknownEvent:
 				highSeverityAnomalyReport(Event::HighSeverityUnknownEvent, in_data);
                		break;                	
                        default:
			   d_error_handler->reportInternalError(ErrorHandler::EventReportTypeUnknown);
                }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    void EventReportService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case EnableReportGenerationOfEvents:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "EnableReportGenerationOfEvents");
#endif
                           enableReportGeneration(message);
                           break;
                        case DisableReportGenerationOfEvents:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "DisableReportGenerationOfEvents");
#endif
			    disableReportGeneration(message);
                           break;
                        case ReportListOfDisabledEvents:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "ReportListOfDisabledEvents");
#endif
                           requestListOfDisabledEvents(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Event Report Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);				   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Event Report Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }


    void EventReportService_impl::informativeEventReport(Event eventID, MessageArray& data) {
	// TM[5,1]
	if (stateOfEvents[static_cast<uint16_t>(eventID)]) {
        	Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			EventReportService::MessageType::InformativeEventReport, 
			counters[EventReportService::MessageType::InformativeEventReport], 0);

		report.appendUint8Array(data);

		d_message_parser->closeMessage(report);
			
		message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

		counters[EventReportService::MessageType::InformativeEventReport]++;
	}
    }

    void EventReportService_impl::lowSeverityAnomalyReport(Event eventID, MessageArray& data) {
	lowSeverityEventCount++;
	// TM[5,2]
	if (stateOfEvents[static_cast<uint16_t>(eventID)]) {
		lowSeverityReportCount++;

        	Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			EventReportService::MessageType::LowSeverityAnomalyReport, 
			counters[EventReportService::MessageType::LowSeverityAnomalyReport], 0);

		report.appendUint8Array(data);

		lastLowSeverityReportID = static_cast<uint16_t>(eventID);

		d_message_parser->closeMessage(report);
			
		message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

		counters[EventReportService::MessageType::LowSeverityAnomalyReport]++;
	}
    }

    void EventReportService_impl::mediumSeverityAnomalyReport(Event eventID, MessageArray& data) {
	mediumSeverityEventCount++;
	// TM[5,3]
	if (stateOfEvents[static_cast<uint16_t>(eventID)]) {
		mediumSeverityReportCount++;

        	Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			EventReportService::MessageType::MediumSeverityAnomalyReport, 
			counters[EventReportService::MessageType::MediumSeverityAnomalyReport], 0);

		report.appendUint8Array(data);
		
		lastMediumSeverityReportID = static_cast<uint16_t>(eventID);

		d_message_parser->closeMessage(report);
				
		message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
                				
		counters[EventReportService::MessageType::MediumSeverityAnomalyReport]++;
	}
    }

    void EventReportService_impl::highSeverityAnomalyReport(Event eventID, MessageArray& data) {
	highSeverityEventCount++;
	// TM[5,4]
	if (stateOfEvents[static_cast<uint16_t>(eventID)]) {
		highSeverityReportCount++;

        	Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			EventReportService::MessageType::HighSeverityAnomalyReport, 
			counters[EventReportService::MessageType::HighSeverityAnomalyReport], 0);

		report.appendUint8Array(data);
		
		lastHighSeverityReportID = static_cast<uint16_t>(eventID);

		d_message_parser->closeMessage(report);
				
		message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
                				
		counters[EventReportService::MessageType::HighSeverityAnomalyReport]++;
	}
    }
     
    void EventReportService_impl::enableReportGeneration(Message request) {
	// TC[5,5]
	if (!d_message_parser->assertTC(request, serviceType, 
			EventReportService::MessageType::EnableReportGenerationOfEvents)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < EVENTS_NUM_EVENTS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= EVENTS_NUM_EVENTS_SIZE;   

	uint16_t length = request.readUint16();

 	if(tcSize != length * EVENTS_ID_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;

	for (uint16_t i = 0; i < length; i++) {
		uint16_t enum16 = request.readEnum16();

		if (enum16 > numberOfEvents) {
			reportExecutionStartError(request, 
				ErrorHandler::InvalidEventSelection);	
			bFaultStartExecution = true;
			continue;	
		}
		stateOfEvents[enum16] = true;

	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
				
	disabledEventsCount = stateOfEvents.size() - stateOfEvents.count();
	
	reportSuccessCompletionExecutionVerification(request);
    }
     
    void EventReportService_impl::disableReportGeneration(Message request) {
	// TC[5,6]
	if (!d_message_parser->assertTC(request, serviceType, 
			EventReportService::MessageType::DisableReportGenerationOfEvents)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < EVENTS_NUM_EVENTS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= EVENTS_NUM_EVENTS_SIZE;   

	uint16_t length = request.readUint16();

 	if(tcSize != length * EVENTS_ID_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	bool bFaultStartExecution = false;

	for (uint16_t i = 0; i < length; i++) {
		uint16_t enum16 = request.readEnum16();

		if (enum16 > numberOfEvents) {
			reportExecutionStartError(request, 
				ErrorHandler::InvalidEventSelection);	
			bFaultStartExecution = true;
			continue;	
		}
		stateOfEvents[enum16] = false;

	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
	
	disabledEventsCount = stateOfEvents.size() - stateOfEvents.count();
	
	reportSuccessCompletionExecutionVerification(request);
    }

    void EventReportService_impl::requestListOfDisabledEvents(Message request) {
	// TC[5,7]
	if (!d_message_parser->assertTC(request, serviceType, 
			EventReportService::MessageType::ReportListOfDisabledEvents)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize > 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);
	
	reportSuccessStartExecutionVerification(request);
			
	listOfDisabledEventsReport();
	
	reportSuccessCompletionExecutionVerification(request);	
    }

    void EventReportService_impl::listOfDisabledEventsReport() {
	// TM[5,8]
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			EventReportService::MessageType::DisabledListEventReport, 
			counters[EventReportService::MessageType::DisabledListEventReport], 0);

	uint16_t numberOfDisabledEvents = stateOfEvents.size() - stateOfEvents.count();
	report.appendUint16(numberOfDisabledEvents);
	for (size_t i = 0; i < stateOfEvents.size(); i++) {
		if (not stateOfEvents[i]) {
			report.appendUint16(i);
		}
	}

	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
                				
	counters[EventReportService::MessageType::DisabledListEventReport]++;
    }


  } /* namespace pus */
} /* namespace gr */
