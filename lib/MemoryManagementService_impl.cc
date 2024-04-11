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
#include "MemoryManagementService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    MemoryManagementService::sptr
    MemoryManagementService::make()
    {
      return gnuradio::make_block_sptr<MemoryManagementService_impl>(
        );
    }


    /*
     * The private constructor
     */
    MemoryManagementService_impl::MemoryManagementService_impl()
      : gr::block("MemoryManagementService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        d_memory_manager_handler = MemoryManager::getInstance();
        
        serviceType = ServiceType;
        for(size_t i = 0; i < MemoryManagementService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);
        
        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;
    }

    /*
     * Our virtual destructor.
     */
    MemoryManagementService_impl::~MemoryManagementService_impl()
    {
    }

    void MemoryManagementService_impl::handle_msg(pmt::pmt_t pdu)
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
                        case LoadRawMemoryDataAreas:   
#ifdef _PUS_DEBUG 
                           GR_LOG_WARN(d_logger, "LoadRawMemoryDataAreas");
#endif
                           loadRawData(message);
                           break;
                        case DumpRawMemoryData:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DumpRawMemoryData");
#endif
                           dumpRawData(message);
                           break;                                             
                        case CheckRawMemoryData:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "CheckRawMemoryData");
#endif
                           checkRawData(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Memory Management Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Memory Management Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

    inline bool MemoryManagementService_impl::dataValidator(MessageArray& data, uint16_t checksum) {
	return (checksum == CRCHelper::calculateMessageCRC(data));
    }

    void MemoryManagementService_impl::loadRawData(Message& request) {
	/**
	 * Bear in mind that there is currently no error checking for invalid parameters.
	 * A future version will include error checking and the corresponding error report/notification,
	 * as the manual implies.
	 *
	 * @todo Add error checking and reporting for the parameters
	 * @todo Add failure reporting
	 */

	if (!d_message_parser->assertTC(request, serviceType, 
			MemoryManagementService::MessageType::LoadRawMemoryDataAreas)) {
		return;
	}
 	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (MEM_MNG_ID + MEM_MNG_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= MEM_MNG_ID + MEM_MNG_SIZE;

	uint8_t readEnum8 = request.readEnum8();
	
	uint16_t iterationCount = request.readUint16();
	
	uint16_t position = request.getMessageReadPosition();
	
	for (std::size_t j = 0; j < iterationCount; j++) {

		if(tcSize < (MEM_MNG_START_ADDR + MEM_MNG_LENGTH + MEM_MNG_CHK)){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);
			return;
		}	
	
 		tcSize -= MEM_MNG_START_ADDR + MEM_MNG_LENGTH + MEM_MNG_CHK;
 		request.setMessageReadPosition(request.getMessageReadPosition() + MEM_MNG_START_ADDR); 	
		
		uint16_t dataLength = request.readUint16();
		
 		if(tcSize < dataLength){     
			reportAcceptanceError(request, ErrorHandler::InvalidLength);
			return;
		}	
 	
 		tcSize -= dataLength;
	 
		request.setMessageReadPosition(request.getMessageReadPosition() + dataLength + MEM_MNG_CHK);				
	}
	  

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);
	
	if(readEnum8 >= MemoryManager::MemoryID::END)
	{
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::undefinedMemory);
		return;
	}

	auto memoryID = static_cast<MemoryManager::MemoryID>(readEnum8);
				
	if (!d_memory_manager_handler->allowedWritting(memoryID))
	{
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::readOnlyMemory);
		return;
	}

	MessageArray readData;
	
	request.setMessageReadPosition(position);
	
	reportSuccessStartExecutionVerification(request);
	for (std::size_t j = 0; j < iterationCount; j++) {
		uint64_t startAddress = request.readUint64();

		uint16_t dataLength = request.readUint16();


		for (uint16_t i = 0; i < dataLength; i++) {
			uint8_t data = request.readUint8();
			readData.push_back(data);
		}

		uint16_t checksum = request.readUint16();

		if (!d_memory_manager_handler->addressValidator(memoryID, startAddress) ||
			    !d_memory_manager_handler->addressValidator(memoryID, startAddress + dataLength)) {
			reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AddressOutOfRange);
			continue;
		}

        	if (!dataValidator(readData, checksum)) {
			reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::ChecksumFailed);
			continue;
		}
		d_memory_manager_handler->writeData(memoryID, startAddress, readData);
	}
	
	reportSuccessCompletionExecutionVerification(request);
     }

    void MemoryManagementService_impl::dumpRawData(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			MemoryManagementService::MessageType::DumpRawMemoryData)) {
		return;
	}
	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (MEM_MNG_ID + MEM_MNG_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= MEM_MNG_ID + MEM_MNG_SIZE;
	
	uint8_t readEnum8 = request.readEnum8();
	
	uint16_t iterationCount = request.readUint16();
	
	if(tcSize != iterationCount * (MEM_MNG_START_ADDR + MEM_MNG_LENGTH)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	
	
	reportSuccessAcceptanceVerification(request);
	
	if(readEnum8 >= MemoryManager::MemoryID::END)
	{
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::undefinedMemory);
		return;
	}

	auto memoryID = static_cast<MemoryManager::MemoryID>(readEnum8);
	
	reportSuccessStartExecutionVerification(request);
		
        Message message = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			MemoryManagementService::MessageType::DumpRawMemoryDataReport, 
			counters[MemoryManagementService::MessageType::DumpRawMemoryDataReport], 0);
	
	message.appendEnum8(readEnum8);

	uint16_t position = request.getMessageReadPosition();
	uint16_t validDumps = 0;
	for (std::size_t j = 0; j < iterationCount; j++) {
		uint64_t startAddress = request.readUint64();

		uint16_t readLength = request.readUint16();

		if (d_memory_manager_handler->addressValidator(memoryID, startAddress) &&
		    d_memory_manager_handler->addressValidator(memoryID, startAddress + readLength)) {
			validDumps++;
		} 
	}

	request.setMessageReadPosition(position);
	
	message.appendUint16(validDumps);
	
	for (std::size_t j = 0; j < iterationCount; j++) {
		uint64_t startAddress = request.readUint64();

		uint16_t readLength = request.readUint16();

		if (d_memory_manager_handler->addressValidator(memoryID, startAddress) &&
		    d_memory_manager_handler->addressValidator(memoryID, startAddress + readLength)) {
			MessageArray dumpData = d_memory_manager_handler->dump(memoryID, startAddress, readLength);

			message.appendUint64(startAddress);
			message.appendUint16(readLength);
			message.appendUint8Array(dumpData);
			message.appendUint16(CRCHelper::calculateMessageCRC(dumpData));
		} else {
			reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AddressOutOfRange);
		}
	}

	d_message_parser->closeMessage(message);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));

        counters[MemoryManagementService::MessageType::DumpRawMemoryDataReport]++;
	
	reportSuccessCompletionExecutionVerification(request);
    }

    void MemoryManagementService_impl::checkRawData(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			MemoryManagementService::MessageType::CheckRawMemoryData)) {
		return;
	}

	
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (MEM_MNG_ID + MEM_MNG_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
 	tcSize -= MEM_MNG_ID + MEM_MNG_SIZE;
	
	uint8_t readEnum8 = request.readEnum8();
	
	uint16_t iterationCount = request.readUint16();
	
	if(tcSize != iterationCount * (MEM_MNG_START_ADDR + MEM_MNG_LENGTH)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	
	
	reportSuccessAcceptanceVerification(request);
	
	if(readEnum8 >= MemoryManager::MemoryID::END)
	{
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::undefinedMemory);
		return;
	}

	auto memoryID = static_cast<MemoryManager::MemoryID>(readEnum8);
	
	reportSuccessStartExecutionVerification(request);
		
        Message message = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			MemoryManagementService::MessageType::CheckRawMemoryDataReport, 
			counters[MemoryManagementService::MessageType::CheckRawMemoryDataReport], 0);
	
	message.appendEnum8(readEnum8);

	uint16_t position = request.getMessageReadPosition();
	uint16_t validDumps = 0;
	for (std::size_t j = 0; j < iterationCount; j++) {
		uint64_t startAddress = request.readUint64();

		uint16_t readLength = request.readUint16();

		if (d_memory_manager_handler->addressValidator(memoryID, startAddress) &&
		    d_memory_manager_handler->addressValidator(memoryID, startAddress + readLength)) {
			validDumps++;
		} 
	}

	request.setMessageReadPosition(position);
	
	message.appendUint16(validDumps);

	for (std::size_t j = 0; j < iterationCount; j++) {
		uint64_t startAddress = request.readUint64();

		uint16_t readLength = request.readUint16();

		if (d_memory_manager_handler->addressValidator(memoryID, startAddress) &&
		    d_memory_manager_handler->addressValidator(memoryID, startAddress + readLength)) {
			MessageArray dumpData = d_memory_manager_handler->dump(memoryID, startAddress, readLength);

			message.appendUint64(startAddress);
			message.appendUint16(readLength);
			message.appendUint16(CRCHelper::calculateMessageCRC(dumpData));
		} else {
			reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AddressOutOfRange);
		}
	}
	
	d_message_parser->closeMessage(message);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(message.getMessageData().size(), message.getMessageRawData())));

        counters[MemoryManagementService::MessageType::CheckRawMemoryDataReport]++;
	
	reportSuccessCompletionExecutionVerification(request);	
    }     
  } /* namespace pus */
} /* namespace gr */
