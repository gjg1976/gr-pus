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
#include "RealTimeForwardingControlService_impl.h"

namespace gr {
  namespace pus {

    RealTimeForwardingControlService::sptr
    RealTimeForwardingControlService::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<RealTimeForwardingControlService_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    RealTimeForwardingControlService_impl::RealTimeForwardingControlService_impl(const std::string& init_file)
      : gr::block("RealTimeForwardingControlService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        
        serviceType = ServiceType;
        for(size_t i = 0; i < RealTimeForwardingControlService::MessageType::end; i++)
        	counters[i] = 0;

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;

        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_in(PMT_IN_MSG);
        set_msg_handler(PMT_IN_MSG,
                    [this](pmt::pmt_t msg) { this->handle_in_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);
        message_port_register_out(PMT_FWD);
   
        parse_json(init_file);
    }

    /*
     * Our virtual destructor.
     */
    RealTimeForwardingControlService_impl::~RealTimeForwardingControlService_impl()
    {
    }

    void RealTimeForwardingControlService_impl::parse_json(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;
		for (auto& elemDef : json["filter"]){
			uint16_t apid = elemDef["apid"];
			for (auto& elemTypeDef : elemDef["type"]){
				uint8_t serviceType = elemTypeDef["serviceType"];
				auto key = std::make_pair(apid, serviceType);
				
                		uint16_t numSubTypes = elemTypeDef["numSubType"];
                		std::vector<uint8_t> subTypes;	
                		ApplicationProcessConfiguration::ReportTypeDefinitions reportTypeDefinitions;
                					
               		for(uint16_t i = 0; i < numSubTypes; i++){
               		         if (reportTypeDefinitions.size() < ECSSMaxReportTypeDefinitions)
                			 	reportTypeDefinitions.push_back(elemTypeDef["serviceSubType"][i]);
                		}
                		applicationProcessConfiguration.definitions[key] = reportTypeDefinitions;
                			                		
			}
			if(controlledApplications.size() < ECSSMaxControlledApplicationProcesses)
				controlledApplications.push_back(apid);
		}		

        } else {
            GR_LOG_WARN(d_logger, "No RealTime Forwarding Control definitions init file found");
        }
        file.close();
    } 

    void RealTimeForwardingControlService_impl::handle_in_msg(pmt::pmt_t pdu)
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
                Message message  = Message(in_data);

                if(!d_error_handler->assertInternal(message.getMessageVersion() == 0U, ErrorHandler::UnacceptablePacket))
                	return;
       
                if(!d_error_handler->assertInternal(message.getMessageSecondaryHeaderFlag(), ErrorHandler::UnacceptablePacket))
                	return;

                if(!d_error_handler->assertInternal(message.getMessageSequenceFlags() == 3U, ErrorHandler::UnacceptablePacket))
                	return;

                if(!d_error_handler->assertInternal(message.getMessagePacketDataLength() == (message.getMessageSize() - CCSDSPrimaryHeaderSize - 1),
                					 ErrorHandler::UnacceptablePacket))
                	return;

                if(!d_error_handler->assertRequest(message.getMessagePUSVersion() == 2U, message, ErrorHandler::UnacceptableMessage)){
      	
                	return;
                }

                
		 if (reportExistsInAppProcessConfiguration(message.getMessageApplicationId(), 
		 	message.getMessageServiceType(), message.getMessageType()))
		 {
#ifdef _PUS_DEBUG
                	printf("Forwarding TM[%u,%u]\n", message.getMessageServiceType(), message.getMessageType());
#endif		 
        		message_port_pub(PMT_FWD, pdu);
		 }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    void RealTimeForwardingControlService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case AddReportTypesToAppProcessConfiguration:  
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AddReportTypesToAppProcessConfiguration");
#endif
                           addReportTypesToAppProcessConfiguration(message);
                           break;
                        case DeleteReportTypesFromAppProcessConfiguration:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "DeleteReportTypesFromAppProcessConfiguration");
#endif
                           deleteReportTypesFromAppProcessConfiguration(message);
                           break;   
                      
                        case ReportEnabledTelemetrySourcePackets:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "ReportEnabledTelemetrySourcePackets");
