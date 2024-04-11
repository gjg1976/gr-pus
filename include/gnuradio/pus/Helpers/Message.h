/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef INCLUDED_PUS_MESSAGE_H
#define INCLUDED_PUS_MESSAGE_H

#include <vector>
#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Definitions/macros.h>
#include <gnuradio/pus/Time/TimeGetter.h>
#include <gnuradio/pus/Helpers/CRCHelper.h>
#include <etl/string.h>
#include <iostream>

/**
 * A telemetry (TM) or telecommand (TC) message (request/report), as specified in ECSS-E-ST-70-41C
 *
 * @todo Make sure that a message can't be written to or read from at the same time, or make
 *       readable and writable message different classes
 */
 namespace gr {
  namespace pus {
  
   class Message {
     private:
	MessageArray messageArray;

	uint16_t messageReadPosition = 0;
    
     public:
	enum PacketType {
		TM = 0, ///< Telemetry
		TC = 1  ///< Telecommand
	};
        
        Message();
        Message(MessageArray& inMessageData);
        ~Message();
						
	void setMessageReadPosition(uint16_t position) { messageReadPosition = position;};
	uint16_t getMessageReadPosition() { return messageReadPosition;};
	uint16_t getMessageSize() { return messageArray.size();};
			
	uint8_t  getMessageVersion() { return (messageArray.size() >= CCSDSPrimaryHeaderSize) ? messageArray[0] >> 5 : 0; };
	enum     PacketType getMessagePacketType() {
			if (messageArray.size() >= CCSDSPrimaryHeaderSize) 
				return ((messageArray[0] & 0x10) == 0) ? Message::TM : Message::TC;
			else
				return Message::TM; 
			};
	bool     getMessageSecondaryHeaderFlag() { 
			if (messageArray.size() >= CCSDSPrimaryHeaderSize) 
				return (messageArray[0] & 0x08) ;
			else
				return false; 
			};

	uint16_t getMessageApplicationId() { return (messageArray.size() >= CCSDSPrimaryHeaderSize) ? 
						((messageArray[0] << 8) | messageArray[1]) & static_cast<uint16_t>(0x07ff) : 0; };
	uint8_t  getMessageSequenceFlags() { return static_cast<uint8_t>(((messageArray[2] << 8) | messageArray[3]) >> 14); };
	uint16_t getMessagePacketSequenceCount() { return (messageArray.size() >= CCSDSPrimaryHeaderSize) ? 
						(((messageArray[2] << 8) | messageArray[3]) & (~0xc000U)) : 0; };

	uint16_t getMessagePacketDataLength() { return (messageArray.size() >= CCSDSPrimaryHeaderSize) ? (messageArray[4] << 8) | messageArray[5] : 0;};

	// 7.4.3.1 Telemetry packet secondary header / 7.4.4.1 Telecommand packet secondary header
	uint8_t  getMessagePUSVersion() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						messageArray[6] >> 4 : 0; };
	void     setMessagePUSVersion();

	uint8_t  getMessageSCTimeRef() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						messageArray[6] & 0x0f : 0; };
	uint8_t  getMessageAckFlags() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						messageArray[6] & 0x0f : 0; };
	// The service and message IDs are 8 bits (5.3.1b, 5.3.3.1d)
	uint8_t  getMessageServiceType() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						messageArray[7] : 0; };
	void     setMessageServiceType(uint8_t serviceType);	
					
	uint8_t  getMessageType() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						messageArray[8] : 0; };
        void     setMessageType(uint8_t messageType);
        
	//> 7.4.3.1b
	uint16_t getMessageTypeCounter() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						(messageArray[9] << 8) | messageArray[10] : 0; };
	uint16_t getMessageDestinationId() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						(messageArray[11] << 8) + messageArray[12] : 0; };
	uint16_t getMessageSourceId() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize) ? 
						(messageArray[9] << 8) + messageArray[10] : 0; };

	uint16_t getMessageCRC() { return (messageArray.size() >= CCSDSPrimaryHeaderSize+ECSSSecondaryTCHeaderSize+ECSSSecondaryTCCRCSize) ? 
						(messageArray[messageArray.size()-2] << 8) + messageArray[messageArray.size()-1] : 0; };
							
	MessageArray& getMessageData() { return messageArray; };
	uint8_t* getMessageRawData() { return messageArray.data(); };
      	void setMessageData(MessageArray& inMessageData);
	
	/**
	 * Compare the message type to an expected one. An unexpected message type will throw an
	 * OtherMessageType error.
	 *
	 * @return True if the message is of correct type, false if not
	 */
	bool assertType(Message::PacketType expectedPacketType, uint8_t expectedServiceType, uint8_t expectedMessageType);
	/**
	 * Alias for Message::assertType(Message::TC, \p expectedServiceType, \p
	 * expectedMessageType)
	 */
	bool assertTC(uint8_t expectedServiceType, uint8_t expectedMessageType)  {
		return assertType(TC, expectedServiceType, expectedMessageType);
	}

	/**
	 * Alias for Message::assertType(Message::TM, \p expectedServiceType, \p
	 * expectedMessageType)
	 */
	bool assertTM(uint8_t expectedServiceType, uint8_t expectedMessageType)  {
		return assertType(TM, expectedServiceType, expectedMessageType);
	}
	
	bool readString(std::string& string, uint16_t maxChars); ///// REVISAR ***************************************************
	bool readString(std::string& string); ///// REVISAR ***************************************************
		
	bool readArray(uint8_t* array, uint16_t size);
	
	MessageArray readMessageArray(uint16_t size);	
	
	/**
	 * Fetches a single-byte boolean value from the current position in the message
	 *
	 * PTC = 1, PFC = 0
	 */
	bool readBoolean() {
		return static_cast<bool>(readByte());
	}

	/**
	 * Fetches an enumerated parameter consisting of 1 byte from the current position in the message
	 *
	 * PTC = 2, PFC = 8
	 */
	uint8_t readEnum8() {
		return readByte();
	}

	/**
	 * Fetches an enumerated parameter consisting of 2 bytes from the current position in the
	 * message
	 *
	 * PTC = 2, PFC = 16
	 */
	uint16_t readEnum16() {
		return readHalfword();
	}

	/**
	 * Fetches an enumerated parameter consisting of 4 bytes from the current position in the
	 * message
	 *
	 * PTC = 2, PFC = 32
	 */
	uint32_t readEnum32() {
		return readWord();
	}

	/**
	 * Fetches an 1-byte unsigned integer from the current position in the message
	 *
	 * PTC = 3, PFC = 4
	 */
	uint8_t readUint8() {
		return readByte();
	}

	/**
	 * Fetches a 2-byte unsigned integer from the current position in the message
	 *
	 * PTC = 3, PFC = 8
	 */
	uint16_t readUint16() {
		return readHalfword();
	}

	/**
	 * Fetches a 4-byte unsigned integer from the current position in the message
	 *
	 * PTC = 3, PFC = 14
	 */
	uint32_t readUint32() {
		return readWord();
	}

	/**
	 * Fetches an 8-byte unsigned integer from the current position in the message
	 *
	 * PTC = 3, PFC = 16
	 */
	uint64_t readUint64() {
		return (static_cast<uint64_t>(readWord()) << 32) | static_cast<uint64_t>(readWord()); // NOLINT(cppcoreguidelines-avoid-magic-numbers)
	}

	/**
	 * Fetches an 1-byte signed integer from the current position in the message
	 *
	 * PTC = 4, PFC = 4
	 */
	int8_t readSint8() {
		uint8_t value = readByte();
		return reinterpret_cast<int8_t&>(value);
	}

	/**
	 * Fetches a 2-byte unsigned integer from the current position in the message
	 *
	 * PTC = 4, PFC = 8
	 */
	int16_t readSint16() {
		uint16_t value = readHalfword();
		return reinterpret_cast<int16_t&>(value);
	}

	/**
	 * Fetches a 4-byte unsigned integer from the current position in the message
	 *
	 * PTC = 4, PFC = 14
	 */
	int32_t readSint32() {
		uint32_t value = readWord();
		return reinterpret_cast<int32_t&>(value);
	}

	/**
	 * Fetches a 4-byte unsigned integer from the current position in the message
	 *
	 * PTC = 4, PFC = 14
	 */
	int64_t readSint64() {
		uint64_t value = readUint64();
		return reinterpret_cast<int64_t&>(value);
	}

	/**
	 * Fetches an 4-byte single-precision floating point number from the current position in the
	 * message
	 *
	 * @todo (#247) Check if endianness matters for this
	 *
	 * PTC = 5, PFC = 1
	 */
	float readFloat() {
		static_assert(sizeof(uint32_t) == sizeof(float), "Floating point numbers must be 32 bits long");

		uint32_t value = readWord();
		return reinterpret_cast<float&>(value);
	}

	double readDouble() {
		static_assert(sizeof(uint64_t) == sizeof(double), "Double numbers must be 64 bits long");

		uint64_t value = readUint64();
		return reinterpret_cast<double&>(value);
	}	

	/**
	 * Reads the next \p size bytes from the message, and stores them into the allocated \p string
	 *
	 * NOTE: We assume that \p string is already allocated, and its size is at least
	 * ECSSMaxStringSize. This function does NOT place a \0 at the end of the created string.
	 */
	void readString(char* string, uint16_t size);

	/**
	 * Reads the next \p size bytes from the message, and stores them into the allocated \p string
	 *
	 * NOTE: We assume that \p string is already allocated, and its size is at least
	 * ECSSMaxStringSize. This function does NOT place a \0 at the end of the created string
	 * @todo (#246) Is uint16_t size too much or not enough? It has to be defined
	 */
	void readString(uint8_t* string, uint16_t size);
		
	/**
	 * Fetches a N-byte string from the current position in the message
	 *
	 * In the current implementation we assume that a preallocated array of sufficient size
	 * is provided as the argument. This does NOT append a trailing `\0` to \p byteString.
	 * @todo (#248) Specify if the provided array size is too small or too large
	 *
	 * PTC = 7, PFC = 0
	 */
	uint16_t readOctetString(uint8_t* byteString) {
		uint16_t const size = readUint16(); // Get the data length from the message

		readString(byteString, size);       // Read the string data

		return size; // Return the string size
	}

	/**
	 * Fetches an N-byte string from the current position in the message. The string can be at most MAX_SIZE long.
	 *
	 * @note This function was not implemented as Message::read() due to an inherent C++ limitation, see
	 * https://www.fluentcpp.com/2017/08/15/function-templates-partial-specialization-cpp/
	 * @tparam MAX_SIZE The memory size of the string in bytes, which corresponds to the max string size
	 */
	template <const size_t MAX_SIZE>
	etl::string<MAX_SIZE> readOctetString() {
		etl::string<MAX_SIZE> string("");

		uint16_t length = readUint16();
		if((messageReadPosition + length) > messageArray.size()){
			messageReadPosition = messageArray.size();
			return string;
		}
		if(length > ECSSMaxStringSize){
			messageReadPosition += length;
			return string; 
		}
		string.assign(messageArray.begin() + messageReadPosition, messageArray.begin() + messageReadPosition + length);
		messageReadPosition += length;
		return string;
	}
	/**
	 * Reads the next 1 byte from the message
	 */	
	MessageArray readMessageSubData(uint16_t start, uint16_t end);
