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
#include "StorageAndRetrievalService_impl.h"
#include <thread>
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {
  
    using input_type = int8_t;
    using output_type = int8_t;
    
    StorageAndRetrievalService::sptr
    StorageAndRetrievalService::make(const std::string& init_file, std::vector<uint16_t> vc_list, double samples_per_sec)
    {
      return gnuradio::make_block_sptr<StorageAndRetrievalService_impl>(
        init_file, vc_list, samples_per_sec);
    }


    /*
     * The private constructor
     */
    StorageAndRetrievalService_impl::StorageAndRetrievalService_impl(const std::string& init_file, std::vector<uint16_t> vc_list, 
    			double samples_per_sec)
      : gr::block("StorageAndRetrievalService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        serviceType = ServiceType;

        d_vc_list = vc_list;
        set_sample_rate(samples_per_sec);
            
        for(size_t i = 0; i < StorageAndRetrievalService_impl::MessageType::end; i++)
        	counters[i] = 0;
        	
        this->message_port_register_in(PMT_IN);
        this->set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        this->message_port_register_in(PMT_IN_MSG);
        this->set_msg_handler(PMT_IN_MSG,
                    [this](pmt::pmt_t msg) { this->handle_in_msg(msg); });
        this->message_port_register_out(PMT_OUT);
        this->message_port_register_out(PMT_VER);
        
        for(uint16_t i = 0; i < d_vc_list.size(); i++){
                d_outputvc.insert({d_vc_list[i], i});
        }
        
        if(vc_list.size() > 1){
            for(uint16_t i = 0; i < vc_list.size(); i++){
                message_port_register_out(pmt::intern("vc" + std::to_string(i)));
                d_outputvc.insert({vc_list[i], i});
            }
        }else{
            d_outputvc.clear();
            message_port_register_out(PMT_VC);
        }

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
             
        parse_json(init_file);

      	d_time_provider = TimeProvider::getInstance();
      	        
    	d_status = true;
    	d_suspend = false;        
    }

    /*
     * Our virtual destructor.
     */
    StorageAndRetrievalService_impl::~StorageAndRetrievalService_impl()
    {
    }
    
    void StorageAndRetrievalService_impl::set_sample_rate(double rate)
    {
        // changing the sample rate performs a reset of state params
        d_sampleRate = rate;
        d_byteDurationUs = 8e6 / rate;
    }

    bool StorageAndRetrievalService_impl::start()
    {
   
        d_finished = false;
        d_thread = gr::thread::thread([this] { run(); });

    	return block::start();
    }

    bool StorageAndRetrievalService_impl::stop()
    {
        // Shut down the thread
        d_finished = true;
        d_thread.interrupt();
        d_thread.join();

   	return block::stop();
    }        

    void StorageAndRetrievalService_impl::run()
    {
        while (!d_finished) {
            double accumulatedTimeUs = 0;
            bool nothing;
            do{
            	nothing = true;
            	for (auto& packetStore: packetStores) {
			if(packetStore.second.openRetrievalStatus == PacketStore::InProgress){
				if(not packetStore.second.storedTelemetryPackets.empty()){
					int16_t indexPacket = -1;
					for (auto& packet: packetStore.second.storedTelemetryPackets) {
						indexPacket++;
						if (packet.first < packetStore.second.currentRetrievalStartTimeTag)
							continue;
						
						uint16_t virtualChannel = (uint16_t)packetStore.second.virtualChannel;
						auto nOut = d_outputvc.find(virtualChannel);
						
						if(nOut == d_outputvc.end())
							break;
						
						packetStore.second.currentRetrievalStartTimeTag =
											packet.first;						
						
						for (int16_t i = indexPacket; i < (int16_t)packetStore.second.storedTelemetryPackets.size();i++){
  							if (packetStore.second.storedTelemetryPackets[i].first == packetStore.second.currentRetrievalStartTimeTag){
								Message message = packetStore.second.storedTelemetryPackets[i].second;
       							message_port_pub(pmt::intern("vc" + std::to_string(nOut->second)),
       								pmt::cons(pmt::PMT_NIL, 
                							pmt::init_u8vector(message.getMessageSize(), message.getMessageRawData())));
#ifdef _PUS_DEBUG	
								printf(" Retrieval: TX on VC[%u] Message TM[%u, %u]\n",
									nOut->second,
									message.getMessageServiceType(), message.getMessageType());	
#endif					
								accumulatedTimeUs += d_byteDurationUs	* message.getMessageSize();
								nothing = false;
							
 							}else{
 								
   								break;
   							}
						}
			
						packetStore.second.currentRetrievalStartTimeTag++;
						break;
					}
				}
			}
			if(packetStore.second.byTimeRangeRetrievalStatus){
				if(not packetStore.second.storedTelemetryPackets.empty()){	
					for (auto& packet: packetStore.second.storedTelemetryPackets) {
						if (packet.first < packetStore.second.retrievalStartTime)
							continue;
						if (packet.first > packetStore.second.retrievalEndTime) {
							packetStore.second.byTimeRangeRetrievalStatus = false;
							break;
						}
						uint16_t virtualChannel = (uint16_t)packetStore.second.virtualChannel;
						auto nOut = d_outputvc.find(virtualChannel);
						if(nOut != d_outputvc.end()){		
							Message message = packet.second;
       						message_port_pub(pmt::intern("vc" + std::to_string(nOut->second)),
       							pmt::cons(pmt::PMT_NIL, 
                						pmt::init_u8vector(message.getMessageSize(), message.getMessageRawData())));
#ifdef _PUS_DEBUG	
							printf(" Time Range: TX on VC[%u] Message TM[%u, %u]\n",
								nOut->second,
								message.getMessageServiceType(), message.getMessageType());	
#endif
							accumulatedTimeUs += d_byteDurationUs	* message.getMessageSize();
							nothing = false;
						}
					}
				}	
			}
           	 }
           	 if(accumulatedTimeUs > SDRStorageAndRetrievalTimeSlotUs){
           	     break;
            	 }
	    }while(not nothing and not d_finished);
	    
	    if(accumulatedTimeUs < SDRStorageAndRetrievalTimeSlotUs){
	    	accumulatedTimeUs = SDRStorageAndRetrievalTimeSlotUs;
	    }

	    boost::this_thread::sleep(
			boost::posix_time::microseconds(static_cast<long>(accumulatedTimeUs)));
	    
        }
    }

    void StorageAndRetrievalService_impl::parse_json(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;

        if (file) {
            file >> json;
            //monitoringEnabled = json["enabled"];
            //monitoringInterval = json["monInterval"];  

            uint8_t numParams = json["numAppID"];
            for(uint8_t i = 0; i < numParams; i++){
              	uint16_t appID = json["appIDMon"][i];
           	appID_monitored_list.push_back(appID);
            }     

             
            for (auto& elem : json["store"]){
		PacketStore newPacketStore;
		std::string idToCreate = elem["name"];
		
		auto packetStore = packetStores.find(idToCreate);
		if (packetStore != packetStores.end()) {
			continue;
		}		
		newPacketStore.sizeInBytes = elem["packetStoreSize"];
		newPacketStore.packetStoreType = elem["packetStoreType"];
		newPacketStore.storageStatus = elem["storageStatus"];
		newPacketStore.byTimeRangeRetrievalStatus = false;
		newPacketStore.openRetrievalStatus = PacketStore::Suspended;
		newPacketStore.virtualChannel = elem["virtualChannel"];
		for (auto& elemDef : elem["filter"]){
			uint16_t apid = elemDef["apid"];
			for (auto& elemTypeDef : elemDef["type"]){
				uint8_t serviceType = elemTypeDef["serviceType"];
				auto key = std::make_pair(apid, serviceType);
				
                		uint16_t numSubTypes = elemTypeDef["numSubType"];
                		std::vector<uint8_t> subTypes;	
                		PacketStore::ReportTypeDefinitions reportTypeDefinitions;
                					
               		for(uint16_t i = 0; i < numSubTypes; i++){
                			 reportTypeDefinitions.push_back(elemTypeDef["serviceSubType"][i]);
                		}
                		newPacketStore.definitions[key] = reportTypeDefinitions;
            		
 			}
			if (std::find(appID_monitored_list.begin(), 
					appID_monitored_list.end(), apid) ==
	   			 appID_monitored_list.end()) {
				appID_monitored_list.push_back(apid);

			}
		}		

		packetStores.insert({idToCreate, newPacketStore});
		if (packetStores.size() >= ECSSMaxPacketStores) {

			;
			//return;
		}

            }
        } else {
            GR_LOG_WARN(d_logger, "No Storage&Retrieval stores definitions init file found");
            appID_monitored_list.push_back(ApplicationId);
        }
        file.close();
    } 
    
    void StorageAndRetrievalService_impl::handle_in_msg(pmt::pmt_t pdu)
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

                for (auto& stores: packetStores) {
			if( !stores.second.storageStatus)
				continue;
			for (auto& appID: stores.second.getApplicationsInStore()) {
				if(message.getMessageApplicationId() == appID){
					if (reportExistsInStoreConfiguration(stores.first, message, 
						appID, message.getMessageServiceType(), message.getMessageType()))
		 			{
#ifdef _PUS_DEBUG
                				printf("Storing TM[%u,%u]\n", message.getMessageServiceType(), message.getMessageType());
#endif
                				addTelemetryToPacketStore(stores.first,
                                               	  TimeProvider::getInstance()->getCurrentTimeDefaultCUC(),
                                              	   message);
                        		}
				}                                           
                	}
                }
        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    void StorageAndRetrievalService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case EnableStorageInPacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "EnableStorageInPacketStores");
