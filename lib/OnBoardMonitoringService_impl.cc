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
#include "OnBoardMonitoringService_impl.h"
#include <gnuradio/pus/EventReportService.h>
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    OnBoardMonitoringService::sptr
    OnBoardMonitoringService::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<OnBoardMonitoringService_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    OnBoardMonitoringService_impl::OnBoardMonitoringService_impl(const std::string& init_file)
      : gr::block("OnBoardMonitoringService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        d_parameter_pool = ParameterPool::getInstance();
                
        serviceType = ServiceType;
        for(size_t i = 0; i < OnBoardMonitoringService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);
        message_port_register_out(PMT_RID);
        
        parse_json(init_file);

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
       	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;

      	d_time_provider = TimeProvider::getInstance();
   
    	d_time_provider->addHandler(
            serviceType,
            std::bind(
                &OnBoardMonitoringService_impl::timerTick,
                this,
                std::placeholders::_1
            )
    	); 

    }

    /*
     * Our virtual destructor.
     */
    OnBoardMonitoringService_impl::~OnBoardMonitoringService_impl()
    {
            d_time_provider->removeHandler(serviceType);  
    }

    void OnBoardMonitoringService_impl::timerTick(TimeProvider *p) {
	if(!parameterMonitoringFunctionStatus)
		return;

    	std::vector<uint16_t> RIDList;

    	uint16_t transitionsCount = 0;

	for (auto& currentPMONBase: parameterMonitoringList) {
		if(currentPMONBase.second.CheckState(RIDList)){
			transitionsCount++;
			transitionDetection = true;
			transitionsCounter++;
			
			transitionList.push_back((currentPMONBase.first >> 8) & 0xFF);
			transitionList.push_back(currentPMONBase.first & 0xFF);
			transitionList.push_back((currentPMONBase.second.monitoredParameterId >> 8) & 0xFF);
			transitionList.push_back(currentPMONBase.second.monitoredParameterId & 0xFF);
			currentPMONBase.second.loadIntoTransitionList(transitionList);	
		}		
	}      
		
	if(RIDList.size() > 0)
	{
		for (auto& RID: RIDList) {
	
			uint8_t message[2] = {static_cast<uint8_t>((RID >> 8) & 0xFF),
						static_cast<uint8_t>(RID & 0xFF)};
                	pmt::pmt_t meta = pmt::make_dict();
                	meta = pmt::dict_add(meta, PMT_EVENT , pmt::from_long(
                		EventReportService::Event::HighSeverityUnknownEvent));
                	message_port_pub(PMT_RID, pmt::cons(meta, 
                		pmt::init_u8vector(2, message)));   
		} 
	}
	if(transitionDetection){
		if(++maximumTransitionReportingDelayCounter > maximumTransitionReportingDelay){
	        	checkTransitionReport();
	        	maximumNumberOfTransitionCounter = 0;
	        	maximumTransitionReportingDelayCounter = 0;
	        	transitionsCount = 0;
	        	transitionDetection =  false;
		}
	}
		
	if(transitionsCount){
		maximumNumberOfTransitionCounter += transitionsCount;
	        if(maximumNumberOfTransitionCounter > MaximumNumberOfTransitions)
	        {
	        	checkTransitionReport();
	        	maximumNumberOfTransitionCounter = 0;
	        	maximumTransitionReportingDelayCounter = 0;
	        	transitionDetection = false;
	        }
	}
	
    }

    void OnBoardMonitoringService_impl::parse_json(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;
            parameterMonitoringFunctionStatus = json["enabled"];
            maximumTransitionReportingDelay = json["maxTransRepDelay"];     
            for (auto& elem : json["monitor"]){
		uint16_t pmonId = elem["pmonId"];
		uint16_t paramId = elem["paramId"];
		uint16_t monitoringInterval = elem["monInterval"];  
		uint16_t repetitionNumber = elem["repetitionNumber"];
		bool enabled = elem["monitoringEnabled"];

		if (!d_parameter_pool->parameterExists(paramId)){
			continue;
		}

                PMONBase PMONbase(paramId, monitoringInterval, repetitionNumber, enabled);

		for (auto& elemDef : elem["definition"]){
			std::string type = elemDef["type"];
			if( type == "ValueCheck"){
                    		double  maskValue = elemDef["maskValue"];
                    		double  expectedValue = elemDef["expectedValue"];
                    		uint16_t  unexpectedRID = elemDef["unexpectedRID"];
                    		
                    		PMONExpectedValueCheck* PMONexpectedValueCheck = new PMONExpectedValueCheck(maskValue, 
                    					expectedValue,	unexpectedRID, repetitionNumber);			
	                       PMONbase.checkDefinition = (PMONCheck*)PMONexpectedValueCheck;

			}else if( type == "LimitCheck"){
			        double  lowLimit = elemDef["lowLimit"];
                    		uint16_t  belowLowLimitRID = elemDef["belowLowLimitRID"];
			        double  highLimit = elemDef["highLimit"];
                    		uint16_t  aboveHighLimitRID = elemDef["aboveHighLimitRID"];
	
                    		PMONLimitCheck* PMONlimitCheck = new PMONLimitCheck(lowLimit, belowLowLimitRID, 
							highLimit, aboveHighLimitRID, repetitionNumber);			
 	                       PMONbase.checkDefinition = (PMONCheck*)PMONlimitCheck;                   					
			}else if( type == "DeltaCheck"){
				auto parameter = d_parameter_pool->getParameter(paramId);
			        double  lowDeltaThreshold = elemDef["lowDeltaThreshold"];
                    		uint16_t  belowLowThresholdRID = elemDef["belowLowThresholdRID"];
			        double  highDeltaThreshold = elemDef["highDeltaThreshold"];
                    		uint16_t  aboveHighThresholdRID = elemDef["aboveHighThresholdRID"];	
                    		uint16_t  deltaRepetition = elemDef["deltaRepetition"];                    		
                    		PMONDeltaCheck* PMONdeltaCheck = new PMONDeltaCheck(lowDeltaThreshold,
	                        			belowLowThresholdRID, highDeltaThreshold,
	                        			aboveHighThresholdRID, repetitionNumber, 
							deltaRepetition,
							parameter->get().getValueAsDouble());			

 	                       PMONbase.checkDefinition = (PMONCheck*)PMONdeltaCheck;     
			}										 
                }						
		if (parameterMonitoringList.size() < ECSSMaxMonitoringDefinitions)
			if (parameterMonitoringList.find(pmonId) == parameterMonitoringList.end()){
				addPMONDefinition(pmonId, std::reference_wrapper<PMONBase>(PMONbase)) ;
		
            		}
            }
        } else {
            GR_LOG_WARN(d_logger, "No on-board monitor definitions init file found");
        }
        file.close();
    }  
    
    void OnBoardMonitoringService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case EnableParameterMonitoringDefinitions:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "EnableParameterMonitoringDefinitions");