/******************************************************************************************************************/	

	/**
	 * Reads the next 1 byte from the message
	 */
	uint8_t readByte();

	/**
	 * Reads the next 2 bytes from the message
	 */
	uint16_t readHalfword();

	/**
	 * Reads the next 4 bytes from the message
	 */
	uint32_t readWord();
/******************************************************************************************************************/	

	/**
	 * Appends a default timestamp object to the message, without the header
	 */
	void appendDefaultCUCTimeStamp(Time::DefaultCUC& timestamp) {
		static_assert(std::is_same_v<uint32_t, decltype(timestamp.formatAsBytes())>, "The conan-profile timestamp should be 4 bytes");
		appendUint32(timestamp.formatAsBytes());
/*		etl::array<uint8_t, Time::CUCTimestampMaximumSize> timeStap = timestamp.formatAsCUC();

		for(size_t i = 0; i < timeStap.size(); i++){
			if(messageReadPosition >= messageArray.size())
				messageArray.push_back(timeStap[i]); 
			else
				messageArray[messageReadPosition] = timeStap[i];
			messageReadPosition++;
		}
*/
	}
	void appendData(Time::DefaultCUC& value)
	{
		appendDefaultCUCTimeStamp(value);
	}	
/******************************************************************************************************************/	
	void appendString(std::string& string, uint16_t maxChars);///// REVISAR ***************************************************
	/**
	 * Appends a number of bytes to the message
	 *
	 * Note that this doesn't append the number of bytes that the string contains. For this, you
	 * need to use a function like Message::appendOctetString(), or have specified the size of the
	 * string beforehand. Note that the standard does not support null-terminated strings.
	 *
	 * This does not append the full size of the string, just its current size. Use
	 * Message::appendFixedString() to have a constant number of characters added.
	 *
	 * @param string The string to insert
	 */
	void appendString(const etl::istring& string);
	
	
	/**
	 * Appends a number of bytes to the message
	 *
	 * Note that this doesn't append the number of bytes that the string contains. For this, you
	 * need to use a function like Message::appendOctetString(), or have specified the size of the
	 * string beforehand. Note that the standard does not support null-terminated strings.
	 *
	 * The number of bytes appended is equal to \p SIZE. To append variable-sized parameters, use
	 * Message::appendString() instead. Missing bytes are padded with zeros, until the length of SIZE
	 * is reached.
	 *
	 * @param string The string to insert
	 */
	void appendFixedString(const etl::istring& string);

	/**
	 * Appends a byte array to the message
	 */
	void appendUint8Array(MessageArray& value);
	void appendUint8Array(uint8_t* value, size_t size);		
	/**
	 * Appends 1 byte to the message
	 */
	void appendByte(uint8_t value);

	/**
	 * Appends 2 bytes to the message
	 */
	void appendHalfword(uint16_t value);

	/**
	 * Appends 4 bytes to the message
	 */
	void appendWord(uint32_t value);
	
	
	
	