#endif
			    enableStorageFunction(message);
                           break;
                        case DisableStorageInPacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DisableStorageInPacketStores");
#endif
			    disableStorageFunction(message);
                           break;                             
                           
                        case AddPacketsDefinitionsToPacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AddPacketsDefinitionsToPacketStores");
#endif
			    addPacketsDefinitionsToPacketStores(message);
                           break;                               
                        case RemovePacketsDefinitionsFromPacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "RemovePacketsDefinitionsFromPacketStores");
#endif
			    removePacketsDefinitionsFromPacketStores(message);
                           break;                                          
                        case ReportContentAPIDStoreConfig:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportContentAPIDStoreConfig");
#endif
			    reportContentAPIDStoreConfig(message);
                           break;                               
                        case StartByTimeRangeRetrieval:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "StartByTimeRangeRetrieval");
#endif
			    startByTimeRangeRetrieval(message);
                           break;
                        case DeletePacketStoreContent:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeletePacketStoreContent");
#endif
			    deletePacketStoreContent(message);
                           break;
                        case ReportContentSummaryOfPacketStores:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "ReportContentSummaryOfPacketStores");
#endif
			    packetStoreContentSummaryReport(message);
                           break;

                        case ChangeOpenRetrievalStartingTime:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ChangeOpenRetrievalStartingTime");
#endif
			    changeOpenRetrievalStartTimeTag(message);
                           break;
                        case ResumeOpenRetrievalOfPacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ResumeOpenRetrievalOfPacketStores");
#endif
			    resumeOpenRetrievalOfPacketStores(message);
                           break;
                        case SuspendOpenRetrievalOfPacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "SuspendOpenRetrievalOfPacketStores");
#endif
                           suspendOpenRetrievalOfPacketStores(message);
                           break;
                        case AbortByTimeRangeRetrieval:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AbortByTimeRangeRetrieval");
#endif
                           abortByTimeRangeRetrieval(message);
                           break;
                        case ReportStatusOfPacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportStatusOfPacketStores");
#endif
			    packetStoresStatusReport(message);
                           break;
                         case CreatePacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "CreatePacketStores");
#endif
                           createPacketStores(message);
                           break;
                        case DeletePacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeletePacketStores");
#endif
                           deletePacketStores(message);
                           break;
                        case ReportConfigurationOfPacketStores:  
#ifdef _PUS_DEBUG  
                           GR_LOG_WARN(d_logger, "ReportConfigurationOfPacketStores");
#endif
                           packetStoreConfigurationReport(message);
                           break;
                        case CopyPacketsInTimeWindow:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "CopyPacketsInTimeWindow");
#endif
                           copyPacketsInTimeWindow(message);
                           break;
                        case ResizePacketStores:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ResizePacketStores");
#endif
                           resizePacketStores(message);
                           break;
                        case ChangeTypeToCircular:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ChangeTypeToCircular");
#endif
                           changeTypeToCircular(message);
                           break;
                        case ChangeTypeToBounded:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "ChangeTypeToBounded");
#endif
                           changeTypeToBounded(message);
                           break;
                        case ChangeVirtualChannel:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ChangeVirtualChannel");
