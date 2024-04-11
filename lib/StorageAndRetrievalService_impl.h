/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_STORAGEANDRETRIEVALSERVICE_IMPL_H
#define INCLUDED_PUS_STORAGEANDRETRIEVALSERVICE_IMPL_H

#include <gnuradio/pus/StorageAndRetrievalService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Helpers/PacketStore.h>
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
#include <nlohmann/json.hpp>
#include <fstream>
#include <chrono>
#include "etl/map.h"
#include "etl/vector.h"


#define STR_RTL_NUM_STORES 2
#define STR_RTL_NUM_APPID 2
#define STR_RTL_APPID_SIZE 2
#define STR_RTL_NUM_SERVICES 2
#define STR_RTL_SERVICES_SIZE 1
#define STR_RTL_NUM_SUBTYPES 2
#define STR_RTL_SUBTYPES_SIZE 1
#define STR_RTL_PKTSTORE_SIZE 2
#define STR_RTL_PKTSTORE_TYPE 1
#define STR_RTL_PKTSTORE_VC 1
#define STR_RTL_PKTSTORE_TIMEWIN_TYPE 1

namespace gr {
  namespace pus {

    class StorageAndRetrievalService_impl : public StorageAndRetrievalService
    {
     public:
	/**
	 * The type of timestamps that the Storage and Retrieval Subservice assigns to each incoming packet.
	 */
	enum TimeStampType : uint8_t { StorageBased = 0, PacketBased = 1 };

	/**
	 * Different types of packet retrieval from a packet store, relative to a specified time-tag.
	 */
	enum TimeWindowType : uint8_t { FromTagToTag = 0, AfterTimeTag = 1, BeforeTimeTag = 2 };

	/**
	 * The type of timestamps that the subservice sets to each incoming telemetry packet.
	 */
	const TimeStampType timeStamping = PacketBased;
	
     private:
      uint16_t counters[StorageAndRetrievalService::MessageType::end];

      std::map<uint16_t, uint16_t> d_outputvc;
      std::vector<uint16_t> d_vc_list;
      std::vector<uint16_t> appID_monitored_list;
            
	typedef std::string packetStoreId;

	/**
	 * All packet stores, held by the Storage and Retrieval Service. Each packet store has its ID as key.
	 */
	etl::map<packetStoreId, PacketStore, ECSSMaxPacketStores> packetStores;

	/**
	 * Helper function that reads the packet store ID string from a TM[15] message
	 */
	static inline std::string readPacketStoreId(Message& message);

	/**
	 * Helper function that, given a time-limit, deletes every packet stored in the specified packet-store, up to the
	 * requested time.
	 *
	 * @param packetStoreId required to access the correct packet store.
	 * @param timeLimit the limit until which, packets are deleted.
	 */
	void deleteContentUntil(const std::string& packetStoreId, uint32_t timeLimit);

	/**
	 * Copies all TM packets from source packet store to the target packet-store, that fall between the two specified
	 * time-tags as per 6.15.3.8.4.d(1) of the standard.
	 *
	 * @param request used to read the time-tags, the packet store IDs and to raise errors.
	 * @return true if an error has occurred.
	 */
	bool copyFromTagToTag(Message& request);

	/**
	 * Copies all TM packets from source packet store to the target packet-store, whose time-stamp is after the
	 * specified time-tag as per 6.15.3.8.4.d(2) of the standard.
	 *
	 * @param request used to read the time-tag, the packet store IDs and to raise errors.
	 * @return true if an error has occurred.
	 */
	bool copyAfterTimeTag(Message& request);

	/**
	 * Copies all TM packets from source packet store to the target packet-store, whose time-stamp is before the
	 * specified time-tag as per 6.15.3.8.4.d(3) of the standard.
	 *
	 * @param request used to raise errors.
	 * @return true if an error has occurred.
	 */
	 
	bool copyBeforeTimeTag(Message& request);

	/**
	 * Checks if the two requested packet stores exist.
	 *
	 * @param fromPacketStoreId the source packet store, whose content is to be copied.
	 * @param toPacketStoreId  the target packet store, which is going to receive the new content.
	 * @param request used to raise errors.
	 * @return true if an error has occurred.
	 */
	bool checkPacketStores(const std::string& fromPacketStoreId,
	                       const std::string& toPacketStoreId, Message& request);

	/**
	 * Checks whether the time window makes logical sense (end time should be after the start time)
	 *
	 * @param request used to raise errors.
	 */
	static bool checkTimeWindow(uint32_t startTime, uint32_t endTime, Message& request);

