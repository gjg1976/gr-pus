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
#include "LargePacketTransferService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    LargePacketTransferService::sptr
    LargePacketTransferService::make()
    {
      return gnuradio::make_block_sptr<LargePacketTransferService_impl>(
        );
    }


    /*
     * The private constructor
     */
    LargePacketTransferService_impl::LargePacketTransferService_impl()
      : gr::block("LargePacketTransferService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        serviceType = ServiceType;
        downlinkLargeMessageTransactionIdentifier = 0;
        
        for(size_t i = 0; i < LargePacketTransferService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_in(PMT_LARGE);
        set_msg_handler(PMT_LARGE,
                    [this](pmt::pmt_t msg) { this->handle_large_in_msg(msg); });
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
                & LargePacketTransferService_impl::timerTick,
                this,
                std::placeholders::_1
            )
    	);           
    }

    /*
     * Our virtual destructor.
     */
    LargePacketTransferService_impl::~LargePacketTransferService_impl()
    {
    }

    void LargePacketTransferService_impl::timerTick(TimeProvider *p) {
	for (auto& uplinkmessage: uplinkMessagesList) {
		if(++uplinkmessage.second.first > ECSSLargeUplinkReceptiontimeOut){
			uint16_t largeMessageTransactionIdentifier = uplinkmessage.first;
			uplinkMessagesList.erase(largeMessageTransactionIdentifier);
			uplinkAbortReport(largeMessageTransactionIdentifier,  
				ErrorHandler::LargePacketUplinkAbortErrorType::LargeUplinkTimeoutExpiress);
		}
	}       
    }
    
    void LargePacketTransferService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case FirstUplinkPartMessage:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "FirstUplinkPartReport");
#endif
			    firstUplinkPartMessage(message);
                           break;
                        case IntermediateUplinkPartMessage:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "IntermediateUplinkPartReport");
#endif
			    intermediateUplinkPartMessage(message);
                           break;                                             
                        case LastUplinkPartMessage:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "LastUplinkPartReport");
