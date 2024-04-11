/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_PACKETSTORE_H
#define ECSS_PACKETSTORE_H

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Helpers/Message.h>
#include <deque>
#include "etl/deque.h"
#include "etl/multimap.h"
#include "etl/vector.h"
#include "etl/map.h"
#include <gnuradio/pus/Helpers/Message.h>

namespace gr {
 namespace pus {
/**
 * This is the Packet Store class, needed for the Storage-Retrieval Service. The purpose of the packet-store is to
 * store all the TM packets transmitted by the other Services.
 */
    class PacketStore {
    public:
	/**
	 * The virtual channel used to transmit the packet store to the ground station. There is an upper and a lower
	 * bound for the virtual channels, defined in 'ECSSDefinitions' file.
	 */
	uint8_t virtualChannel;
	/**
	 * The time-tag that defines the starting point of the open retrieval process, meaning that we retrieve packets,
	 * starting from the open-retrieval-start-time-tag until the latest packet.
	 */
	uint32_t openRetrievalStartTimeTag = 0;
	
	/**
	 * The time-tag that defines keep tracking the point of the open retrieval process, meaning that we retrieve packets,
	 * starting from the open-retrieval-start-time-tag until the latest packet.
	 */
	uint32_t currentRetrievalStartTimeTag = 0;
	/**
	 * The start time of a by-time-range retrieval process, i.e. retrieval of packets between two specified time-tags.
	 */
	uint32_t retrievalStartTime = 0;
	/**
	 * The end time of a by-time-range retrieval process, i.e. retrieval of packets between two specified time-tags.
	 */
	uint32_t retrievalEndTime = 0;
	/**
	 * The maximum size of the packet store, in bytes.
	 *
	 * @todo: add a way of defining each packets store's size in bytes
	 */
	uint64_t sizeInBytes;

	/**
	 * Whether the insertion of packets stores in the packet-store should cyclically overwrite older packets, or be
	 * suspended when the packet-store is full.
	 */
	enum PacketStoreType : uint8_t { Circular = 0, Bounded = 1 };

	/**
	 * Whether the open retrieval status of the packet-store is in progress or not.
	 */
	enum PacketStoreOpenRetrievalStatus : bool { Suspended = false, InProgress = true };

	/**
+	 * Whether the storage of TM packets is enabled for this packet store
	 */
	bool storageStatus = false;

	/**
	 * Whether the by-time-range retrieval of packet stores is enabled for this packet-store.
	 */
	bool byTimeRangeRetrievalStatus = false;
	PacketStoreType packetStoreType;
	PacketStoreOpenRetrievalStatus openRetrievalStatus;

	PacketStore() = default;
	~PacketStore() = default;
	/**
	 * A queue containing the TM messages stored by the packet store. Every TM is accompanied by its timestamp.
	 *
	 * @note A convention is made that this should be filled out using `push_back` and NOT `push_front`, dictating that
	 * earlier packets are placed in the front position. So removing the earlier packets is done with `pop_front`.
	 *
	 * 				old packets  <---------->  new packets
	 * 				[][][][][][][][][][][][][][][][][][][]	<--- deque
	 */
	std::deque<std::pair<uint32_t, Message>> storedTelemetryPackets;
	
	/**
	 * Vector containing the Report Type definitions. Each definition has its unique name of type uint8. For
	 * example, a Report Type definition could be 'ReportHousekeepingStructures'.
	 */
	typedef etl::vector<uint8_t, ECSSMaxReportTypeDefinitions> ReportTypeDefinitions;

	/**
	 * This is the key for the application process configuration map. It contains a pair with the applicationID and
	 * the serviceType.
	 */
	typedef std::pair<uint16_t, uint8_t> AppServiceKey;

	/**
	 * Map containing the report type definitions. Each application process has its own ID. The combination of the
	 * application ID and the service type is used as a key to provide access to the list of report type definitions.
	 *
	 * @note
	 * The report type definitions are basically the message types of each service. For example a message type for the
	 * 'ParameterStatisticsService' (ST04) is 'ParameterStatisticsService::MessageType::ParameterStatisticsReport'. The
	 * Real Time Forwarding Control Service (ST14) uses this map as a lookup table, to identify whether a requested
	 * triplet (app->service->message type) is allowed to be forwarded to the ground station via the corresponding virtual
	 * channel. The requested message type is only forwarded, if the requested application process ID and service type
	 * already exist in the map, and the requested report type is located in the vector of report types, which corresponds
	 * to the appID and service type.
	 */
	etl::map<AppServiceKey, ReportTypeDefinitions, ECSSMaxApplicationsServicesCombinations> definitions;
	
	/**
	 * Returns the sum of the sizes of the packets stored in this PacketStore, in bytes.
	 */
	uint16_t calculateSizeInBytes();
	/**
	 * The virtual channel used to transmit the packet store to the ground station. There is an upper and a lower
	 * bound for the virtual channels, defined in 'ECSSDefinitions' file.
	 */
	std::vector<uint16_t> getApplicationsInStore();	
   };
  } // namespace pus
} // namespace gr
#endif