#endif
                           enableParameterMonitoringDefinitions(message);
                           break;
                        case DisableParameterMonitoringDefinitions:   
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DisableParameterMonitoringDefinitions");
#endif
                           disableParameterMonitoringDefinitions(message);
                           break;                                             
                        case ChangeMaximumTransitionReportingDelay:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ChangeMaximumTransitionReportingDelay");
#endif
                           changeMaximumTransitionReportingDelay(message);
                           break;
                        case DeleteAllParameterMonitoringDefinitions:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeleteAllParameterMonitoringDefinitions");
#endif
                           deleteAllParameterMonitoringDefinitions(message);
                           break;
                        case AddParameterMonitoringDefinitions:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AddParameterMonitoringDefinitions");
#endif
                           addParameterMonitoringDefinitions(message);				
                           break;
                        case DeleteParameterMonitoringDefinitions:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeleteParameterMonitoringDefinitions");
#endif
                           deleteParameterMonitoringDefinitions(message);
                           break;
                        case ModifyParameterMonitoringDefinitions:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ModifyParameterMonitoringDefinitions");
#endif
                           modifyParameterMonitoringDefinitions(message);				
                           break;
                        case ReportParameterMonitoringDefinitions:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportParameterMonitoringDefinitions");
#endif
                           reportParameterMonitoringDefinitions(message);
                           break;
                        case ReportStatusOfParameterMonitoringDefinition:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportStatusOfParameterMonitoringDefinition");
#endif
                           reportStatusOfParameterMonitoringDefinition(message);
                           break;
                  
                        case ReportOutOfLimits:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportOutOfLimits");
#endif
                           reportOutOfLimits(message);
                           break;                           
                        case EnableParameterMonitoringFunction:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "EnableParameterMonitoringFunction");
