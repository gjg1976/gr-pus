/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_HOUSEKEEPINGSERVICE_IMPL_H
#define INCLUDED_PUS_HOUSEKEEPINGSERVICE_IMPL_H

#include <gnuradio/pus/HousekeepingService.h>
#include <gnuradio/pus/Helpers/ParameterPool.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/HousekeepingStructure.h>
#include <nlohmann/json.hpp>
#include <fstream>
#include <gnuradio/pus/RequestVerificationService.h>
#include "etl/map.h"
#include <chrono>
#include "etl/vector.h"

#define HK_STRUCT_ID_SIZE  1
#define HK_STRUCT_INTERVAL_SIZE  2
#define HK_STRUCT_NUM_PARAM_SIZE  2
#define HK_STRUCT_PARAM_SIZE  2
#define HK_STRUCT_NUM_FIXED_ARRAY_SIZE  2
#define HK_STRUCT_SUPER_CONMUTATED_REPETITION_SIZE  1
#define HK_STRUCT_NUM_SUPER_CONMUTATED_ARRAY_SIZE  1
#define HK_NUM_STRUCT_SIZE  1
#define HK_STRUCT_SIZE  1

namespace gr {
  namespace pus {

    class HousekeepingService_impl : public HousekeepingService
    {
     private:
      uint16_t counters[HousekeepingService::MessageType::end];
      TimeProvider* d_time_provider;
      
      ParameterPool* d_parameter_pool;

	/**
	 * Map containing the housekeeping structures. Map[i] contains the housekeeping structure with ID = i.
	 */
	etl::map<uint8_t, HousekeepingStructure, ECSSMaxHousekeepingStructures> housekeepingStructures;


	/**
	 * Returns a reference to the structure at position of "id" in the map.
	 * @param id Housekeeping structure ID
	 * @return optional<std::reference_wrapper<HousekeepingStructure>> Reference to Housekeeping Structure
	 */
	inline std::optional<std::reference_wrapper<HousekeepingStructure>> getStruct(uint8_t id) {
		if (hasNonExistingStructInternalError(id)) {
			return {};
		}
		return housekeepingStructures.at(id);
	}

	/**
	 * Returns the collection interval (how often data is collected) of a Housekeeping structure.
	 * @param id Housekeeping structure ID
	 * @return uint32_t Integer multiples of the minimum sampling interval
	 */
	inline uint32_t getCollectionInterval(uint8_t id) {
		HousekeepingStructure newStructure{};
		if (hasNonExistingStructInternalError(id)) {
			return newStructure.collectionInterval;
		}
		return housekeepingStructures.at(id).collectionInterval;
	}
	
	/**
	 * Checks if the structure exists in the map.
	 * @param id Housekeeping structure ID
	 * @return boolean True if the structure exists, false otherwise
	 */
      inline bool structExists(uint8_t id) {
		return (housekeepingStructures.find(id) != housekeepingStructures.end());
      };
	/**
	 * Returns true if the given parameter ID exists in the parameters contained in the housekeeping structure.
	 */
      inline bool existsInVector(const etl::vector<uint16_t, ECSSMaxSimplyCommutatedParameters>& ids, uint16_t parameterId){
		return std::find(std::begin(ids), std::end(ids), parameterId) != std::end(ids);
	};

	/**
	 * Returns the periodic generation action status of a Housekeeping structure.
	 * @param id Housekeeping structure ID
	 * @return boolean True if periodic generation of housekeeping reports is enabled, false otherwise
	 */
	inline bool getPeriodicGenerationActionStatus(uint8_t id) {
		HousekeepingStructure newStructure{};
		if (hasNonExistingStructInternalError(id)) {
			return newStructure.periodicGenerationActionStatus;
		}
		return housekeepingStructures.at(id).periodicGenerationActionStatus;
	}

	/**
	 * Sets the periodic generation action status of a Housekeeping structure.
	 * @param id Housekeeping structure ID
	 * @param status Periodic generation status of housekeeping reports
	 */
	inline void setPeriodicGenerationActionStatus(uint8_t id, bool status) {
		if (hasNonExistingStructInternalError(id)) {
			return;
		}
		housekeepingStructures.at(id).periodicGenerationActionStatus = status;
	}

	/**
	 * Sets the collection interval of a Housekeeping structure.
	 * @param id Housekeeping structure ID
	 * @param interval Integer multiples of the minimum sampling interval
	 */
	inline void setCollectionInterval(uint8_t id, uint32_t interval) {
		if (hasNonExistingStructInternalError(id)) {
			return;
		}
		housekeepingStructures.at(id).collectionInterval = interval;
	}

	/**
	 * Checks if the super conmutated array exists in the housekeeping struct.
	 * @param id Housekeeping structure 
	 * @param superConmutatedInterval super conmutated array to look for
	 */
      bool hasAlreadyExistingSuperConmutatedArray(HousekeepingStructure& housekeepingStruct, uint8_t superConmutatedInterval);		
	
	/**
	 * Checks if the struct requested exists and if it exists reports execution error.
	 * @param id Housekeeping structure ID
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if the structure exists, false otherwise
	 */
      bool hasAlreadyExistingStructError(uint8_t id, Message& request );

	/**
	 * Reports execution error if the max number of housekeeping structures is exceeded.
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if max number of housekeeping structures is exceeded, false otherwise
	 */
      bool hasExceededMaxNumOfHousekeepingStructsError(Message& request);