#endif
                           reportEnabledTelemetrySourcePackets(message);
                           break;    
                                                                    
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Real Time Forwarding Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Real Time Forwarding Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }
     
    /*************************************************************************************************************/
    /*************************************************************************************************************/
    /*************************************************************************************************************/ 
    
    void RealTimeForwardingControlService_impl::addAllReportsOfApplication(uint16_t applicationID) {
	for (const auto& service: AllMessageTypes::MessagesOfService) {
		uint8_t serviceType = service.first;
		addAllReportsOfService(applicationID, serviceType);
	}
    }

    void RealTimeForwardingControlService_impl::addAllReportsOfService(uint16_t applicationID, uint8_t serviceType) {
	for (const auto& messageType: AllMessageTypes::MessagesOfService.at(serviceType)) {
		auto appServicePair = std::make_pair(applicationID, serviceType);
		applicationProcessConfiguration.definitions[appServicePair].push_back(messageType);
	}
    }

    uint8_t RealTimeForwardingControlService_impl::countReportsOfService(uint16_t applicationID, uint8_t serviceType) {
	auto appServicePair = std::make_pair(applicationID, serviceType);
	return applicationProcessConfiguration.definitions[appServicePair].size();
    }

    bool RealTimeForwardingControlService_impl::maxServiceTypesReached(Message& request, uint16_t applicationID) {
	if (countServicesOfApplication(applicationID) >= ECSSMaxServiceTypeDefinitions) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxServiceTypesReached);
		return true;
	}
	return false;
    }

    bool RealTimeForwardingControlService_impl::checkService(Message& request, uint16_t applicationID, uint8_t numOfMessages) {
	if (maxServiceTypesReached(request, applicationID)) {
		request.setMessageReadPosition(request.getMessageReadPosition()+numOfMessages);
		return false;
	}
	return true;
    }

    bool RealTimeForwardingControlService_impl::maxReportTypesReached(Message& request, uint16_t applicationID,
                                                             uint8_t serviceType) {
	if (AllMessageTypes::MessagesOfService.find(serviceType) == AllMessageTypes::MessagesOfService.end()) {
		reportExecutionStartError(request, ErrorHandler::NonExistentServiceTypeDefinition);
		return true;
	}	
	if (countReportsOfService(applicationID, serviceType) >= AllMessageTypes::MessagesOfService.at(serviceType).size()) {
		reportExecutionStartError(request, ErrorHandler::MaxReportTypesReachedInProgress);
		return true;
	}
	return false;
    }

    bool RealTimeForwardingControlService_impl::checkMessage(Message& request, uint16_t applicationID, uint8_t serviceType,
                                                    uint8_t messageType) {
	if(maxReportTypesReached(request, applicationID, serviceType)) 
		return false;
	if(reportExistsInAppProcessConfiguration(applicationID, serviceType, messageType)){
		reportExecutionStartError(request, ErrorHandler::NonExistentReportTypeDefinition);
		return false;
	}
	return true;
    }

    bool RealTimeForwardingControlService_impl::reportExistsInAppProcessConfiguration(uint16_t applicationID, uint8_t serviceType,
                                                                             uint8_t messageType) {
	auto key = std::make_pair(applicationID, serviceType);
	auto& messages = applicationProcessConfiguration.definitions[key];
	return (std::find(messages.begin(), messages.end(), messageType) != messages.end());

    }   
   
    uint8_t RealTimeForwardingControlService_impl::countServicesOfApplication(uint16_t applicationID) {
	uint8_t serviceCounter = 0;
	for (auto& definition: applicationProcessConfiguration.definitions) {
		const auto& pair = definition.first;
		if (pair.first == applicationID) {
			serviceCounter++;
		}
	}
	return serviceCounter;
    }

    bool RealTimeForwardingControlService_impl::checkAppControlled(Message& request, uint16_t applicationId) {
	if (std::find(controlledApplications.begin(), controlledApplications.end(), applicationId) ==
	    controlledApplications.end()) {
		reportExecutionStartError(request, ErrorHandler::NotControlledApplication);
		return false;
	}
	return true;
    }

    bool RealTimeForwardingControlService_impl::checkApplicationOfAppProcessConfig(Message& request, uint16_t applicationID,
                                                                          uint8_t numOfServices) {
	if (not checkAppControlled(request, applicationID) or allServiceTypesAllowed(request, applicationID)) {
		for (uint8_t i = 0; i < numOfServices; i++) {
			request.setMessageReadPosition(request.getMessageReadPosition() + 1);
		
			uint8_t numOfMessages = request.readUint8();
				
			request.setMessageReadPosition(request.getMessageReadPosition() + numOfMessages);
		}
		return false;
	}
	return true;
    }

    bool RealTimeForwardingControlService_impl::allServiceTypesAllowed(Message& request, uint16_t applicationID) {
	if (countServicesOfApplication(applicationID) >= ECSSMaxServiceTypeDefinitions) {
		reportExecutionStartError(request, ErrorHandler::AllServiceTypesAlreadyAllowed);
		return true;
	}
	return false;
    }

    bool RealTimeForwardingControlService_impl::isApplicationEnabled(uint16_t targetAppID) {
	auto& definitions = applicationProcessConfiguration.definitions;
	return std::any_of(std::begin(definitions), std::end(definitions), [targetAppID](auto& definition) { 
				return targetAppID == definition.first.first; });
    }

    bool RealTimeForwardingControlService_impl::isServiceTypeEnabled(uint16_t applicationID, uint8_t targetService) {
	auto& definitions = applicationProcessConfiguration.definitions;
	return std::any_of(std::begin(definitions), std::end(definitions), [applicationID, targetService](auto& definition) { 
				return applicationID == definition.first.first and targetService == definition.first.second; });
    }

    bool RealTimeForwardingControlService_impl::isReportTypeEnabled(uint8_t target, uint16_t applicationID,
                                                      uint8_t serviceType) {
	auto appServicePair = std::make_pair(applicationID, serviceType);
	auto serviceTypes = applicationProcessConfiguration.definitions.find(appServicePair);
	if (serviceTypes == applicationProcessConfiguration.definitions.end()) {
		return false;
	}
	return std::find(serviceTypes->second.begin(), serviceTypes->second.end(), target) != serviceTypes->second.end();
    }

    void RealTimeForwardingControlService_impl::deleteApplicationProcess(uint16_t applicationID) {
	auto& definitions = applicationProcessConfiguration.definitions;
	auto iter = std::begin(definitions);
	while (iter != definitions.end()) {
		iter = std::find_if(
		    std::begin(definitions), std::end(definitions), [applicationID](auto& definition) { 
		    	return applicationID == definition.first.first; });
		definitions.erase(iter);
	}
    }

    bool RealTimeForwardingControlService_impl::isApplicationInConfiguration(Message& request, uint16_t applicationID,
                                                         uint8_t numOfServices) {
	if (not isApplicationEnabled(applicationID)) {
		reportExecutionStartError(request, ErrorHandler::NonExistentApplicationProcess);
		for (uint8_t currentServiceNumber = 0; currentServiceNumber < numOfServices; currentServiceNumber++) {
			request.setMessageReadPosition(request.getMessageReadPosition() + 1);
			uint8_t numOfMessages = request.readUint8();

			request.setMessageReadPosition(request.getMessageReadPosition() + numOfMessages);
		}
		return false;
	}
	return true;
    }
    
    bool RealTimeForwardingControlService_impl::isServiceTypeInConfiguration(Message& request, uint16_t applicationID, uint8_t serviceType,
                                                         uint8_t numOfMessages) {
	if (not isServiceTypeEnabled(applicationID, serviceType)) {
		reportExecutionStartError(request, ErrorHandler::NonExistentServiceTypeDefinition);
		request.setMessageReadPosition(request.getMessageReadPosition() + numOfMessages);
		return false;
	}
	return true;
    }

    bool RealTimeForwardingControlService_impl::isReportTypeInConfiguration(Message& request, uint16_t applicationID, uint8_t serviceType,
                                                        uint8_t messageType) {
	if (not isReportTypeEnabled(messageType, applicationID, serviceType)) {
		reportExecutionStartError(request, ErrorHandler::NonExistentServiceTypeDefinition);
		return false;
	}
	return true;
    }

    void RealTimeForwardingControlService_impl::deleteServiceRecursive(uint16_t applicationID, uint8_t serviceType) {
	auto appServicePair = std::make_pair(applicationID, serviceType);
	applicationProcessConfiguration.definitions.erase(appServicePair);
    }

    void RealTimeForwardingControlService_impl::deleteReportRecursive(uint16_t applicationID, uint8_t serviceType,
                                                             uint8_t messageType) {
	auto appServicePair = std::make_pair(applicationID, serviceType);
	auto reportTypes = applicationProcessConfiguration.definitions.find(appServicePair);
	if (reportTypes == applicationProcessConfiguration.definitions.end()) {
		return;
	}
	reportTypes->second.erase(std::remove(reportTypes->second.begin(), reportTypes->second.end(), messageType));

	if (applicationProcessConfiguration.definitions[appServicePair].empty()) {
		deleteServiceRecursive(applicationID, serviceType);
	}
    }   


    bool RealTimeForwardingControlService_impl::realtimeForwardTCSizeVerification(Message& request) {  
 	uint16_t currentPosition = request.getMessageReadPosition();
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < RT_FWD_NUM_APP_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return false;
	}
	uint16_t numOfApplications = request.readUint16();

 	tcSize -= RT_FWD_NUM_APP_SIZE;
	
	for (uint16_t currentApplicationNumber = 0; currentApplicationNumber < numOfApplications; currentApplicationNumber++) {
 		if(tcSize < (RT_FWD_APPID_SIZE + RT_FWD_NUM_SERVICES_SIZE)){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);
			return false;
		}
		tcSize -= (RT_FWD_APPID_SIZE + RT_FWD_NUM_SERVICES_SIZE);
		
		uint16_t applicationID = request.readUint16();
		uint16_t numOfServices = request.readUint16();

		for (uint8_t currentServiceNumber = 0; currentServiceNumber < numOfServices; currentServiceNumber++) {
 			if(tcSize < (RT_FWD_SERVICES_SIZE + RT_FWD_NUM_SUBTYPES_SIZE)){     
				reportAcceptanceError(request, ErrorHandler::InvalidLength);
				return false;
			}
			tcSize -= (RT_FWD_SERVICES_SIZE + RT_FWD_NUM_SUBTYPES_SIZE);


			uint8_t serviceType = request.readUint8();
			uint16_t numOfMessages = request.readUint16();

 			if(tcSize < (RT_FWD_SUBTYPES_SIZE * numOfMessages)){     
				reportAcceptanceError(request, ErrorHandler::InvalidLength);
				return false;
			}
			tcSize -= (RT_FWD_SUBTYPES_SIZE * numOfMessages);
			request.setMessageReadPosition(request.getMessageReadPosition() + (RT_FWD_SUBTYPES_SIZE * numOfMessages));
		}
	}

	if(tcSize > 0){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return false;
	}
	request.setMessageReadPosition(currentPosition);	

	return true;    
    }         


    /*************************************************************************************************************/
    /*************************************************************************************************************/
    /*************************************************************************************************************/
        
    void RealTimeForwardingControlService_impl::addReportTypesToAppProcessConfiguration(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RealTimeForwardingControlService_impl::MessageType::AddReportTypesToAppProcessConfiguration)) {
		return;
	}

	if(not realtimeForwardTCSizeVerification(request))
		return;

	reportSuccessAcceptanceVerification(request);
	
	uint16_t numOfApplications = request.readUint16();

	bool bFaultStartExecution = false;
	
	for (uint16_t currentApplicationNumber = 0; currentApplicationNumber < numOfApplications; currentApplicationNumber++) {
		bool bAddReport = true;
		uint16_t applicationID = request.readUint16();
		uint16_t numOfServices = request.readUint16();

		if (not checkApplicationOfAppProcessConfig(request, applicationID, numOfServices)) {
			bAddReport = false;
		}

		if (numOfServices == 0) {
			if (bAddReport)
				addAllReportsOfApplication(applicationID);
			continue;
		}

		for (uint8_t currentServiceNumber = 0; currentServiceNumber < numOfServices; currentServiceNumber++) {
			uint8_t serviceType = request.readUint8();
			uint16_t numOfMessages = request.readUint16();
			
			if (bAddReport){
				if (not checkService(request, applicationID, numOfMessages)) {
					bAddReport = false;
				}
			}

			if (numOfMessages == 0) {
				if (bAddReport)
					addAllReportsOfService(applicationID, serviceType);
				continue;
			}

			for (uint8_t currentMessageNumber = 0; currentMessageNumber < numOfMessages; currentMessageNumber++) {
				uint8_t messageType = request.readUint8();
				if (bAddReport){
					if (not checkMessage(request, applicationID, serviceType, messageType)) {
						bAddReport = false;
					}
				}

				if (bAddReport){
					auto key = std::make_pair(applicationID, serviceType);
					applicationProcessConfiguration.definitions[key].push_back(messageType);
				}
			}
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }

    void RealTimeForwardingControlService_impl::deleteReportTypesFromAppProcessConfiguration(Message& request) {

	if (!d_message_parser->assertTC(request, serviceType, 
			RealTimeForwardingControlService_impl::MessageType::DeleteReportTypesFromAppProcessConfiguration)) {
		return;
	}

	if(not realtimeForwardTCSizeVerification(request))
		return;

	reportSuccessAcceptanceVerification(request);

	uint16_t numOfApplications = request.readUint16();
	
	if (numOfApplications == 0) {
		applicationProcessConfiguration.definitions.clear();
		reportSuccessStartExecutionVerification(request);
		reportSuccessCompletionExecutionVerification(request);		
		
		return;
	}

	bool bFaultStartExecution = false;
		
	for (uint8_t currentApplicationNumber = 0; currentApplicationNumber < numOfApplications; currentApplicationNumber++) {
		bool bDelReport = true;
		uint16_t applicationID = request.readUint16();
		uint16_t numOfServices = request.readUint16();

		if (not isApplicationInConfiguration(request, applicationID, numOfServices)) {
			bDelReport = false;
		}
				
		if (numOfServices == 0) {
			if(bDelReport)
				deleteApplicationProcess(applicationID);
			continue;
		}

		for (uint8_t currentServiceNumber = 0; currentServiceNumber < numOfServices; currentServiceNumber++) {
			uint8_t serviceType = request.readUint8();
			uint16_t numOfMessages = request.readUint16();

			if(bDelReport){
				if (not isServiceTypeInConfiguration(request, applicationID, serviceType, numOfMessages)) {
					bDelReport = false;
				}
			}
			
			if (numOfMessages == 0) {
				if(bDelReport)
					deleteServiceRecursive(applicationID, serviceType);
				continue;
			}

			for (uint8_t currentMessageNumber = 0; currentMessageNumber < numOfMessages; currentMessageNumber++) {
				uint8_t messageType = request.readUint8();
				if(bDelReport){
					if (not isReportTypeInConfiguration(request, applicationID, serviceType, messageType)) {
						bDelReport = false;
					}
				}
				if(bDelReport)
					deleteReportRecursive(applicationID, serviceType, messageType);

			}
		}
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
				
	reportSuccessCompletionExecutionVerification(request);
     }
     
     void RealTimeForwardingControlService_impl::reportEnabledTelemetrySourcePackets(Message& request) 
     {
	if (!d_message_parser->assertTC(request, serviceType, 
			RealTimeForwardingControlService_impl::MessageType::ReportEnabledTelemetrySourcePackets)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize >0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);
	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);    

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RealTimeForwardingControlService_impl::MessageType::EnabledTelemetrySourcePacketsReport, 
			counters[RealTimeForwardingControlService_impl::MessageType::EnabledTelemetrySourcePacketsReport], 0);
			
	uint16_t numApplications = controlledApplications.size();		
	report.appendUint16(numApplications);
	for (auto& application: controlledApplications) {
		report.appendUint16(application);
		
		auto& definitions = applicationProcessConfiguration.definitions;
		uint16_t numMessagesTypes = 0;
		for (auto& messagesTypes: AllMessageTypes::MessagesOfService){
			uint8_t targetService = messagesTypes.first;
			if( std::any_of(std::begin(definitions), std::end(definitions), [application, targetService](auto& definition) { 
				return application == definition.first.first and targetService == definition.first.second; }))
					numMessagesTypes++;
					
		}	
		report.appendUint16(numMessagesTypes);
		for (auto& messagesTypes: AllMessageTypes::MessagesOfService){
			uint8_t targetService = messagesTypes.first;
			if( std::any_of(std::begin(definitions), std::end(definitions), [application, targetService](auto& definition) { 
				return application == definition.first.first and targetService == definition.first.second; })){
					report.appendUint8(targetService);
					auto key = std::make_pair(application, targetService);
					auto& messagesSubType = applicationProcessConfiguration.definitions[key];
					uint16_t numMessagesSubType = messagesSubType.size();
					report.appendUint16(numMessagesSubType);
					for (auto& messagesSubTypes: messagesSubType){
						report.appendUint8(messagesSubTypes);
					}
			}
		}			
	}

	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[RealTimeForwardingControlService_impl::MessageType::EnabledTelemetrySourcePacketsReport]++;	
     }

  } /* namespace pus */
} /* namespace gr */
