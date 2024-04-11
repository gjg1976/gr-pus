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
#include "ParameterService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    ParameterService::sptr
    ParameterService::make()
    {
      return gnuradio::make_block_sptr<ParameterService_impl>(
        );
    }


    /*
     * The private constructor
     */
    ParameterService_impl::ParameterService_impl()
      : gr::block("ParameterService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        
        d_parameter_pool = ParameterPool::getInstance();
        serviceType = ServiceType;
        for(size_t i = 0; i < ParameterService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);

         std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
    }

    /*
     * Our virtual destructor.
     */
    ParameterService_impl::~ParameterService_impl()
    {
    }


    void ParameterService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case ReportParameterValues:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportParameterValues");
#endif
                           reportParameters(message);
                           break;
                                            
                        case SetParameterValues:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "SetParameterValues");
#endif
                           setParameters(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Parameter Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Parameter Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);

               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    void ParameterService_impl::reportParameters(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterService::MessageType::ReportParameterValues)) {
		return;
	}

 	uint16_t currentPosition = request.getMessageReadPosition();
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < PARAM_NUM_PARAMS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}
	
 	tcSize -= PARAM_NUM_PARAMS_SIZE;   

	uint16_t numOfIds = request.readUint16();

 	if(tcSize != numOfIds * PARAM_ID_SIZE){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);				
		return;
	}

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;
	
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			ParameterService::MessageType::ParameterValuesReport, 
			counters[ParameterService::MessageType::ParameterValuesReport], 0);
			
	currentPosition = request.getMessageReadPosition();
	
	uint16_t numberOfValidIds = 0;
	for (uint16_t i = 0; i < numOfIds; i++) {
		uint16_t currId = request.readUint16();

		if (d_parameter_pool->parameterExists(currId)) {
			numberOfValidIds++;
		}
	}
	report.appendUint16(numberOfValidIds);   	
	
	request.setMessageReadPosition(currentPosition);
			
	for (uint16_t i = 0; i < numOfIds; i++) {
		uint16_t currId = request.readUint16();

		auto parameter = d_parameter_pool->getParameter(currId);

		if (!parameter) {
			reportExecutionStartError(request, ErrorHandler::GetNonExistingParameter);
			bFaultStartExecution = true;
			continue;
		}

		report.appendUint16(currId);   	

		parameter->get().appendValueToMessage(report);
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[ParameterService::MessageType::ParameterValuesReport]++;

	reportSuccessCompletionExecutionVerification(request);	
    }

    void ParameterService_impl::setParameters(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			ParameterService::MessageType::SetParameterValues)) {
		return;
	}

 	uint16_t currentPosition = request.getMessageReadPosition();
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < PARAM_NUM_PARAMS_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}
 	tcSize -= PARAM_NUM_PARAMS_SIZE;  
 	
	uint16_t numOfIds = request.readUint16();

	for (uint16_t i = 0; i < numOfIds; i++) {
		if(tcSize < PARAM_ID_SIZE + 1){  
			reportAcceptanceError(request, ErrorHandler::InvalidLength);				
			return;
		}
		tcSize -= PARAM_ID_SIZE;
		uint16_t currId = request.readUint16();
		
		auto parameter = d_parameter_pool->getParameter(currId);
		if (!parameter) {
			reportSuccessAcceptanceVerification(request);	
			reportExecutionStartError(request, ErrorHandler::ParameterUnknown);		
			return; // Setting parameters is impossible, since the size of value to be read is unknown
		}
		uint16_t parameterSize = parameter->get().appendValueToVector().size();
		if(tcSize < parameterSize){  
			reportAcceptanceError(request, ErrorHandler::InvalidLength);				
			return;
		}
		tcSize -= parameterSize;
		request.setMessageReadPosition(request.getMessageReadPosition()+parameterSize);		
	}	
	if(tcSize > 0){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);				
		return;
	}
	request.setMessageReadPosition(currentPosition+PARAM_NUM_PARAMS_SIZE);	
		
	reportSuccessAcceptanceVerification(request);
	reportSuccessStartExecutionVerification(request);
		
	for (uint16_t i = 0; i < numOfIds; i++) {
		uint16_t currId = request.readUint16();
		
		auto parameter = d_parameter_pool->getParameter(currId);
	
		parameter->get().setValueFromMessage(request);
		

	}
	
	reportSuccessCompletionExecutionVerification(request);
    }


  } /* namespace pus */
} /* namespace gr */