#endif
                           changeVirtualChannel(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Storage and Retrieval Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);
	   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Storage and Retrieval Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

     std::string StorageAndRetrievalService_impl::readPacketStoreId(Message& message) {
	std::string packetStoreId;
	message.readString(packetStoreId, ECSSPacketStoreIdSize);

	return packetStoreId;
     }

     void StorageAndRetrievalService_impl::deleteContentUntil(const std::string& packetStoreId,
                                                    uint32_t timeLimit) {
	auto& telemetryPackets = packetStores[packetStoreId].storedTelemetryPackets;
	while (not telemetryPackets.empty() and telemetryPackets.front().first <= timeLimit) {
		telemetryPackets.pop_front();
	}
     }

     bool StorageAndRetrievalService_impl::copyFromTagToTag(Message& request) {
	uint32_t startTime = request.readUint32();
	uint32_t endTime = request.readUint32();
	
	auto fromPacketStoreId = readPacketStoreId(request);
	auto toPacketStoreId = readPacketStoreId(request);

	if (failedFromTagToTag(fromPacketStoreId, toPacketStoreId, startTime, endTime, request)) {
		return true;
	}

	for (auto& packet: packetStores[fromPacketStoreId].storedTelemetryPackets) {
		if (packet.first < startTime) {
			continue;
		}
		if (packet.first > endTime) {
			break;
		}
		packetStores[toPacketStoreId].storedTelemetryPackets.push_back(packet);
	}
	return false;
     }

     bool StorageAndRetrievalService_impl::copyAfterTimeTag(Message& request) {
	uint32_t startTime = request.readUint32();
	
	auto fromPacketStoreId = readPacketStoreId(request);
	auto toPacketStoreId = readPacketStoreId(request);

	if (failedAfterTimeTag(fromPacketStoreId, toPacketStoreId, startTime, request)) {
		return true;
	}

	for (auto& packet: packetStores[fromPacketStoreId].storedTelemetryPackets) {
		if (packet.first < startTime) {
			continue;
		}
		packetStores[toPacketStoreId].storedTelemetryPackets.push_back(packet);
	}
	return false;
     }

     bool StorageAndRetrievalService_impl::copyBeforeTimeTag(Message& request) {
	uint32_t endTime = request.readUint32();
	
	auto fromPacketStoreId = readPacketStoreId(request);
	auto toPacketStoreId = readPacketStoreId(request);

	if (failedBeforeTimeTag(fromPacketStoreId, toPacketStoreId, endTime, request)) {
		return true;
	}

	for (auto& packet: packetStores[fromPacketStoreId].storedTelemetryPackets) {
		if (packet.first > endTime) {
			break;
		}
		packetStores[toPacketStoreId].storedTelemetryPackets.push_back(packet);
	}
	return false;
     }

     bool StorageAndRetrievalService_impl::checkPacketStores(const std::string& fromPacketStoreId,
                                                   const std::string& toPacketStoreId,
                                                   Message& request) {
	if (packetStores.find(fromPacketStoreId) == packetStores.end() or
	    packetStores.find(toPacketStoreId) == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		return false;
	}
	return true;
     }

     bool StorageAndRetrievalService_impl::checkTimeWindow(uint32_t startTime, uint32_t endTime, Message& request) {
	if (startTime >= endTime) {
		//reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::InvalidTimeWindow);
		return true;
	}
	return false;
     }

     bool StorageAndRetrievalService_impl::checkDestinationPacketStore(const std::string& toPacketStoreId,
                                                             Message& request) {
	if (not packetStores[toPacketStoreId].storedTelemetryPackets.empty()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::DestinationPacketStoreNotEmtpy);
		return true;
	}
	return false;
     }

     bool StorageAndRetrievalService_impl::noTimestampInTimeWindow(const std::string& fromPacketStoreId,
                                                         uint32_t startTime, uint32_t endTime, Message& request) {
	if (endTime < packetStores[fromPacketStoreId].storedTelemetryPackets.front().first ||
	    startTime > packetStores[fromPacketStoreId].storedTelemetryPackets.back().first) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::CopyOfPacketsFailed);
		return true;
	}
	return false;
     }

     bool StorageAndRetrievalService_impl::noTimestampInTimeWindow(const std::string& fromPacketStoreId,
                                                         uint32_t timeTag, Message& request, bool isAfterTimeTag) {
	if (isAfterTimeTag) {
		if (timeTag > packetStores[fromPacketStoreId].storedTelemetryPackets.back().first) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::CopyOfPacketsFailed);
			return true;
		}
		return false;
	} else if (timeTag < packetStores[fromPacketStoreId].storedTelemetryPackets.front().first) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::CopyOfPacketsFailed);
		return true;
	}
	return false;
     }

     bool StorageAndRetrievalService_impl::failedFromTagToTag(const std::string& fromPacketStoreId,
                                                    const std::string& toPacketStoreId,
                                                    uint32_t startTime, uint32_t endTime, Message& request) {
	return (not checkPacketStores(fromPacketStoreId, toPacketStoreId, request) or
	        checkTimeWindow(startTime, endTime, request) or checkDestinationPacketStore(toPacketStoreId, request) or
	        noTimestampInTimeWindow(fromPacketStoreId, startTime, endTime, request));
     }

     bool StorageAndRetrievalService_impl::failedAfterTimeTag(const std::string& fromPacketStoreId,
                                                    const std::string& toPacketStoreId,
                                                    uint32_t startTime, Message& request) {
	return (not checkPacketStores(fromPacketStoreId, toPacketStoreId, request) or
	        checkDestinationPacketStore(toPacketStoreId, request) or
	        noTimestampInTimeWindow(fromPacketStoreId, startTime, request, true));
     }

     bool StorageAndRetrievalService_impl::failedBeforeTimeTag(const std::string& fromPacketStoreId,
                                                     const std::string& toPacketStoreId,
                                                     uint32_t endTime, Message& request) {
	return (not checkPacketStores(fromPacketStoreId, toPacketStoreId, request) or
	        checkDestinationPacketStore(toPacketStoreId, request) or
	        noTimestampInTimeWindow(fromPacketStoreId, endTime, request, false));
     }
