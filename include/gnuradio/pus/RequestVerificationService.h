/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_REQUESTVERIFICATIONSERVICE_H
#define INCLUDED_PUS_REQUESTVERIFICATIONSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API RequestVerificationService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 1;

	enum MessageType : uint8_t {
		SuccessfulAcceptanceReport = 1,
		FailedAcceptanceReport = 2,
		SuccessfulStartOfExecution = 3,
		FailedStartOfExecution = 4,
		SuccessfulProgressOfExecution = 5,
		FailedProgressOfExecution = 6,
		SuccessfulCompletionOfExecution = 7,
		FailedCompletionOfExecution = 8,
		FailedRoutingReport = 10,
		end = 11
	};
	uint8_t All[9] = {
		SuccessfulAcceptanceReport,
		FailedAcceptanceReport,
		SuccessfulStartOfExecution,
		FailedStartOfExecution,
		SuccessfulProgressOfExecution,
		FailedProgressOfExecution,
		SuccessfulCompletionOfExecution,
		FailedCompletionOfExecution,
		FailedRoutingReport
	 };
      typedef std::shared_ptr<RequestVerificationService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::RequestVerificationService.
       *
       * To avoid accidental use of raw pointers, pus::RequestVerificationService's
       * constructor is in a private implementation
       * class. pus::RequestVerificationService::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_REQUESTVERIFICATIONSERVICE_H */
