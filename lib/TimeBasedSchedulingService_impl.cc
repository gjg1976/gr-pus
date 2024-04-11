/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "TimeBasedSchedulingService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    TimeBasedSchedulingService::sptr
    TimeBasedSchedulingService::make()
    {
      return gnuradio::make_block_sptr<TimeBasedSchedulingService_impl>(
        );
    }


    /*
     * The private constructor
     */
    TimeBasedSchedulingService_impl::TimeBasedSchedulingService_impl()
      : gr::block("TimeBasedSchedulingService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        serviceType = ServiceType;
        for(size_t i = 0; i < TimeBasedSchedulingService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);
        message_port_register_out(PMT_REL);

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;


    	d_time_provider = TimeProvider::getInstance();
    
    	d_time_provider->addHandler(
            serviceType,
            std::bind(
                &TimeBasedSchedulingService_impl::timerTick,
                this,
                std::placeholders::_1
            )
    	);
    }

    /*
     * Our virtual destructor.
     */
    TimeBasedSchedulingService_impl::~TimeBasedSchedulingService_impl()
    {
            d_time_provider->removeHandler(serviceType);  
    }

    void TimeBasedSchedulingService_impl::timerTick(TimeProvider *p) {
        // Gets called when new data arrives 
       executeScheduledActivity(Time::DefaultCUC(d_time_provider->getCurrentTimeUTC()));
        
    }
    
    void TimeBasedSchedulingService_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);

        // extract data
        if (pmt::is_u8vector(v_data)) {
                std::vector<uint8_t> inData = pmt::u8vector_elements(v_data);

                MessageArray in_data(inData.data(), inData.data() + inData.size());                
                Message message  = d_message_parser->ParseMessageCommand(in_data);
                if(serviceType == message.getMessageServiceType()){
                    switch (message.getMessageType()) {
                        case EnableTimeBasedScheduleExecutionFunction:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "EnableTimeBasedScheduleExecutionFunction");
#endif
                           enableScheduleExecution(message);
                           break;
                        case DisableTimeBasedScheduleExecutionFunction:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DisableTimeBasedScheduleExecutionFunction");
#endif
                           disableScheduleExecution(message);
                           break;                                             
                        case ResetTimeBasedSchedule:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "ResetTimeBasedSchedule");
#endif
                           resetSchedule(message);
                           break;
                        case InsertActivities:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "InsertActivities");
#endif
                           insertActivities(message);
                           break;
                        case DeleteActivitiesById:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeleteActivitiesById");
#endif
                           deleteActivitiesByID(message);
                           break;
                        case TimeShiftActivitiesById:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "TimeShiftActivitiesById");
#endif
                           timeShiftActivitiesByID(message);
                           break;
                        case DetailReportActivitiesById:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DetailReportActivitiesById");
#endif
                           detailReportActivitiesByID(message);
                           break;
                        case ActivitiesSummaryReportById:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ActivitiesSummaryReportById");
#endif
                           summaryReportActivitiesByID(message);
                           break;
                        case TimeShiftAllScheduledActivities:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "TimeShiftAllScheduledActivities");
#endif
                           timeShiftAllActivities(message);
                           break;
                        case DetailReportAllScheduledActivities:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "DetailReportAllScheduledActivities");
#endif
                           detailReportAllActivities(message);
                           break;                     
                        case SummaryReportAllScheduledActivities:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "SummaryReportAllScheduledActivities");
