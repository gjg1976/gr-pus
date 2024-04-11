/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_REQUESTSEQUENCINGSERVICE_IMPL_H
#define INCLUDED_PUS_REQUESTSEQUENCINGSERVICE_IMPL_H

#include <gnuradio/pus/RequestSequencingService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Time/TimeProvider.h>
#include <gnuradio/pus/Helpers/SequenceStore.h>
#include <nlohmann/json.hpp>
#include <fstream>
#include "etl/list.h"
#include "etl/map.h"

#define REQ_SEQ_NUM_RQ 2

namespace gr {
  namespace pus {

    class RequestSequencingService_impl : public RequestSequencingService
    {
     private:
      uint16_t counters[RequestSequencingService::MessageType::end];
	TimeProvider* d_time_provider;

	void parse_json(const std::string& filename);  
	bool parse_json_request(const std::string& sequenceStoreId, const std::string& filename, Message* request, bool activated);
	
	bool maxActivatedSequences();
	uint32_t trackedTime;
		
	typedef std::string sequenceId;

	/**
	 * All packet stores, held by the Storage and Retrieval Service. Each packet store has its ID as key.
	 */
	etl::map<sequenceId, SequenceStore, ECSSMaxSequenceStores> sequenceStores;	

	std::string readSequenceStoreId(Message& message);
	
     public:
      RequestSequencingService_impl(const std::string& init_file);
      ~RequestSequencingService_impl();

	/**
	 * timer Tick hook, each time is called, it will search for all periodicGenerationActionStatus
	 * Housekeeping structures and increase a counter, when the counter reach collectionInterval value
	 * then a housekeepingParametersReport is generated.
	 * @param p TimeProvider singleton
	 * @return void
	 */
	void timerTick(TimeProvider *p) ;
	
 	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
       void handle_msg(pmt::pmt_t pdu);

	/**
	 * Direct load a Sequence TC[12,1].
	 */
	void directLoadRequestSequence(Message& message);

	/**
	 * Load a Sequence by reference to a file TC[12,2].
	 */
	void loadRequestSequenceByRef(Message& message);
	
	/**
	 * Unload a Sequence TC[12,3].
	 */
	void unloadRequestSequence(Message& message);
	
	/**
	 * Activate a Sequence TC[12,4].
	 */
	void activateRequestSequence(Message& message);
	
	/**
	 * Abort a Sequence TC[12,5].
	 */
	void abortRequestSequence(Message& message);
	
	/**
	 * Report the execution status of each Sequence TC[12,6].
	 */
	void reportExecutionStatusOfEachRequestSequence(Message& message);	

	/**
	 * Load a Sequence by reference to a file and execute TC[12,8].
	 */
	void loadByRefAndActivateRequestSequence(Message& message);
	
	/**
	 * Get the checksum of a Sequence TC[12,9].
	 */
	void checksumRequestSequence(Message& message);

	/**
	 * Get the content of a Sequence TC[12,11].
	 */
	void reportContentRequestSequence(Message& message);	

	/**
	 * Abort all request sequences and report TC[12,13].
	 */
	void abortAllRequestSequencesAndReport(Message& message);			
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_REQUESTSEQUENCINGSERVICE_IMPL_H */
