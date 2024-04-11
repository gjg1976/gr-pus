/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 

#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/RequestVerificationService.h>

namespace gr {
  namespace pus {


	/**
	 * TM[1,1] successful acceptance verification report
	 */
    void Service::reportSuccessAcceptanceVerification(Message& request){
        if(ACK_FLAGS::SuccessAcceptanceVerification & request.getMessageAckFlags()){
               pmt::pmt_t meta = pmt::make_dict();
        	meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::SuccessfulAcceptanceReport));
        	message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));      
        }       	
    }  
    
	/**
	 * TM[1,2] failed acceptance verification report
	 */
    void Service::reportAcceptanceError(Message& request, ErrorHandler::AcceptanceErrorType errorCode) {    
        pmt::pmt_t meta = pmt::make_dict();
        meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::FailedAcceptanceReport));
        meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(errorCode));
        message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));              	
        d_error_handler->reportError(request, errorCode);               
    } 
     
	/**
	 * TM[1,3] successful start of execution verification report
	 */
    void Service::reportSuccessStartExecutionVerification(Message& request){
        if(ACK_FLAGS::SuccessStartExecutionVerification & request.getMessageAckFlags()){
        	pmt::pmt_t meta = pmt::make_dict();
                meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::SuccessfulStartOfExecution));
                message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));     
         }        	
    }  
    
	/**
	 * TM[1,4] failed start of execution verification report
	 */             
    void Service::reportExecutionStartError(Message& request, ErrorHandler::ExecutionStartErrorType errorCode) {    
        pmt::pmt_t meta = pmt::make_dict();
        meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::FailedStartOfExecution));
        meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(errorCode));
        message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));                	
        d_error_handler->reportError(request, errorCode);               
    } 

	/**
	 * TM[1,5] successful progress of execution verification report
	 */
    void Service::reportSuccessProgressExecutionVerification(Message& request, uint8_t stepID) {  
        if(ACK_FLAGS::SuccessProgressExecutionVerification & request.getMessageAckFlags()){
                pmt::pmt_t meta = pmt::make_dict();
                meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::SuccessfulProgressOfExecution));
                meta = pmt::dict_add(meta, PMT_STEP, pmt::from_long(stepID));
                message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));           	
        }
    }  
    
	/**
	 * TM[1,6] failed progress of execution verification report
	 */        
    void Service::reportExecutionProgressError(Message& request, ErrorHandler::ExecutionProgressErrorType errorCode, uint8_t stepID) {    
        pmt::pmt_t meta = pmt::make_dict();
        meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::FailedProgressOfExecution));
        meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(errorCode));
        meta = pmt::dict_add(meta, PMT_STEP, pmt::from_long(stepID));
        message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));               	
        d_error_handler->reportError(request, errorCode, stepID);               
    } 

	/**
	 * TM[1,7] successful completion of execution verification report
	 */
    void Service::reportSuccessCompletionExecutionVerification(Message& request){
        if(ACK_FLAGS::SuccessCompletionExecutionVerification & request.getMessageAckFlags()){
                pmt::pmt_t meta = pmt::make_dict();
                meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::SuccessfulCompletionOfExecution));
                message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));               	
        }
    }  
    
	/**
	 * TM[1,8] failed completion of execution verification report
	 */        
    void Service::reportExecutionCompletionError(Message& request, ErrorHandler::ExecutionCompletionErrorType errorCode) {    
        pmt::pmt_t meta = pmt::make_dict();
        meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::FailedCompletionOfExecution));
        meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(errorCode));
        message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));          	
        d_error_handler->reportError(request, errorCode);               
    } 

	/**
	 * TM[1,10] failed routing verification report
 	 */            
    void Service::failRoutingVerification(Message& request, ErrorHandler::RoutingErrorType errorCode) {    
        pmt::pmt_t meta = pmt::make_dict();
        meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::MessageType::FailedRoutingReport));
        meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(errorCode));
        message_port_pub(PMT_VER, pmt::cons(meta, 
                		pmt::init_u8vector(request.getMessageData().size(), request.getMessageRawData())));             	
        d_error_handler->reportError(errorCode);               
    }        
  } // namespace pus
} // namespace gr