	/**
	 * Checks if the destination packet store is empty, in order to proceed with the copying of packets.
	 *
	 * @param toPacketStoreId  the target packet store, which is going to receive the new content. Needed for error
	 * checking.
	 * @param request used to raise errors.
	 */
	bool checkDestinationPacketStore(const std::string& toPacketStoreId, Message& request);

	/**
	 * Checks if there are no stored timestamps that fall between the two specified time-tags.
	 *
	 * @param fromPacketStoreId  the source packet store, whose content is to be copied. Needed for error checking.
	 * @param request used to raise errors.
	 *
	 * @note
	 * This function assumes that `startTime` and `endTime` are valid at this point, so any necessary error checking
	 * regarding these variables, should have already occurred.
	 */
	bool noTimestampInTimeWindow(const std::string& fromPacketStoreId, uint32_t startTime,
	                             uint32_t endTime, Message& request);

	/**
	 * Checks if there are no stored timestamps that fall between the two specified time-tags.
	 *
	 * @param isAfterTimeTag true indicates that we are examining the case of AfterTimeTag. Otherwise, we are referring
	 * to the case of BeforeTimeTag.
	 * @param request used to raise errors.
	 * @param fromPacketStoreId the source packet store, whose content is to be copied.
	 */
	bool noTimestampInTimeWindow(const std::string& fromPacketStoreId, uint32_t timeTag,
	                             Message& request, bool isAfterTimeTag);

	/**
	 * Performs all the necessary error checking for the case of FromTagToTag copying of packets.
	 *
	 * @param fromPacketStoreId the source packet store, whose content is to be copied.
	 * @param toPacketStoreId  the target packet store, which is going to receive the new content.
	 * @param request used to raise errors.
	 * @return true if an error has occurred.
	 */
	bool failedFromTagToTag(const std::string& fromPacketStoreId,
	                        const std::string& toPacketStoreId, uint32_t startTime,
	                        uint32_t endTime, Message& request);

	/**
	 * Performs all the necessary error checking for the case of AfterTimeTag copying of packets.
	 *
	 * @param fromPacketStoreId the source packet store, whose content is to be copied.
	 * @param toPacketStoreId  the target packet store, which is going to receive the new content.
	 * @param request used to raise errors.
	 * @return true if an error has occurred.
	 */
	bool failedAfterTimeTag(const std::string& fromPacketStoreId,
	                        const std::string& toPacketStoreId, uint32_t startTime,
	                        Message& request);

	/**
	 * Performs all the necessary error checking for the case of BeforeTimeTag copying of packets.
	 *
	 * @param fromPacketStoreId the source packet store, whose content is to be copied.
	 * @param toPacketStoreId  the target packet store, which is going to receive the new content.
	 * @param request used to raise errors.
	 * @return true if an error has occurred.
	 */
	bool failedBeforeTimeTag(const std::string& fromPacketStoreId,
	                         const std::string& toPacketStoreId, uint32_t endTime,
	                         Message& request);

	/**
	 * Performs the necessary error checking for a request to start the by-time-range retrieval process.
	 *
	 * @param request used to raise errors.
	 * @return true if an error has occurred.
	 */
	bool failedStartOfByTimeRangeRetrieval(const std::string& packetStoreId, Message& request);

	/**
	 * Performs the necessary size checking for a request to add or delete packet stores.
	 *
	 * @param request used to raise errors.
	 * @return true if an error has occurred.
	 */	
	bool storeAndRetrievalTCSizeVerification(Message& request);
	
	/**
	 * Forms the content summary of the specified packet-store and appends it to a report message.
	 */
	void createContentSummary(Message& report, const std::string& packetStoreId);

	/**
	 * Counts the number of report types, stored for the specified service type.
	 */
	uint8_t countReportsOfService(const std::string& packetStoreId,
							uint16_t applicationID, uint8_t serviceType);
	
	/**
	 * Counts the number of service types, stored for the specified application process of a specific PacketStore.
	 */
	uint8_t countServicesOfApplication(const std::string& packetStoreId,
    									uint16_t applicationID);

	/**
	 * Performs the necessary error checking/logging for a specific service type. Also, skips the necessary bytes
	 * from the request message, in case of an invalid request.
	 *
	 * @return True: if the service type is valid and passes all the necessary error checking.
	 */
	bool checkService(Message& request, const std::string& packetStoreId, uint16_t applicationID, uint8_t numOfMessages);

	/**
	 * Checks if the maximum number of report type definitions per service type definition is reached.
	 */
	bool maxReportTypesReached(Message& request, const std::string& packetStoreId, 
							uint16_t applicationID, uint8_t serviceType);