/******************************************************************************************************************/		
	
	/**
	 * Adds a single-byte boolean value to the end of the message
	 *
	 * PTC = 1, PFC = 0
	 */
	void appendBoolean(bool value) {
		return appendByte(static_cast<uint8_t>(value));
	}

	/**
	 * Adds an enumerated parameter consisting of 1 byte to the end of the message
	 *
	 * PTC = 2, PFC = 8
	 */
	void appendEnum8(uint8_t value) {
		return appendByte(value);
	};

	/**
	 * Adds an enumerated parameter consisting of 2 bytes to the end of the message
	 *
	 * PTC = 2, PFC = 16
	 */
	void appendEnum16(uint16_t value) {
		return appendHalfword(value);
	}

	/**
	 * Adds an enumerated parameter consisting of 4 bytes to the end of the message
	 *
	 * PTC = 2, PFC = 32
	 */
	void appendEnum32(uint32_t value) {
		return appendWord(value);
	}

	/**
	 * Adds a 1 byte unsigned integer to the end of the message
	 *
	 * PTC = 3, PFC = 4
	 */
	void appendUint8(uint8_t value) {
		return appendByte(value);
	}

	/**
	 * Adds a 2 byte unsigned integer to the end of the message
	 *
	 * PTC = 3, PFC = 8
	 */
	void appendUint16(uint16_t value) {
		return appendHalfword(value);
	}

	/**
	 * Adds a 4 byte unsigned integer to the end of the message
	 *
	 * PTC = 3, PFC = 14
	 */
	void appendUint32(uint32_t value) {
		return appendWord(value);
	}

	/**
	 * Adds an 8 byte unsigned integer to the end of the message
	 *
	 * PTC = 3, PFC = 16
	 */
	void appendUint64(uint64_t value) {
		appendWord(static_cast<uint32_t>(value >> 32)); // NOLINT(cppcoreguidelines-avoid-magic-numbers)
		appendWord(static_cast<uint32_t>(value));
	}

	/**
	 * Adds a 1 byte signed integer to the end of the message
	 *
	 * PTC = 4, PFC = 4
	 */
	void appendSint8(int8_t value) {
		return appendByte(reinterpret_cast<uint8_t&>(value));
	}

	/**
	 * Adds a 2 byte signed integer to the end of the message
	 *
	 * PTC = 4, PFC = 8
	 */
	void appendSint16(int16_t value) {
		return appendHalfword(reinterpret_cast<uint16_t&>(value));
	}

	/**
	 * Adds a 4 byte signed integer to the end of the message
	 *
	 * PTC = 4, PFC = 14
	 */
	void appendSint32(int32_t value) {
		return appendWord(reinterpret_cast<uint32_t&>(value));
	}


	/**
	 * Adds a 8 byte signed integer to the end of the message
	 *
	 * PTC = 4, PFC = 16
	 */
	void appendSint64(int64_t value) {
		return appendUint64(reinterpret_cast<uint64_t&>(value));
	}

	/**
	 * Adds an 8 byte time Offset to the message
	 */
	void appendRelativeTime(Time::RelativeTime value) {
		return appendSint64(value);
	}

	/**
	 * Adds a 4-byte single-precision floating point number to the end of the message
	 *
	 * PTC = 5, PFC = 1
	 */
	void appendFloat(float value) {
		static_assert(sizeof(uint32_t) == sizeof(value), "Floating point numbers must be 32 bits long");

		return appendWord(reinterpret_cast<uint32_t&>(value));
	}

	/**
	 * Adds a double to the end of the message
	 */
	void appendDouble(double value) {
		static_assert(sizeof(uint64_t) == sizeof(value), "Double numbers must be 64 bits long");

		return appendUint64(reinterpret_cast<uint64_t&>(value));
	}		
	/**
	 * Adds a N-byte string to the end of the message
	 *
	 *
	 * PTC = 7, PFC = 0
	 */
	void appendOctetString(const etl::istring& string);	
   };

  } // namespace pus
} // namespace gr
#endif // INCLUDED_PUS_MESSAGE_H
