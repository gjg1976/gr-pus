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
#include "HousekeepingService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    HousekeepingService::sptr
    HousekeepingService::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<HousekeepingService_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    HousekeepingService_impl::HousekeepingService_impl(const std::string& init_file)
      : gr::block("HousekeepingService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        
        d_parameter_pool = ParameterPool::getInstance();
        
        serviceType = ServiceType;
        for(size_t i = 0; i < HousekeepingService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);
        
        parse_json(init_file);

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
        
      	d_time_provider = TimeProvider::getInstance();
    
    	d_time_provider->addHandler(
            serviceType,
            std::bind(
                &HousekeepingService_impl::timerTick,
                this,
                std::placeholders::_1
            )
    	);      
    }

    /*
     * Our virtual destructor.
     */
    HousekeepingService_impl::~HousekeepingService_impl()
    {
        d_time_provider->removeHandler(serviceType);  
    }

    void HousekeepingService_impl::timerTick(TimeProvider *p) {
	for (auto& currentHKStructure: housekeepingStructures) {
		if(currentHKStructure.second.periodicGenerationActionStatus){
			if(++currentHKStructure.second.counterInterval >= currentHKStructure.second.collectionInterval){
				currentHKStructure.second.counterInterval = 0;
				housekeepingParametersReport(currentHKStructure.first);
			}
			for (auto& superid: currentHKStructure.second.superCommutatedArrays) {
				if(++superid.second.counterSuperConmutatedInterval >= 
					(currentHKStructure.second.collectionInterval / superid.second.superConmutatedInterval)){
					superid.second.counterSuperConmutatedInterval = 0;
					HousekeepingSuperConmutatedArrays::superConmutatedVector superConmutatedData;
					for (auto id: superid.second.superCommutatedParameterIds) {
						if (auto parameter = d_parameter_pool->getParameter(id)){
							std::vector<uint8_t> value = parameter->get().appendValueToVector();				superConmutatedData.insert(superConmutatedData.end(), value.begin(), value.end());
						}
					}
					superid.second.superCommutatedDataArray.push_back(superConmutatedData);
					if (superid.second.superCommutatedDataArray.size() > superid.second.superConmutatedInterval)
						superid.second.superCommutatedDataArray.pop_front();
				}
			}
		}
	}       
    }
   
    void HousekeepingService_impl::parse_json(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;
            for (auto& elem : json["housekeeping"]){
                uint8_t id = elem["id"];
                uint32_t interval = elem["interval"];
                HousekeepingStructure newStructure;
		 if (structExists(id)) {
				continue;
		 }
                newStructure.structureId = id;
                newStructure.collectionInterval = interval;
                newStructure.periodicGenerationActionStatus = elem["periodicEnabled"];

                uint16_t numParams = elem["numParams"];
                for(uint16_t i = 0; i < numParams; i++){
                	uint16_t newParamId = elem["Params"][i];
			if (!d_parameter_pool->parameterExists(newParamId)) {
				continue;
			}
                	newStructure.simplyCommutatedParameterIds.push_back(newParamId);
                }
               	
                for (auto& arrayElem : elem["SuperArrays"]){
                 	HousekeepingSuperConmutatedArrays newSuperConmutatedArray;
                 	uint8_t superConmutatedInterval = arrayElem["superRepetition"];
                	newSuperConmutatedArray.superConmutatedInterval = superConmutatedInterval;
                	uint8_t numParams = arrayElem["numParams"];
                	for(uint8_t i = 0; i < numParams; i++){
                		uint16_t newParamId = arrayElem["Params"][i];
				if (!d_parameter_pool->parameterExists(newParamId)) {
					continue;
				}
                		newSuperConmutatedArray.superCommutatedParameterIds.push_back(newParamId);
                	}     
                	newStructure.superCommutatedArrays.insert({superConmutatedInterval, newSuperConmutatedArray});
     		
                }
 
                housekeepingStructures.insert({id, newStructure});
            }
        } else {
            GR_LOG_WARN(d_logger, "No housekeeping init file found");
        }
        file.close();
    }  

    void HousekeepingService_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
#ifdef _PUS_DEBUG
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
#endif
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
                        case CreateHousekeepingReportStructure:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "CreateHousekeepingReportStructure");
#endif
                           createHousekeepingReportStructure(message);
                           break;
                        case DeleteHousekeepingReportStructure:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeleteHousekeepingReportStructure");
#endif
                           deleteHousekeepingReportStructure(message);
                           break;                                             
                        case EnablePeriodicHousekeepingParametersReport:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "EnablePeriodicHousekeepingParametersReport");
#endif
                           enablePeriodicHousekeepingParametersReport(message);
                           break;
                        case DisablePeriodicHousekeepingParametersReport:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DisablePeriodicHousekeepingParametersReport");
#endif
                           disablePeriodicHousekeepingParametersReport(message);
                           break;
                        case ReportHousekeepingStructures:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportHousekeepingStructures");
#endif
                           reportHousekeepingStructures(message);
                           break;
                        case GenerateOneShotHousekeepingReport:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "GenerateOneShotHousekeepingReport");
#endif
                           generateOneShotHousekeepingReport(message);
                           break;
                        case AppendParametersToHousekeepingStructure:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AppendParametersToHousekeepingStructure");
#endif
                           appendParametersToHousekeepingStructure(message);
                           break;
                        case ModifyCollectionIntervalOfStructures:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ModifyCollectionIntervalOfStructures");
#endif
                           modifyCollectionIntervalOfStructures(message);
                           break;
                        case ReportHousekeepingPeriodicProperties:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportHousekeepingPeriodicProperties");
#endif
                           reportHousekeepingPeriodicProperties(message);
                           break;
                           
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Housekeeping Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Housekeeping Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
#ifdef _PUS_DEBUG
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
#endif
        }
     }

    bool HousekeepingService_impl::hasAlreadyExistingStructError(uint8_t id, Message& req) 
    {
	if (structExists(id)) {
		reportExecutionStartError(req, ErrorHandler::RequestedAlreadyExistingStructure);
		return true;
	}
	return false;
    }

    bool HousekeepingService_impl::hasAlreadyExistingParameterError(HousekeepingStructure& housekeepingStruct, uint8_t id, 
    			Message& req) {
	if (existsInVector(housekeepingStruct.simplyCommutatedParameterIds, id)) {
		reportExecutionStartError(req, ErrorHandler::AlreadyExistingParameter);
		return true;
	}
	return false;
    }

    bool HousekeepingService_impl::hasAlreadyExistingSuperConmutatedParameterError(HousekeepingSuperConmutatedArrays& housekeepingSuperArray, uint8_t id, 
    			Message& req) {
	if (existsInVector(housekeepingSuperArray.superCommutatedParameterIds, id)) {
		reportExecutionStartError(req, ErrorHandler::AlreadyExistingParameter);
		return true;
	}
	return false;
    }

    bool HousekeepingService_impl::hasAlreadyExistingSuperConmutatedArray(HousekeepingStructure& housekeepingStruct, uint8_t superConmutatedInterval) {
	if (housekeepingStruct.superCommutatedArrays.find(superConmutatedInterval) != housekeepingStruct.superCommutatedArrays.end()) {
		return true;
	}
	return false;
    }
        
    bool HousekeepingService_impl::hasNonExistingStructExecutionError(uint8_t id, Message& req) {
	if (!structExists(id)) {
		reportExecutionStartError(req, ErrorHandler::RequestedNonExistingStructure);
		return true;
	}
	return false;
    }

    bool HousekeepingService_impl::hasRequestedDeletionOfEnabledHousekeepingError(uint8_t id, Message& req) {
	if (getPeriodicGenerationActionStatus(id)) {
		reportExecutionStartError(req, 
			ErrorHandler::RequestedDeletionOfEnabledHousekeeping);
		return true;
	}
	return false;
    }

    bool HousekeepingService_impl::hasNonExistingStructInternalError(uint8_t id) {
	if (!structExists(id)) {
		d_error_handler->reportInternalError(ErrorHandler::InternalErrorType::NonExistentHousekeeping);
		return true;
	}
	return false;
    } 
    
    bool HousekeepingService_impl::hasNonExistingStructError(uint8_t id, Message& req) {
	if (!structExists(id)) {
		reportExecutionStartError(req, 
			ErrorHandler::RequestedNonExistingStructure);
		return true;
	}
	return false;
    }   

    bool HousekeepingService_impl::hasRequestedAppendToEnabledHousekeepingError(HousekeepingStructure& housekeepingStruct, Message& req
   							) {
	if (housekeepingStruct.periodicGenerationActionStatus) {
		reportExecutionStartError(req, 
				ErrorHandler::RequestedAppendToEnabledHousekeeping);
		return true;
	}
	return false;
    } 
    
    bool HousekeepingService_impl::hasExceededMaxNumOfSimplyCommutatedParamsError(HousekeepingStructure& housekeepingStruct, Message& req) {
	if (housekeepingStruct.simplyCommutatedParameterIds.size() >= ECSSMaxSimplyCommutatedParameters) {
		reportExecutionStartError(req, 
				ErrorHandler::ExecutionStartErrorType::ExceededMaxNumberOfSimplyCommutatedParameters);
		return true;
	}
	return false;
    }   
    
    bool HousekeepingService_impl::hasExceededMaxNumOfHousekeepingStructsError(Message& req) {
	if (housekeepingStructures.size() >= ECSSMaxHousekeepingStructures) {
		reportExecutionStartError(req, 
				ErrorHandler::ExecutionStartErrorType::ExceededMaxNumberOfHousekeepingStructures);
		return true;
	}
	return false;
    }  
    
    bool HousekeepingService_impl::housekeepingReportStructureSizeVerification(Message& request, bool intervalSizePresent) {  
 	uint16_t currentPosition = request.getMessageReadPosition();
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	uint16_t intevalSize = HK_STRUCT_INTERVAL_SIZE;
 	
 	if(tcSize < HK_STRUCT_ID_SIZE + HK_STRUCT_INTERVAL_SIZE + HK_STRUCT_NUM_PARAM_SIZE + HK_STRUCT_NUM_FIXED_ARRAY_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return false;
	}
	if(not intervalSizePresent){
		intevalSize = 0;
	}
 	tcSize -= (HK_STRUCT_ID_SIZE + intevalSize + HK_STRUCT_NUM_PARAM_SIZE + HK_STRUCT_NUM_FIXED_ARRAY_SIZE);
	
	request.setMessageReadPosition(request.getMessageReadPosition() + HK_STRUCT_ID_SIZE + intevalSize);

	uint16_t numOfSimplyCommutatedParams = request.readUint16();	
 	
 	if(tcSize < numOfSimplyCommutatedParams * HK_STRUCT_PARAM_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return false;
	}
	tcSize -= (numOfSimplyCommutatedParams * HK_STRUCT_PARAM_SIZE);

	request.setMessageReadPosition(request.getMessageReadPosition() + numOfSimplyCommutatedParams * HK_STRUCT_PARAM_SIZE);

	uint16_t numOfSuperCommutatedArrays = request.readUint16();	
	
	uint16_t superConmutatedSize = tcSize;
	uint16_t superConmutatedCumulativeSize = 0;

	for(uint16_t i = 0; i < numOfSuperCommutatedArrays; i++){
		if(tcSize >= (HK_STRUCT_SUPER_CONMUTATED_REPETITION_SIZE + HK_STRUCT_NUM_SUPER_CONMUTATED_ARRAY_SIZE)){  
			tcSize -= HK_STRUCT_SUPER_CONMUTATED_REPETITION_SIZE + HK_STRUCT_NUM_SUPER_CONMUTATED_ARRAY_SIZE;
			superConmutatedCumulativeSize += HK_STRUCT_SUPER_CONMUTATED_REPETITION_SIZE + HK_STRUCT_NUM_SUPER_CONMUTATED_ARRAY_SIZE;
			
 			request.setMessageReadPosition(request.getMessageReadPosition() + HK_STRUCT_SUPER_CONMUTATED_REPETITION_SIZE);
 			
 			uint8_t numOfSuperCommutatedParams = request.readUint8();	
			
			if(tcSize < numOfSuperCommutatedParams * HK_STRUCT_PARAM_SIZE){  
				reportAcceptanceError(request, ErrorHandler::InvalidLength);
				return false;
			}
			superConmutatedCumulativeSize += numOfSuperCommutatedParams * HK_STRUCT_PARAM_SIZE;
			request.setMessageReadPosition(request.getMessageReadPosition() + numOfSuperCommutatedParams * HK_STRUCT_PARAM_SIZE);
		}else{
			reportAcceptanceError(request, ErrorHandler::InvalidLength);
			return false;		
		}	
	}

	if(superConmutatedSize != superConmutatedCumulativeSize){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return false;
	}
	request.setMessageReadPosition(currentPosition);	
	return true;    
    }         