#endif
			    lastUplinkPartMessage(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Large Packet Transfer Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Large Packet Transfer Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    void LargePacketTransferService_impl::handle_large_in_msg(pmt::pmt_t pdu)
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
                std::vector<uint8_t> in_data = pmt::u8vector_elements(v_data);
                split(in_data, downlinkLargeMessageTransactionIdentifier++);

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }
    void LargePacketTransferService_impl::firstDownlinkPartReport(uint16_t largeMessageTransactionIdentifier,
                                                         uint16_t partSequenceNumber,
                                                         MessageArray& data) {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			LargePacketTransferService::MessageType::FirstDownlinkPartReport, 
			counters[LargePacketTransferService::MessageType::FirstDownlinkPartReport], 0);
	report.appendUint16(largeMessageTransactionIdentifier);
	report.appendUint16(partSequenceNumber);
	report.appendUint8Array(data);

	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[LargePacketTransferService::MessageType::FirstDownlinkPartReport]++;	
    }

    void LargePacketTransferService_impl::intermediateDownlinkPartReport(
    			uint16_t largeMessageTransactionIdentifier, uint16_t partSequenceNumber,
   			MessageArray& data) {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			LargePacketTransferService::MessageType::InternalDownlinkPartReport, 
			counters[LargePacketTransferService::MessageType::InternalDownlinkPartReport], 0);
	report.appendUint16(largeMessageTransactionIdentifier);
	report.appendUint16(partSequenceNumber);
	report.appendUint8Array(data);

	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[LargePacketTransferService::MessageType::InternalDownlinkPartReport]++;
    }

    void LargePacketTransferService_impl::lastDownlinkPartReport(uint16_t largeMessageTransactionIdentifier,
                                                        uint16_t partSequenceNumber,
                                                        MessageArray& data) {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			LargePacketTransferService::MessageType::LastDownlinkPartReport, 
			counters[LargePacketTransferService::MessageType::LastDownlinkPartReport], 0);
	report.appendUint16(largeMessageTransactionIdentifier);
	report.appendUint16(partSequenceNumber);
	report.appendUint8Array(data);

	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[LargePacketTransferService::MessageType::LastDownlinkPartReport]++;	
    }
 
    void LargePacketTransferService_impl::firstUplinkPartMessage(Message& request)
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			LargePacketTransferService::MessageType::FirstUplinkPartMessage)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize != (LARGE_PACKET_TRANS_ID_SIZE + LARGE_PACKET_TRANS_COUNTER_SIZE + ECSSMaxFixedOctetMessageSize)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

 	 	
	reportSuccessAcceptanceVerification(request);
		
	uint16_t largeMessageTransactionIdentifier = request.readUint16();


	uint16_t partSequenceNumber = request.readUint16();


	if(uplinkMessagesList.find(largeMessageTransactionIdentifier) != uplinkMessagesList.end())	{
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionIDAlreadyExist);
		return;
	}
	
	if(partSequenceNumber != 0){
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionWrongSequenceNumber);
		return;	
	}
	MessageArray messagePart = d_message_parser->parseUpToEndfromMessage(request);
	reportSuccessStartExecutionVerification(request);

	uplinkMessageParts uplinkmessageparts = {{partSequenceNumber,messagePart}};
	uplinkMessageEntry uplinkmessageentry = {0, uplinkmessageparts};
	uplinkMessagesList[largeMessageTransactionIdentifier] = uplinkmessageentry;

	reportSuccessCompletionExecutionVerification(request);
    }

    void LargePacketTransferService_impl::intermediateUplinkPartMessage(Message& request)
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			LargePacketTransferService::MessageType::IntermediateUplinkPartMessage)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize != (LARGE_PACKET_TRANS_ID_SIZE + LARGE_PACKET_TRANS_COUNTER_SIZE + ECSSMaxFixedOctetMessageSize)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

 	 	
	reportSuccessAcceptanceVerification(request);
		
	uint16_t largeMessageTransactionIdentifier = request.readUint16();


	uint16_t partSequenceNumber = request.readUint16();
	
	auto uplinkmessage = uplinkMessagesList.find(largeMessageTransactionIdentifier) ;
	if(uplinkmessage == uplinkMessagesList.end())	{
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionIDNonExist );
		return;
	}
	
	if(partSequenceNumber == 0){
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionWrongSequenceNumber);
		return;	
	}
	if(uplinkmessage->second.second.find(partSequenceNumber) != uplinkmessage->second.second.end()){
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionWrongSequenceNumber);
		return;	
	}

	MessageArray messagePart = d_message_parser->parseUpToEndfromMessage(request);
	reportSuccessStartExecutionVerification(request);

	uplinkmessage->second.second[partSequenceNumber] = messagePart;
	uplinkmessage->second.first = 0;

	reportSuccessCompletionExecutionVerification(request);
    }
    
    void LargePacketTransferService_impl::lastUplinkPartMessage(Message& request)	    
    {
	if (!d_message_parser->assertTC(request, serviceType, 
			LargePacketTransferService::MessageType::LastUplinkPartMessage)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < (LARGE_PACKET_TRANS_ID_SIZE + LARGE_PACKET_TRANS_COUNTER_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	} 
 	 	
	reportSuccessAcceptanceVerification(request);
		
	uint16_t largeMessageTransactionIdentifier = request.readUint16();

	uint16_t partSequenceNumber = request.readUint16();
	
	auto uplinkmessage = uplinkMessagesList.find(largeMessageTransactionIdentifier) ;
	if(uplinkmessage == uplinkMessagesList.end())	{
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionIDNonExist );
		return;
	}
	std::cout << " largeMessageTransactionIdentifier " << largeMessageTransactionIdentifier << "\n";
	if(partSequenceNumber == 0){
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionWrongSequenceNumber);
		return;	
	}
	if(uplinkmessage->second.second.find(partSequenceNumber) != uplinkmessage->second.second.end()){
		reportExecutionStartError(request, 
				ErrorHandler::ExecutionStartErrorType::LargePacketTransactionWrongSequenceNumber);
		return;	
	}

	MessageArray messagePart = d_message_parser->parseUpToEndfromMessage(request);
	
	reportSuccessStartExecutionVerification(request);

	uplinkmessage->second.second[partSequenceNumber] = messagePart;
	uplinkmessage->second.first = 0;

	reportSuccessCompletionExecutionVerification(request);
	
	joint(largeMessageTransactionIdentifier, partSequenceNumber+1);
    }
    
    void LargePacketTransferService_impl::uplinkAbortReport(uint16_t largeMessageTransactionIdentifier, 
    							uint8_t failureIdentification)
    {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			LargePacketTransferService::MessageType::UplinkAbortReport, 
			counters[LargePacketTransferService::MessageType::UplinkAbortReport], 0);

        report.appendUint16(largeMessageTransactionIdentifier);
        
        report.appendUint8(failureIdentification);        
        
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
                				        
        counters[LargePacketTransferService::MessageType::UplinkAbortReport]++;
    }
    
    void LargePacketTransferService_impl::split(std::vector<uint8_t>& message, uint16_t largeMessageTransactionIdentifier) {
	//TODO: Should this be uint32?
	uint16_t size = message.size();
	if (size <= ECSSMaxFixedOctetMessageSize){
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "LargePacketTransferService: Packet shorter than the splitter required");
#endif	
		return;	
	}
	uint16_t parts = (size / ECSSMaxFixedOctetMessageSize) ;
	if (size % ECSSMaxFixedOctetMessageSize > 0)
		parts++;
		
	uint16_t last_part = size - (parts - 1) * ECSSMaxFixedOctetMessageSize ;

	MessageArray dataPart;
	dataPart.reserve(ECSSMaxFixedOctetMessageSize);

	for (uint16_t i = 0; i < ECSSMaxFixedOctetMessageSize; i++) {
		dataPart.push_back(message[i]);
	}
	message.erase(message.begin(), message.begin() + ECSSMaxFixedOctetMessageSize);
	 std::cout << "size " << message.size();
	firstDownlinkPartReport(largeMessageTransactionIdentifier, 0, dataPart);
	
	dataPart.clear();

	for (uint16_t part = 1; part < (parts - 1U); part++) {
		for (uint16_t i = 0; i < ECSSMaxFixedOctetMessageSize; i++) {
			dataPart.push_back(message[i]);
		}
		message.erase(message.begin(), message.begin() + ECSSMaxFixedOctetMessageSize);
		intermediateDownlinkPartReport(largeMessageTransactionIdentifier, part, dataPart);
		dataPart.clear();
	}

	for (uint16_t i = 0; i < last_part; i++) {
		dataPart.push_back(message[i]);
	}
		
	lastDownlinkPartReport(largeMessageTransactionIdentifier, (parts - 1U), dataPart);
    }
    
    void LargePacketTransferService_impl::joint(uint16_t largeMessageTransactionIdentifier,
    				uint16_t numParts)
    {

	auto uplinkmessage = uplinkMessagesList.find(largeMessageTransactionIdentifier) ;
	if(uplinkmessage == uplinkMessagesList.end())	{
		uplinkAbortReport(largeMessageTransactionIdentifier, 
				ErrorHandler::LargePacketUplinkAbortErrorType::LargeUplinkNoPacketFound);
		return;
	}
	
	std::vector<uint8_t> largeMessageData;
	
	for(uint16_t i = 0; i < numParts; i++){
		auto uplinkmessagepart = uplinkmessage->second.second.find(i);
		if(uplinkmessagepart == uplinkmessage->second.second.end()){
			uplinkMessagesList.erase(largeMessageTransactionIdentifier);
			uplinkAbortReport(largeMessageTransactionIdentifier,  
				ErrorHandler::LargePacketUplinkAbortErrorType::LargeUplinkMissingPart);
			return;		
		}
		largeMessageData.insert(largeMessageData.end(), 
				uplinkmessagepart->second.begin(), uplinkmessagepart->second.end());

	}
	uplinkMessagesList.erase(largeMessageTransactionIdentifier);		
        message_port_pub(PMT_REL, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(largeMessageData.size(), largeMessageData)));
    }   

  } /* namespace pus */
} /* namespace gr */
