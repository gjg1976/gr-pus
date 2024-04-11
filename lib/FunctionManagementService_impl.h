/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_FUNCTIONMANAGEMENTSERVICE_IMPL_H
#define INCLUDED_PUS_FUNCTIONMANAGEMENTSERVICE_IMPL_H

#include <gnuradio/pus/FunctionManagementService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/FunctionPool.h>
#include "etl/vector.h"
namespace gr {
  namespace pus {

    class FunctionManagementService_impl : public FunctionManagementService
    {
     private:
      uint16_t counters[FunctionManagementService::MessageType::end];
      uint16_t d_funcNameSize;
      uint16_t d_funcParamSize;

      FunctionPool* d_function_pool;
            
     public:
      FunctionManagementService_impl(uint16_t funcNameSize, uint16_t funcParamSize);
      ~FunctionManagementService_impl();

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);
	/**
	 * Calls the function described in the TC[8,1] message *msg*, passing the arguments contained
	 * and, if non-existent, generates a failed start of execution notification. Returns an unneeded
	 * int, for testing purposes.
	 * @param msg A TC[8,1] message
	 */
	void call(Message& message);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_FUNCTIONMANAGEMENTSERVICE_IMPL_H */
