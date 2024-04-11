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
#include <gnuradio/pus/Helpers/MessageParser.h>

namespace gr {
  namespace pus {

    MessageParser* MessageParser::inst_messageparser = NULL;
    
    MessageParser::MessageParser() 
    {
    }
    
    MessageParser* MessageParser::getInstance()
    {
       if(inst_messageparser == NULL)
           inst_messageparser = new MessageParser();
       
       return inst_messageparser;
    }
    
    /*
     * The private constructor
     */
    bool MessageParser::config(uint16_t apid, bool crc_enable)
    {
    	d_apid = apid;
    	d_crc_enable = crc_enable;
    	d_counter = 0;
        
    	d_timeprovider = TimeProvider::getInstance();

    	return true;    
    }

/*****************************************************************************************************************/

    Message MessageParser::ParseMessageCommand(MessageArray& in_data) 
    {
    	if(in_data.size() <= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize)
    	    return Message();
    	    
    	Message message = Message(in_data);
    	
	message.setMessageReadPosition(CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize);
	
	return message;
    }

    Message MessageParser::CreateMessageReport(uint8_t scTimeRef, uint8_t serviceType, 
			uint8_t messageType, uint16_t messageTypeCounter,
			uint16_t destinationId, MessageArray& payload) 
    {
	Message message = CreateMessageReport(d_apid, d_counter, scTimeRef, serviceType, 
			messageType, messageTypeCounter, destinationId, payload); 	
	counter_inc();
	
	return message;
    }

    Message MessageParser::CreateEmptyMessageReport(uint8_t scTimeRef, uint8_t serviceType, 
			uint8_t messageType, uint16_t messageTypeCounter,
			uint16_t destinationId) 
    {
	MessageArray data;
	etl::vector<uint8_t, ECSSMaxTimeField> stamp = TimeProvider::getInstance()->getCurrentTimeStamp();
	
        // Parts of the header
	uint16_t packetId = d_apid;
	packetId |= (1U << 11U);                                              // Secondary header flag
	packetId |= (0U); // Ignore-MISRA
	uint16_t packetSequenceControl = d_counter | (3U << 14U);
	uint16_t packetDataLength = stamp.size() + ECSSSecondaryTMHeaderSize - 1;

	if (packetDataLength > CCSDSMaxMessageSize) {
		Message empty_message = Message();
		return empty_message;
	}

	data.resize(CCSDSPrimaryHeaderSize + packetDataLength + 1);
	
	// Compile the header
	data[0] = packetId >> 8U;
	data[1] = packetId & 0xffU;
	data[2] = packetSequenceControl >> 8U;
	data[3] = packetSequenceControl & 0xffU;
	data[4] = packetDataLength >> 8U;
	data[5] = packetDataLength & 0xffU;

	// Sanity check that there is enough space for the string
	//ASSERT_INTERNAL((ecssMessage.size() + CCSDSPrimaryHeaderSize) <= CCSDSMaxMessageSize, ErrorHandler::StringTooLarge);

	data[CCSDSPrimaryHeaderSize+0] = ECSSPUSVersion << 4U; // Assign the pusVersion = 2
	data[CCSDSPrimaryHeaderSize+0] |= scTimeRef & 0x0FU;                 // Spacecraft time reference status
	data[CCSDSPrimaryHeaderSize+1] = serviceType;
	data[CCSDSPrimaryHeaderSize+2] = messageType;
	data[CCSDSPrimaryHeaderSize+3] = static_cast<uint8_t>(messageTypeCounter >> 8U);
	data[CCSDSPrimaryHeaderSize+4] = static_cast<uint8_t>(messageTypeCounter & 0xffU);
	data[CCSDSPrimaryHeaderSize+5] = destinationId >> 8U; // DestinationID
	data[CCSDSPrimaryHeaderSize+6] = destinationId;
	
	for(size_t i = 0; i < stamp.size(); i++)
		data[CCSDSPrimaryHeaderSize + 7 + i] = stamp[i];

	Message message = Message(data);
	
	message.setMessageReadPosition(data.size());
	
	counter_inc();
	
	return message;
    }
    