/****************************************************************************************************************/    
    
    void HousekeepingService_impl::createHousekeepingReportStructure(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::CreateHousekeepingReportStructure)) {
		return;
	}

	if(not housekeepingReportStructureSizeVerification(request, true))
		return;

	reportSuccessAcceptanceVerification(request);
	
	uint8_t idToCreate = request.readUint8();	
 	
	HousekeepingStructure newStructure;
	newStructure.structureId = idToCreate;
	
	newStructure.collectionInterval = request.readUint16();
	newStructure.periodicGenerationActionStatus = false;

	uint16_t numOfSimplyCommutatedParams = request.readUint16();	

	if (hasAlreadyExistingStructError(idToCreate, request)) {
		return;
	}
	
	if (hasExceededMaxNumOfHousekeepingStructsError(request)) {
		return;
	}
        			
	for (uint16_t i = 0; i < numOfSimplyCommutatedParams; i++) {
		uint16_t newParamId = request.readUint16();	

		if (!d_parameter_pool->parameterExists(newParamId)) {
			reportExecutionStartError(request, ErrorHandler::GetNonExistingParameter);
			return;
		}
		
		if (hasAlreadyExistingParameterError(newStructure, newParamId, request)) 
			return;
	
		newStructure.simplyCommutatedParameterIds.push_back(newParamId);
	}

	uint16_t numOfSuperCommutatedArrays = request.readUint16();		
	
	for (uint16_t i = 0; i < numOfSuperCommutatedArrays; i++) {
		uint8_t superConmutatedInterval = request.readUint8();	
		
		HousekeepingSuperConmutatedArrays *newSuperConmutatedArray = new HousekeepingSuperConmutatedArrays();
		
		newSuperConmutatedArray->superConmutatedInterval = superConmutatedInterval;
		
		uint8_t numOfSuperCommutatedParams = request.readUint8();	

		for (uint8_t j = 0; j < numOfSuperCommutatedParams; j++) {				
			uint16_t newParamId = request.readUint16();	

			if (!d_parameter_pool->parameterExists(newParamId)) {
				reportExecutionStartError(request, ErrorHandler::GetNonExistingParameter);
				return;
			}
		
			if (hasAlreadyExistingSuperConmutatedParameterError(newSuperConmutatedArray[0], newParamId, request)) 
				return;
				
			newSuperConmutatedArray->superCommutatedParameterIds.push_back(newParamId);
		}

		newStructure.superCommutatedArrays.insert({superConmutatedInterval, newSuperConmutatedArray[0]});
	}
		
        reportSuccessStartExecutionVerification(request);
			
	housekeepingStructures.insert({idToCreate, newStructure});

	reportSuccessCompletionExecutionVerification(request);

    }

    void HousekeepingService_impl::deleteHousekeepingReportStructure(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::DeleteHousekeepingReportStructure)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < HK_STRUCT_NUM_PARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= HK_NUM_STRUCT_SIZE;   

	uint8_t numOfStructuresToDelete = request.readUint8();	

 	if(tcSize != numOfStructuresToDelete * HK_STRUCT_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;
				
	for (uint8_t i = 0; i < numOfStructuresToDelete; i++) {
		uint8_t structureId = request.readUint8();	

		if (hasNonExistingStructExecutionError(structureId, request)) {
			bFaultStartExecution = true;
			continue;
		}

		if (hasRequestedDeletionOfEnabledHousekeepingError(structureId, request)){
			bFaultStartExecution = true;
			continue;
		}
						
		housekeepingStructures.erase(structureId);

	} 
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void HousekeepingService_impl::enablePeriodicHousekeepingParametersReport(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::EnablePeriodicHousekeepingParametersReport)) {
		return;
	}
        
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < HK_STRUCT_NUM_PARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= HK_NUM_STRUCT_SIZE;   

	uint8_t numOfStructIds = request.readUint8();	

 	if(tcSize != numOfStructIds * HK_STRUCT_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;
	
	for (uint8_t i = 0; i < numOfStructIds; i++) {
		uint8_t structIdToEnable = request.readUint8();	

		if (hasNonExistingStructExecutionError(structIdToEnable, request))  {
			bFaultStartExecution = true;
			continue;
		}		
		setPeriodicGenerationActionStatus(structIdToEnable, true);
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);

	reportSuccessCompletionExecutionVerification(request);
    }

    void HousekeepingService_impl::disablePeriodicHousekeepingParametersReport(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::DisablePeriodicHousekeepingParametersReport)) {
		return;
	}
        
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < HK_STRUCT_NUM_PARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= HK_NUM_STRUCT_SIZE;   

	uint8_t numOfStructIds = request.readUint8();	

 	if(tcSize != numOfStructIds * HK_STRUCT_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;
	
	for (uint8_t i = 0; i < numOfStructIds; i++) {
		uint8_t structIdToDisable = request.readUint8();	

		if (hasNonExistingStructExecutionError(structIdToDisable, request))  {
			bFaultStartExecution = true;
			continue;
		}		
		setPeriodicGenerationActionStatus(structIdToDisable, false);
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);

	reportSuccessCompletionExecutionVerification(request);
    }

    void HousekeepingService_impl::reportHousekeepingStructures(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::ReportHousekeepingStructures)) {
		return;
	}
        
        
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < HK_STRUCT_NUM_PARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= HK_NUM_STRUCT_SIZE;   

	uint8_t numOfStructsToReport = request.readUint8();

 	if(tcSize != numOfStructsToReport * HK_STRUCT_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	bool bFaultStartExecution = false;
		
	for (uint8_t i = 0; i < numOfStructsToReport; i++) {
		uint8_t structureId = request.readUint8();

		if (hasNonExistingStructExecutionError(structureId, request)) {
			bFaultStartExecution = true;
			continue;
		}
				
		housekeepingStructureReport(structureId);
		
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void HousekeepingService_impl::housekeepingStructureReport(uint8_t structIdToReport) {
	auto housekeepingStructure = housekeepingStructures.find(structIdToReport);
	if (hasNonExistingStructInternalError(structIdToReport)) {
		return;
	}

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			HousekeepingService::MessageType::HousekeepingStructuresReport, 
			counters[HousekeepingService::MessageType::HousekeepingStructuresReport], 0);

        report.appendUint8(structIdToReport);
        report.appendBoolean(housekeepingStructure->second.periodicGenerationActionStatus);
        report.appendUint16(housekeepingStructure->second.collectionInterval);
 	
        report.appendUint16(housekeepingStructure->second.simplyCommutatedParameterIds.size());   
        
	for (auto parameterId: housekeepingStructure->second.simplyCommutatedParameterIds) {
		report.appendUint16(parameterId);  		
	}
	report.appendUint16(housekeepingStructure->second.superCommutatedArrays.size());   
	for (auto superArray: housekeepingStructure->second.superCommutatedArrays) {
		report.appendUint8(superArray.second.superConmutatedInterval);
		report.appendUint8(superArray.second.superCommutatedParameterIds.size());  
		for (auto parameterId: superArray.second.superCommutatedParameterIds) {
			report.appendUint16(parameterId);  		
		}		

	}			    
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[HousekeepingService::MessageType::HousekeepingStructuresReport]++;

    }

    void HousekeepingService_impl::housekeepingParametersReport(uint8_t structureId) {
	if (hasNonExistingStructInternalError(structureId)) {
		return;
	}

	auto& housekeepingStructure = getStruct(structureId)->get();

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			HousekeepingService::MessageType::HousekeepingParametersReport, 
			counters[HousekeepingService::MessageType::HousekeepingParametersReport], 0);
			
        report.appendUint8(structureId);
        
	for (auto id: housekeepingStructure.simplyCommutatedParameterIds) {
		if (auto parameter = d_parameter_pool->getParameter(id)) {
		 	parameter->get().appendValueToMessage(report);

		}
	}
	for (auto superid: housekeepingStructure.superCommutatedArrays) {
		if (superid.second.superCommutatedDataArray.size() < superid.second.superConmutatedInterval){
			for(uint16_t i = superid.second.superCommutatedDataArray.size();
				i < superid.second.superConmutatedInterval; i++){
					HousekeepingSuperConmutatedArrays::superConmutatedVector superConmutatedData;
					for (auto id: superid.second.superCommutatedParameterIds) {
						if (auto parameter = d_parameter_pool->getParameter(id)){
							std::vector<uint8_t> value = parameter->get().appendValueToVector();				superConmutatedData.insert(superConmutatedData.end(), value.begin(), value.end());
						}
					}
					superid.second.superCommutatedDataArray.push_back(superConmutatedData);
				}
				
		}
		for (auto superArray: superid.second.superCommutatedDataArray) {
			MessageArray payloadSuperArray;
			for(auto b: superArray)
				payloadSuperArray.push_back(b);
			report.appendUint8Array(payloadSuperArray);
		}
	
	}

	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[HousekeepingService::MessageType::HousekeepingParametersReport]++;


    }

    void HousekeepingService_impl::generateOneShotHousekeepingReport(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::GenerateOneShotHousekeepingReport)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < HK_STRUCT_NUM_PARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
 	tcSize -= HK_NUM_STRUCT_SIZE;   

	uint8_t numOfStructsToReport = request.readUint8();

 	if(tcSize != numOfStructsToReport * HK_STRUCT_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;
		
	for (uint8_t i = 0; i < numOfStructsToReport; i++) {
		uint8_t structureId = request.readUint8();

		if (hasNonExistingStructExecutionError(structureId, request)) {
			bFaultStartExecution = true;
			continue;
		}
						
		housekeepingParametersReport(structureId);

	}


	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void HousekeepingService_impl::appendParametersToHousekeepingStructure(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::AppendParametersToHousekeepingStructure)) {
		return;
	}

	if(not housekeepingReportStructureSizeVerification(request, false))
		return;

	reportSuccessAcceptanceVerification(request);

	uint8_t targetStructId  = request.readUint8();

	if (hasNonExistingStructExecutionError(targetStructId, request)) {
		return;
	}

	
	auto& housekeepingStructure = getStruct(targetStructId)->get();
	if (hasRequestedAppendToEnabledHousekeepingError(housekeepingStructure, request)) {
		return;
	}

 	uint16_t currentPosition = request.getMessageReadPosition();
 			
	uint16_t numOfSimplyCommutatedParameters = request.readUint16();
       
        HousekeepingStructure newStructure;
        
	for (uint16_t i = 0; i < numOfSimplyCommutatedParameters; i++) {
		uint16_t newParamId = request.readUint16();
		
		if (!d_parameter_pool->parameterExists(newParamId)) {
			reportExecutionStartError(request, ErrorHandler::GetNonExistingParameter);
			return;
		}
		if (hasAlreadyExistingParameterError(housekeepingStructure, newParamId, request))
			return;
		
		if (hasAlreadyExistingParameterError(newStructure, newParamId, request)) 
			return;
	
		newStructure.simplyCommutatedParameterIds.push_back(newParamId);
	}

	uint16_t numOfSuperCommutatedArrays = request.readUint16();	

	for (uint16_t i = 0; i < numOfSuperCommutatedArrays; i++) {
		uint8_t superConmutatedInterval = request.readUint8();
		HousekeepingSuperConmutatedArrays *newSuperConmutatedArray = new HousekeepingSuperConmutatedArrays();
		HousekeepingSuperConmutatedArrays *existingSuperConmutatedArray = NULL;

		if (hasAlreadyExistingSuperConmutatedArray(housekeepingStructure, superConmutatedInterval))
			existingSuperConmutatedArray = &housekeepingStructure.superCommutatedArrays.find(superConmutatedInterval)->second;

		uint8_t numOfSuperCommutatedParams = request.readUint8();

		for (uint8_t j = 0; j < numOfSuperCommutatedParams; j++) {				
			uint16_t newParamId = request.readUint16();
			
			if (!d_parameter_pool->parameterExists(newParamId)) {
				reportExecutionStartError(request, ErrorHandler::GetNonExistingParameter);
				return;
			}
			
			if (hasAlreadyExistingSuperConmutatedParameterError(*newSuperConmutatedArray, newParamId, request)) 
				return;
			
			if (existingSuperConmutatedArray)
				if(hasAlreadyExistingSuperConmutatedParameterError(*existingSuperConmutatedArray, newParamId, request)) 
					return;
			
			newSuperConmutatedArray->superCommutatedParameterIds.push_back(newParamId);
		}

	}
	request.setMessageReadPosition(currentPosition);	
	
	reportSuccessStartExecutionVerification(request);

	numOfSimplyCommutatedParameters = request.readUint16();
  
	for (uint16_t i = 0; i < numOfSimplyCommutatedParameters; i++) {
		uint16_t newParamId = request.readUint16();
			
		housekeepingStructure.simplyCommutatedParameterIds.push_back(newParamId);
	}

	numOfSuperCommutatedArrays = request.readUint16();

	for (uint16_t i = 0; i < numOfSuperCommutatedArrays; i++) {
		HousekeepingSuperConmutatedArrays superConmutatedArray;
		uint8_t superConmutatedInterval = request.readUint8();
		HousekeepingSuperConmutatedArrays* newSuperConmutatedArray = &superConmutatedArray;

		if (hasAlreadyExistingSuperConmutatedArray(housekeepingStructure, superConmutatedInterval))
			newSuperConmutatedArray = &housekeepingStructure.superCommutatedArrays.find(superConmutatedInterval)->second;

		newSuperConmutatedArray->superConmutatedInterval = superConmutatedInterval;

		uint8_t numOfSuperCommutatedParams = request.readUint8();

		for (uint8_t j = 0; j < numOfSuperCommutatedParams; j++) {				
			uint16_t newParamId = request.readUint16();
	
			newSuperConmutatedArray->superCommutatedParameterIds.push_back(newParamId);

		}
		
		if (not hasAlreadyExistingSuperConmutatedArray(housekeepingStructure, superConmutatedInterval)){		
			housekeepingStructure.superCommutatedArrays.insert({superConmutatedInterval, *newSuperConmutatedArray});
			}
	
	}
	
	reportSuccessCompletionExecutionVerification(request);
    }

    void HousekeepingService_impl::modifyCollectionIntervalOfStructures(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::ModifyCollectionIntervalOfStructures)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < HK_STRUCT_NUM_PARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}
	
 	tcSize -= HK_NUM_STRUCT_SIZE;   

	uint8_t numOfTargetStructs = request.readUint8();

 	if(tcSize != numOfTargetStructs * (HK_STRUCT_SIZE + HK_STRUCT_INTERVAL_SIZE)){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);			
		return;
	}

	reportSuccessAcceptanceVerification(request);
		
	bool bFaultStartExecution = false;
	
	for (uint8_t i = 0; i < numOfTargetStructs; i++) {
		uint8_t targetStructId = request.readUint8();
		uint16_t newCollectionInterval = request.readUint16();
		
		if (hasNonExistingStructExecutionError(targetStructId, request))  {
			bFaultStartExecution = true;
			continue;
		}
						
		setCollectionInterval(targetStructId, newCollectionInterval);

	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
	
	reportSuccessCompletionExecutionVerification(request);
    }

    void HousekeepingService_impl::reportHousekeepingPeriodicProperties(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			HousekeepingService::MessageType::ReportHousekeepingPeriodicProperties)) {
		return;
	}
        
 	uint16_t currentPosition = request.getMessageReadPosition();
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < HK_NUM_STRUCT_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}
	
 	tcSize -= HK_NUM_STRUCT_SIZE;   

	uint8_t numOfStructIds = request.readUint8();

 	if(tcSize != numOfStructIds * HK_STRUCT_ID_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	uint8_t numOfValidIds = 0;
	for (uint8_t i = 0; i < numOfStructIds; i++) {
		uint8_t structIdToReport = request.readUint8();
		if (structExists(structIdToReport)) {
			numOfValidIds++;
		}
	}
			
	request.setMessageReadPosition(currentPosition + HK_STRUCT_ID_SIZE);
        
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			HousekeepingService::MessageType::HousekeepingPeriodicPropertiesReport, 
			counters[HousekeepingService::MessageType::HousekeepingPeriodicPropertiesReport], 0);

        report.appendUint8(numOfValidIds);

	bool bFaultStartExecution = false;
	        
	for (uint8_t i = 0; i < numOfStructIds; i++) {
		uint8_t structIdToReport = request.readUint8();

		if (hasNonExistingStructExecutionError(structIdToReport, request)){		
			bFaultStartExecution = true;
			continue;
		}

        	report.appendUint8(structIdToReport);
        	report.appendBoolean(getPeriodicGenerationActionStatus(structIdToReport));
        	report.appendUint16(getCollectionInterval(structIdToReport));

 
 	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
					    
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[HousekeepingService::MessageType::HousekeepingPeriodicPropertiesReport]++;

	reportSuccessCompletionExecutionVerification(request);
    }
               
  } /* namespace pus */
} /* namespace gr */
