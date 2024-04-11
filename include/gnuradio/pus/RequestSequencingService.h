/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_REQUESTSEQUENCINGSERVICE_H
#define INCLUDED_PUS_REQUESTSEQUENCINGSERVICE_H

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
    class PUS_API RequestSequencingService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 21;
	enum MessageType : uint8_t {
		DirectLoadRequestSequence = 1,
		LoadRequestSequenceByRef = 2,
		UnloadRequestSequence = 3,
		ActivateRequestSequence = 4,
		AbortRequestSequence = 5,
		ReportExecutionStatusOfEachRequestSequence = 6,
		ExecutionStatusOfEachRequestSequenceReport = 7,
		LoadByRefAndActivateRequestSequence = 8,
		ChecksumRequestSequence = 9,
		ChecksumRequestSequenceReport = 10,
		ReportContentRequestSequence = 11,
		ContentRequestSequenceReport = 12,
		AbortAllRequestSequencesAndReport = 13,
		AbortedRequestSequenceReport = 14,
		end = 15
	};

	uint8_t All[14] = {
		DirectLoadRequestSequence,
		LoadRequestSequenceByRef,
		UnloadRequestSequence,
		ActivateRequestSequence,
		AbortRequestSequence,
		ReportExecutionStatusOfEachRequestSequence,
		ExecutionStatusOfEachRequestSequenceReport,
		LoadByRefAndActivateRequestSequence,
		ChecksumRequestSequence,
		ChecksumRequestSequenceReport,
		ReportContentRequestSequence,
		ContentRequestSequenceReport,
		AbortAllRequestSequencesAndReport,
		AbortedRequestSequenceReport
	 };     

      typedef std::shared_ptr<RequestSequencingService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::RequestSequencingService.
       *
       * To avoid accidental use of raw pointers, pus::RequestSequencingService's
       * constructor is in a private implementation
       * class. pus::RequestSequencingService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_REQUESTSEQUENCINGSERVICE_H */
