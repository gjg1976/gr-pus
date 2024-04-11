/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_REALTIMEFORWARDINGCONTROLSERVICE_IMPL_H
#define INCLUDED_PUS_REALTIMEFORWARDINGCONTROLSERVICE_IMPL_H

#include <gnuradio/pus/RealTimeForwardingControlService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Helpers/ForwardControlConfiguration.h>
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
#include "etl/vector.h"
#include <nlohmann/json.hpp>
#include <fstream>

#define RT_FWD_NUM_APP_SIZE  2
#define RT_FWD_APPID_SIZE  2
#define RT_FWD_NUM_SERVICES_SIZE  2
#define RT_FWD_SERVICES_SIZE  1
#define RT_FWD_NUM_SUBTYPES_SIZE  2
#define RT_FWD_SUBTYPES_SIZE  1 

namespace gr {
  namespace pus {

    class RealTimeForwardingControlService_impl : public RealTimeForwardingControlService
    {
     private:
      uint16_t counters[RealTimeForwardingControlService::MessageType::end];

	/**
	 * Contains the Application IDs, controlled by the Service.
	 */
	etl::vector<uint16_t, ECSSMaxControlledApplicationProcesses> controlledApplications;

	/**
	 * The Application Process configuration, containing all the application process, service type and message type
	 * definitions.
	 */
	ApplicationProcessConfiguration applicationProcessConfiguration;
	
	/**
	 * Adds all report types of the specified application process definition, to the application process configuration.
	 */
	void addAllReportsOfApplication(uint16_t applicationID);

	/**
	 * Adds all report types of the specified service type, to the application process configuration.
	 */
	void addAllReportsOfService(uint16_t applicationID, uint8_t serviceType);

	/**
	 * Counts the number of service types, stored for the specified application process.
	 */
	uint8_t countServicesOfApplication(uint16_t applicationID);

	/**
	 * Counts the number of report types, stored for the specified service type.
	 */
	uint8_t countReportsOfService(uint16_t applicationID, uint8_t serviceType);

	/**
	 * Checks whether the specified message type already exists in the specified application process and service
	 * type definition.
	 */
	bool reportExistsInAppProcessConfiguration(uint16_t applicationID, uint8_t serviceType, uint8_t messageType);

	/**
	 * Performs the necessary error checking/logging for a specific application process ID. Also, skips the necessary
	 * bytes from the request message, in case of an invalid request.
	 *
	 * @return True: if the application is valid and passes all the necessary error checking.
	 */
	bool checkApplicationOfAppProcessConfig(Message& request, uint16_t applicationID, uint8_t numOfServices);

	/**
	 * Checks if the specified application process is controlled by the Service and returns true if it does.
	 */
	bool checkAppControlled(Message& request, uint16_t applicationID);

	/**
	 * Checks if all service types are allowed already, i.e. if the application process contains no service type
	 * definitions.
	 */
	bool allServiceTypesAllowed(Message& request, uint16_t applicationID);

	/**
	 * Checks if the maximum number of service type definitions per application process is reached.
	 */
	bool maxServiceTypesReached(Message& request, uint16_t applicationID);

	/**
	 * Performs the necessary error checking/logging for a specific service type. Also, skips the necessary bytes
	 * from the request message, in case of an invalid request.
	 *
	 * @return True: if the service type is valid and passes all the necessary error checking.
	 */
	bool checkService(Message& request, uint16_t applicationID, uint8_t numOfMessages);

	/**
	 * Checks if the maximum number of report type definitions per service type definition is reached.
	 */
	bool maxReportTypesReached(Message& request, uint16_t applicationID, uint8_t serviceType);

	/**
	 * Checks if the maximum number of message types that can be contained inside a service type definition, is
	 * already reached.
	 *
	 * @return True: if the message type is valid and passes all the necessary error checking.
	 */
	bool checkMessage(Message& request, uint16_t applicationID, uint8_t serviceType, uint8_t messageType);

	/**
	 * Returns true, if the defined application exists in the application process configuration map.
	 */
	bool isApplicationEnabled(uint16_t targetAppID);

	/**
	 * Returns true, if the defined service type exists in the application process configuration map.
	 */
	bool isServiceTypeEnabled(uint16_t applicationID, uint8_t targetService);

	/**
	 * Checks whether the specified message type already exists in the specified application process and service
	 * type definition.
	 */
	bool isReportTypeEnabled(uint8_t target, uint16_t applicationID, uint8_t serviceType);

	/**
	 * Deletes every pair containing the requested application process ID, from the application process configuration, if it exists.
	 */
	void deleteApplicationProcess(uint16_t applicationID);

	/**
	 * Checks whether the requested application is present in the application process configuration.
	 * Reports an error if one exist, skipping the necessary amount of bytes in the request.
	 */
	bool isApplicationInConfiguration(Message& request, uint16_t applicationID, uint8_t numOfServices);

	/**
	 * Checks whether the requested service type is present in the application process configuration.
	 * Reports an error if one exist, skipping the necessary amount of bytes in the request.
	 */
	bool isServiceTypeInConfiguration(Message& request, uint16_t applicationID, uint8_t serviceType, uint8_t numOfMessages);

	/**
	 * Checks whether the requested report type is present in the application process configuration.
	 * Reports an error if one exist.
	 */
	bool isReportTypeInConfiguration(Message& request, uint16_t applicationID, uint8_t serviceType, uint8_t messageTypep);

	/**
	 * Deletes the requested service type from the application process configuration. If the deletion results in an
	 * empty application process, it deletes the corresponding application process definition as well.
	 */
	void deleteServiceRecursive(uint16_t applicationID, uint8_t serviceType);

	/**
	 * Deletes the requested report type from the application process configuration. If the deletion results in an
	 * empty service, it deletes the corresponding service. If the deletion of the service, results in an empty
	 * application process, it deletes the corresponding application process definition as well.
	 */
	void deleteReportRecursive(uint16_t applicationID, uint8_t serviceType, uint8_t messageType);

	/**
	 * Verifies the size of the RT forward service telecommands.
	 */
	bool realtimeForwardTCSizeVerification(Message& request);
  	
     public:
      RealTimeForwardingControlService_impl(const std::string& init_file);
      ~RealTimeForwardingControlService_impl();


	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);

      void handle_in_msg(pmt::pmt_t pdu);

      void parse_json(const std::string& filename);
	 /**
	 * TC[14,1] 'Add report types to the application process forward control configuration'.
	 */
	void addReportTypesToAppProcessConfiguration(Message& request);

	/**
	 * TC[14,2] 'Delete report types from the application process forward control configuration'.
	 */  
	void deleteReportTypesFromAppProcessConfiguration(Message& request);

	/**
	 * TC[14,3] 'Retrieve the report types from the application process forward control configuration'.
	 */  
	void reportEnabledTelemetrySourcePackets(Message& request);

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_REALTIMEFORWARDINGCONTROLSERVICE_IMPL_H */