/*******************************************************************************************************************************
*
*
*******************************************************************************************************************************/
     void StorageAndRetrievalService_impl::createContentSummary(Message& report,
                                                      const std::string& packetStoreId) {
	uint32_t oldestStoredPacketTime = 0;
	uint32_t newestStoredPacketTime = 0;
		
	if (packetStores[packetStoreId].storedTelemetryPackets.size() > 0 ){
		oldestStoredPacketTime = packetStores[packetStoreId].storedTelemetryPackets.front().first;
		newestStoredPacketTime = packetStores[packetStoreId].storedTelemetryPackets.back().first;
	}
	report.appendUint32(oldestStoredPacketTime);

	report.appendUint32(newestStoredPacketTime);

	report.appendUint32(packetStores[packetStoreId].openRetrievalStartTimeTag);

	auto filledPercentage1 = static_cast<uint16_t>(static_cast<float>(packetStores[packetStoreId].storedTelemetryPackets.size()) * 100 /
                                               ECSSMaxPacketStoreSize);
	report.appendUint16(filledPercentage1);


	uint16_t numOfPacketsToBeTransferred = 0;
	numOfPacketsToBeTransferred = std::count_if(
	    std::begin(packetStores[packetStoreId].storedTelemetryPackets),
	    std::end(packetStores[packetStoreId].storedTelemetryPackets), [this, &packetStoreId](auto packet) {
		    return packet.first >= packetStores[packetStoreId].openRetrievalStartTimeTag;
	    });
	
	auto filledPercentage2 = static_cast<uint16_t>(static_cast<float>(numOfPacketsToBeTransferred) * 100 / ECSSMaxPacketStoreSize);
	report.appendUint16(filledPercentage2);
     }

     bool StorageAndRetrievalService_impl::failedStartOfByTimeRangeRetrieval(
   					 const std::string& packetStoreId, Message& request) {
	bool errorFlag = false;

	if (packetStores.find(packetStoreId) == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		errorFlag = true;
	} else if (packetStores[packetStoreId].openRetrievalStatus == PacketStore::InProgress) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithOpenRetrievalInProgress);
		errorFlag = true;
	} else if (packetStores[packetStoreId].byTimeRangeRetrievalStatus) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ByTimeRangeRetrievalAlreadyEnabled);
		errorFlag = true;
	}
	if (errorFlag) {
		uint16_t numberOfBytesToSkip = d_time_provider->getTimeSize() * 2;
		request.setMessageReadPosition(request.getMessageReadPosition()+numberOfBytesToSkip);
		return true;
	}
	return false;
     }

     void StorageAndRetrievalService_impl::addPacketStore(const std::string& packetStoreId,
                                                const PacketStore& packetStore) {
	packetStores.insert({packetStoreId, packetStore});
     }

     void StorageAndRetrievalService_impl::addTelemetryToPacketStore(const std::string& packetStoreId,
                                                           uint32_t timestamp,
                                                           Message& tmPacket) {
	packetStores[packetStoreId].storedTelemetryPackets.push_back({timestamp, tmPacket});
     }

     void StorageAndRetrievalService_impl::resetPacketStores() {
	packetStores.clear();
     }

     uint16_t StorageAndRetrievalService_impl::currentNumberOfPacketStores() {
	return packetStores.size();
     }

     PacketStore& StorageAndRetrievalService_impl::getPacketStore(const std::string& packetStoreId) {
	auto packetStore = packetStores.find(packetStoreId);
	d_error_handler->assertInternal(packetStore != packetStores.end(), ErrorHandler::InternalErrorType::ElementNotInArray);
	return packetStore->second;
     }

     bool StorageAndRetrievalService_impl::packetStoreExists(const std::string& packetStoreId) {
	return packetStores.find(packetStoreId) != packetStores.end();
     }
     
    bool StorageAndRetrievalService_impl::reportExistsInStoreConfiguration(const std::string& packetStoreId,
    							Message& message, uint16_t applicationID, 
    							uint8_t serviceType, uint8_t messageType) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return false;
	}
	auto key = std::make_pair(applicationID, serviceType);
	auto& messages = packetStore->second.definitions[key];

	if(std::find(messages.begin(), messages.end(), messageType) != messages.end())
		return true;	
	
	return false;
    }

    bool StorageAndRetrievalService_impl::reportExistsInAppProcessConfiguration(uint16_t applicationID, 
    							uint8_t serviceType, uint8_t messageType) {

	for (const auto& allMessageType: AllMessageTypes::MessagesOfService.at(serviceType)) {
		if(allMessageType == messageType )
			return true;
	}
	return false;
    }    

	
	
    uint8_t StorageAndRetrievalService_impl::countReportsOfService(const std::string& packetStoreId,
    							uint16_t applicationID, uint8_t serviceType) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return 0;
	}
	auto appServicePair = std::make_pair(applicationID, serviceType);
	return packetStore->second.definitions[appServicePair].size();
    }

    bool StorageAndRetrievalService_impl::maxReportTypesReached(Message& request, const std::string& packetStoreId,
    								uint16_t applicationID,
                                                             uint8_t serviceType) {
	if (countReportsOfService(packetStoreId, applicationID, serviceType) >= AllMessageTypes::MessagesOfService.at(serviceType).size()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxReportTypesReached);
		return true;
	}
	return false;
    }
    
    bool StorageAndRetrievalService_impl::checkMessage(Message& request, const std::string& packetStoreId,
    				 uint16_t applicationID, uint8_t serviceType, uint8_t messageType) {

	if(maxReportTypesReached(request, packetStoreId, applicationID, serviceType)) 
		return false;
	if(reportExistsInStoreConfiguration(packetStoreId, request,
    						applicationID, serviceType, messageType)){
		reportExecutionStartError(request, ErrorHandler::alreadyExistingReportTypeDefinition);
		return false;
	}
	if(!reportExistsInAppProcessConfiguration(applicationID, serviceType, messageType)){
		reportExecutionStartError(request, ErrorHandler::NonExistentReportTypeDefinition);
		return false;
	}

	return true;
    						
	       						

    }

    bool StorageAndRetrievalService_impl::allServiceTypesAllowed(Message& request, const std::string& packetStoreId,
    									uint16_t applicationID) {
	if (countServicesOfApplication(packetStoreId, applicationID) >= ECSSMaxServiceTypeDefinitions) {
		reportExecutionStartError(request, ErrorHandler::AllServiceTypesAlreadyAllowed);
		return true;
	}
	return false;
    }
    
     uint8_t StorageAndRetrievalService_impl::countServicesOfApplication(const std::string& packetStoreId,
     									uint16_t applicationID) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return false;
	}
	uint8_t serviceCounter = 0;
	for (auto& definition: packetStore->second.definitions) {
		const auto& pair = definition.first;
		if (pair.first == applicationID) {
			serviceCounter++;
		}
	}
	return serviceCounter;
    }
       
    bool StorageAndRetrievalService_impl::isServiceTypeEnabled(const std::string& packetStoreId,
    							uint16_t applicationID, uint8_t targetService) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return false;
	}
	auto& definitions = packetStore->second.definitions;
	return std::any_of(std::begin(definitions), std::end(definitions), [applicationID, targetService](auto& definition) { 
				return applicationID == definition.first.first and targetService == definition.first.second; });
    }
        
    bool StorageAndRetrievalService_impl::isReportTypeEnabled(const std::string& packetStoreId,
    							uint8_t target, 
    							uint16_t applicationID,
                                                      uint8_t serviceType) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return false;
	}
	
	auto appServicePair = std::make_pair(applicationID, serviceType);
	auto serviceTypes = packetStore->second.definitions.find(appServicePair);
	if (serviceTypes == packetStore->second.definitions.end()) {
		return false;
	}
	return std::find(serviceTypes->second.begin(), serviceTypes->second.end(), target) != serviceTypes->second.end();
    }
     
    bool StorageAndRetrievalService_impl::isServiceTypeInConfiguration(Message& request, 
    							const std::string& packetStoreId,
    							uint16_t applicationID, uint8_t serviceType,
                                                         uint8_t numOfMessages) {

	if (not isServiceTypeEnabled(packetStoreId, applicationID, serviceType)) {
		reportExecutionStartError(request, 
				ErrorHandler::NonExistentServiceTypeDefinition);
		request.setMessageReadPosition(request.getMessageReadPosition()+numOfMessages);
		return false;
	}
	return true;
    }
        
    bool StorageAndRetrievalService_impl::isReportTypeInConfiguration(Message& request, 
    							const std::string& packetStoreId,
    							uint16_t applicationID, uint8_t serviceType,
                                                        uint8_t messageType) {
	if (not isReportTypeEnabled(packetStoreId, messageType, applicationID, serviceType)) {
		reportExecutionStartError(request, 
				ErrorHandler::NonExistentReportTypeDefinition);
		return false;
	}
	return true;
    }
    
     void StorageAndRetrievalService_impl::deleteApplicationProcess(const std::string& packetStoreId,
     									uint16_t applicationID) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return;
	}
	auto& definitions = packetStore->second.definitions;
	auto iter = std::begin(definitions);
	while (iter != definitions.end()) {
		iter = std::find_if(
		    std::begin(definitions), std::end(definitions), [applicationID](auto& definition) { 
		    	return applicationID == definition.first.first; });
		definitions.erase(iter);
	}
    }
       
    void StorageAndRetrievalService_impl::deleteServiceRecursive(const std::string& packetStoreId,
    							uint16_t applicationID, uint8_t serviceType) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return;
	}
	auto appServicePair = std::make_pair(applicationID, serviceType);
	packetStore->second.definitions.erase(appServicePair);
    }
    
    void StorageAndRetrievalService_impl::deleteReportRecursive(const std::string& packetStoreId,
    					uint16_t applicationID, uint8_t serviceType,
                                                             uint8_t messageType) {
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return;
	}
	
	auto appServicePair = std::make_pair(applicationID, serviceType);
	auto reportTypes = packetStore->second.definitions.find(appServicePair);
	if (reportTypes == packetStore->second.definitions.end()) {
		return;
	}
	reportTypes->second.erase(std::remove(reportTypes->second.begin(), reportTypes->second.end(), messageType));

	if (packetStore->second.definitions[appServicePair].empty()) {
		deleteServiceRecursive(packetStoreId, applicationID, serviceType);
	}
    } 
 
    bool StorageAndRetrievalService_impl::checkAppControlled(Message& request, uint16_t applicationId) {
	if (std::find(appID_monitored_list.begin(), 
			appID_monitored_list.end(), applicationId) ==
	    appID_monitored_list.end()) {
		reportExecutionStartError(request, ErrorHandler::NotControlledApplication);
		return false;
	}
	return true;
    } 

    bool StorageAndRetrievalService_impl::checkApplicationOfAppProcessConfig(Message& request, 
    						const std::string& packetStoreId, uint16_t applicationID,
                                                                          uint8_t numOfServices) {
	if (not checkAppControlled(request, applicationID) or 
				allServiceTypesAllowed(request, packetStoreId, applicationID)) {
		for (uint8_t i = 0; i < numOfServices; i++) {
			request.setMessageReadPosition(request.getMessageReadPosition()+1);
	
			uint8_t numOfMessages = request.readUint8();
				
			request.setMessageReadPosition(request.getMessageReadPosition()+numOfMessages);
		}
		return false;
	}
	return true;
    }

    bool StorageAndRetrievalService_impl::checkService(Message& request, 
    						const std::string& packetStoreId, 
    						uint16_t applicationID, uint8_t numOfMessages) {
	if (maxServiceTypesReached(request, packetStoreId, applicationID)) {
		request.setMessageReadPosition(request.getMessageReadPosition()+numOfMessages);
		return false;
	}
	return true;
    }
    
    bool StorageAndRetrievalService_impl::maxServiceTypesReached(Message& request, 
    						const std::string& packetStoreId, uint16_t applicationID) {
	if (countServicesOfApplication(packetStoreId, applicationID) >= ECSSMaxServiceTypeDefinitions) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxServiceTypesReached);
		return true;
	}
	return false;
    }
            
    void StorageAndRetrievalService_impl::executeOnPacketStores(Message& request,
                                                       const std::function<void(PacketStore&)>& function) {
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_STORES){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_STORES;
 	
	uint16_t numOfPacketStores = request.readUint16();

 	if(tcSize != (numOfPacketStores * ECSSPacketStoreIdSize)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);

	if (numOfPacketStores == 0) {
		for (auto& packetStore: packetStores) {
			function(packetStore.second);
		}

		reportSuccessStartExecutionVerification(request);
		reportSuccessCompletionExecutionVerification(request);	
		return;
	}
	bool bFaultStartExecution = false;
	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		auto packetStore = packetStores.find(packetStoreId);
		if (packetStore == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		function(packetStores[packetStoreId]);
	}
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);

     }
    
    void StorageAndRetrievalService_impl::addAllReportsOfService(const std::string& packetStoreId,
    							uint16_t applicationID, uint8_t serviceType) {
	
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		return;
	}
	for (const auto& messageType: AllMessageTypes::MessagesOfService.at(serviceType)) {
		auto appServicePair = std::make_pair(applicationID, serviceType);
		packetStore->second.definitions[appServicePair].push_back(messageType);
	}
    }
    
     void StorageAndRetrievalService_impl::enableStorageFunction(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::EnableStorageInPacketStores)) {
		return;
	}
	
	executeOnPacketStores(request, [](PacketStore& p) { p.storageStatus = true; });
    
     }

     void StorageAndRetrievalService_impl::disableStorageFunction(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::DisableStorageInPacketStores)) {
		return;
	}
	
	executeOnPacketStores(request, [](PacketStore& p) { p.storageStatus = false; });
	
     }