	/**
	 * Checks if the maximum number of message types that can be contained inside a service type definition, is
	 * already reached.
	 *
	 * @return True: if the message type is valid and passes all the necessary error checking.
	 */
	bool checkMessage(Message& request, const std::string& packetStoreId, 
					uint16_t applicationID, uint8_t serviceType, uint8_t messageType);

	/**
	 * Checks whether the specified message type already exists in the specified Store with application process and service
	 * type definition.
	 */
	bool reportExistsInStoreConfiguration(const std::string& packetStoreId, 
							Message& message,
							uint16_t applicationID, uint8_t serviceType, 
							uint8_t messageType);

	/**
	 * Checks whether the specified message type already exists in the specified application process pool and service
	 * type definition.
	 */
	bool reportExistsInAppProcessConfiguration(uint16_t applicationID, uint8_t serviceType, 
							uint8_t messageType);
							
	/**
	 * Adds all report types of the specified service type, to the application process configuration.
	 */
	void addAllReportsOfService(const std::string& packetStoreId, uint16_t applicationID, uint8_t serviceType);

	/**
	 * Returns true, if the defined service type exists in the application process configuration map.
	 */
	bool isServiceTypeEnabled(const std::string& packetStoreId, uint16_t applicationID, uint8_t targetService);

	/**
	 * Checks whether the specified message type already exists in the specified application process and service
	 * type definition.
	 */
	bool isReportTypeEnabled(const std::string& packetStoreId, uint8_t target, uint16_t applicationID, uint8_t serviceType);

	/**
	 * Checks whether the requested service type is present in the application process configuration.
	 * Reports an error if one exist, skipping the necessary amount of bytes in the request.
	 */
	bool isServiceTypeInConfiguration(Message& request, const std::string& packetStoreId, 
						uint16_t applicationID, uint8_t serviceType, uint8_t numOfMessages);
	
	/**
	 * Checks whether the requested report type is present in the application process configuration.
	 * Reports an error if one exist.
	 */
	bool isReportTypeInConfiguration(Message& request, const std::string& packetStoreId, 
						uint16_t applicationID, uint8_t serviceType, uint8_t messageType);
	
	/**
	 * Deletes the requested service type from the application process configuration. If the deletion results in an
	 * empty application process, it deletes the corresponding application process definition as well.
	 */
	void deleteServiceRecursive(const std::string& packetStoreId, uint16_t applicationID, uint8_t serviceType);

	/**
	 * Deletes the requested report type from the application process configuration. If the deletion results in an
	 * empty service, it deletes the corresponding service. If the deletion of the service, results in an empty
	 * application process, it deletes the corresponding application process definition as well.
	 */
	void deleteReportRecursive(const std::string& packetStoreId, uint16_t applicationID, uint8_t serviceType, uint8_t messageType);
	
	/**
	 * Deletes every pair containing the requested application process ID, from the application process configuration, if it exists.
	 */
	void deleteApplicationProcess(const std::string& packetStoreId, uint16_t applicationID);			

	/**
	 * Checks if the specified application process is controlled by the Service and returns true if it does.
	 */
	bool checkAppControlled(Message& request, uint16_t applicationID);
	
	/**
	 * Performs the necessary error checking/logging for a specific application process ID. Also, skips the necessary
	 * bytes from the request message, in case of an invalid request.
	 *
	 * @return True: if the application is valid and passes all the necessary error checking.
	 */
	bool checkApplicationOfAppProcessConfig(Message& request, const std::string& packetStoreId,
							 uint16_t applicationID, uint8_t numOfServices);
	
	/**
	 * Checks if all service types are allowed already, i.e. if the application process contains no service type
	 * definitions.
	 */
	bool allServiceTypesAllowed(Message& request, const std::string& packetStoreId, uint16_t applicationID);		    	
	
	/**
	 * Checks if the maximum number of service type definitions per application process is reached.
	 */
	bool maxServiceTypesReached(Message& request, const std::string& packetStoreId, uint16_t applicationID);

    	void set_sample_rate(double rate);
    	
      	void parse_json(const std::string& filename);  

      TimeProvider* d_time_provider;

    	double d_sampleRate;
    	double d_byteDurationUs;

    	gr::thread::thread d_thread;
    	std::atomic<bool> d_finished;    
    	bool d_status;
    	bool d_suspend;
    
    	void run();
    	
     public:
      StorageAndRetrievalService_impl(const std::string& init_file, std::vector<uint16_t> vc_list, double samples_per_sec);
      ~StorageAndRetrievalService_impl();

