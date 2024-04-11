/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#include <gnuradio/pus/Helpers/PMONBase.h>

 namespace gr {
  namespace pus {
  
  	PMONCheck::PMONCheck(uint8_t type, uint16_t repetitionNumber)
    	  : d_type(type),
  	    repetitionNumber(repetitionNumber)
  	{
  		clearDefinitionStatus() ;
  	}

  	void PMONCheck::clearDefinitionStatus() 
      	{
 		checkingStatus = Unchecked;
 		lastCheckingStatus = Unchecked;
              	checkTransitionList[0] = checkTransitionList[1];
              	checkTransitionList[1] = checkingStatus;
      		repetitionCounter = 0;
      	}
      	  	
  	bool PMONExpectedValueCheck::Check(double parameterValue, uint16_t& RID, bool& RID_added)
  	{
  		RID = 0;
	
  		if( parameterValue != expectedValue)
  			checkingStatus = PMONCheck::CheckingStatus::UnexpectedValue;
  		else
  			checkingStatus = PMONCheck::CheckingStatus::ExpectedValue;
   		
   		if(lastCheckingStatus != checkingStatus){
  			lastCheckingStatus= checkingStatus; 		
  			repetitionCounter = 0;
  		}
  		
  		if(checkTransitionList[1] != checkingStatus){
  			if(repetitionCounter++ == repetitionNumber){
               		transitionValue = parameterValue;

				transitionTime = TimeProvider::getInstance()->getCurrentTimeDefaultCUC();
				
				repetitionCounter = 0;

				limitCrossedValue = expectedValue;

				if(checkingStatus == PMONCheck::CheckingStatus::UnexpectedValue){
					RID = unexpectedValueEvent;
 				        limitCrossedValue = expectedValue;					
					RID_added = true;
     		
				}
               		checkTransitionList[0] = checkTransitionList[1];
               		checkTransitionList[1] = checkingStatus;
				
				if(checkTransitionList[0] != PMONCheck::CheckingStatus::Unchecked){
					return true;
				}

			}
		}else{
			repetitionCounter = 0;
		}

  		return false;
 	}

  	bool PMONLimitCheck::Check(double parameterValue, uint16_t& RID, bool& RID_added)
  	{
  		RID = 0;
  		if( parameterValue < lowLimit){
 			checkingStatus = PMONCheck::CheckingStatus::BelowLowLimit;
 		}else if(parameterValue > highLimit){
  			checkingStatus = PMONCheck::CheckingStatus::AboveHighLimit;
 		}else{
  			checkingStatus = PMONCheck::CheckingStatus::WithinLimits;
  		}	
   		if(lastCheckingStatus != checkingStatus){
  			lastCheckingStatus= checkingStatus; 		
  			repetitionCounter = 0;
  		}
  		
  		if(checkTransitionList[1] != checkingStatus){
  			if(repetitionCounter++ == repetitionNumber){
               		transitionValue = parameterValue;
               		transitionTime = TimeProvider::getInstance()->getCurrentTimeDefaultCUC();
               		repetitionCounter = 0;
               		
				if(checkingStatus == PMONCheck::CheckingStatus::BelowLowLimit){
					RID = belowLowLimitEvent;
					limitCrossedValue = lowLimit;
					RID_added = true;
				}else if(checkingStatus == PMONCheck::CheckingStatus::AboveHighLimit){
					RID = aboveHighLimitEvent;
					limitCrossedValue = highLimit;
					RID_added = true;
				}else{
					if(checkTransitionList[1] == PMONCheck::CheckingStatus::BelowLowLimit)
						limitCrossedValue = lowLimit;
					else if(checkingStatus == PMONCheck::CheckingStatus::AboveHighLimit)
						limitCrossedValue = highLimit;
				}
               		checkTransitionList[0] = checkTransitionList[1];
               		checkTransitionList[1] = checkingStatus;
				
				if(checkTransitionList[0] != PMONCheck::CheckingStatus::Unchecked){
					return true;
				}
			}
		}else{
			repetitionCounter = 0;
		}  	
  		return false;
 	}
 
   	bool PMONDeltaCheck::Check(double parameterValue, uint16_t& RID, bool& RID_added)
  	{
 		RID = 0;
		acumulativeParameter += parameterValue - previousValue;
		previousValue = parameterValue;

  		if(++consecutiveDeltaCount >= consecutiveDelta){

			consecutiveDeltaCount = 0;
	 		lastAcumulativeParameter = acumulativeParameter/(double)consecutiveDelta;
	 		acumulativeParameter = 0.0;
	 		
  			if( lastAcumulativeParameter < lowDeltaThreshold){
 				checkingStatus = PMONCheck::CheckingStatus::BelowLowThreshold;
  			}else if(lastAcumulativeParameter > highDeltaThreshold){
  				checkingStatus = PMONCheck::CheckingStatus::AboveHighThreshold;
 			}else{
  				checkingStatus = PMONCheck::CheckingStatus::WithinThreshold;	
  			}	 		
   			if(lastCheckingStatus != checkingStatus){
  				lastCheckingStatus= checkingStatus; 		
  				repetitionCounter = 0;
  			}
  		
  			if(checkTransitionList[1] != checkingStatus){
	  			if(++repetitionCounter >= repetitionNumber){

               			transitionValue = lastAcumulativeParameter;
               			transitionTime = TimeProvider::getInstance()->getCurrentTimeDefaultCUC();
               			repetitionCounter = 0;
               		               	
					if(checkingStatus == PMONCheck::CheckingStatus::BelowLowThreshold){
						RID = belowLowThresholdEvent;
						limitCrossedValue = lowDeltaThreshold;
						RID_added = true;
					}else if(checkingStatus == PMONCheck::CheckingStatus::AboveHighThreshold){
						RID = aboveHighThresholdEvent;
						limitCrossedValue = highDeltaThreshold;
						RID_added = true;
					}else{
						if(checkTransitionList[1] == PMONCheck::CheckingStatus::BelowLowThreshold)
							limitCrossedValue = lowDeltaThreshold;
						else if(checkingStatus == PMONCheck::CheckingStatus::AboveHighThreshold)
							limitCrossedValue = highDeltaThreshold;
					}

            		   		checkTransitionList[0] = checkTransitionList[1];
               			checkTransitionList[1] = checkingStatus;
				
					if(checkTransitionList[0] != PMONCheck::CheckingStatus::Unchecked){
						return true;
					}
				}	
 			}else{
				repetitionCounter = 0;
			}  	
  		 }
		 return false;
 	}
  
	PMONBase::PMONBase(uint16_t monitoredParameterId, uint16_t monitoringInterval, uint16_t repetitionNumber, bool enabled)
  	  : monitoredParameterId(monitoredParameterId),
  	    monitoringInterval(monitoringInterval),
  	    repetitionNumber(repetitionNumber)
  	{
  		d_parameter_pool = ParameterPool::getInstance();
		
  		setDefinitionEnableStatus(enabled);
  	}


	bool PMONBase::CheckState(std::vector<uint16_t>& RIDList)
	{
		if(!monitoringEnabled)
			return false;	
			
		bool checkDetection = false;
		
		if(monitoringIntervalCounter++ >= monitoringInterval)
			monitoringIntervalCounter = 0;
		else
			return false;	

		auto parameter = d_parameter_pool->getParameter(monitoredParameterId);
		if (!parameter) {
			return false;
		}
	
		double ParameterValue = parameter->get().getValueAsDouble();
	
		if(checkDefinition) {
			uint16_t RID = 0;
			bool RID_added = false;
               	bool result = checkDefinition->Check(ParameterValue, RID, RID_added);
               	if(RID_added){
				RIDList.push_back(RID);
               	}
               	if(result){
               		checkDetection = true;


               	}	
          			
            	}
            	return checkDetection;
	}

  	void PMONBase::loadIntoTransitionList(TransitionList& transitionList) 
      	{
		auto parameter = d_parameter_pool->getParameter(monitoredParameterId);
		if (!parameter) {
			return;
		}

		transitionList.push_back(checkDefinition->getType());
		if(checkDefinition->getType() == 0)
				parameter->get().appendValueAsTypeToVector(
					static_cast<PMONExpectedValueCheck*>(checkDefinition)->maskValue, transitionList);			
		parameter->get().appendValueAsTypeToVector(checkDefinition->transitionValue, transitionList);
		parameter->get().appendValueAsTypeToVector(checkDefinition->limitCrossedValue, transitionList);
		transitionList.push_back(checkDefinition->checkTransitionList[0]);
		transitionList.push_back(checkDefinition->checkTransitionList[1]);
		transitionList.push_back(static_cast<uint8_t>((checkDefinition->transitionTime >> 24) & 0xFF));
		transitionList.push_back(static_cast<uint8_t>((checkDefinition->transitionTime >> 16) & 0xFF));
		transitionList.push_back(static_cast<uint8_t>((checkDefinition->transitionTime >> 8) & 0xFF));
		transitionList.push_back(static_cast<uint8_t>(checkDefinition->transitionTime & 0xFF));
      	}

  	void PMONBase::setDefinitionEnableStatus(bool status) 
      	{
      		monitoringEnabled = status;
      		if(!monitoringEnabled){
 			if(checkDefinition){
      				checkDefinition->clearDefinitionStatus();
      			}
      		}
      	}	
  } // namespace pus
} // namespace gr