    Message MessageParser::CreateMessageReport(uint16_t apid,
    			uint16_t packetSequenceCounter, uint8_t scTimeRef, uint8_t serviceType, 
			uint8_t messageType, uint16_t messageTypeCounter,
			uint16_t destinationId, MessageArray& payload) 
    {
	MessageArray data;
	etl::vector<uint8_t, ECSSMaxTimeField> stamp = TimeProvider::getInstance()->getCurrentTimeStamp();
	
        // Parts of the header
	uint16_t packetId = apid;
	packetId |= (1U << 11U);                                              // Secondary header flag
	packetId |= (0U); // Ignore-MISRA
	uint16_t packetSequenceControl = packetSequenceCounter | (3U << 14U);
	uint16_t packetDataLength = stamp.size() + payload.size() - 1;
	packetDataLength += ECSSSecondaryTMHeaderSize; 

	if (packetDataLength > CCSDSMaxMessageSize) {
		Message empty_message = Message();
		return empty_message;
	}
	
	data.resize(CCSDSPrimaryHeaderSize + packetDataLength + 1);

	packetDataLength += (d_crc_enable) ? 2 : 0;		
	// Compile the header
	data[0] = packetId >> 8U;
	data[1] = packetId & 0xffU;
	data[2] = packetSequenceControl >> 8U;
	data[3] = packetSequenceControl & 0xffU;
	data[4] = packetDataLength >> 8U;
	data[5] = packetDataLength & 0xffU;

	// Sanity check that there is enough space for the string
	//ASSERT_INTERNAL((ecssMessage.size() + CCSDSPrimaryHeaderSize) <= CCSDSMaxMessageSize, ErrorHandler::StringTooLarge);

	data[CCSDSPrimaryHeaderSize+0] = ECSSPUSVersion << 4U; // Assign the pusVersion = 2
	data[CCSDSPrimaryHeaderSize+0] |= scTimeRef & 0x0FU;                 // Spacecraft time reference status
	data[CCSDSPrimaryHeaderSize+1] = serviceType;
	data[CCSDSPrimaryHeaderSize+2] = messageType;
	data[CCSDSPrimaryHeaderSize+3] = static_cast<uint8_t>(messageTypeCounter >> 8U);
	data[CCSDSPrimaryHeaderSize+4] = static_cast<uint8_t>(messageTypeCounter & 0xffU);
	data[CCSDSPrimaryHeaderSize+5] = destinationId >> 8U; // DestinationID
	data[CCSDSPrimaryHeaderSize+6] = destinationId;

	for(size_t i = 0; i < stamp.size(); i++)
		data[CCSDSPrimaryHeaderSize + 7 + i] = stamp[i];
	
	for(size_t i = 0; i < payload.size(); i++)
		data[CCSDSPrimaryHeaderSize + ECSSSecondaryTMHeaderSize + stamp.size() + i] = payload[i];
		
	if(d_crc_enable){
		// Append CRC field
		uint16_t crcField = CRCHelper::calculateMessageCRC(data);
		data.push_back(static_cast<uint8_t>(crcField >> 8U));
		data.push_back(static_cast<uint8_t>(crcField & 0xFF));
	}
	
	Message message = Message(data);
	
	message.setMessageReadPosition(data.size());
	
	return message;
    }
    
    void MessageParser::closeMessage(Message& message)
    {

	uint16_t packetDataLength = message.getMessageSize() - 1;
	 
	packetDataLength -= CCSDSPrimaryHeaderSize;
	packetDataLength += (d_crc_enable) ? 2 : 0;		
	message.setMessageReadPosition(4);
	message.appendUint16(packetDataLength);	

  	if(d_crc_enable){
		// Append CRC field
		uint16_t crcField = CRCHelper::calculateMessageCRC(message.getMessageData());
		message.setMessageReadPosition(message.getMessageSize());
		message.appendUint16(crcField);
	}  
    }	
    
   MessageArray MessageParser::parseTCfromMessage(Message& message)
    {
 	uint16_t startPosition = message.getMessageReadPosition();
	uint16_t endPosition = startPosition;
	
	uint16_t dummy = message.readUint16();
	dummy = message.readUint16();
	
	uint16_t pkt_size = message.readUint16() & (~0xc000U);
	
	endPosition += pkt_size + 1 + CCSDSPrimaryHeaderSize;

 	return message.readMessageSubData(startPosition, endPosition);   
    }   

    MessageArray MessageParser::parseUpToEndfromMessage(Message& message)
    {
 	uint16_t startPosition = message.getMessageReadPosition();
	uint16_t endPosition = message.getMessageSize() - ECSSSecondaryTCCRCSize;

 	return message.readMessageSubData(startPosition, endPosition);   	   
    }     
  } /* namespace pus */
} /* namespace gr */
