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
#include "FunctionManagementService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    FunctionManagementService::sptr
    FunctionManagementService::make(uint16_t funcNameSize, uint16_t funcParamSize)
    {
      return gnuradio::make_block_sptr<FunctionManagementService_impl>(
        funcNameSize, funcParamSize);
    }


    /*
     * The private constructor
     */
    FunctionManagementService_impl::FunctionManagementService_impl(uint16_t funcNameSize, uint16_t funcParamSize)
      : gr::block("FunctionManagementService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)),
              d_funcNameSize(funcNameSize),
              d_funcParamSize(funcParamSize)
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        d_function_pool = FunctionPool::getInstance();
        
        d_function_pool->setFuncNameSize(d_funcNameSize);
        
        serviceType = ServiceType;

        for(size_t i = 0; i < FunctionManagementService::MessageType::end; i++)
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
    FunctionManagementService_impl::~FunctionManagementService_impl()
    {
    }


    void FunctionManagementService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case PerformFunction:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "PerformFunction");
#endif
                           call(message);
                           break;
                     
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Function Management Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Function Management Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     } 	
    void FunctionManagementService_impl::call(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FunctionManagementService::MessageType::PerformFunction)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize != (d_funcNameSize + d_funcParamSize)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);		
		return;
	}

	reportSuccessAcceptanceVerification(request);	
		
	uint8_t funcName[d_funcNameSize] = {0};   // the function's name
	uint8_t funcArgs[d_funcParamSize] = {0}; // arguments for the function
	
	request.readArray(funcName, d_funcNameSize);
	request.readArray(funcArgs, d_funcParamSize);

	// locate the appropriate function pointer
	std::string name(reinterpret_cast<char *>(funcName));

	FunctionMap::iterator iter = d_function_pool->funcPtrIndex.find(name);

	if (iter == d_function_pool->funcPtrIndex.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingFunction);
		return;
	}

	reportSuccessStartExecutionVerification(request);

	auto selected = *iter->second;
        
        std::vector<uint8_t> args(funcArgs, funcArgs+d_funcParamSize);
	// execute the function if there are no obvious flaws (defined in the standard, pg.158)
	selected(args);

	reportSuccessCompletionExecutionVerification(request);
}


  } /* namespace pus */
} /* namespace gr */
