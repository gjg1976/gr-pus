/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_MEMORYMANAGEMENTSERVICE_IMPL_H
#define INCLUDED_PUS_MEMORYMANAGEMENTSERVICE_IMPL_H

#include <gnuradio/pus/MemoryManagementService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/MemoryManager.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"

#define MEM_MNG_ID	1
#define MEM_MNG_SIZE	2
#define MEM_MNG_START_ADDR	8
#define MEM_MNG_LENGTH	2
#define MEM_MNG_CHK	2

namespace gr {
  namespace pus {

    class MemoryManagementService_impl : public MemoryManagementService
    {
     private:
      uint16_t counters[MemoryManagementService::MessageType::end];

	MemoryManager* d_memory_manager_handler;
	
	bool dataValidator(MessageArray& data, uint16_t checksum);
     public:
      MemoryManagementService_impl();
      ~MemoryManagementService_impl();

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);
      
	/**
	 * TC[6,2] load raw values to memory
	 *
	 * @details This function loads new values to memory data areas
	 * 			specified in the request
	 * @param request Provide the received message as a parameter
	 * @todo Only allow aligned memory address to be start addresses
	 */
      void loadRawData(Message& request);

	/**
	 * TC[6,5] read raw memory values
	 *
	 * @details This function reads the raw data from the RAM memory and
	 * 			triggers a TM[6,6] report
	 * @param request Provide the received message as a parameter
	 * @todo In later embedded version, implement error checking for address validity for
	 * 		 different memory types
	 * @todo Only allow aligned memory address to be start addresses
	 */
      void dumpRawData(Message& request);

	/**
	 * TC[6,9] check raw memory data
	 *
	 * @details This function reads the raw data from the specified memory and
	 * 			triggers a TM[6,10] report
	 * @param request Provide the received message as a parameter
	 * @todo In later embedded version, implement error checking for address validity for
	 * 		 different memory types
	 * @todo Only allow aligned memory address to be start addresses
	 */
      void checkRawData(Message& request);      
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_MEMORYMANAGEMENTSERVICE_IMPL_H */
