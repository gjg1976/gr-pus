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
#include "RequestVerificationService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    RequestVerificationService::sptr
    RequestVerificationService::make()
    {
      return gnuradio::make_block_sptr<RequestVerificationService_impl>(
        );
    }


    /*
     * The private constructor
     */
    RequestVerificationService_impl::RequestVerificationService_impl()
      : gr::block("RequestVerificationService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        serviceType = ServiceType;
        for(size_t i = 0; i < RequestVerificationService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        
        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
    }

    /*
     * Our virtual destructor.
     */
    RequestVerificationService_impl::~RequestVerificationService_impl()
    {
    }

    void RequestVerificationService_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);

        // extract data
        if (pmt::is_u8vector(v_data) && pmt::dict_has_key(meta, PMT_REQ) ){
                std::vector<uint8_t> inData = pmt::u8vector_elements(v_data);

                MessageArray in_data(inData.data(), inData.data() + inData.size());                

        	if(in_data.size() < CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize)
        		return;
        	
        	if(!pmt::is_integer(pmt::dict_ref(meta, PMT_REQ, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
            		GR_LOG_WARN(d_logger, "No valid REQUEST metadata found");
#endif
			return;	
		 }
                uint16_t report_req = (uint16_t) pmt::to_long(pmt::dict_ref(meta, PMT_REQ, pmt::PMT_NIL));
                uint16_t error_type = 0;
                uint8_t step_id = 0;
                                                
                Message message = d_message_parser->ParseMessageCommand(in_data);
                switch (report_req) {
                        case SuccessfulAcceptanceReport:  
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "SuccessfulAcceptanceReport");
#endif
			   successAcceptanceVerification(message);
			   break;
                        case FailedAcceptanceReport:  
                	   if (pmt::dict_has_key(meta, PMT_ERROR_TYPE)){

                	   	if(!pmt::is_integer(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
            				GR_LOG_WARN(d_logger, "No valid ERROR_TYPE metadata found");
#endif
					break;	
				}
#ifdef _PUS_DEBUG
				GR_LOG_WARN(d_logger, "FailedAcceptanceReport");
#endif

		     		error_type = (uint16_t)pmt::to_long(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL));

			   	failAcceptanceVerification(message, 
			   		(ErrorHandler::AcceptanceErrorType)error_type);
		 	   }
			   break;
                        case SuccessfulStartOfExecution:  
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "SuccessfulStartOfExecution");
#endif
			   successStartExecutionVerification(message);
			   break;
			   
                        case FailedStartOfExecution:  
                	   if (pmt::dict_has_key(meta, PMT_ERROR_TYPE)){
                	   	if(!pmt::is_integer(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
            				GR_LOG_WARN(d_logger, "No valid ERROR_TYPE metadata found");
#endif
					break;	
				}
#ifdef _PUS_DEBUG
                           	GR_LOG_WARN(d_logger, "FailedStartOfExecution");
#endif

		     		error_type = (uint16_t)pmt::to_long(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL));

				failStartExecutionVerification(message, 
			   		(ErrorHandler::ExecutionStartErrorType)error_type);
		 	   }
			   break;
			   
                        case SuccessfulProgressOfExecution:  
			   if (pmt::dict_has_key(meta, PMT_STEP)){
                	   	if(!pmt::is_integer(pmt::dict_ref(meta, PMT_STEP, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
            				GR_LOG_WARN(d_logger, "No valid STEP_ID metadata found");
#endif
					break;	
				}
#ifdef _PUS_DEBUG
                           	GR_LOG_WARN(d_logger, "SuccessfulProgressOfExecution");
#endif

		     		step_id = (uint8_t)pmt::to_long(pmt::dict_ref(meta, PMT_STEP, pmt::PMT_NIL));
			   	successProgressExecutionVerification(message, step_id);
			   }
			   break;
                        case FailedProgressOfExecution:  

               	   if (pmt::dict_has_key(meta, PMT_ERROR_TYPE)){


#ifdef _PUS_DEBUG
                           	GR_LOG_WARN(d_logger, "FailedProgressOfExecution");
#endif


		     		error_type = (uint16_t)pmt::to_long(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL));
                 		if (pmt::dict_has_key(meta, PMT_STEP)){
	                	   	if(!pmt::is_integer(pmt::dict_ref(meta, PMT_STEP, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
	            				GR_LOG_WARN(d_logger, "No valid STEP_ID metadata found");
#endif
						break;	
					}                 		
                 		
		     			step_id = (uint8_t)pmt::to_long(pmt::dict_ref(meta, PMT_STEP, pmt::PMT_NIL));
			   		
			   		failProgressExecutionVerification(message, 
			   			(ErrorHandler::ExecutionProgressErrorType)error_type, step_id);
				} 
		 	   }

			   break;
                        case SuccessfulCompletionOfExecution:  
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "SuccessfulCompletionOfExecution");
#endif
			   successCompletionExecutionVerification(message);
			   break;
                        case FailedCompletionOfExecution:  
               	   if (pmt::dict_has_key(meta, PMT_ERROR_TYPE)){
                	   	if(!pmt::is_integer(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
            				GR_LOG_WARN(d_logger, "No valid ERROR_TYPE metadata found");
#endif
					break;	
				}

#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "FailedCompletionOfExecution");
#endif

		     		error_type = (uint16_t)pmt::to_long(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL));

				failCompletionExecutionVerification(message, 
			   		(ErrorHandler::ExecutionCompletionErrorType)error_type);
		 	   }
                    
			   break;
                        case FailedRoutingReport:  
               	   if (pmt::dict_has_key(meta, PMT_ERROR_TYPE)){
                	   	if(!pmt::is_integer(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL))){
#ifdef _PUS_DEBUG
            				GR_LOG_WARN(d_logger, "No valid ERROR_TYPE metadata found");
#endif
					break;	
				}
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "FailedRoutingReport");
#endif

		     		error_type = (uint16_t)pmt::to_long(pmt::dict_ref(meta, PMT_ERROR_TYPE, pmt::PMT_NIL));

				failRoutingVerification(message, (ErrorHandler::RoutingErrorType)error_type);
		 	   }               
			   break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Request Verification Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);
                 }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector or the dictionary is incomplete");
        }
     }

    void RequestVerificationService_impl::successAcceptanceVerification(Message request) {
	// TM[1,1] successful acceptance verification report

        MessageArray payload;
        
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::SuccessfulAcceptanceReport,
			counters[RequestVerificationService::MessageType::SuccessfulAcceptanceReport], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::SuccessfulAcceptanceReport]++;
    }

    void RequestVerificationService_impl::failAcceptanceVerification(Message request,
                                                            ErrorHandler::AcceptanceErrorType errorCode) {
	// TM[1,2] failed acceptance verification report
        MessageArray payload;
        
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);
        
        payload.push_back(errorCode >> 8U);
        payload.push_back(errorCode & 0xffU);
        
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::FailedAcceptanceReport,
			counters[RequestVerificationService::MessageType::FailedAcceptanceReport], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::FailedAcceptanceReport]++;
    }

    void RequestVerificationService_impl::successStartExecutionVerification(Message request) {
	// TM[1,3] successful start of execution verification report
        MessageArray payload;
        
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::SuccessfulStartOfExecution,
			counters[RequestVerificationService::MessageType::SuccessfulStartOfExecution], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::SuccessfulStartOfExecution]++;
    }

    void RequestVerificationService_impl::failStartExecutionVerification(Message request,
                                                                ErrorHandler::ExecutionStartErrorType errorCode) {
	// TM[1,4] failed start of execution verification report
        MessageArray payload;
        
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);
        
        payload.push_back(errorCode >> 8U);
        payload.push_back(errorCode & 0xffU);

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::FailedStartOfExecution,
			counters[RequestVerificationService::MessageType::FailedStartOfExecution], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::FailedStartOfExecution]++;
    }

    void RequestVerificationService_impl::successProgressExecutionVerification(Message request, uint8_t stepID) {
	// TM[1,5] successful progress of execution verification report
        MessageArray payload;
        
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);
        
        payload.push_back(stepID);

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::SuccessfulProgressOfExecution,
			counters[RequestVerificationService::MessageType::SuccessfulProgressOfExecution], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::SuccessfulProgressOfExecution]++;		
    }

    void RequestVerificationService_impl::failProgressExecutionVerification(Message request,
                                                                   ErrorHandler::ExecutionProgressErrorType errorCode,
                                                                   uint8_t stepID) {
	// TM[1,6] failed progress of execution verification report
        MessageArray payload;
        
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);
        
        payload.push_back(stepID);
        payload.push_back(errorCode >> 8U);
        payload.push_back(errorCode & 0xffU);


        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::FailedProgressOfExecution,
			counters[RequestVerificationService::MessageType::FailedProgressOfExecution], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::FailedProgressOfExecution]++;	
    }

    void RequestVerificationService_impl::successCompletionExecutionVerification(Message request) {
	// TM[1,7] successful completion of execution verification report
        MessageArray payload;
        
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::SuccessfulCompletionOfExecution,
			counters[RequestVerificationService::MessageType::SuccessfulCompletionOfExecution], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::SuccessfulCompletionOfExecution]++;	
    }

    void RequestVerificationService_impl::failCompletionExecutionVerification(Message request,
                                                         ErrorHandler::ExecutionCompletionErrorType errorCode) {
	// TM[1,8] failed completion of execution verification report
        MessageArray payload;
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);
        
        payload.push_back(errorCode >> 8U);
        payload.push_back(errorCode & 0xffU);
        
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::FailedCompletionOfExecution,
			counters[RequestVerificationService::MessageType::FailedCompletionOfExecution], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
                
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::FailedCompletionOfExecution]++;	
    }

    void RequestVerificationService_impl::failRoutingVerification(Message request,
                                                         ErrorHandler::RoutingErrorType errorCode) {
	// TM[1,10] failed routing verification report
        MessageArray payload;
        payload.push_back(request.getMessageRawData()[0]);
        payload.push_back(request.getMessageRawData()[1]);
        payload.push_back(request.getMessageRawData()[2]);
        payload.push_back(request.getMessageRawData()[3]);
        
        payload.push_back(errorCode >> 8U);
        payload.push_back(errorCode & 0xffU);

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestVerificationService::MessageType::FailedRoutingReport,
			counters[RequestVerificationService::MessageType::FailedRoutingReport], 0);

	report.appendUint8Array(payload);
			       
        d_message_parser->closeMessage(report);
        
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[RequestVerificationService::MessageType::FailedRoutingReport]++;
    }
     
  } /* namespace pus */
} /* namespace gr */