/*************************************************************************************************/
/*************************************************************************************************/
/*************************************************************************************************/

    bool StorageAndRetrievalService_impl::storeAndRetrievalTCSizeVerification(Message& request) {  
 	uint16_t currentPosition = request.getMessageReadPosition();
 	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (ECSSPacketStoreIdSize + STR_RTL_NUM_APPID)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return false;
	}
 	tcSize -= (ECSSPacketStoreIdSize + STR_RTL_NUM_APPID);

 	request.setMessageReadPosition(currentPosition + ECSSPacketStoreIdSize);

	uint16_t numOfApplications = request.readUint16();
	
	for (uint16_t currentApplicationNumber = 0; currentApplicationNumber < numOfApplications; currentApplicationNumber++) {
 		if(tcSize < (STR_RTL_APPID_SIZE + STR_RTL_NUM_SERVICES)){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);
			return false;
		}
		tcSize -= (STR_RTL_APPID_SIZE + STR_RTL_NUM_SERVICES);
		
		request.readUint16();
		uint16_t numOfServices = request.readUint16();

		for (uint8_t currentServiceNumber = 0; currentServiceNumber < numOfServices; currentServiceNumber++) {
 			if(tcSize < (STR_RTL_SERVICES_SIZE + STR_RTL_NUM_SUBTYPES)){     
				reportAcceptanceError(request, ErrorHandler::InvalidLength);
				return false;
			}
			tcSize -= (STR_RTL_SERVICES_SIZE + STR_RTL_NUM_SUBTYPES);
			request.readUint8();
			uint16_t numOfMessages = request.readUint16();

 			if(tcSize < (STR_RTL_SUBTYPES_SIZE * numOfMessages)){     
				reportAcceptanceError(request, ErrorHandler::InvalidLength);
				return false;
			}
			tcSize -= (STR_RTL_SUBTYPES_SIZE * numOfMessages);
			request.setMessageReadPosition(request.getMessageReadPosition() + (STR_RTL_SUBTYPES_SIZE * numOfMessages));
		}
	}

	if(tcSize > 0){  
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return false;
	}
	request.setMessageReadPosition(currentPosition);	

	return true;   
    }         