#endif
                           summaryReportAllActivities(message);
                           break; 
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Time Based Scheduling Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);
			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Time Based Scheduling Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }
   
    Time::DefaultCUC TimeBasedSchedulingService_impl::executeScheduledActivity(Time::DefaultCUC currentTime) {
	if (currentTime >= scheduledActivities.front().requestReleaseTime && !scheduledActivities.empty()) {
		if (scheduledActivities.front().requestID.applicationID == ApplicationId) {
		      if(executionFunctionStatus){
              		 message_port_pub(PMT_REL, pmt::cons(pmt::PMT_NIL, 
                			pmt::init_u8vector(scheduledActivities.front().request.getMessageData().size(),
                			scheduledActivities.front().request.getMessageRawData())));
                      }
		}
		scheduledActivities.pop_front();
	}

	if (!scheduledActivities.empty()) {
		return scheduledActivities.front().requestReleaseTime;
	} else {
		return Time::DefaultCUC::max();
	}
    }

    void TimeBasedSchedulingService_impl::enableScheduleExecution(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::EnableTimeBasedScheduleExecutionFunction)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	reportSuccessAcceptanceVerification(request);

	executionFunctionStatus = true;

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);

    }

    void TimeBasedSchedulingService_impl::disableScheduleExecution(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::DisableTimeBasedScheduleExecutionFunction)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	reportSuccessAcceptanceVerification(request);

	executionFunctionStatus = false;

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
    }

    void TimeBasedSchedulingService_impl::resetSchedule(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::ResetTimeBasedSchedule)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	reportSuccessAcceptanceVerification(request);
	
	executionFunctionStatus = false;
	scheduledActivities.clear();
	// todo: Add resetting for sub-schedules and groups, if defined

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
    }

    void TimeBasedSchedulingService_impl::insertActivities(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::InsertActivities)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < TIME_SCH_NUM_TC){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	tcSize -= TIME_SCH_NUM_TC;
		
	// todo: Get the sub-schedule ID if they are implemented
	uint16_t iterationCount = request.readUint16();

 	uint16_t currentPosition = request.getMessageReadPosition();
 	
 	for (uint16_t i = 0; i < iterationCount; i++) {	
 		if(tcSize < TIME_SCH_TIME_DEF){
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return;
		} 
		tcSize -= TIME_SCH_TIME_DEF;
		
		uint32_t time = request.readUint32();
		MessageArray message_definition = d_message_parser->parseTCfromMessage(request);
		if(message_definition.size() == 0){
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return;
		} 
		tcSize -= message_definition.size();
 	}
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}  	
 	request.setMessageReadPosition(currentPosition);	
	reportSuccessAcceptanceVerification(request);	
	
	bool bFaultStartExecution = false;	
	while (iterationCount-- != 0) {
		// todo: Get the group ID first, if groups are used
		Time::DefaultCUC currentTime = TimeGetter::getCurrentTimeDefaultCUC();


		uint32_t time = request.readUint32();

		std::chrono::duration<uint32_t, Time::DefaultCUC::Ratio> duration(time);

		Time::DefaultCUC releaseTime = Time::DefaultCUC(duration);
		if ((scheduledActivities.available() == 0) || (releaseTime < (currentTime + ECSSTimeMarginForActivation))) {
			reportExecutionStartError(request, ErrorHandler::InstructionExecutionStartError);
std::cout << "Sch time " << time << ", now: " << TimeProvider::getInstance()->getCurrentTimeDefaultCUC()<< "\n";			
			bFaultStartExecution = true;
			d_message_parser->parseTCfromMessage(request);
		} else {
			MessageArray message_definition = d_message_parser->parseTCfromMessage(request);
			
			Message receivedTCPacket = Message(message_definition);
			
			ScheduledActivity newActivity;

			newActivity.request = receivedTCPacket;
			newActivity.requestReleaseTime = releaseTime;

			newActivity.requestID.sourceID = receivedTCPacket.getMessageSourceId();
			newActivity.requestID.applicationID = receivedTCPacket.getMessageApplicationId();
			newActivity.requestID.sequenceCount = receivedTCPacket.getMessagePacketSequenceCount();

			scheduledActivities.push_back(newActivity);
		}
	}
	sortActivitiesReleaseTime(scheduledActivities);
	notifyNewActivityAddition();

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);

    }

    void TimeBasedSchedulingService_impl::timeShiftAllActivities(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::TimeShiftAllScheduledActivities)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != TIME_SCH_TIME_DEF){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	reportSuccessAcceptanceVerification(request);	
	
	Time::DefaultCUC current_time = TimeGetter::getCurrentTimeDefaultCUC();

	const auto releaseTimes =
	    etl::minmax_element(scheduledActivities.begin(), scheduledActivities.end(),
	                        [](ScheduledActivity const& leftSide, ScheduledActivity const& rightSide) {
		                        return leftSide.requestReleaseTime < rightSide.requestReleaseTime;
	                        });
	// todo: Define what the time format is going to be
	int32_t relativeTime = request.readSint32();

	Time::RelativeTime relativeOffset = relativeTime;
	if ((releaseTimes.first->requestReleaseTime + std::chrono::seconds(relativeOffset)) < (current_time + ECSSTimeMarginForActivation)) {
		reportExecutionStartError(request, ErrorHandler::SubServiceExecutionStartError);
		return;
	}
	for (auto& activity: scheduledActivities) {
		activity.requestReleaseTime += std::chrono::seconds(relativeOffset);
	}
	reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);  
    }

    void TimeBasedSchedulingService_impl::timeShiftActivitiesByID(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::TimeShiftActivitiesById)) {
		return;
	}


 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < (TIME_SCH_TIME_DEF + TIME_SCH_NUM_TC)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	tcSize -= (TIME_SCH_TIME_DEF + TIME_SCH_NUM_TC);
		
	// todo: Get the sub-schedule ID if they are implemented
	int32_t relativeTime = request.readSint32();

	uint16_t iterationCount = request.readUint16();

 	if(tcSize != (iterationCount * (TIME_SCH_SRC_ID + TIME_SCH_APP_ID +TIME_SCH_SEQ_COUNTER))){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 

	reportSuccessAcceptanceVerification(request);	

	Time::DefaultCUC current_time = TimeGetter::getCurrentTimeDefaultCUC();

	auto relativeOffset = std::chrono::seconds(relativeTime);
	
	bool bFaultStartExecution = false;
	while (iterationCount-- != 0) {
		RequestID receivedRequestID;
		receivedRequestID.sourceID = request.readUint16();
		receivedRequestID.applicationID = request.readUint16();
		receivedRequestID.sequenceCount = request.readUint16();
		auto requestIDMatch = etl::find_if_not(scheduledActivities.begin(), scheduledActivities.end(),
		                                       [&receivedRequestID](ScheduledActivity const& currentElement) {
			                                       return receivedRequestID != currentElement.requestID;
		                                       });

		if (requestIDMatch != scheduledActivities.end()) {
			if ((requestIDMatch->requestReleaseTime + relativeOffset) <
			    (current_time + ECSSTimeMarginForActivation)) {
				reportExecutionStartError(request, ErrorHandler::InstructionExecutionStartError);
				bFaultStartExecution = true;
			} else {
				requestIDMatch->requestReleaseTime += relativeOffset;
			}
		} else {
			reportExecutionStartError(request, ErrorHandler::InstructionExecutionStartError);
			bFaultStartExecution = true;
		}
	}
	sortActivitiesReleaseTime(scheduledActivities);
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);		
    }

    void TimeBasedSchedulingService_impl::deleteActivitiesByID(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::DeleteActivitiesById)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < TIME_SCH_NUM_TC){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	tcSize -= TIME_SCH_NUM_TC;
		
	// todo: Get the sub-schedule ID if they are implemented
	uint16_t iterationCount = request.readUint16();

 	if(tcSize != (iterationCount * (TIME_SCH_SRC_ID + TIME_SCH_APP_ID +TIME_SCH_SEQ_COUNTER))){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 

	reportSuccessAcceptanceVerification(request);	

	bool bFaultStartExecution = false;
	
	while (iterationCount-- != 0) {
		RequestID receivedRequestID;
		receivedRequestID.sourceID = request.readUint16();
		receivedRequestID.applicationID = request.readUint16();
		receivedRequestID.sequenceCount = request.readUint16();


		const auto requestIDMatch = etl::find_if_not(scheduledActivities.begin(), scheduledActivities.end(),
		                                             [&receivedRequestID](ScheduledActivity const& currentElement) {
			                                             return receivedRequestID != currentElement.requestID;
		                                             });

		if (requestIDMatch != scheduledActivities.end()) {
			scheduledActivities.erase(requestIDMatch);
		} else {
			reportExecutionStartError(request, ErrorHandler::InstructionExecutionStartError);
			bFaultStartExecution = true;
		}
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);	
    }

    void TimeBasedSchedulingService_impl::detailReportAllActivities(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::DetailReportAllScheduledActivities)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	reportSuccessAcceptanceVerification(request);

	timeBasedScheduleDetailReport(scheduledActivities);

	reportSuccessStartExecutionVerification(request);

	reportSuccessCompletionExecutionVerification(request);	
	
    }

    void TimeBasedSchedulingService_impl::timeBasedScheduleDetailReport(etl::list<ScheduledActivity, ECSSMaxNumberOfTimeSchedActivities>& listOfActivities) {
	// todo: append sub-schedule and group ID if they are defined
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			TimeBasedSchedulingService::MessageType::TimeBasedScheduleReportById, 
			counters[TimeBasedSchedulingService::MessageType::TimeBasedScheduleReportById], 0);

	report.appendUint16(static_cast<uint16_t>(listOfActivities.size()));

	for (auto& activity: listOfActivities) {
		// todo: append sub-schedule and group ID if they are defined

		report.appendData(activity.requestReleaseTime);
		report.appendUint8Array(activity.request.getMessageData());
	}
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
                				
	counters[TimeBasedSchedulingService::MessageType::TimeBasedScheduleReportById]++;

    }

    void TimeBasedSchedulingService_impl::detailReportActivitiesByID(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::DetailReportActivitiesById)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < TIME_SCH_NUM_TC){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	tcSize -= TIME_SCH_NUM_TC;
		
	// todo: Get the sub-schedule ID if they are implemented
	uint16_t iterationCount = request.readUint16();

 	if(tcSize != (iterationCount * (TIME_SCH_SRC_ID + TIME_SCH_APP_ID +TIME_SCH_SEQ_COUNTER))){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 

	reportSuccessAcceptanceVerification(request);	
			
	etl::list<ScheduledActivity, ECSSMaxNumberOfTimeSchedActivities> matchedActivities;

	bool bFaultStartExecution = false;
	while (iterationCount-- != 0) {
		RequestID receivedRequestID;
		receivedRequestID.sourceID = request.readUint16();
		receivedRequestID.applicationID = request.readUint16();
		receivedRequestID.sequenceCount = request.readUint16();
		 
		const auto requestIDMatch = etl::find_if_not(scheduledActivities.begin(), scheduledActivities.end(),
		                                             [&receivedRequestID](ScheduledActivity const& currentElement) {
			                                             return receivedRequestID != currentElement.requestID;
		                                             });

		if (requestIDMatch != scheduledActivities.end()) {
			matchedActivities.push_back(*requestIDMatch);

		} else {
			reportExecutionStartError(request, ErrorHandler::InstructionExecutionStartError);
			bFaultStartExecution = true;
		}
	}

	sortActivitiesReleaseTime(matchedActivities);

	timeBasedScheduleDetailReport(matchedActivities);

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);		
    }

    void TimeBasedSchedulingService_impl::summaryReportAllActivities(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::SummaryReportAllScheduledActivities)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	reportSuccessAcceptanceVerification(request);

	timeBasedScheduleSummaryReport(scheduledActivities);

	reportSuccessStartExecutionVerification(request);

	reportSuccessCompletionExecutionVerification(request);	
	
    }
    
    void TimeBasedSchedulingService_impl::summaryReportActivitiesByID(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			TimeBasedSchedulingService::MessageType::ActivitiesSummaryReportById)) {
		return;
	}
	
	etl::list<ScheduledActivity, ECSSMaxNumberOfTimeSchedActivities> matchedActivities;
 	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	
 	if(tcSize < TIME_SCH_NUM_TC){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 
	tcSize -= TIME_SCH_NUM_TC;
		
	// todo: Get the sub-schedule ID if they are implemented
	uint16_t iterationCount = request.readUint16();

 	if(tcSize != (iterationCount * (TIME_SCH_SRC_ID + TIME_SCH_APP_ID +TIME_SCH_SEQ_COUNTER))){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	} 

	reportSuccessAcceptanceVerification(request);
	
	bool bFaultStartExecution = false;	
	while (iterationCount-- != 0) {
		RequestID receivedRequestID;
		receivedRequestID.sourceID = request.readUint16();
		receivedRequestID.applicationID = request.readUint16();
		receivedRequestID.sequenceCount = request.readUint16();

		auto requestIDMatch = etl::find_if_not(scheduledActivities.begin(), scheduledActivities.end(),
		                                       [&receivedRequestID](ScheduledActivity const& currentElement) {
			                                       return receivedRequestID != currentElement.requestID;
		                                       });

		if (requestIDMatch != scheduledActivities.end()) {
			matchedActivities.push_back(*requestIDMatch);
		} else {
			reportExecutionStartError(request, ErrorHandler::InstructionExecutionStartError);
			bFaultStartExecution = true;	
		}
	}
	sortActivitiesReleaseTime(matchedActivities);

	timeBasedScheduleSummaryReport(matchedActivities);

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
			
	reportSuccessCompletionExecutionVerification(request);	
    }

    void TimeBasedSchedulingService_impl::timeBasedScheduleSummaryReport(etl::list<ScheduledActivity, ECSSMaxNumberOfTimeSchedActivities>& listOfActivities) {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			TimeBasedSchedulingService::MessageType::TimeBasedScheduledSummaryReport, 
			counters[TimeBasedSchedulingService::MessageType::TimeBasedScheduledSummaryReport], 0);

	report.appendUint16(static_cast<uint16_t>(listOfActivities.size()));
	for (auto& match: listOfActivities) {
		// todo: append sub-schedule and group ID if they are defined
		report.appendData(match.requestReleaseTime);
		report.appendUint16(match.requestID.sourceID);
		report.appendUint16(match.requestID.applicationID);
		report.appendUint16(match.requestID.sequenceCount);
	}
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
                				
	counters[TimeBasedSchedulingService::MessageType::TimeBasedScheduledSummaryReport]++;

    }

  } /* namespace pus */
} /* namespace gr */
