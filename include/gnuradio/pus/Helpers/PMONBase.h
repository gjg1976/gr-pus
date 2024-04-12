/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_PMONBASE_H
#define ECSS_PMONBASE_H
#include <cstdint>
#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Helpers/ParameterPool.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include "etl/vector.h"

namespace gr {
  namespace pus {

    typedef std::vector<uint8_t> TransitionList;

class PMONCheck
{
    protected:
     	uint8_t d_type;
     	
    public:
	enum CheckingStatus : uint8_t {
		Unchecked = 1,
		Invalid = 2,
		ExpectedValue = 3,
		UnexpectedValue = 4,
		WithinLimits = 5,
		BelowLowLimit = 6,
		AboveHighLimit = 7,
		WithinThreshold = 8,
		BelowLowThreshold = 9,
		AboveHighThreshold = 10
	};
		
    	enum CheckType : uint8_t {
		ValueCheck = 0,
		LimitCheck = 1,
		DeltaCheck = 2
     	};

  	
	CheckingStatus checkingStatus = Unchecked;
	CheckingStatus lastCheckingStatus = Unchecked;
		
	std::array<CheckingStatus, 2> checkTransitionList = {};

	/**
	 * The number of checks that need to be conducted in order to set a new Parameter Monitoring Status.
	 */
	uint16_t paramID;
	/**
	 * The number of checks that need to be conducted in order to set a new Parameter Monitoring Status.
	 */
	uint16_t repetitionNumber;
	/**
	 * The number of checks that have been conducted so far.
	 */
	uint16_t repetitionCounter = 0;
	
	uint32_t transitionTime = 0;
	
	double transitionValue = 0;
	
	double limitCrossedValue = 0;
     
     	PMONCheck(uint8_t type, uint16_t repetitionNumber);
     	virtual ~PMONCheck() {};
     	virtual bool Check(double parameterValue, uint16_t& RID, bool& RID_added) = 0;
      	    	
     	inline uint8_t getType() {return d_type;};
     	
     	void clearDefinitionStatus() ;
};

/**
 * Contains the variables specific to Parameter Monitoring definitions of expected value check type.
 */
class PMONExpectedValueCheck : public PMONCheck {
public:
	double maskValue;
	double expectedValue;
	uint16_t unexpectedValueEvent;

	explicit PMONExpectedValueCheck(double maskValue, double expectedValue,
	                                uint16_t unexpectedValueEvent,
	                                uint16_t repetitionNumber)
	    : PMONCheck(PMONCheck::CheckType::ValueCheck, repetitionNumber), 
	        maskValue(maskValue), expectedValue(expectedValue), 
	        unexpectedValueEvent(unexpectedValueEvent){};

     	bool Check(double parameterValue, uint16_t& RID, bool& RID_added) override;
};

/**
 * Contains the variables specific to Parameter Monitoring definitions of limit check type.
 */
class PMONLimitCheck : public PMONCheck {
public:
	double lowLimit;
	uint16_t belowLowLimitEvent;
	double highLimit;
	uint16_t aboveHighLimitEvent;

	explicit PMONLimitCheck(double lowLimit, uint16_t belowLowLimitEvent, 
				double highLimit, uint16_t aboveHighLimitEvent,
	                                uint16_t repetitionNumber)
	    : PMONCheck(PMONCheck::CheckType::LimitCheck, repetitionNumber),
	       lowLimit(lowLimit), belowLowLimitEvent(belowLowLimitEvent), highLimit(highLimit),
	      aboveHighLimitEvent(aboveHighLimitEvent){};

     	bool Check(double parameterValue, uint16_t& RID, bool& RID_added) override;
};

/**
 * Contains the variables specific to Parameter Monitoring definitions of delta check type.
 */
class PMONDeltaCheck : public PMONCheck {
public:
	double lastAcumulativeParameter = 0.0;	
	double acumulativeParameter = 0.0;	
	double previousValue = 0.0;
	double lowDeltaThreshold;
	uint16_t belowLowThresholdEvent;
	double highDeltaThreshold;
	uint16_t aboveHighThresholdEvent;
	uint16_t consecutiveDelta;
	uint16_t consecutiveDeltaCount = 0;
	
	explicit PMONDeltaCheck(double lowDeltaThreshold,
	                        uint16_t belowLowThresholdEvent, double highDeltaThreshold,
	                        uint16_t aboveHighThresholdEvent,
	                        uint16_t repetitionNumber,
	                        uint16_t consecutiveDelta,
	                        double startValue)
	    : PMONCheck(PMONCheck::CheckType::DeltaCheck, repetitionNumber),
	      previousValue(startValue), lowDeltaThreshold(lowDeltaThreshold),
	      belowLowThresholdEvent(belowLowThresholdEvent), highDeltaThreshold(highDeltaThreshold),
	      aboveHighThresholdEvent(aboveHighThresholdEvent), consecutiveDelta(consecutiveDelta){};

     	bool Check(double parameterValue, uint16_t& RID, bool& RID_added) override;
};
/**
 * Base class for Parameter Monitoring definitions. Contains the common variables of all check types.
 */
class PMONBase {
public:
	uint16_t monitoredParameterId;

	ParameterPool* d_parameter_pool;
	/**
	 * The number of ticks from timer before his parameter checked.
	 */
	uint16_t monitoringInterval;
	/**
	 * The numberof ticks that have been counter so far.
	 */
	uint16_t monitoringIntervalCounter = 0;
	/**
	 * The number of checks that need to be conducted in order to set a new Parameter Monitoring Status.
	 */
	uint16_t repetitionNumber;
	/**
	 * The number of checks that have been conducted so far.
	 */
	uint16_t repetitionCounter = 0;
	/**
	 * The number of checks that need to be conducted in order to set a new Parameter Monitoring Status for delta checks.
	 */
	uint16_t deltaRepetitionNumber;
	/**
	 * The number of checks that have been conducted so far for delta checks.
	 */
	uint16_t deltaRepetitionCounter = 0;
	
      	void setDefinitionEnableStatus(bool status);	
      	
     	inline bool getDefinitionEnableStatus() {return monitoringEnabled;};
	/**
	 * @brief Hold the check definitions
	 *
	 * @details The check definition for the monitored parameter are held in this list.
	 */
	PMONCheck* checkDefinition = NULL;

	/**
	 * @param monitoredParameterId is assumed to be correct and not checked.
	 */
	PMONBase(uint16_t monitoredParameterId, uint16_t monitoringInterval, uint16_t repetitionNumber, bool enabled = false);
	
	bool CheckState(std::vector<uint16_t>& RID);

	void loadIntoTransitionList(TransitionList& transitionList); 
	  	
    protected:
   	bool monitoringEnabled = false;   

};

  } /* namespace pus */
} /* namespace gr */
#endif // ECSS_PMONBASE_H