#endif
                           enableParameterMonitoringFunction(message);
                           break;
                        case DisableParameterMonitoringFunction:   
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DisableParameterMonitoringFunction");
#endif
                           disableParameterMonitoringFunction(message);
                           break;                               
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "On Board Monitoring Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "On Board Monitoring Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);

               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    bool OnBoardMonitoringService_impl::hasExistingDefinition(uint8_t defType, PMONBase& PMONbase) {
	for (auto& currentParam: parameterMonitoringList) {
		if(currentParam.second.checkDefinition)
               	if(currentParam.second.checkDefinition->getType() == defType)
               		return true;
 	}      
	return false;
    }
  
    bool OnBoardMonitoringService_impl::hasNonExistingParameterMonitoringExecutionError(uint8_t id, Message& req) {
	if (!parameterMonitoringExists(id)) {
		reportExecutionStartError(req, ErrorHandler::GetNonExistingParameterMonitoringDefinition);
		return true;
	}
	return false;
    }

    bool OnBoardMonitoringService_impl::parameterMonitoringIsEnabledExecutionError(uint8_t id, Message& req) {
	auto paramMON = parameterMonitoringList.find(id);
	if (paramMON == parameterMonitoringList.end()){
		reportExecutionStartError(req, ErrorHandler::GetNonExistingParameterMonitoringDefinition);
		return true;
	}
	if (paramMON->second.getDefinitionEnableStatus() ) {
		reportExecutionStartError(req, ErrorHandler::deleteMonitoringDefinitionEnabled);
		return true;
	}
	return false;
    }
 
    void OnBoardMonitoringService_impl::enableParameterMonitoringDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::EnableParameterMonitoringDefinitions)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < ONBOARD_MON_NUM_PMON){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 	
	uint16_t numberOfPMONDefinitions = request.readUint16();
	
	tcSize -= ONBOARD_MON_NUM_PMON;

 	if(tcSize != numberOfPMONDefinitions * ONBOARD_MON_PMONID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 

	reportSuccessAcceptanceVerification(request);

	bool bFaultStartExecution = false;	
	for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {
		uint16_t currentId = request.readUint16();
		auto definition = parameterMonitoringList.find(currentId);
		if (definition == parameterMonitoringList.end()) {
			reportExecutionStartError(request, ErrorHandler::GetNonExistingParameterMonitoringDefinition);
			bFaultStartExecution = true;
			continue;
		}
		definition->second.repetitionNumber = 0;
		definition->second.setDefinitionEnableStatus(true);
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);	
    }

    void OnBoardMonitoringService_impl::disableParameterMonitoringDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::DisableParameterMonitoringDefinitions)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < ONBOARD_MON_NUM_PMON){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 	
	uint16_t numberOfPMONDefinitions = request.readUint16();
	
	tcSize -= ONBOARD_MON_NUM_PMON;

 	if(tcSize != numberOfPMONDefinitions * ONBOARD_MON_PMONID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 

	reportSuccessAcceptanceVerification(request);

	bool bFaultStartExecution = false;	
	for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {
		uint16_t currentId = request.readUint16();
		auto definition = parameterMonitoringList.find(currentId);
		if (definition == parameterMonitoringList.end()) {
			reportExecutionStartError(request, ErrorHandler::GetNonExistingParameterMonitoringDefinition);
			bFaultStartExecution = true;
			continue;
		}
		definition->second.repetitionNumber = 0;
		definition->second.setDefinitionEnableStatus(false);
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);	
    }

    void OnBoardMonitoringService_impl::changeMaximumTransitionReportingDelay(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::ChangeMaximumTransitionReportingDelay)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != ONBOARD_MON_TRANS_DELAY){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 	
	
	reportSuccessAcceptanceVerification(request);

	maximumTransitionReportingDelay = request.readUint16();

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void OnBoardMonitoringService_impl::deleteAllParameterMonitoringDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::DeleteAllParameterMonitoringDefinitions)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	
	reportSuccessAcceptanceVerification(request);

	if (parameterMonitoringFunctionStatus) {
		reportExecutionStartError(request, ErrorHandler::InvalidRequestToDeleteAllParameterMonitoringDefinitions);
		return;
	}else{
		reportSuccessStartExecutionVerification(request);	
		
		parameterMonitoringList.clear();
	
		parameterMonitoringFunctionStatus = false;  
	}
	
	reportSuccessCompletionExecutionVerification(request);
    }

    void OnBoardMonitoringService_impl::addParameterMonitoringDefinitions(Message& message)
    {
    	if (!d_message_parser->assertTC(message, serviceType, 
			OnBoardMonitoringService::MessageType::AddParameterMonitoringDefinitions)) {
		return;
	}
 	
 	uint16_t tcSize = message.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < ONBOARD_MON_NUM_PMON){     
		reportAcceptanceError(message, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= ONBOARD_MON_NUM_PMON; 
 	
	uint16_t numberOfPMONDefinitions = message.readUint16();
        bool bFaultStartExecution = false;

 	uint16_t currentPosition = message.getMessageReadPosition();

	for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {

 		if(tcSize < (ONBOARD_MON_PMONID + ONBOARD_MON_PARAMID + ONBOARD_MON_INTERVAL + ONBOARD_MON_COUNTER)){     
			reportAcceptanceError(message, ErrorHandler::InvalidLength);
			return;
		}		
 		tcSize -= (ONBOARD_MON_PMONID + ONBOARD_MON_PARAMID + ONBOARD_MON_INTERVAL + ONBOARD_MON_COUNTER); 
		message.setMessageReadPosition(message.getMessageReadPosition() + ONBOARD_MON_PMONID);

		uint16_t paramId = message.readUint16();
			
		if (!d_parameter_pool->parameterExists(paramId)){
			reportSuccessAcceptanceVerification(message);
			reportExecutionStartError(message, ErrorHandler::GetNonExistingParameter);
			return;
		}
	
		auto parameter = d_parameter_pool->getParameter(paramId);
		
		message.setMessageReadPosition(message.getMessageReadPosition() + ONBOARD_MON_INTERVAL + ONBOARD_MON_COUNTER);

		if(tcSize < ONBOARD_MON_DEF_TYPE){     
			reportAcceptanceError(message, ErrorHandler::InvalidLength);
			return;
		}		
 		tcSize -= ONBOARD_MON_DEF_TYPE;
		uint8_t checkType = message.readUint8();

		switch(checkType){
			case PMONCheck::ValueCheck:
			{
				uint16_t valueSize = 2 * parameter->get().appendValueToVector().size();
				if(tcSize < (valueSize + ONBOARD_MON_RID)){
					reportAcceptanceError(message, ErrorHandler::InvalidLength);
					return;
				}		
 				tcSize -= (valueSize + ONBOARD_MON_RID);
 				
				message.setMessageReadPosition(message.getMessageReadPosition() + valueSize + ONBOARD_MON_RID);
				break;
			}

			case PMONCheck::LimitCheck:
			{
				uint16_t valueSize = parameter->get().appendValueToVector().size();
				
				if(tcSize < 2 * (valueSize + ONBOARD_MON_RID)){
					reportAcceptanceError(message, ErrorHandler::InvalidLength);
					return;
				}		
 				tcSize -= (2 * (valueSize + ONBOARD_MON_RID));
 				
				message.setMessageReadPosition(message.getMessageReadPosition() + 2 * (valueSize + ONBOARD_MON_RID));

				break;
			}
			case PMONCheck::DeltaCheck:
			{
				uint16_t valueSize = parameter->get().appendValueToVector().size();
				
				if(tcSize < (2 * (valueSize + ONBOARD_MON_RID) + ONBOARD_MON_DELTA_COUNTER)){
					reportAcceptanceError(message, ErrorHandler::InvalidLength);
					return;
				}		
 				tcSize -= (2 * (valueSize + ONBOARD_MON_RID) + ONBOARD_MON_DELTA_COUNTER);
 				
				message.setMessageReadPosition(message.getMessageReadPosition() + 2 * (valueSize + ONBOARD_MON_RID) + ONBOARD_MON_DELTA_COUNTER);

				break;
			}
			default:
				reportSuccessAcceptanceVerification(message);
				reportExecutionStartError(message, ErrorHandler::setNonExistingParameterMonitoringCheckDefinition);			
				return;
		}														

	}	
	if (tcSize > 0){
		reportAcceptanceError(message, ErrorHandler::InvalidLength);
		return;
	}		

	message.setMessageReadPosition(currentPosition);	
	reportSuccessAcceptanceVerification(message);	
      
	for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {
		bool newPMONdef = false;
		uint16_t currentId = message.readUint16();

		uint16_t paramId = message.readUint16();
				
		auto parameter = d_parameter_pool->getParameter(paramId);
			
		uint16_t monitorInterval = message.readUint16();

		uint16_t repetitionNumberCount = message.readUint16();

		PMONBase* PMONbase;
		
		auto pmonbase = parameterMonitoringList.find(currentId);
		if(pmonbase == parameterMonitoringList.end()){
			newPMONdef = true;
        		PMONbase = new PMONBase(paramId, monitorInterval, repetitionNumberCount, false);
       	}else{
       		PMONbase = &pmonbase->second;
       	}
		
		uint8_t checkType = message.readUint8();
		
		switch(checkType){
			case PMONCheck::ValueCheck:
			{
				double maskValue = parameter->get().getValueAsDoubleFromMessage(message);
				double expectedThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t unexpectedRIDNumber = message.readUint16();
				PMONExpectedValueCheck* PMONexpectedValueCheck = new PMONExpectedValueCheck(
							maskValue, expectedThresholdValue,
	                                		unexpectedRIDNumber, repetitionNumberCount);	
	              		if(!newPMONdef)
	              			break;
	              		if(PMONbase->checkDefinition)
	              			delete PMONbase->checkDefinition;
	              		PMONbase->checkDefinition = (PMONCheck*)PMONexpectedValueCheck;

				break;
			}
			case PMONCheck::LimitCheck:
			{
				double lowThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t belowLowThresholdRIDNumber = message.readUint16();
				double highThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t aboveHighThresholdRIDNumber = message.readUint16();
	              		
	              		if(!newPMONdef)
	              			break;
				
				if(lowThresholdValue > highThresholdValue){
					reportExecutionStartError(message, ErrorHandler::setInvalidMonitoringCheckDefinition);			
					return;
				}
				PMONLimitCheck* PMONlimitCheck = new PMONLimitCheck(
							lowThresholdValue, belowLowThresholdRIDNumber, 
							highThresholdValue, aboveHighThresholdRIDNumber, repetitionNumberCount);
	              		if(PMONbase->checkDefinition)
	              			delete PMONbase->checkDefinition;
	              		PMONbase->checkDefinition = (PMONCheck*)PMONlimitCheck;

				break;
			}
			case PMONCheck::DeltaCheck:
			{
				double lowDeltaThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t belowDeltaLowThresholdRIDNumber = message.readUint16();

				double highDeltaThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t aboveDeltaHighThresholdRIDNumber = message.readUint16();

				uint16_t deltaRepetitionNumberCount = message.readUint16();
				
	              		if(!newPMONdef)
	              			break;	
	              			
				if(lowDeltaThresholdValue > highDeltaThresholdValue){
					reportExecutionStartError(message, ErrorHandler::setInvalidMonitoringCheckDefinition);			
					return;
				}

				PMONDeltaCheck* PMONdeltaCheck = new PMONDeltaCheck(
							lowDeltaThresholdValue, belowDeltaLowThresholdRIDNumber, 
							highDeltaThresholdValue, aboveDeltaHighThresholdRIDNumber,
							repetitionNumberCount, deltaRepetitionNumberCount,
							parameter->get().getValueAsDouble());		
	              		if(PMONbase->checkDefinition)
	              			delete PMONbase->checkDefinition;
	              		PMONbase->checkDefinition = (PMONCheck*)PMONdeltaCheck;  

				break;
			}
			default:
				reportExecutionStartError(message, ErrorHandler::setNonExistingParameterMonitoringCheckDefinition);			
				return;
		}														
		if(newPMONdef){
			addPMONDefinition(currentId, std::reference_wrapper<PMONBase>(*PMONbase)) ;
		}else{
			reportExecutionStartError(message, ErrorHandler::setInvalidMonitoringCheckDefinitionAlreadyExists);
			bFaultStartExecution = true;
		}
	}			
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(message);

	reportSuccessCompletionExecutionVerification(message);
    }

    void OnBoardMonitoringService_impl::deleteParameterMonitoringDefinitions(Message& message)
    {
    	if (!d_message_parser->assertTC(message, serviceType, 
			OnBoardMonitoringService::MessageType::DeleteParameterMonitoringDefinitions)) {
		return;
	}

 	uint16_t tcSize = message.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < ONBOARD_MON_NUM_PMON){     
		reportAcceptanceError(message, ErrorHandler::InvalidLength);	
		return;
	} 	
	uint16_t numberOfPMONDefinitions = message.readUint16();
	
	tcSize -= ONBOARD_MON_NUM_PMON;

 	if(tcSize != numberOfPMONDefinitions * ONBOARD_MON_PMONID){     
		reportAcceptanceError(message, ErrorHandler::InvalidLength);	
		return;
	} 

	reportSuccessAcceptanceVerification(message);
	
	bool bFaultStartExecution = false;

	for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {
		uint16_t currentId = message.readUint16();

		if (hasNonExistingParameterMonitoringExecutionError(currentId , message)) {
			bFaultStartExecution = true;
			continue;
		}

		if (parameterMonitoringIsEnabledExecutionError(currentId , message)) {
			bFaultStartExecution = true;
			continue;
		}

		parameterMonitoringList.erase(currentId);
		
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(message);

	reportSuccessCompletionExecutionVerification(message);
    }

    void OnBoardMonitoringService_impl::modifyParameterMonitoringDefinitions(Message& message)
    {
    	if (!d_message_parser->assertTC(message, serviceType, 
			OnBoardMonitoringService::MessageType::ModifyParameterMonitoringDefinitions)) {
		return;
	}
 	
 	uint16_t tcSize = message.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < ONBOARD_MON_NUM_PMON){     
		reportAcceptanceError(message, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= ONBOARD_MON_NUM_PMON; 
 	
	uint16_t numberOfPMONDefinitions = message.readUint16();

 	uint16_t currentPosition = message.getMessageReadPosition();

	for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {

 		if(tcSize < (ONBOARD_MON_PMONID + ONBOARD_MON_PARAMID + ONBOARD_MON_COUNTER)){     
			reportAcceptanceError(message, ErrorHandler::InvalidLength);
			return;
		}		
 		tcSize -= (ONBOARD_MON_PMONID + ONBOARD_MON_PARAMID + ONBOARD_MON_COUNTER); 
		message.setMessageReadPosition(message.getMessageReadPosition() + ONBOARD_MON_PMONID);

		uint16_t paramId = message.readUint16();

		if (!d_parameter_pool->parameterExists(paramId)){
			reportSuccessAcceptanceVerification(message);
			reportExecutionStartError(message, ErrorHandler::GetNonExistingParameter);
			return;
		}
	
		auto parameter = d_parameter_pool->getParameter(paramId);
		
		message.setMessageReadPosition(message.getMessageReadPosition() + ONBOARD_MON_COUNTER);

		if(tcSize < ONBOARD_MON_DEF_TYPE){     
			reportAcceptanceError(message, ErrorHandler::InvalidLength);
			return;
		}		
 		tcSize -= ONBOARD_MON_DEF_TYPE;
		uint8_t checkType = message.readUint8();

		switch(checkType){
			case PMONCheck::ValueCheck:
			{
				uint16_t valueSize = 2 * parameter->get().appendValueToVector().size();
				if(tcSize < (valueSize + ONBOARD_MON_RID)){
					reportAcceptanceError(message, ErrorHandler::InvalidLength);
					return;
				}		
 				tcSize -= (valueSize + ONBOARD_MON_RID);
 				
				message.setMessageReadPosition(message.getMessageReadPosition() + valueSize + ONBOARD_MON_RID);
				break;
			}

			case PMONCheck::LimitCheck:
			{
				uint16_t valueSize = parameter->get().appendValueToVector().size();
				
				if(tcSize < 2 * (valueSize + ONBOARD_MON_RID)){
					reportAcceptanceError(message, ErrorHandler::InvalidLength);
					return;
				}		
 				tcSize -= (2 * (valueSize + ONBOARD_MON_RID));
 				
				message.setMessageReadPosition(message.getMessageReadPosition() + 2 * (valueSize + ONBOARD_MON_RID));

				break;
			}
			case PMONCheck::DeltaCheck:
			{
				uint16_t valueSize = parameter->get().appendValueToVector().size();
				
				if(tcSize < (2 * (valueSize + ONBOARD_MON_RID) + ONBOARD_MON_DELTA_COUNTER)){
					reportAcceptanceError(message, ErrorHandler::InvalidLength);
					return;
				}		
 				tcSize -= (2 * (valueSize + ONBOARD_MON_RID) + ONBOARD_MON_DELTA_COUNTER);
 				
				message.setMessageReadPosition(message.getMessageReadPosition() + 2 * (valueSize + ONBOARD_MON_RID) + ONBOARD_MON_DELTA_COUNTER);

				break;
			}
			default:
				reportSuccessAcceptanceVerification(message);
				reportExecutionStartError(message, ErrorHandler::setNonExistingParameterMonitoringCheckDefinition);			
				return;
		}														

	}	
	if (tcSize > 0){
		reportAcceptanceError(message, ErrorHandler::InvalidLength);
		return;
	}		

	message.setMessageReadPosition(currentPosition);	
	reportSuccessAcceptanceVerification(message);	
	
	bool bFaultStartExecution = false;
              
	for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {
		bool newPMONdef = false;
		bool wrongPMONdef = false;

		uint16_t currentId = message.readUint16();

		uint16_t paramId = message.readUint16();
						
		uint16_t repetitionNumberCount = message.readUint16();

		PMONBase* PMONbase;
		
		auto pmonbase = parameterMonitoringList.find(currentId);

		if(pmonbase == parameterMonitoringList.end()){
			newPMONdef = true;
        		PMONbase = new PMONBase(paramId, 0, repetitionNumberCount, false);
       	}else{
       		PMONbase = &pmonbase->second;
			if (PMONbase->monitoredParameterId != paramId){
				wrongPMONdef = true;
			}

       	}
       	
		auto parameter = d_parameter_pool->getParameter(paramId);
		
		uint8_t checkType = message.readUint8();
		
		switch(checkType){
			case PMONCheck::ValueCheck:
			{
				double maskValue = parameter->get().getValueAsDoubleFromMessage(message);
				double expectedThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t unexpectedRIDNumber = message.readUint16();
				
				if (wrongPMONdef){
					break;
				}

				PMONExpectedValueCheck* PMONexpectedValueCheck = new PMONExpectedValueCheck(maskValue,
							expectedThresholdValue,
	                                		unexpectedRIDNumber, repetitionNumberCount);	
	              		if(PMONbase->checkDefinition)
	              			delete PMONbase->checkDefinition;
	              		PMONbase->checkDefinition = (PMONCheck*)PMONexpectedValueCheck;

				break;
			}
			case PMONCheck::LimitCheck:
			{
				double lowThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t belowLowThresholdRIDNumber = message.readUint16();
				double highThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t aboveHighThresholdRIDNumber = message.readUint16();

				if(lowThresholdValue > highThresholdValue){
					reportExecutionStartError(message, ErrorHandler::setInvalidMonitoringCheckDefinition);			
					bFaultStartExecution = true;
					continue;
				}
				
				if (wrongPMONdef){
					break;
				}
				
				PMONLimitCheck* PMONlimitCheck = new PMONLimitCheck(
							lowThresholdValue, belowLowThresholdRIDNumber, 
							highThresholdValue, aboveHighThresholdRIDNumber, repetitionNumberCount);

	              		if(PMONbase->checkDefinition)
	              			delete PMONbase->checkDefinition;
	              		PMONbase->checkDefinition = (PMONCheck*)PMONlimitCheck;

	               	break;
			}
			case PMONCheck::DeltaCheck:
			{
				double lowDeltaThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t belowDeltaLowThresholdRIDNumber = message.readUint16();

				double highDeltaThresholdValue = parameter->get().getValueAsDoubleFromMessage(message);
				uint16_t aboveDeltaHighThresholdRIDNumber = message.readUint16();

				uint16_t deltaRepetitionNumberCount = message.readUint16();
	
				if(lowDeltaThresholdValue > highDeltaThresholdValue){
					reportExecutionStartError(message, ErrorHandler::setInvalidMonitoringCheckDefinition);			
					bFaultStartExecution = true;
					continue;
				}
				
				
				if (wrongPMONdef){
					break;
				}
				
				PMONDeltaCheck* PMONdeltaCheck = new PMONDeltaCheck(
							lowDeltaThresholdValue, belowDeltaLowThresholdRIDNumber, 
							highDeltaThresholdValue, aboveDeltaHighThresholdRIDNumber,
							repetitionNumberCount, deltaRepetitionNumberCount,
							parameter->get().getValueAsDouble());
	              		if(PMONbase->checkDefinition)
	              			delete PMONbase->checkDefinition;
	              		PMONbase->checkDefinition = (PMONCheck*)PMONdeltaCheck;  				
				
	               	break;				
			}
			default:
				reportExecutionStartError(message, ErrorHandler::setNonExistingParameterMonitoringCheckDefinition);			
				return;
		}														
		if(newPMONdef){
			reportExecutionStartError(message, ErrorHandler::GetNonExistingParameterMonitoringDefinition);
			bFaultStartExecution = true;
		}
		if(wrongPMONdef){
			reportExecutionStartError(message, ErrorHandler::invalidMonitoringCheckDefinitionWrongParameter);
			bFaultStartExecution = true;
		}
		PMONbase->repetitionNumber = repetitionNumberCount;
	}			
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(message);

	reportSuccessCompletionExecutionVerification(message);
    }
    
    void OnBoardMonitoringService_impl::reportParameterMonitoringDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::ReportParameterMonitoringDefinitions)) {
		return;
	}	

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	uint16_t numberOfPMONDefinitions = 0;
	if(tcSize > 0){
 		if(tcSize < ONBOARD_MON_NUM_PMON){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return;
		} 	

		numberOfPMONDefinitions = request.readUint16();
	
		tcSize -= ONBOARD_MON_NUM_PMON;

 		if(tcSize != numberOfPMONDefinitions * ONBOARD_MON_PMONID){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return;
		} 
	}
	reportSuccessAcceptanceVerification(request);
	
	std::vector<uint16_t> parametersList;
	
	bool bFaultStartExecution = false;			
	if(numberOfPMONDefinitions == 0){
		for (auto& currentParam: parameterMonitoringList) {
			parametersList.push_back(currentParam.first);
		}	
	}else{
		for (uint16_t i = 0; i < numberOfPMONDefinitions; i++) {
			uint16_t currentId = request.readUint16();
			auto definition = parameterMonitoringList.find(currentId);
			if (definition == parameterMonitoringList.end()) {
				reportExecutionStartError(request, ErrorHandler::GetNonExistingParameterMonitoringDefinition);
				bFaultStartExecution = true;
				continue;
			}
			parametersList.push_back(currentId);
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
	
	parameterMonitoringDefinitionReport(parametersList);
	
	reportSuccessCompletionExecutionVerification(request);	
    }
    
    void OnBoardMonitoringService_impl::parameterMonitoringDefinitionReport(std::vector<uint16_t> parameterList) {
        Message message = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			OnBoardMonitoringService::MessageType::ParameterMonitoringDefinitionReport, 
			counters[OnBoardMonitoringService::MessageType::ParameterMonitoringDefinitionReport], 0);
	
	message.appendUint16(maximumTransitionReportingDelay);
	message.appendUint16(parameterList.size());

	for (auto& currentPMON: parameterList) {
		auto currentParam = parameterMonitoringList.find(currentPMON);
		uint16_t currentId = currentParam->first;

		if (!d_parameter_pool->parameterExists(currentParam->second.monitoredParameterId)){
			return;
		}
		if (currentParam->second.checkDefinition == NULL){
			return;
		}
		
		auto parameter = d_parameter_pool->getParameter(currentParam->second.monitoredParameterId);

		message.appendUint16(currentId);
		message.appendUint16(currentParam->second.monitoredParameterId);
		message.appendUint16(currentParam->second.monitoringInterval);
		message.appendBoolean(currentParam->second.getDefinitionEnableStatus());	
		message.appendUint16(currentParam->second.repetitionNumber);	
		

			message.appendUint8(currentParam->second.checkDefinition->getType());	
               	switch(currentParam->second.checkDefinition->getType()){
               		case PMONCheck::CheckType::ValueCheck:
               		{
 					PMONExpectedValueCheck* expectedValueCheckBMON = 
 						static_cast<PMONExpectedValueCheck*>(currentParam->second.checkDefinition); 
					parameter->get().appendValueAsTypeToMessage(expectedValueCheckBMON->maskValue, message);
					parameter->get().appendValueAsTypeToMessage(expectedValueCheckBMON->expectedValue, message);
					message.appendUint16(expectedValueCheckBMON->unexpectedValueEvent);
               			break;
               		}
               		case PMONCheck::CheckType::LimitCheck:
               		{	
					PMONLimitCheck* limitCheckBMON = static_cast<PMONLimitCheck*>(currentParam->second.checkDefinition);
					parameter->get().appendValueAsTypeToMessage(limitCheckBMON->lowLimit, message);
					message.appendUint16(limitCheckBMON->belowLowLimitEvent);
					parameter->get().appendValueAsTypeToMessage(limitCheckBMON->highLimit, message);
					message.appendUint16(limitCheckBMON->aboveHighLimitEvent);
               			break;
               		}
               		case PMONCheck::CheckType::DeltaCheck:
               		{
					PMONDeltaCheck* deltaCheckBMON = static_cast<PMONDeltaCheck*>(currentParam->second.checkDefinition);
					parameter->get().appendValueAsTypeToMessage(deltaCheckBMON->lowDeltaThreshold, message);
					message.appendUint16(deltaCheckBMON->belowLowThresholdEvent);
					parameter->get().appendValueAsTypeToMessage(deltaCheckBMON->highDeltaThreshold, message);
					message.appendUint16(deltaCheckBMON->aboveHighThresholdEvent);
					message.appendUint16(deltaCheckBMON->consecutiveDelta);
               			break;
               		}

               	} 		

	}	

	d_message_parser->closeMessage(message);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));

        counters[OnBoardMonitoringService::MessageType::ParameterMonitoringDefinitionReport]++;
    }
        
    void OnBoardMonitoringService_impl::reportOutOfLimits(Message& request)
    {
    	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::ReportOutOfLimits)) {
		return;
	}	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 	
	
	reportSuccessAcceptanceVerification(request);
	
	reportSuccessStartExecutionVerification(request);
		
	outOfLimitsReport();
	
	reportSuccessCompletionExecutionVerification(request);
    }
    
    void OnBoardMonitoringService_impl::outOfLimitsReport()
    {
  	Message message = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			OnBoardMonitoringService::MessageType::OutOfLimitsReport, 
			counters[OnBoardMonitoringService::MessageType::OutOfLimitsReport], 0);
			
 	uint16_t outOfLimitsCounter = 0;
 	
	for (auto& currentParam: parameterMonitoringList) {
		if(!currentParam.second.getDefinitionEnableStatus())
			continue;
		 if(currentParam.second.checkDefinition){
		 	if(currentParam.second.checkDefinition->checkTransitionList[1] < PMONCheck::UnexpectedValue  ||
		 		currentParam.second.checkDefinition->checkTransitionList[1] == PMONCheck::CheckingStatus::WithinLimits ||
		 		currentParam.second.checkDefinition->checkTransitionList[1] == PMONCheck::CheckingStatus::WithinThreshold)
		 		continue;
			outOfLimitsCounter++;
		 }
	}

	message.appendUint16(outOfLimitsCounter);	
	
	for (auto& currentParam: parameterMonitoringList) {
		if(!currentParam.second.getDefinitionEnableStatus())
			continue;

		auto parameter = d_parameter_pool->getParameter(currentParam.second.monitoredParameterId);	
		
		if(currentParam.second.checkDefinition){

		 	if(currentParam.second.checkDefinition->checkTransitionList[1] < PMONCheck::UnexpectedValue  ||
		 		currentParam.second.checkDefinition->checkTransitionList[1] == PMONCheck::CheckingStatus::WithinLimits ||
		 		currentParam.second.checkDefinition->checkTransitionList[1] == PMONCheck::CheckingStatus::WithinThreshold)
		 		continue;
			
			message.appendUint16(currentParam.first);
			message.appendUint16(currentParam.second.monitoredParameterId);
			message.appendUint8(currentParam.second.checkDefinition->getType());
			if(currentParam.second.checkDefinition->getType() == 0){
				parameter->get().appendValueAsTypeToMessage(
				(static_cast<PMONExpectedValueCheck*>(currentParam.second.checkDefinition))->maskValue, message);
			}
			parameter->get().appendValueAsTypeToMessage(currentParam.second.checkDefinition->transitionValue, message);
			parameter->get().appendValueAsTypeToMessage(currentParam.second.checkDefinition->limitCrossedValue, message);
			message.appendUint8(currentParam.second.checkDefinition->checkTransitionList[0]);
			message.appendUint8(currentParam.second.checkDefinition->checkTransitionList[1]);
			message.appendUint32(currentParam.second.checkDefinition->transitionTime);
		}		

		
	}	  	
  	d_message_parser->closeMessage(message);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));

        counters[OnBoardMonitoringService::MessageType::OutOfLimitsReport]++;  
    }

    void OnBoardMonitoringService_impl::checkTransitionReport()
    {
  	MessageArray messageTransitionList(transitionList.data(), transitionList.data() + transitionList.size());  
  	Message message = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			OnBoardMonitoringService::MessageType::CheckTransitionReport, 
			counters[OnBoardMonitoringService::MessageType::CheckTransitionReport], 0);

	message.appendUint16(transitionsCounter);	

	message.appendUint8Array(messageTransitionList);

	transitionsCounter = 0;
	transitionList.clear();
	
	for (auto& currentParam: parameterMonitoringList) 
		if(currentParam.second.checkDefinition)
			currentParam.second.checkDefinition->clearDefinitionStatus();
	  	
  	d_message_parser->closeMessage(message);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));

        counters[OnBoardMonitoringService::MessageType::CheckTransitionReport]++;  
    }
    
    void OnBoardMonitoringService_impl::reportStatusOfParameterMonitoringDefinition(Message& request)
    {
    	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::ReportStatusOfParameterMonitoringDefinition)) {
		return;
	}	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 	
	
	reportSuccessAcceptanceVerification(request);
	
	reportSuccessStartExecutionVerification(request);
		
	parameterMonitoringDefinitionStatusReport();
	
	reportSuccessCompletionExecutionVerification(request);
    }
    
    void OnBoardMonitoringService_impl::parameterMonitoringDefinitionStatusReport()
    {
  	Message message = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			OnBoardMonitoringService::MessageType::ParameterMonitoringDefinitionStatusReport, 
			counters[OnBoardMonitoringService::MessageType::ParameterMonitoringDefinitionStatusReport], 0);

 	message.appendUint16(parameterMonitoringList.size());

	for (auto& currentParam: parameterMonitoringList) {
		uint16_t currentId = currentParam.first;

		message.appendUint16(currentId);
		message.appendUint8(currentParam.second.getDefinitionEnableStatus());	
	}
			
  	d_message_parser->closeMessage(message);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));

        counters[OnBoardMonitoringService::MessageType::ParameterMonitoringDefinitionStatusReport]++;  
    }

    void OnBoardMonitoringService_impl::enableParameterMonitoringFunction(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::EnableParameterMonitoringFunction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	
	reportSuccessAcceptanceVerification(request);

	reportSuccessStartExecutionVerification(request);
	
	parameterMonitoringFunctionStatus = true;  
	
	reportSuccessCompletionExecutionVerification(request);
    }        

    void OnBoardMonitoringService_impl::disableParameterMonitoringFunction(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			OnBoardMonitoringService::MessageType::DisableParameterMonitoringFunction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	
	reportSuccessAcceptanceVerification(request);

	reportSuccessStartExecutionVerification(request);
	
	parameterMonitoringFunctionStatus = false;  
	
	reportSuccessCompletionExecutionVerification(request);
    }  

  } /* namespace pus */
} /* namespace gr */
