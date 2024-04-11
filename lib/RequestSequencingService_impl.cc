/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "RequestSequencingService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>

namespace gr {
  namespace pus {

    RequestSequencingService::sptr
    RequestSequencingService::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<RequestSequencingService_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    RequestSequencingService_impl::RequestSequencingService_impl(const std::string& init_file)
      : gr::block("RequestSequencingService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        serviceType = ServiceType;
        
        for(size_t i = 0; i < RequestSequencingService::MessageType::end; i++)
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
	
        parse_json(init_file);

    	d_time_provider = TimeProvider::getInstance();
    
    	d_time_provider->addHandler(
            serviceType,
            std::bind(
                &RequestSequencingService_impl::timerTick,
                this,
                std::placeholders::_1
            )
    	);
    }
    /*
     * Our virtual destructor.
     */
    RequestSequencingService_impl::~RequestSequencingService_impl()
    {
                d_time_provider->removeHandler(serviceType);  
    }

    void RequestSequencingService_impl::timerTick(TimeProvider *p) {
	uint32_t currentTime = d_time_provider->getCurrentTimeDefaultCUC();

	if(trackedTime < currentTime){
		for (auto& sequenceStore: sequenceStores) {
			if(sequenceStore.second.sequenceStatus == SequenceStore::SequenceStatus::Execution) {
				SequenceStore::MessageList message_list = sequenceStore.second.step();
				for(auto message: message_list)
				{
      					message_port_pub(PMT_REL, pmt::cons(pmt::PMT_NIL, 
               					pmt::init_u8vector(message->getMessageData().size(), message->getMessageRawData())));
				}

			}
		}

	}
	trackedTime = currentTime;

    }

    void RequestSequencingService_impl::parse_json(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;
   	    for (auto& elem : json["sequenceStores"]){
   	    	std::string seqName = elem["name"];
   	    	std::string seqFile = elem["seqFile"];
   	    	parse_json_request(seqName, seqFile, NULL, false);
   	    }
        } else {
            GR_LOG_WARN(d_logger, "No request sequencing definitions init file found");
        }
        file.close();
    }  

    bool RequestSequencingService_impl::parse_json_request(const std::string& sequenceStoreId, const std::string& filename, Message* request, bool activated)
    {
        std::ifstream file(filename);
        nlohmann::json json;
        if (file) {
            	file >> json;
  
		auto sequenceStore = sequenceStores.find(sequenceStoreId);
		if (sequenceStore != sequenceStores.end()) {
			if (request){
				reportExecutionStartError(*request, ErrorHandler::ExecutionStartErrorType::AlreadyExistingSequenceStore);
			}
			return false;
		}
   	   	
   	   	SequenceStore newSequence;
   	   	for (auto& elem : json["sequence"]){
           	     size_t pos = 0;
           	     std::string data = elem["data"];
           	     std::string separator = ",";
           	     std::string token;

           	     MessageArray action_definition;
               
           	     while((pos = data.find(separator)) != std::string::npos){
                	token = data.substr(0, pos);
            	    	data.erase(0, pos + separator.length());
                	action_definition.push_back(std::stoul(token, nullptr, 16));	
                	
           	     }
           	     token = data.substr(0, pos);
           	     data.erase(0, pos + separator.length());
           	     action_definition.push_back(std::stoul(token, nullptr, 16));	
           	     Message receivedTCPacket = Message(action_definition);
           	     
           	     uint32_t delay = elem["delay"];
           	     std::chrono::duration<uint32_t, Time::DefaultCUC::Ratio> duration(delay);

           	     Time::DefaultCUC delayTime = Time::DefaultCUC(duration);


           	     SequenceStore::SequenceActivity newActivity;

           	     newActivity.request = receivedTCPacket;
           	     newActivity.requestDelayTime = delayTime;

           	     newSequence.sequenceActivities.push_back(newActivity);

   	        }
   	        if (newSequence.sequenceActivities.size() >= ECSSMaxNumberOfSequenceActivities){
			if (request){
				reportExecutionStartError(*request, ErrorHandler::ExecutionStartErrorType::NumberOfSequenceActivitiesOverflow);
			}
			return false;	
		}	  
 
		sequenceStores.insert({sequenceStoreId, newSequence});   	    
           	if(activated){
			auto sequenceStore = sequenceStores.find(sequenceStoreId);
			if (sequenceStore != sequenceStores.end()) {
				sequenceStore->second.activated();
			}
           	 }	     
        } else {
#ifdef _PUS_DEBUG
            GR_LOG_WARN(d_logger, "No request sequence file found");
#endif
	    if (request){
		   reportExecutionStartError(*request, ErrorHandler::ExecutionStartErrorType::FileNotFound);	    
	    }
	    return false;
        }
        file.close();
        return true;
    }  
        
