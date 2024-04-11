/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_ONBOARDMONITORINGSERVICE_IMPL_H
#define INCLUDED_PUS_ONBOARDMONITORINGSERVICE_IMPL_H

#include <gnuradio/pus/OnBoardMonitoringService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Helpers/PMONBase.h>
#include "etl/map.h"
#include "etl/vector.h"

#define ONBOARD_MON_NUM_PMON  2
#define ONBOARD_MON_PMONID 2
#define ONBOARD_MON_TRANS_DELAY 2
#define ONBOARD_MON_PARAMID 2
#define ONBOARD_MON_INTERVAL 2
#define ONBOARD_MON_COUNTER 2
#define ONBOARD_MON_DEF_TYPE 1
#define ONBOARD_MON_RID 2
#define ONBOARD_MON_DELTA_COUNTER 2


namespace gr {
  namespace pus {


    class OnBoardMonitoringService_impl : public OnBoardMonitoringService
    {
     private:
      uint16_t counters[OnBoardMonitoringService::MessageType::end];
      TimeProvider* d_time_provider;
       ParameterPool* d_parameter_pool;
	/**
	 * Map storing the parameter monitoring definitions.
	 */
	etl::map<uint16_t, PMONBase, ECSSMaxMonitoringDefinitions> parameterMonitoringList;

      void parse_json(const std::string& filename);  

      bool hasNonExistingParameterMonitoringExecutionError(uint8_t id, Message& req);

      bool parameterMonitoringIsEnabledExecutionError(uint8_t id, Message& req);


	/**
	 * Checks if the parameter monitoring definition is in the map.
	 * @param id parameter ID
	 * @return boolean True if the definition exists, false otherwise
	 */
      inline bool parameterMonitoringExists(uint16_t id) {
		return (parameterMonitoringList.find(id) != parameterMonitoringList.end());
      };     

      inline bool parameterExists(uint16_t id) {
		auto parameter = d_parameter_pool->getParameter(id);
		if (!parameter) {
			return false;
		}
		return true;
      };  
      
      bool hasExistingDefinition(uint8_t defType, PMONBase& PMONbase);
 
 			
      uint16_t transitionsCounter = 0;
      TransitionList transitionList; 
 	     
     public:
	enum MessageType : uint8_t {
		expectedValueChecking = 0,
		limitChecking = 1,
		deltaChecking = 2
	};
	   
      OnBoardMonitoringService_impl(const std::string& init_file);
      ~OnBoardMonitoringService_impl();

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
	 * The maximum time between two transition reports.
	 * Measured in "on-board parameter minimum sampling interval" units (see 5.4.3.2c in ECSS-E-ST-70-41C).
	 */
	uint16_t maximumTransitionReportingDelay = MaximumTransitionsReportDelay;
	uint16_t maximumTransitionReportingDelayCounter = 0;
	uint16_t maximumNumberOfTransitionCounter = 0;
	bool transitionDetection = false;
	/**
	 * If true, parameter monitoring is enabled
	 */
	bool parameterMonitoringFunctionStatus = false;
	/*
	 * Adds a new Parameter Monitoring definition to the parameter monitoring list.
	 */
	void addPMONDefinition(uint16_t PMONId, PMONBase& PMONDefinition) {
		parameterMonitoringList.insert({PMONId, PMONDefinition});
	}

	/**
	 * @param PMONId
	 * @return Parameter Monitoring definition
	 */
	PMONBase getPMONDefinition(uint16_t PMONId) {
		return parameterMonitoringList.at(PMONId);
	}
	/**
	 * @return true if PMONList is empty.
	 */
	bool isPMONListEmpty() {
		return parameterMonitoringList.empty();
	}
	/**
	 * Enables the PMON definitions which correspond to the ids in TC[12,1].
	 */
	void enableParameterMonitoringDefinitions(Message& message);

	/**
	 * Disables the PMON definitions which correspond to the ids in TC[12,2].
	 */
	void disableParameterMonitoringDefinitions(Message& message);

	/**
	 * TC[12,3]
	 * Changes the maximum time between two transition reports.
	 */
	void changeMaximumTransitionReportingDelay(Message& message);

	/**
	 * TC[12,4]
	 * Deletes all the PMON definitions in the PMON list.
	 */
	void deleteAllParameterMonitoringDefinitions(Message& message);
	
	/**
	 * TC[12,5]
	 * Add PMON definitions in the PMON list.
	 */
	void addParameterMonitoringDefinitions(Message& message);
	
	/**
	 * TC[12,6]
	 * Delete a PMON definitions from the PMON list.
	 */
	void deleteParameterMonitoringDefinitions(Message& message);

	/**
	 * TC[12,7]
	 * Modify PMON definitions from the PMON list.
	 */
	void modifyParameterMonitoringDefinitions(Message& message);	
	/**
	 * TC[12,8]
	 * Request a reports with all the PMON definitions in the PMON list.
	 */
	void reportParameterMonitoringDefinitions(Message& message);
	
	
	/**
	 * TM[12,9]
	 * Reports with all the PMON definitions in the PMON list.
	 */
	void parameterMonitoringDefinitionReport(std::vector<uint16_t> parameterList);
	
	
	/**
	 * TC[12,10]
	 * Report Current Parameters Out of Limits.
	 */
	void reportOutOfLimits(Message& message);

	/**
	 * TM[12,11]
	 * Current Parameters Out of Limits Report.
	 */
	void outOfLimitsReport();

	/**
	 * TM[12,12]
	 * check Transition Report.
	 */
	void checkTransitionReport();	

	/**
	 * TM[12,13]
	 * Report Monitoring Definition Status.
	 */	
	void reportStatusOfParameterMonitoringDefinition(Message& message);
	
	/**
	 * TM[12,14]
	 * Monitoring Definition Status Report.
	 */	
	void parameterMonitoringDefinitionStatusReport();

	/**
	 * Enables the PMON function TC[12,15].
	 */
	void enableParameterMonitoringFunction(Message& message);

	/**
	 * Disables the PMON function TC[12,16].
	 */
	void disableParameterMonitoringFunction(Message& message);

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_ONBOARDMONITORINGSERVICE_IMPL_H */
