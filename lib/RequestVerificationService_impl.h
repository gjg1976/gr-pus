/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_REQUESTVERIFICATIONSERVICE_IMPL_H
#define INCLUDED_PUS_REQUESTVERIFICATIONSERVICE_IMPL_H

#include <gnuradio/pus/RequestVerificationService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"
namespace gr {
  namespace pus {

    class RequestVerificationService_impl : public RequestVerificationService
    {
     private:
      pmt::pmt_t meta;
      uint16_t counters[RequestVerificationService::MessageType::end];

      MessageParser* d_message_parser;
      ErrorHandler* d_error_handler;
            
     public:
      RequestVerificationService_impl();
      ~RequestVerificationService_impl();

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);

	/**
	 * TM[1,1] successful acceptance verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic info
	 * of the telecommand packet that accepted successfully
	 */
	void successAcceptanceVerification(Message request);

	/**
	 * TM[1,2] failed acceptance verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic
	 * info of the telecommand packet that failed to be accepted
	 * @param errorCode The cause of creating this type of report
	 */
	void failAcceptanceVerification(Message request, ErrorHandler::AcceptanceErrorType errorCode);

	/**
	 * TM[1,3] successful start of execution verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic info
	 * of the telecommand packet that its start of execution is successful
	 */
	void successStartExecutionVerification(Message request);

	/**
	 * TM[1,4] failed start of execution verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic info
	 * of the telecommand packet that its start of execution has failed
	 * @param errorCode The cause of creating this type of report
	 */
	void failStartExecutionVerification(Message request, ErrorHandler::ExecutionStartErrorType errorCode);

	/**
	 * TM[1,5] successful progress of execution verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic info
	 * of the telecommand packet that its progress of execution is successful
	 * @param stepID If the execution of a request is a long process, then we can divide
	 * the process into steps. Each step goes with its own definition, the stepID.
	 * @todo Each value,that the stepID is assigned, should be documented.
	 * @todo error handling for undocumented assigned values to stepID
	 */
	void successProgressExecutionVerification(Message request, uint8_t stepID);

	/**
	 * TM[1,6] failed progress of execution verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic info
	 * of the telecommand packet that its progress of execution has failed
	 * @param errorCode The cause of creating this type of report
	 * @param stepID If the execution of a request is a long process, then we can divide
	 * the process into steps. Each step goes with its own definition, the stepID.
	 * @todo Each value,that the stepID is assigned, should be documented.
	 * @todo error handling for undocumented assigned values to stepID
	 */
	void failProgressExecutionVerification(Message request, ErrorHandler::ExecutionProgressErrorType errorCode,
	                                       uint8_t stepID);

	/**
	 * TM[1,7] successful completion of execution verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually data members of Message that contain the basic info of the
	 * telecommand packet that executed completely and successfully
	 */
	void successCompletionExecutionVerification(Message request);

	/**
	 * TM[1,8] failed completion of execution verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic info of the
	 * telecommand packet that failed to be executed completely
	 * @param errorCode The cause of creating this type of report
	 */
	void failCompletionExecutionVerification(Message request,
	                                         ErrorHandler::ExecutionCompletionErrorType errorCode);

	/**
	 * TM[1,10] failed routing verification report
	 *
	 * @param request Contains the necessary data to send the report.
	 * The data is actually some data members of Message that contain the basic info of the
	 * telecommand packet that failed the routing
	 * @param errorCode The cause of creating this type of report
 	 */
	void failRoutingVerification(Message request, ErrorHandler::RoutingErrorType errorCode);
	      
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_REQUESTVERIFICATIONSERVICE_IMPL_H */