    void RequestSequencingService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case DirectLoadRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DirectLoadRequestSequence");
#endif
                           directLoadRequestSequence(message);
                           break;
                        case LoadRequestSequenceByRef:   
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "LoadRequestSequenceByRef");
#endif
                           loadRequestSequenceByRef(message);
                           break;                                             
                        case UnloadRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "UnloadRequestSequence");
#endif
                           unloadRequestSequence(message);
                           break;
                        case ActivateRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ActivateRequestSequence");
#endif
                           activateRequestSequence(message);
                           break;
                        case AbortRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AbortRequestSequence");
#endif
                           abortRequestSequence(message);				
                           break;
                        case ReportExecutionStatusOfEachRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportExecutionStatusOfEachRequestSequence");
#endif
                           reportExecutionStatusOfEachRequestSequence(message);
                           break;
                        case LoadByRefAndActivateRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "LoadByRefAndActivateRequestSequence");
#endif
                           loadByRefAndActivateRequestSequence(message);				
                           break;
                        case ChecksumRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ChecksumRequestSequence");
#endif
                           checksumRequestSequence(message);
                           break;
                        case ReportContentRequestSequence:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportContentRequestSequence");
#endif
                           reportContentRequestSequence(message);
                           break;
                  
                        case AbortAllRequestSequencesAndReport:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AbortAllRequestSequencesAndReport");
