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
#include "ParameterStatisticsService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    ParameterStatisticsService::sptr
    ParameterStatisticsService::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<ParameterStatisticsService_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    ParameterStatisticsService_impl::ParameterStatisticsService_impl(const std::string& init_file)
      : gr::block("ParameterStatisticsService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();

        d_parameter_pool = ParameterPool::getInstance();
        d_time_provider = TimeProvider::getInstance();
                
        serviceType = ServiceType;
        for(size_t i = 0; i < ParameterStatisticsService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);
        
        reportingIntervalMs = 0;
        periodicStatisticsReportingStatus = false;
        
        parse_json(init_file);

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
 	
 	evaluationStartTime = TimeGetter::getCurrentTimeDefaultCUC();
    
    	d_time_provider->addHandler(
            serviceType,
            std::bind(
                &ParameterStatisticsService_impl::timerTick,
                this,
                std::placeholders::_1
            )
    	); 
    }

    /*
     * Our virtual destructor.
     */
    ParameterStatisticsService_impl::~ParameterStatisticsService_impl()
    {
            d_time_provider->removeHandler(serviceType);  
    }
 
    void ParameterStatisticsService_impl::timerTick(TimeProvider *p) {

        for (auto& currentParam: statisticsMap) {
        	uint16_t currentId = currentParam.first;
		if(++currentParam.second.samplingIntervalCounter > currentParam.second.selfSamplingInterval){
		        currentParam.second.samplingIntervalCounter = 0;

			if (auto parameter = ParameterPool::getInstance()->getParameter(currentId)) {
		 		currentParam.second.updateStatistics(parameter->get().getValueAsDouble());
			}
		}
        }
            
        if(!periodicStatisticsReportingStatus)
            	return;
            	 

        if(++counterIntervalMs > reportingIntervalMs){
               //printf("Reporting \n");
            	counterIntervalMs = 0;
            	parameterStatisticsReport(); 
        }
    }

    void ParameterStatisticsService_impl::parse_json(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;

            if (json["periodicEnabled"]){
		if(d_time_provider->getTimerResolutionMs() != 0){
			periodicStatisticsReportingStatus = true;

			reportingIntervalMs = (uint32_t) (MinimumSamplingParameterInterval * 1000/d_time_provider->getTimerResolutionMs());
		}
	    }

            for (auto& elem : json["statistics"]){

		uint16_t currentId = elem["id"];
		uint16_t interval = elem["interval"];
		if (!d_parameter_pool->parameterExists(currentId))
			continue;
		bool exists = statisticsMap.find(currentId) != statisticsMap.end();

		if (not exists) {
			if (statisticsMap.size() >= ECSSMaxStatisticParameters) 
				break;
			Statistic newStatistic;
			newStatistic.setSelfSamplingInterval(interval);
			statisticsMap.insert({currentId, newStatistic});
		} else {
			statisticsMap.at(currentId).setSelfSamplingInterval(interval);
			statisticsMap.at(currentId).resetStatistics();
		}
            }
        } else {
            GR_LOG_WARN(d_logger, "No statistic init file found");
        }
        file.close();
    }  
        
    void ParameterStatisticsService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case ReportParameterStatistics:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportParameterStatistics");
#endif
                           reportParameterStatistics(message);
                           break;
                        case ResetParameterStatistics:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ResetParameterStatistics");
#endif
                           resetParameterStatistics(message);
                         //  currentTime = getCurrentTime();
                           break;
                        case EnablePeriodicParameterReporting:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "EnablePeriodicParameterReporting");
#endif
			 //   currentTime = getCurrentTime();
			    enablePeriodicStatisticsReporting(message);
                           break;
                        case DisablePeriodicParameterReporting:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DisablePeriodicParameterReporting");
#endif
			    disablePeriodicStatisticsReporting(message);
                           break;
                        case AddOrUpdateParameterStatisticsDefinitions:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "AddOrUpdateParameterStatisticsDefinitions");
#endif
			    addOrUpdateStatisticsDefinitions(message);
                           break;
                        case DeleteParameterStatisticsDefinitions:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "DeleteParameterStatisticsDefinitions");
#endif
	      		    deleteStatisticsDefinitions(message);
                           break;
                        case ReportParameterStatisticsDefinitions:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "ReportParameterStatisticsDefinitions");
