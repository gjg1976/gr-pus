/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_PARAMETERSERVICE_IMPL_H
#define INCLUDED_PUS_PARAMETERSERVICE_IMPL_H

#include <gnuradio/pus/ParameterService.h>
#include <gnuradio/pus/Helpers/ParameterPool.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"

#define PARAM_NUM_PARAMS_SIZE  2
#define PARAM_ID_SIZE  2

namespace gr {
  namespace pus {

    class ParameterService_impl : public ParameterService
    {
     private:
      uint16_t counters[ParameterService::MessageType::end];

      ParameterPool* d_parameter_pool;
     public:
      ParameterService_impl();
      ~ParameterService_impl();

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);
      
	/**
	 * This function receives a TC[20, 1] packet and returns a TM[20, 2] packet
	 * containing the current configuration
	 * **for the parameters specified in the carried valid IDs**.
	 *
	 * @param paramId: a TC[20, 1] packet carrying the requested parameter IDs
	 * @return None (messages are stored using storeMessage())
	 */
      void reportParameters(Message& paramIds);

	/**
	 * This function receives a TC[20, 3] message and after checking whether its type is correct,
	 * iterates over all contained parameter IDs and replaces the settings for each valid parameter,
	 * while ignoring all invalid IDs.
	 *
	 * @param newParamValues: a valid TC[20, 3] message carrying parameter ID and replacement value
	 */
      void setParameters(Message& newParamValues) ;
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_PARAMETERSERVICE_IMPL_H */