      void handle_in_msg(pmt::pmt_t pdu);
	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);


      // Overloading these to start and stop the internal thread that
      // periodically produces the message.
    bool start() override;
    bool stop() override;
      
	/**
	 * Adds new packet store into packet stores.
	 */
	void addPacketStore(const std::string& packetStoreId, const PacketStore& packetStore);

	/**
	 * Adds telemetry to the specified packet store and timestamps it.
	 */
	void addTelemetryToPacketStore(const std::string& packetStoreId, uint32_t timestamp, Message& tmPacket);

	/**
	 * Deletes the content from all the packet stores.
	 */
	void resetPacketStores();

	/**
	 * Returns the number of existing packet stores.
	 */
	uint16_t currentNumberOfPacketStores();

	/**
	 * Returns the packet store with the specified packet store ID.
	 */
	PacketStore& getPacketStore(const std::string& packetStoreId);

	/**
	 * Returns true if the specified packet store is present in packet stores.
	 */
	bool packetStoreExists(const std::string& packetStoreId);

	/**
	 * Given a request that contains a number N, followed by N packet store IDs, this method calls function on every
	 * packet store. Implemented to reduce duplication. If N = 0, then function is applied to all packet stores.
	 * Incorrect packet store IDs are ignored and generate an error.

	 * @param function the job to be done after the error checking.
	 */
	void executeOnPacketStores(Message& request, const std::function<void(PacketStore&)>& function);

	/**
	 * TC[15,1] request to enable the packet stores' storage function
	 */
	void enableStorageFunction(Message& request);
	
	/**
	 * TC[15,2] request to disable the packet stores' storage function
	 */
	void disableStorageFunction(Message& request);

	/**
	 * TC[15,3] request to Add Packets definition to a packet store' storage function
	 */
	void addPacketsDefinitionsToPacketStores(Message& request);
	
	/**
	 * TC[15,4] request to Remove Packets definition to a packet store' storage function
	 */
	void removePacketsDefinitionsFromPacketStores(Message& request);
	
	/**
	 * TC[15,5] request an aplication process storage-control configuration content report
	 */
	void reportContentAPIDStoreConfig(Message& request);

	/**
	 * TC[15,9] start the by-time-range retrieval of packet stores
	 */
	void startByTimeRangeRetrieval(Message& request);

	/**
	 * TC[15,11] delete the packet store content up to the specified time
	 */
	void deletePacketStoreContent(Message& request);

	/**
	 * This function takes a TC[15,12] 'report the packet store content summary' as argument and responds with a TM[15,
	 * 13] 'packet store content summary report' report message.
	 */
	void packetStoreContentSummaryReport(Message& request);

	/**
	 * TC[15,14] change the open retrieval start time tag
	 */
	void changeOpenRetrievalStartTimeTag(Message& request);

	/**
	 * TC[15,15] resume the open retrieval of packet stores
	 */
	void resumeOpenRetrievalOfPacketStores(Message& request);

	/**
	 * TC[15,16] suspend the open retrieval of packet stores
	 */
	void suspendOpenRetrievalOfPacketStores(Message& request);

	/**
	 * TC[15,17] abort the by-time-range retrieval of packet stores
	 */
	void abortByTimeRangeRetrieval(Message& request);

	/**
	 * This function takes a TC[15,18] 'report the status of packet stores' request as argument and responds with a
	 * TM[15,19] 'packet stores status' report message.
	 */
	void packetStoresStatusReport(Message& request);

	/**
	 * TC[15,20] create packet stores
	 */
	void createPacketStores(Message& request);

	/**
	 * TC[15,21] delete packet stores
	 */
	void deletePacketStores(Message& request);

	/**
	 * This function takes a TC[15,22] 'report the packet store configuration' as argument and responds with a TM[15,
	 * 23] 'packet store configuration report' report message.
	 */
	void packetStoreConfigurationReport(Message& request);

	/**
	 * TC[15,24] copy the packets contained into a packet store, selected by the time window
	 */
	void copyPacketsInTimeWindow(Message& request);

	/**
	 * TC[15,25] resize packet stores
	 */
	void resizePacketStores(Message& request);

	/**
	 * TC[15,26] change the packet store type to circular
	 */
	void changeTypeToCircular(Message& request);

	/**
	 * TC[15,27] change the packet store type to bounded
	 */
	void changeTypeToBounded(Message& request);

	/**
	 * TC[15,28] change the virtual channel used by a packet store
	 */
	void changeVirtualChannel(Message& request);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_STORAGEANDRETRIEVALSERVICE_IMPL_H */