#endif
		//	    currentTime = getCurrentTime();
			    reportStatisticsDefinitions(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Parameter Statistics Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);
			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Parameter Statistics Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

     void ParameterStatisticsService_impl::parameterStatisticsReport() {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			ParameterStatisticsService::MessageType::ParameterStatisticsReport, 
			counters[ParameterStatisticsService::MessageType::ParameterStatisticsReport], 0);
			
	report.appendData(evaluationStartTime);
	auto evaluationStopTime = TimeGetter::getCurrentTimeDefaultCUC();
	report.appendData(evaluationStopTime);

	uint16_t numOfValidParameters = 0;
	for (auto& currentStatistic: statisticsMap) {
		uint16_t numOfSamples = currentStatistic.second.sampleCounter;
		if (numOfSamples == 0) {
			continue;
		}
		numOfValidParameters++;
	}

        report.appendUint16(numOfValidParameters);   

	for (auto& currentStatistic: statisticsMap) {
		uint16_t currentId = currentStatistic.first;
		uint16_t numOfSamples = currentStatistic.second.sampleCounter;
		if (numOfSamples == 0) {
			continue;
		}

		report.appendUint16(currentId);  

		report.appendUint16(numOfSamples); 

		currentStatistic.second.appendStatisticsToMessage(report, currentId);
	}

	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
                				
        counters[ParameterStatisticsService::MessageType::ParameterStatisticsReport]++;

    }

    void ParameterStatisticsService_impl::resetParameterStatistics() {
	for (auto& it: statisticsMap) {
		it.second.resetStatistics();
	}
	evaluationStartTime = TimeGetter::getCurrentTimeDefaultCUC();
    }


    void ParameterStatisticsService_impl::statisticsDefinitionsReport() {
        Message message = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			ParameterStatisticsService::MessageType::ParameterStatisticsDefinitionsReport, 
			counters[ParameterStatisticsService::MessageType::ParameterStatisticsDefinitionsReport], 0);

	uint32_t currentReportingIntervalMs = 0;
	if (periodicStatisticsReportingStatus) {
		currentReportingIntervalMs = (uint32_t) (reportingIntervalMs * d_time_provider->getTimerResolutionMs()/1000);
	}
	
	message.appendUint32(currentReportingIntervalMs); 

	message.appendUint16(statisticsMap.size());
	 
	for (auto& currentParam: statisticsMap) {
		uint16_t currentId = currentParam.first;
		uint32_t samplingInterval = currentParam.second.selfSamplingInterval;
		message.appendUint16(currentId);

		if (supportsSamplingInterval) {
			message.appendUint32(samplingInterval);
		}
	}
	
	d_message_parser->closeMessage(message);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));

        counters[ParameterStatisticsService::MessageType::ParameterStatisticsDefinitionsReport]++;
    }

    void ParameterStatisticsService_impl::reportParameterStatistics(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterStatisticsService::MessageType::ReportParameterStatistics)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != PARAM_STATS_RESET_FLAG_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 
	
	reportSuccessAcceptanceVerification(request);
	
	bool reset = request.readBoolean();

	reportSuccessStartExecutionVerification(request);
	
	parameterStatisticsReport();

	if (hasAutomaticStatisticsReset or reset) {
		resetParameterStatistics();
	}

	reportSuccessCompletionExecutionVerification(request);
     }

    void ParameterStatisticsService_impl::resetParameterStatistics(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterStatisticsService::MessageType::ResetParameterStatistics)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
		
	reportSuccessAcceptanceVerification(request);

	reportSuccessStartExecutionVerification(request);
		
	resetParameterStatistics();
	
	reportSuccessCompletionExecutionVerification(request);
    }

    void ParameterStatisticsService_impl::enablePeriodicStatisticsReporting(Message& request) {
	Time::RelativeTime constexpr SamplingParameterInterval = MinimumSamplingParameterInterval;

	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterStatisticsService::MessageType::EnablePeriodicParameterReporting)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != PARAM_STATS_RELATIVE_TIME_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);
		
	uint32_t timeInterval = request.readUint32();
		
	if (timeInterval < SamplingParameterInterval) {
		reportExecutionStartError(request, ErrorHandler::InvalidSamplingRateError);
	}else{
		periodicStatisticsReportingStatus = true;
		reportingIntervalMs = (uint32_t) (timeInterval * 1000/d_time_provider->getTimerResolutionMs());
	}
	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void ParameterStatisticsService_impl::disablePeriodicStatisticsReporting(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterStatisticsService::MessageType::DisablePeriodicParameterReporting)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);

	reportSuccessStartExecutionVerification(request);
		
	periodicStatisticsReportingStatus = false;
	reportingIntervalMs = 0;
	
	reportSuccessCompletionExecutionVerification(request);	
    }

    void ParameterStatisticsService_impl::addOrUpdateStatisticsDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterStatisticsService::MessageType::AddOrUpdateParameterStatisticsDefinitions)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < PARAM_STATS_NUMPARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 	
	uint16_t numOfIds = request.readUint16();
	
	tcSize -= PARAM_STATS_NUMPARAM_SIZE;

 	if(tcSize != numOfIds * (PARAM_STATS_PARAMID_SIZE + PARAM_STATS_RELATIVE_TIME_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 
		
	reportSuccessAcceptanceVerification(request);
		
	bool bFaultStartExecution = false;

	for (uint16_t i = 0; i < numOfIds; i++) {
		uint16_t currentId = request.readUint16();

		if (!d_parameter_pool->parameterExists(currentId)) {
			reportExecutionStartError(request,
					ErrorHandler::SetNonExistingParameter);
			if (supportsSamplingInterval) {
				request.setMessageReadPosition(request.getMessageReadPosition()+4);
			}
			bFaultStartExecution = true;
			continue;
		}

		bool exists = statisticsMap.find(currentId) != statisticsMap.end();
		uint32_t interval = 0;
		if (supportsSamplingInterval) {
			interval = request.readUint32();
			if ((interval * 1000 / d_time_provider->getTimerResolutionMs()) < reportingIntervalMs ) {
				reportExecutionStartError(request,
						ErrorHandler::InvalidSamplingRateError);
			        bFaultStartExecution = true;
			        continue;
			}

		}
		if (not exists) {
			if (statisticsMap.size() >= ECSSMaxStatisticParameters) {
				reportExecutionStartError(request, 
				                          ErrorHandler::MaxStatisticDefinitionsReached);
			        bFaultStartExecution = true;
			        continue;
			}
			Statistic newStatistic;
			if (supportsSamplingInterval) {
				newStatistic.setSelfSamplingInterval(interval);
			}
			statisticsMap.insert({currentId, newStatistic});
			// TODO: start the evaluation of statistics for this parameter.
		} else {
			if (supportsSamplingInterval) {
				statisticsMap.at(currentId).setSelfSamplingInterval(interval);
			}
			statisticsMap.at(currentId).resetStatistics();
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);
    }

    void ParameterStatisticsService_impl::deleteStatisticsDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterStatisticsService::MessageType::DeleteParameterStatisticsDefinitions)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < PARAM_STATS_NUMPARAM_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 	
	uint16_t numOfIds = request.readUint16();
	
	tcSize -= PARAM_STATS_NUMPARAM_SIZE;

 	if(tcSize != numOfIds * PARAM_STATS_PARAMID_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 
	
	if (numOfIds == 0) {
		statisticsMap.clear();
		periodicStatisticsReportingStatus = false;
		return;
	}
	
	reportSuccessAcceptanceVerification(request);
		
	bool bFaultStartExecution = false;
		
	for (uint16_t i = 0; i < numOfIds; i++) {
		uint16_t currentId = request.readUint16();

		if (!d_parameter_pool->parameterExists(currentId)) {
			reportExecutionStartError(request, ErrorHandler::GetNonExistingParameter);
			bFaultStartExecution = true;
			continue;
		}

		statisticsMap.erase(currentId);
	}	
	
	if (statisticsMap.empty()) {
		periodicStatisticsReportingStatus = false;
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);
    }

    void ParameterStatisticsService_impl::reportStatisticsDefinitions(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterStatisticsService::MessageType::ReportParameterStatisticsDefinitions)) {
		return;
	}
		
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);

	reportSuccessStartExecutionVerification(request);
		
	statisticsDefinitionsReport();
	
	reportSuccessCompletionExecutionVerification(request);
    }


  } /* namespace pus */
} /* namespace gr */