#endif
                           abortAllRequestSequencesAndReport(message);
                           break;                           

                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Request Sequencing Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Request Sequencing Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);

               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

     bool RequestSequencingService_impl::maxActivatedSequences()
     {
	uint16_t sequencesInExecution = 0;
	for (auto& sequenceStore: sequenceStores) {
		if(sequenceStore.second.sequenceStatus == SequenceStore::SequenceStatus::Execution) {
			sequencesInExecution++;
		}
	}  
	if (sequencesInExecution >= ECSSMaxNumberOfUnderExecutionSequences)
		return true;
	return false;
     
     }
     
     std::string RequestSequencingService_impl::readSequenceStoreId(Message& message) {
	std::string sequenceStoreId;
	message.readString(sequenceStoreId, ECSSPacketStoreIdSize);

	return sequenceStoreId;
     }

     void RequestSequencingService_impl::directLoadRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::DirectLoadRequestSequence)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (ECSSPacketStoreIdSize + REQ_SEQ_NUM_RQ)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= (ECSSPacketStoreIdSize + REQ_SEQ_NUM_RQ);

	auto sequenceStoreId = readSequenceStoreId(request);
	 	
 	uint16_t numOfRequests = request.readUint16();

 	uint16_t currentPosition = request.getMessageReadPosition();

 	for (uint16_t i = 0; i < numOfRequests; i++) {	

		MessageArray message_definition = d_message_parser->parseTCfromMessage(request);
		if(message_definition.size() == 0){
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return;
		} 
		tcSize -= message_definition.size();
		
 		if(tcSize < d_time_provider->getTimeSize()){
			reportAcceptanceError(request, ErrorHandler::InvalidLength);	
			return;
		} 
		tcSize -= d_time_provider->getTimeSize();
		
		request.setMessageReadPosition(request.getMessageReadPosition() + d_time_provider->getTimeSize());

 	}
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);	
		return;
	}  	
	
 	request.setMessageReadPosition(currentPosition);	
 	
	reportSuccessAcceptanceVerification(request);	

	auto sequenceStore = sequenceStores.find(sequenceStoreId);
	if (sequenceStore != sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::AlreadyExistingSequenceStore);
		return;
	}
	
	if (sequenceStores.size() + 1 >= ECSSMaxSequenceStores){
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxNumberOfSequenceStoresReached);
		return;	
	}
	
	if (numOfRequests >= ECSSMaxNumberOfSequenceActivities){
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NumberOfSequenceActivitiesOverflow);
		return;	
	}	
	
	SequenceStore newSequence;	
	while (numOfRequests-- != 0) {
		MessageArray message_definition = d_message_parser->parseTCfromMessage(request);
			
		Message receivedTCPacket = Message(message_definition);
		
		uint32_t time = request.readUint32();

		std::chrono::duration<uint32_t, Time::DefaultCUC::Ratio> duration(time);

		Time::DefaultCUC releaseTime = Time::DefaultCUC(duration);


		SequenceStore::SequenceActivity newActivity;

		newActivity.request = receivedTCPacket;
		newActivity.requestDelayTime = releaseTime;

		newSequence.sequenceActivities.push_back(newActivity);
	}	
	
	sequenceStores.insert({sequenceStoreId, newSequence});

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);

     }			


     void RequestSequencingService_impl::loadRequestSequenceByRef(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::LoadRequestSequenceByRef)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (ECSSPacketStoreIdSize + 2)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= ECSSPacketStoreIdSize;

	auto sequenceStoreId = readSequenceStoreId(request);

	reportSuccessAcceptanceVerification(request);	

	auto sequenceStore = sequenceStores.find(sequenceStoreId);
	if (sequenceStore != sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::AlreadyExistingSequenceStore);
		return;
	}
	
	if (sequenceStores.size() + 1 >= ECSSMaxSequenceStores){
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxNumberOfSequenceStoresReached);
		return;	
	}

	std::string path = "";
	request.readString(path);
	
	std::string fileName = "";
	request.readString(fileName);
	
	if(!parse_json_request(sequenceStoreId, path+fileName, &request, false))
		return;
	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);

     }			
	

     void RequestSequencingService_impl::unloadRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::UnloadRequestSequence)) {
		return;
	}
	
	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);	

	auto sequenceStoreId = readSequenceStoreId(request);
	auto sequenceStore = sequenceStores.find(sequenceStoreId);
	if (sequenceStore == sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingSequenceStore);
		return;
	}
	if (sequenceStore->second.sequenceStatus == SequenceStore::SequenceStatus::Execution) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::UnderExecutionSequenceStore);
		return;
	}

	sequenceStores.erase(sequenceStoreId);
	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }			
	

     void RequestSequencingService_impl::activateRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::ActivateRequestSequence)) {
		return;
	}
	
	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);	


	auto sequenceStoreId = readSequenceStoreId(request);
	auto sequenceStore = sequenceStores.find(sequenceStoreId);
	if (sequenceStore == sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingSequenceStore);
		return;
	}

	if (maxActivatedSequences()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxActivatedSequencesReach);
		return;
	}
	sequenceStore->second.activated();

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }			
	

     void RequestSequencingService_impl::abortRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::AbortRequestSequence)) {
		return;
	}
	
	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);
		
	auto sequenceStoreId = readSequenceStoreId(request);
	auto sequenceStore = sequenceStores.find(sequenceStoreId);
	if (sequenceStore == sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingSequenceStore);
		return;
	}

	if(sequenceStore->second.sequenceStatus == SequenceStore::SequenceStatus::Inactive){
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::AlreadyInactiveSequence);
		return;
	}
	sequenceStore->second.abort();

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }			
	

     void RequestSequencingService_impl::reportExecutionStatusOfEachRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::ReportExecutionStatusOfEachRequestSequence)) {
		return;
	}

	
	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);	

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestSequencingService::MessageType::ExecutionStatusOfEachRequestSequenceReport, 
			counters[RequestSequencingService::MessageType::ExecutionStatusOfEachRequestSequenceReport], 0);

	report.appendUint16(sequenceStores.size());
	
	for (auto& sequenceStore: sequenceStores) {
		auto sequenceStoreId = sequenceStore.first;
		report.appendString(sequenceStoreId, ECSSPacketStoreIdSize);
		report.appendUint8(sequenceStore.second.sequenceStatus);
	}	
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[RequestSequencingService::MessageType::ExecutionStatusOfEachRequestSequenceReport]++;

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }				


     void RequestSequencingService_impl::loadByRefAndActivateRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::LoadByRefAndActivateRequestSequence)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (ECSSPacketStoreIdSize + 2)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= ECSSPacketStoreIdSize;

	auto sequenceStoreId = readSequenceStoreId(request);

	reportSuccessAcceptanceVerification(request);	

	auto sequenceStore = sequenceStores.find(sequenceStoreId);

	if (sequenceStore != sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::AlreadyExistingSequenceStore);
		return;
	}
	
	if (sequenceStores.size() + 1 >= ECSSMaxSequenceStores){
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxNumberOfSequenceStoresReached);
		return;	
	}

	std::string path;
	request.readString(path);
	
	std::string fileName;
	request.readString(fileName);
	
	if(!parse_json_request(sequenceStoreId, path+fileName, &request, true))
		return;
	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);

     }			
	

     void RequestSequencingService_impl::checksumRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::ChecksumRequestSequence)) {
		return;
	}
	
	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);	

	auto sequenceStoreId = readSequenceStoreId(request);
	auto sequenceStore = sequenceStores.find(sequenceStoreId);
	if (sequenceStore == sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingSequenceStore);
		return;
	}

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestSequencingService::MessageType::ChecksumRequestSequenceReport, 
			counters[RequestSequencingService::MessageType::ChecksumRequestSequenceReport], 0);

	report.appendString(sequenceStoreId, ECSSPacketStoreIdSize);
	report.appendUint16(sequenceStore->second.calculateSequenceCRC());
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[RequestSequencingService::MessageType::ChecksumRequestSequenceReport]++;	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
 
     }			


     void RequestSequencingService_impl::reportContentRequestSequence(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::ReportContentRequestSequence)) {
		return;
	}
	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);	

	auto sequenceStoreId = readSequenceStoreId(request);

	auto sequenceStore = sequenceStores.find(sequenceStoreId);
	if (sequenceStore == sequenceStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingSequenceStore);
		return;
	}

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestSequencingService::MessageType::ContentRequestSequenceReport, 
			counters[RequestSequencingService::MessageType::ContentRequestSequenceReport], 0);

	report.appendString(sequenceStoreId, ECSSPacketStoreIdSize);
	
	report.appendUint16(sequenceStore->second.sequenceActivities.size());
	
	for (auto& activity: sequenceStore->second.sequenceActivities) {
		report.appendUint8Array(activity.request.getMessageData());
		report.appendData(activity.requestDelayTime);
	}	
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[RequestSequencingService::MessageType::ContentRequestSequenceReport]++;
	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);

     }				


     void RequestSequencingService_impl::abortAllRequestSequencesAndReport(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			RequestSequencingService::MessageType::AbortAllRequestSequencesAndReport)) {
		return;
	}
 
	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 
	
	reportSuccessAcceptanceVerification(request);	

        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			RequestSequencingService::MessageType::AbortedRequestSequenceReport, 
			counters[RequestSequencingService::MessageType::AbortedRequestSequenceReport], 0);

	uint16_t sequencesInExecution = 0;
	for (auto& sequenceStore: sequenceStores) {
		if(sequenceStore.second.sequenceStatus == SequenceStore::SequenceStatus::Execution) {
			sequencesInExecution++;
		}
	}

	report.appendUint16( sequencesInExecution);
	for (auto& sequenceStore: sequenceStores) {
		if(sequenceStore.second.sequenceStatus == SequenceStore::SequenceStatus::Execution) {
			auto sequenceStoreId = sequenceStore.first;
			report.appendString(sequenceStoreId, ECSSPacketStoreIdSize);
			sequenceStore.second.abort();
		}
	}
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[RequestSequencingService::MessageType::AbortedRequestSequenceReport]++;
        
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }			

  } /* namespace pus */
} /* namespace gr */
