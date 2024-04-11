/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 
#include <gnuradio/pus/Helpers/Message.h>
#include <cstring>
#include <iostream>

namespace gr {
  namespace pus {

    /*
     * The public constructors
     */
    Message::Message()
    {
	messageArray.clear();
    }
    
    Message::Message(MessageArray& inMessageData): Message()
    {
	messageArray.clear();
	messageArray = inMessageData; 
    }

    void Message::setMessageData(MessageArray& inMessageData)  /// REMOVE
    {
	messageArray.clear();
	messageArray = inMessageData; 
    }
        
    Message::~Message()
    {
	messageArray.clear();
    }
    
    bool Message::assertType(Message::PacketType expectedPacketType, uint8_t expectedServiceType, uint8_t expectedMessageType) 
    {
	bool status = true;

	if ((getMessagePacketType() != expectedPacketType) || (getMessageServiceType() != expectedServiceType) ||
		    (getMessageType() != expectedMessageType)) {
		status = false;
	}

	return status;
    }
    
    void Message::setMessagePUSVersion()
    {
      if(messageArray.size() >= ECSSSecondaryTMHeaderSize)
      		messageArray[0] = ECSSPUSVersion << 4U;
    }    

    void Message::setMessageServiceType(uint8_t serviceType)
    {
      if(messageArray.size() >= ECSSSecondaryTMHeaderSize)
      		messageArray[1] = serviceType;
    }  
    
    void Message::setMessageType(uint8_t messageType)
    {
      if(messageArray.size() >= ECSSSecondaryTMHeaderSize)
      		messageArray[2] = messageType;
    } 

    bool Message::readString(std::string& string, uint16_t maxChars) { ///// REVISAR ***************************************************
	std::vector<uint8_t> p;
	
	uint16_t i = 0;
	
	for(; i < maxChars; i++, messageReadPosition++){
		if(messageArray[messageReadPosition] == 0)
			break;
		p.push_back(messageArray[messageReadPosition]);
	}
	messageReadPosition += maxChars - i;

	string.assign(p.begin(), p.end());
	return true;
    }  
    bool Message::readString(std::string& string) {     ///// REVISAR ***************************************************
	
	uint16_t i = readUint16();
		
	if(messageReadPosition + i > messageArray.size()){
		return false; 
	}	
	return readString(string, i);
    }  
    
    bool Message::readArray(uint8_t* array, uint16_t size) {
	if((messageReadPosition + size) > messageArray.size()){
		return false; 
	}
	for(uint16_t i = 0; i < size; i++)
		array[i] = readUint8();

	return true;
	
    }
    
MessageArray Message::readMessageArray(uint16_t size){
	MessageArray byteArray;
	
	if((messageReadPosition + size) < messageArray.size() and size < ECSSMaxMessageSize){
		for(uint16_t i = 0; i < size; i++)
			byteArray.push_back(readUint8());
	}
	return byteArray;
}

/******************************************************************************************************************/

uint8_t Message::readByte() {
	uint8_t value = 0;
	
	if(messageReadPosition < messageArray.size() + 1){
		value = messageArray[messageReadPosition];
		messageReadPosition += 1;
	}
	return value;
}

    uint16_t Message::readHalfword() {
	uint16_t value = 0;
	
	if((messageReadPosition + 2) < messageArray.size() + 1){
		value = (messageArray[messageReadPosition] << 8) | messageArray[messageReadPosition + 1]; 
		messageReadPosition += 2;
	}
	return value;
    }
    
    uint32_t Message::readWord() {
	uint32_t value = 0;
	
	if((messageReadPosition + 4) < messageArray.size() + 1){
		value =  (messageArray[messageReadPosition] << 24) | (messageArray[messageReadPosition + 1] << 16) |
			 (messageArray[messageReadPosition + 2] << 8) | messageArray[messageReadPosition + 3];
		messageReadPosition += 4;
	}
	return value;
    }    


/******************************************************************************************************************/
    void Message::readString(char* string, uint16_t size) {
	if((messageReadPosition + size) > messageArray.size()){
		return; 
	}
	if(size < ECSSMaxStringSize){
		return; 
	}
	std::copy(messageArray.begin() + messageReadPosition, messageArray.begin() + messageReadPosition + size, string);
	messageReadPosition += size;
    }
    
    void Message::readString(uint8_t* string, uint16_t size) {
	if((messageReadPosition + size) > messageArray.size()){
		return; 
	}
	if(size < ECSSMaxStringSize){
		return; 
	}
	std::copy(messageArray.begin() + messageReadPosition, messageArray.begin() + messageReadPosition + size, string);
	messageReadPosition += size;
    }

    void Message::appendString(const etl::istring& string) {
	for(auto chr: string)
		appendUint8(static_cast<uint8_t>(chr));
    }

    void Message::appendOctetString(const etl::istring& string) {
	// Make sure that the string is large enough to count
	if(string.size() > (std::numeric_limits<uint16_t>::max)())
		return;

	appendUint16(string.size());
	appendString(string);
    }

    void Message::appendFixedString(const etl::istring& string) {
	for(auto chr: string)
		appendByte(static_cast<uint8_t>(chr));
    }

/******************************************************************************************************************/
void Message::appendByte(uint8_t value) {
	if(messageReadPosition >= messageArray.size())
		messageArray.push_back(value); 
	else
		messageArray[messageReadPosition] = value;
	messageReadPosition++;
}

void Message::appendHalfword(uint16_t value) {
	appendByte(static_cast<uint8_t>((value >> 8) & 0xFF));
	appendByte(static_cast<uint8_t>(value & 0xFF));
}

void Message::appendWord(uint32_t value) {
	appendByte(static_cast<uint8_t>((value >> 24) & 0xFF));
	appendByte(static_cast<uint8_t>((value >> 16) & 0xFF));
	appendByte(static_cast<uint8_t>((value >> 8) & 0xFF));
	appendByte(static_cast<uint8_t>(value & 0xFF));
}


MessageArray Message::readMessageSubData(uint16_t start, uint16_t end){
	MessageArray subdata;
	
	if(end >= messageArray.size()){
		end = messageArray.size() - 1; 
	}
	
	subdata.insert(subdata.end(), messageArray.begin() + start, messageArray.begin() + end);
	
	messageReadPosition = end;
	
	return subdata;
}
    
    
/******************************************************************************************************************/

    void Message::appendString(std::string& string, uint16_t maxChars) {///// REVISAR ***************************************************
	std::vector<uint8_t> p(string.begin(), string.end());
	uint8_t zero = 0;
	
	for(uint16_t i = p.size(); i < maxChars; i++){
		p.push_back(zero);
	}
	
	appendUint8Array(p.data(), p.size());
    }

    void Message::appendUint8Array(MessageArray& value) {
	for(size_t i = 0; i < value.size(); i++){
		if(messageReadPosition >= messageArray.size())
			messageArray.push_back(value[i]); 
		else
			messageArray[messageReadPosition] = value[i];
		messageReadPosition++;
	}
    } 

    void Message::appendUint8Array(uint8_t* value, size_t size) {
	for(size_t i = 0; i < size; i++){
		if(messageReadPosition >= messageArray.size())
			messageArray.push_back(value[i]); 
		else
			messageArray[messageReadPosition] = value[i];
		messageReadPosition++;
	}
    } 

  } /* namespace pus */
} /* namespace gr */

