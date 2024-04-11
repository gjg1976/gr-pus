/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_TESTSERVICE_IMPL_H
#define INCLUDED_PUS_TESTSERVICE_IMPL_H

#include <gnuradio/pus/TestService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"

namespace gr {
  namespace pus {

    class TestService_impl : public TestService
    {
     private:
      uint16_t counters[TestService::MessageType::end];
      
     public:
      TestService_impl();
      ~TestService_impl();

        void storeMessage(Message& report);
	/**
	 * TC[17,1] perform an are-you-alive connection test
	 */
	void areYouAlive(Message& request);

	/**
	 * TM[17,2] are-you-alive connection test report to show that the MCU is alive and well
	 */
	void areYouAliveReport();

	/**
	 * TC[17,3] perform an on-board connection test
	 *
	 */
	void onBoardConnection(Message& request);

	/**
	 * TM[17,4] on-board connection test report to show that the MCU is connected to the on-board
	 */
	void onBoardConnectionReport(uint16_t applicationProcessId);

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_TESTSERVICE_IMPL_H */