	/**
	 * Checks if the structure doesn't exist in the map and then accordingly reports execution start error.
	 * @param id Housekeeping structure ID
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if the structure doesn't exist, false otherwise
	 */
	bool hasNonExistingStructExecutionError(uint8_t id, Message& request);
	
	/**
	 * Checks if the parameter exists in the vector and if it does it reports an error.
	 * @param id Parameter ID
	 * @param housekeepingStruct Housekkeping Structure
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if the parameter exists, false otherwise
	 */
      bool hasAlreadyExistingParameterError(HousekeepingStructure& housekeepingStruct, uint8_t id, Message& request);

	/**
	 * Checks if the parameter exists in the vector and if it does it reports an error.
	 * @param id Parameter ID
	 * @param housekeepingSuperArray Housekeeping Super Conmutated Array
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if the parameter exists, false otherwise
	 */
      bool hasAlreadyExistingSuperConmutatedParameterError(HousekeepingSuperConmutatedArrays& housekeepingSuperArray, uint8_t id, 
    			Message& req);
	/**
	 * Reports execution error if it's attempted to delete structure which has the periodic reporting status enabled.
	 * @param id Housekeeping structure ID
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if periodic reporting status is enabled, false otherwise
	 */
	bool hasRequestedDeletionOfEnabledHousekeepingError(uint8_t id, Message& request);	
	
	/**
	 * Checks if the structure doesn't exist in the map and then accordingly reports internal error.
	 * @param id Housekeeping structure ID
	 * @return boolean True if the structure doesn't exist, false otherwise
	 */
	bool hasNonExistingStructInternalError(uint8_t id);

	/**
	 * Checks if the structure doesn't exist in the map and then accordingly reports error.
	 * @param id Housekeeping structure ID
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if the structure doesn't exist, false otherwise
	 */
	bool hasNonExistingStructError(uint8_t id, Message& request);		      		

	/**
	 * Reports execution error if it's attempted to append a new parameter id to a housekeeping structure, but the periodic generation status is enabled.
	 * @param housekeepingStruct Housekkeping Structure
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if periodic generation status is enabled, false otherwise
	 */
	bool hasRequestedAppendToEnabledHousekeepingError(HousekeepingStructure& housekeepingStruct, Message& request);	

	/**
	 * Reports execution error if the max number of simply commutated parameters is exceeded.
	 * @param housekeepingStruct Housekkeping Structure
	 * @param request Telemetry (TM) or telecommand (TC) message
	 * @return boolean True if max number of simply commutated parameters is exceeded, false otherwise
	 */
	bool hasExceededMaxNumOfSimplyCommutatedParamsError(HousekeepingStructure& housekeepingStruct, Message& request);

	/**
	 * Reports verification size for create and delete Housekeeping structure messages.
	 * @param request telecommand (TC) message
	 * @return boolean True if size match with expected one, false otherwise
	 */	
        bool housekeepingReportStructureSizeVerification(Message& request, bool intervalSizePresent);
	
	void parse_json(const std::string& filename);   
	
     public:
      HousekeepingService_impl(const std::string& init_file);
      ~HousekeepingService_impl();
         
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
	 * Implementation of TC[3,1]. Request to create a housekeeping parameters report structure.
	 */
      void createHousekeepingReportStructure(Message& request);

	/**
	 * Implementation of TC[3,3]. Request to delete a housekeeping parameters report structure.
	 */
      void deleteHousekeepingReportStructure(Message& request);

	/**
	 * Implementation of TC[3,5]. Request to enable the periodic housekeeping parameters reporting for a specific
	 * housekeeping structure.
	 */
      void enablePeriodicHousekeepingParametersReport(Message& request);

	/**
	 * Implementation of TC[3,6]. Request to disable the periodic housekeeping parameters reporting for a specific
	 * housekeeping structure.
	 */
      void disablePeriodicHousekeepingParametersReport(Message& request);
      
	/**
	 * This function gets a message type TC[3,9] 'report housekeeping structures'.
	 */
      void reportHousekeepingStructures(Message& request);

	/**
	 * This function takes a structure ID as argument and constructs/stores a TM[3,10] housekeeping structure report.
	 */
      void housekeepingStructureReport(uint8_t structIdToReport);

	/**
	 * This function gets a housekeeping structure ID and stores a TM[3,25] 'housekeeping
	 * parameter report' message.
	 */
      void housekeepingParametersReport(uint8_t structureId);

	/**
	 * This function takes as argument a message type TC[3,27] 'generate one shot housekeeping report' and stores
	 * TM[3,25] report messages.
	 */
      void generateOneShotHousekeepingReport(Message& request);

	/**
	 * This function receives a message type TC[3,29] 'append new parameters to an already existing housekeeping
	 * structure'
	 *
	 * @note As per 6.3.3.8.d.4, in case of an invalid parameter, the whole message shall be rejected. However, a
	 * convention was made, saying that it would be more practical to just skip the invalid parameter and continue
	 * processing the rest of the message.
	 */
      void appendParametersToHousekeepingStructure(Message& request);

	/**
	 * This function receives a message type TC[3,31] 'modify the collection interval of specified structures'.
	 */
      void modifyCollectionIntervalOfStructures(Message& request);

	/**
	 * This function takes as argument a message type TC[3,33] 'report housekeeping periodic properties' and
	 * responds with a TM[3,35] 'housekeeping periodic properties report'.
	 */
      void reportHousekeepingPeriodicProperties(Message& request);

  
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_HOUSEKEEPINGSERVICE_IMPL_H */