/*************************************************************************************************/
/*************************************************************************************************/
/*************************************************************************************************/

     void StorageAndRetrievalService_impl::addPacketsDefinitionsToPacketStores(Message& request){
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::AddPacketsDefinitionsToPacketStores)) {
		return;
	}

 	if(!storeAndRetrievalTCSizeVerification(request)){     
		return;
	}
	reportSuccessAcceptanceVerification(request);
	 	
	auto packetStoreId = readPacketStoreId(request);

	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		return;
	}
	uint16_t numOfApplications = request.readUint16();

	bool bFaultStartExecution = false;
	
	for (uint16_t currentApplicationNumber = 0; currentApplicationNumber < numOfApplications; currentApplicationNumber++) {
		uint16_t applicationID = request.readUint16();
		uint16_t numOfServices = request.readUint16();

		if (not checkApplicationOfAppProcessConfig(request, packetStoreId, applicationID, numOfServices)) {
			bFaultStartExecution = true;
			continue;
		}
		
		if (numOfServices == 0) {
			for (const auto& serviceType: AllMessageTypes::MessagesOfService) {
				
				auto appServicePair = std::make_pair(applicationID, serviceType.first);
				for (auto& messageType: serviceType.second){
					if(!reportExistsInStoreConfiguration(packetStoreId, request,
    						applicationID, serviceType.first, messageType)){
							packetStore->second.definitions[appServicePair].push_back(messageType);
					}
				}
			}
			continue;
		}

		for (uint8_t currentServiceNumber = 0; currentServiceNumber < numOfServices; currentServiceNumber++) {
			uint8_t serviceType = request.readUint8();
			uint16_t numOfMessages = request.readUint16();

			if (not checkService(request, packetStoreId, applicationID, numOfMessages)) {
				bFaultStartExecution = true;
				continue;
			}

			if (numOfMessages == 0) {
				addAllReportsOfService(packetStoreId, applicationID, serviceType);
				continue;
			}

			for (uint8_t currentMessageNumber = 0; currentMessageNumber < numOfMessages; currentMessageNumber++) {
				uint8_t messageType = request.readUint8();

				if (not checkMessage(request, packetStoreId, applicationID, serviceType, messageType)) {
					bFaultStartExecution = true;
					continue;
				}
				auto key = std::make_pair(applicationID, serviceType);
				packetStore->second.definitions[key].push_back(
				    messageType);

			}
		}
	}
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }
     	
     void StorageAndRetrievalService_impl::removePacketsDefinitionsFromPacketStores(Message& request){
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::RemovePacketsDefinitionsFromPacketStores)) {
		return;
	}

 	if(!storeAndRetrievalTCSizeVerification(request)){     
		return;
	}
	reportSuccessAcceptanceVerification(request);
	
	auto packetStoreId = readPacketStoreId(request);
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		return;
	}

	uint16_t numOfApplications = request.readUint16();
	
	if (numOfApplications == 0) {
		packetStore->second.definitions.clear();
		return;
	}
		
	bool bFaultStartExecution = false;
	
	for (uint16_t currentApplicationNumber = 0; currentApplicationNumber < numOfApplications; currentApplicationNumber++) {
		uint16_t applicationID = request.readUint16();
		uint16_t numOfServices = request.readUint16();
		
		if (numOfServices == 0) {
			deleteApplicationProcess(packetStoreId,  applicationID);
			continue;
		}

		for (uint16_t currentServiceNumber = 0; currentServiceNumber < numOfServices; currentServiceNumber++) {
			uint8_t serviceType = request.readUint8();
			uint16_t numOfMessages = request.readUint16();

			if (not isServiceTypeInConfiguration(request, packetStoreId, 
							applicationID, serviceType, numOfMessages)) {
				bFaultStartExecution = true;
				continue;
			}
			if (numOfMessages == 0) {
				deleteServiceRecursive(packetStoreId, applicationID, serviceType);
				continue;
			}

			for (uint16_t currentMessageNumber = 0; currentMessageNumber < numOfMessages; currentMessageNumber++) {
				uint8_t messageType = request.readUint8();

				if (not isReportTypeInConfiguration(request, packetStoreId, 
							 applicationID, serviceType, messageType)) {
					bFaultStartExecution = true;
					continue;
				}
				deleteReportRecursive(packetStoreId, applicationID, serviceType, messageType);
			}
		}
	}
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
   }

     void StorageAndRetrievalService_impl::reportContentAPIDStoreConfig(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ReportContentAPIDStoreConfig)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);
 		
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			StorageAndRetrievalService::MessageType::ContentAPIDStoreConfigReport, 
			counters[StorageAndRetrievalService::MessageType::ContentAPIDStoreConfigReport], 0);
			
	auto packetStoreId = readPacketStoreId(request);
	auto packetStore = packetStores.find(packetStoreId);
	if (packetStore == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		return;
	}
	
	report.appendString(packetStoreId, ECSSPacketStoreIdSize);
	
	std::vector<uint16_t> appList = packetStore->second.getApplicationsInStore();	
	uint16_t numApplications = appList.size();		
	
	report.appendUint16(numApplications);
	for (auto& application: appList) {
		report.appendUint16(application);
		
		auto& definitions = packetStore->second.definitions;
		uint16_t numMessagesTypes = 0;
		for (auto& messagesTypes: AllMessageTypes::MessagesOfService){
			uint8_t targetService = messagesTypes.first;
			if( std::any_of(std::begin(definitions), std::end(definitions), [application, targetService](auto& definition) { 
				return application == definition.first.first and targetService == definition.first.second; }))
					numMessagesTypes++;
					
		}	
		report.appendUint16(numMessagesTypes);
		for (auto& messagesTypes: AllMessageTypes::MessagesOfService){
			uint8_t targetService = messagesTypes.first;
			if( std::any_of(std::begin(definitions), std::end(definitions), [application, targetService](auto& definition) { 
				return application == definition.first.first and targetService == definition.first.second; })){
					report.appendUint8(targetService);
					auto key = std::make_pair(application, targetService);
					auto& messagesSubType = packetStore->second.definitions[key];
					uint16_t numMessagesSubType = messagesSubType.size();
					report.appendUint16(numMessagesSubType);
					for (auto& messagesSubTypes: messagesSubType){
						report.appendUint8(messagesSubTypes);
					}
			}
		}			
	}

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[StorageAndRetrievalService::MessageType::ContentAPIDStoreConfigReport]++;	
     }

     void StorageAndRetrievalService_impl::startByTimeRangeRetrieval(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::StartByTimeRangeRetrieval)) {
		return;
	}
 	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();

	if(tcSize != numOfPacketStores * (ECSSPacketStoreIdSize + d_time_provider->getTimeSize() * 2)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 		
	reportSuccessAcceptanceVerification(request);

	bool bFaultStartExecution = false;	

	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (failedStartOfByTimeRangeRetrieval(packetStoreId, request)) {
			bFaultStartExecution = true;	
			continue;
		}
		uint32_t retrievalStartTime = request.readUint32();
	
		uint32_t retrievalEndTime = request.readUint32();

		if (retrievalStartTime >= retrievalEndTime) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::InvalidTimeWindow);
			bFaultStartExecution = true;
			continue;
		}

		// todo: 6.15.3.5.2.d(4), actually count the current time

		auto& packetStore = packetStores[packetStoreId];
		packetStore.byTimeRangeRetrievalStatus = true;
		packetStore.retrievalStartTime = retrievalStartTime;
		packetStore.retrievalEndTime = retrievalEndTime;
		// todo: start the by-time-range retrieval process according to the priority policy
		
		/*********************************************************************
		DOWNLOAD
		*********************************************************************/
	}
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }

     void StorageAndRetrievalService_impl::deletePacketStoreContent(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::DeletePacketStoreContent)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (d_time_provider->getTimeSize() + STR_RTL_NUM_APPID)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= (d_time_provider->getTimeSize() + STR_RTL_NUM_APPID);
	
	uint32_t timeLimit = request.readUint32();

	uint16_t numOfPacketStores = request.readUint16();
	
	if(tcSize != numOfPacketStores * ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 
	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;	


	if (numOfPacketStores == 0) {
		for (auto& packetStore: packetStores) {
			if (packetStore.second.byTimeRangeRetrievalStatus) {
				reportExecutionStartError(
				    request, ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithByTimeRangeRetrieval);
				bFaultStartExecution = true;
				continue;
			}
			if (packetStore.second.openRetrievalStatus == PacketStore::InProgress) {
				reportExecutionStartError(
				    request, ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithOpenRetrievalInProgress);
				bFaultStartExecution = true;
				continue;
			}
			deleteContentUntil(packetStore.first, timeLimit);
		}
		return;
	}
	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (packetStores.find(packetStoreId) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStores[packetStoreId].byTimeRangeRetrievalStatus) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithByTimeRangeRetrieval);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStores[packetStoreId].openRetrievalStatus == PacketStore::InProgress) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithOpenRetrievalInProgress);
			bFaultStartExecution = true;
			continue;
		}
		deleteContentUntil(packetStoreId, timeLimit);
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);		
     }

     void StorageAndRetrievalService_impl::packetStoreContentSummaryReport(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ReportContentSummaryOfPacketStores)) {
		return;
	}
	
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			StorageAndRetrievalService::MessageType::PacketStoreContentSummaryReport, 
			counters[StorageAndRetrievalService::MessageType::PacketStoreContentSummaryReport], 0);

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();

	if(tcSize != numOfPacketStores * ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);
	
	uint16_t oldnumOfPacketStores = 0;
	oldnumOfPacketStores = numOfPacketStores;

	uint16_t position = request.getMessageReadPosition();
	
	bool bFaultStartExecution = false;

	if (numOfPacketStores == 0) {
		report.appendUint16(packetStores.size());
		for (auto& packetStore: packetStores) {
			auto packetStoreId = packetStore.first;
			report.appendString(packetStoreId, ECSSPacketStoreIdSize);

			createContentSummary(report, packetStoreId);

		}
		d_message_parser->closeMessage(report);
			
        	message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

       	counters[StorageAndRetrievalService::MessageType::PacketStoreContentSummaryReport]++;
		
		reportSuccessStartExecutionVerification(request);
		
		reportSuccessCompletionExecutionVerification(request);

		return;
	}
	
	uint16_t numOfValidPacketStores = 0;
	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (packetStores.find(packetStoreId) != packetStores.end()) {
			numOfValidPacketStores++;
		}
	}
	
	report.appendUint16(numOfValidPacketStores);
	numOfPacketStores = oldnumOfPacketStores;

	request.setMessageReadPosition(position);
	
	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (packetStores.find(packetStoreId) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		report.appendString(packetStoreId, ECSSPacketStoreIdSize);
		createContentSummary(report, packetStoreId);
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[StorageAndRetrievalService::MessageType::PacketStoreContentSummaryReport]++;	
	
     }

     void StorageAndRetrievalService_impl::changeOpenRetrievalStartTimeTag(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ChangeOpenRetrievalStartingTime)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (d_time_provider->getTimeSize() + STR_RTL_NUM_APPID)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= (d_time_provider->getTimeSize() + STR_RTL_NUM_APPID);
	
	uint32_t newStartTimeTag = request.readUint32();

	uint16_t numOfPacketStores = request.readUint16();
	
	if(tcSize != numOfPacketStores * ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 
	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;
	
	if (numOfPacketStores == 0) {
		for (auto& packetStore: packetStores) {
			if (packetStore.second.openRetrievalStatus == PacketStore::InProgress) {
				reportExecutionStartError(
				    request, ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithOpenRetrievalInProgress);
				bFaultStartExecution = true;
				continue;
			}
			packetStore.second.openRetrievalStartTimeTag = newStartTimeTag;
			packetStore.second.currentRetrievalStartTimeTag = newStartTimeTag;
		}
		return;
	}

	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (packetStores.find(packetStoreId) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStores[packetStoreId].openRetrievalStatus == PacketStore::InProgress) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithOpenRetrievalInProgress);
			bFaultStartExecution = true;
			continue;
		}
		packetStores[packetStoreId].openRetrievalStartTimeTag = newStartTimeTag;
		packetStores[packetStoreId].currentRetrievalStartTimeTag = newStartTimeTag;
	}
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }

     void StorageAndRetrievalService_impl::resumeOpenRetrievalOfPacketStores(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ResumeOpenRetrievalOfPacketStores)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();
	
	if(tcSize != numOfPacketStores * ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	

	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;
	
	if (numOfPacketStores == 0) {
		for (auto& packetStore: packetStores) {
			if (packetStore.second.byTimeRangeRetrievalStatus) {
				reportExecutionStartError(
				    request, ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithByTimeRangeRetrieval);
			        bFaultStartExecution = true;
				continue;
			}
			packetStore.second.openRetrievalStatus = PacketStore::InProgress;
		}
		return;
	}
	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (packetStores.find(packetStoreId) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		auto& packetStore = packetStores[packetStoreId];
		if (packetStore.byTimeRangeRetrievalStatus) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::SetPacketStoreWithByTimeRangeRetrieval);
			bFaultStartExecution = true;
			continue;
		}
		packetStore.openRetrievalStatus = PacketStore::InProgress;
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }

     void StorageAndRetrievalService_impl::suspendOpenRetrievalOfPacketStores(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::SuspendOpenRetrievalOfPacketStores)) {
		return;
	}
	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();

	if(tcSize != numOfPacketStores * ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	

	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;
	
	if (numOfPacketStores == 0) {
		for (auto& packetStore: packetStores) {
			packetStore.second.openRetrievalStatus = PacketStore::Suspended;
		}
		return;
	}
	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (packetStores.find(packetStoreId) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		packetStores[packetStoreId].openRetrievalStatus = PacketStore::Suspended;
	}
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }

     void StorageAndRetrievalService_impl::abortByTimeRangeRetrieval(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::AbortByTimeRangeRetrieval)) {
		return;
	}
	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();

	if(tcSize != numOfPacketStores * ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	

	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;
	
	if (numOfPacketStores == 0) {
		for (auto& packetStore: packetStores) {
			packetStore.second.byTimeRangeRetrievalStatus = false;
		}
		return;
	}
	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		if (packetStores.find(packetStoreId) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		packetStores[packetStoreId].byTimeRangeRetrievalStatus = false;
	}
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }

     void StorageAndRetrievalService_impl::packetStoresStatusReport(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ReportStatusOfPacketStores)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);
	
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			StorageAndRetrievalService::MessageType::PacketStoresStatusReport, 
			counters[StorageAndRetrievalService::MessageType::PacketStoresStatusReport], 0);

       report.appendUint16(packetStores.size());
	for (auto& packetStore: packetStores) {
		auto packetStoreId = packetStore.first;
		report.appendString(packetStoreId, ECSSPacketStoreIdSize);
		report.appendUint8(packetStore.second.storageStatus);
		report.appendUint8(packetStore.second.openRetrievalStatus);
		report.appendUint8(packetStore.second.byTimeRangeRetrievalStatus);
	}
	
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[StorageAndRetrievalService::MessageType::PacketStoresStatusReport]++;

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);		
     }

     void StorageAndRetrievalService_impl::createPacketStores(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::CreatePacketStores)) {
		return;
	}
	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();

	if(tcSize != numOfPacketStores * (ECSSPacketStoreIdSize + STR_RTL_PKTSTORE_SIZE + STR_RTL_PKTSTORE_TYPE + STR_RTL_PKTSTORE_VC)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	

	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;


	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		if (packetStores.size() >= ECSSMaxPacketStores) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::MaxNumberOfPacketStoresReached);
			bFaultStartExecution = true;
			return;
		}
		auto idToCreate = readPacketStoreId(request);

		if (packetStores.find(idToCreate) != packetStores.end()) {
			uint16_t numberOfBytesToSkip = 4;
			request.setMessageReadPosition(request.getMessageReadPosition() + numberOfBytesToSkip);	
				
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::AlreadyExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		uint16_t packetStoreSize = request.readUint16();
		 
		uint8_t typeCode = request.readUint8();
	
		PacketStore::PacketStoreType packetStoreType = (typeCode == 0) ? PacketStore::Circular : PacketStore::Bounded;
		uint8_t virtualChannel = request.readUint8();
	

		if (virtualChannel < VirtualChannelLimits.min or virtualChannel > VirtualChannelLimits.max) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::InvalidVirtualChannel);
			bFaultStartExecution = true;
			continue;
		}
		PacketStore newPacketStore;
		newPacketStore.sizeInBytes = packetStoreSize;
		newPacketStore.packetStoreType = packetStoreType;
		newPacketStore.storageStatus = false;
		newPacketStore.byTimeRangeRetrievalStatus = false;
		newPacketStore.openRetrievalStatus = PacketStore::Suspended;
		newPacketStore.virtualChannel = virtualChannel;
		packetStores.insert({idToCreate, newPacketStore});
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }

     void StorageAndRetrievalService_impl::deletePacketStores(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::DeletePacketStores)) {
		return;
	}
	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();

	if(tcSize != numOfPacketStores * ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	

	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;
	
	if (numOfPacketStores == 0) {
		uint16_t numOfPacketStoresToDelete = 0;
		std::string packetStoresToDelete[ECSSMaxPacketStores];
		for (auto& packetStore: packetStores) {
			if (packetStore.second.storageStatus) {
				reportExecutionStartError(
				    request, ErrorHandler::ExecutionStartErrorType::DeletionOfPacketStoreWithStorageStatusEnabled);
				bFaultStartExecution = true;
				continue;
			}
			if (packetStore.second.byTimeRangeRetrievalStatus) {
				reportExecutionStartError(
				    request, ErrorHandler::ExecutionStartErrorType::DeletionOfPacketWithByTimeRangeRetrieval);
				bFaultStartExecution = true;
				continue;
			}
			if (packetStore.second.openRetrievalStatus == PacketStore::InProgress) {
				reportExecutionStartError(
				    request, ErrorHandler::ExecutionStartErrorType::DeletionOfPacketWithOpenRetrievalInProgress);
				bFaultStartExecution = true;
				continue;
			}
			packetStoresToDelete[numOfPacketStoresToDelete] = packetStore.first;
			numOfPacketStoresToDelete++;
		}
		for (uint16_t l = 0; l < numOfPacketStoresToDelete; l++) {
			uint8_t data[ECSSPacketStoreIdSize];
			std::string idToDelete = packetStoresToDelete[l];
			std::copy(idToDelete.begin(), idToDelete.end(), data);
			std::string key = reinterpret_cast<char *>(data);
			packetStores.erase(key);
		}
		return;
	}

	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto idToDelete = readPacketStoreId(request);
		if (packetStores.find(idToDelete) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		auto& packetStore = packetStores[idToDelete];

		if (packetStore.storageStatus) {
			reportExecutionStartError(
			    request, ErrorHandler::ExecutionStartErrorType::DeletionOfPacketStoreWithStorageStatusEnabled);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStore.byTimeRangeRetrievalStatus) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::DeletionOfPacketWithByTimeRangeRetrieval);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStore.openRetrievalStatus == PacketStore::InProgress) {
			reportExecutionStartError(
			    request, ErrorHandler::ExecutionStartErrorType::DeletionOfPacketWithOpenRetrievalInProgress);
			bFaultStartExecution = true;
			continue;
		}
		packetStores.erase(idToDelete);
	}
	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);	
     }

     void StorageAndRetrievalService_impl::packetStoreConfigurationReport(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ReportConfigurationOfPacketStores)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);
	
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			StorageAndRetrievalService::MessageType::PacketStoreConfigurationReport, 
			counters[StorageAndRetrievalService::MessageType::PacketStoreConfigurationReport], 0);

        report.appendUint16(packetStores.size());
	for (auto& packetStore: packetStores) {
		auto packetStoreId = packetStore.first;
		report.appendString(packetStoreId, ECSSPacketStoreIdSize);
		report.appendUint16(packetStore.second.sizeInBytes);
		uint8_t typeCode = (packetStore.second.packetStoreType == PacketStore::Circular) ? 0 : 1;
		report.appendUint8(typeCode);
		report.appendUint8(packetStore.second.virtualChannel);
	}
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[StorageAndRetrievalService::MessageType::PacketStoreConfigurationReport]++;
	
	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);

     }

     void StorageAndRetrievalService_impl::copyPacketsInTimeWindow(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::CopyPacketsInTimeWindow)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != (STR_RTL_PKTSTORE_TIMEWIN_TYPE + 2 * (ECSSPacketStoreIdSize + d_time_provider->getTimeSize()))){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	
	uint8_t typeOfTimeWindow = request.readUint8();

	bool bFaultStartExecution = false;
	switch (typeOfTimeWindow) {
		case FromTagToTag:
			bFaultStartExecution = copyFromTagToTag(request);
			break;
		case AfterTimeTag:
			bFaultStartExecution = copyAfterTimeTag(request);
			break;
		case BeforeTimeTag:
			bFaultStartExecution = copyBeforeTimeTag(request);
			break;
		default:
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::InvalidTimeWindow);
			break;
	}

	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }

     void StorageAndRetrievalService_impl::resizePacketStores(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ResizePacketStores)) {
		return;
	}
	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < STR_RTL_NUM_APPID){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= STR_RTL_NUM_APPID;
	
	uint16_t numOfPacketStores = request.readUint16();

	if(tcSize != numOfPacketStores * (ECSSPacketStoreIdSize + STR_RTL_PKTSTORE_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	

	reportSuccessAcceptanceVerification(request);
	bool bFaultStartExecution = false;
	

	for (uint16_t i = 0; i < numOfPacketStores; i++) {
		auto packetStoreId = readPacketStoreId(request);
		uint16_t packetStoreSize = request.readUint16();
		
		if (packetStores.find(packetStoreId) == packetStores.end()) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
			bFaultStartExecution = true;
			continue;
		}
		auto& packetStore = packetStores[packetStoreId];

		if (packetStoreSize >= ECSSMaxPacketStoreSizeInBytes) {
			reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::UnableToHandlePacketStoreSize);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStore.storageStatus) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithStorageStatusEnabled);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStore.openRetrievalStatus == PacketStore::InProgress) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithOpenRetrievalInProgress);
			bFaultStartExecution = true;
			continue;
		}
		if (packetStore.byTimeRangeRetrievalStatus) {
			reportExecutionStartError(request,
			                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithByTimeRangeRetrieval);
			bFaultStartExecution = true;
			continue;
		}
		packetStore.sizeInBytes = packetStoreSize;
	}
 	
	if(not bFaultStartExecution)
		reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }

     void StorageAndRetrievalService_impl::changeTypeToCircular(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ChangeTypeToCircular)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);
		
	auto idToChange = readPacketStoreId(request);
	if (packetStores.find(idToChange) == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		return;
	}
	auto& packetStore = packetStores[idToChange];

	if (packetStore.storageStatus) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithStorageStatusEnabled);
		return;
	}
	if (packetStore.byTimeRangeRetrievalStatus) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithByTimeRangeRetrieval);
		return;
	}
	if (packetStore.openRetrievalStatus == PacketStore::InProgress) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithOpenRetrievalInProgress);
		return;
	}
	packetStore.packetStoreType = PacketStore::Circular;

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }

     void StorageAndRetrievalService_impl::changeTypeToBounded(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ChangeTypeToBounded)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize != ECSSPacketStoreIdSize){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);
	
	auto idToChange = readPacketStoreId(request);
	if (packetStores.find(idToChange) == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		return;
	}
	auto& packetStore = packetStores[idToChange];

	if (packetStore.storageStatus) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithStorageStatusEnabled);
		return;
	}
	if (packetStore.byTimeRangeRetrievalStatus) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithByTimeRangeRetrieval);
		return;
	}
	if (packetStore.openRetrievalStatus == PacketStore::InProgress) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithOpenRetrievalInProgress);
		return;
	}
	packetStore.packetStoreType = PacketStore::Bounded;

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }

     void StorageAndRetrievalService_impl::changeVirtualChannel(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			StorageAndRetrievalService::MessageType::ChangeVirtualChannel)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize != (ECSSPacketStoreIdSize + STR_RTL_PKTSTORE_VC)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	reportSuccessAcceptanceVerification(request);
		
	auto idToChange = readPacketStoreId(request);
	uint8_t virtualChannel = request.readUint8();
		
	if (packetStores.find(idToChange) == packetStores.end()) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::NonExistingPacketStore);
		return;
	}
	auto& packetStore = packetStores[idToChange];

	if (virtualChannel < VirtualChannelLimits.min or virtualChannel > VirtualChannelLimits.max) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::InvalidVirtualChannel);
		return;
	}
	if (packetStore.byTimeRangeRetrievalStatus) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithByTimeRangeRetrieval);
		return;
	}
	if (packetStore.openRetrievalStatus == PacketStore::InProgress) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::GetPacketStoreWithOpenRetrievalInProgress);
		return;
	}
	packetStore.virtualChannel = virtualChannel;

	reportSuccessStartExecutionVerification(request);
		
	reportSuccessCompletionExecutionVerification(request);
     }


  } /* namespace pus */
} /* namespace gr */
