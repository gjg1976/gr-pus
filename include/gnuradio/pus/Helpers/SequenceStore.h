/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_SEQUENCESTORE_H
#define ECSS_SEQUENCESTORE_H

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Helpers/Message.h>
#include <gnuradio/pus/Helpers/CRCHelper.h>
#include "etl/list.h"
#include "etl/map.h"
#include "etl/vector.h"

namespace gr {
 namespace pus {
/**
 * This is the Packet Store class, needed for the Storage-Retrieval Service. The purpose of the packet-store is to
 * store all the TM packets transmitted by the other Services.
 */
    class SequenceStore {
    public:
	typedef etl::vector<Message *, ECSSMaxNumberOfReleasedSequenceActivities> MessageList;
	struct SequenceActivity {
		Message request;                         ///< Hold the received command request
		Time::DefaultCUC requestDelayTime{0}; ///< Delay time until next steps
	};

	/**
	 * @brief Hold the sequence of activities
	 *
	 * @details The scheduled activities in this list are ordered by their release time, as the
	 * standard requests.
	 */
	etl::list<SequenceActivity, ECSSMaxNumberOfSequenceActivities> sequenceActivities;


	enum SequenceStatus : bool { Inactive = false, Execution = true };
	
	SequenceStatus sequenceStatus = Inactive;
	etl::list<SequenceActivity, ECSSMaxNumberOfSequenceActivities>::iterator currentStep = sequenceActivities.begin();
	
	uint32_t countDown = 0;

	SequenceStore() = default;
	~SequenceStore() = default;
	
	void activated();
	void abort();
	MessageList step();
	uint16_t calculateSequenceCRC();	
   };
  } // namespace pus
} // namespace gr
#endif
