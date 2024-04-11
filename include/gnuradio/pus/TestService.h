/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_TESTSERVICE_H
#define INCLUDED_PUS_TESTSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API TestService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 17;

	enum MessageType : uint8_t {
		AreYouAliveTest = 1,
		AreYouAliveTestReport = 2,
		OnBoardConnectionTest = 3,
		OnBoardConnectionTestReport = 4,
		end = 5
	};
	uint8_t All[4] = {
		AreYouAliveTest,
		AreYouAliveTestReport,
		OnBoardConnectionTest,
		OnBoardConnectionTestReport
	 };
      typedef std::shared_ptr<TestService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::TestService.
       *
       * To avoid accidental use of raw pointers, pus::TestService's
       * constructor is in a private implementation
       * class. pus::TestService::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_TESTSERVICE_H */
