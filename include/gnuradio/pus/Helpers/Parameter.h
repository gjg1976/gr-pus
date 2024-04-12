/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_PARAMETER_HPP
#define ECSS_PARAMETER_HPP

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Helpers/Message.h>
#include <typeinfo>
#include <iostream>
 namespace gr {
  namespace pus {


template <typename T>
inline std::vector<uint8_t> append(T& value) {
	return append(std::underlying_type_t<T>(value));
}

template <typename T>
inline void append(Message& message, T& value) {
	append(std::underlying_type_t<T>(value));
}

template <typename T>
inline T read(Message& message) {
	return static_cast<T>(read<std::underlying_type_t<T>>());
}

template <typename T>
inline T read(std::vector<uint8_t> message) {
	return static_cast<T>(read<std::underlying_type_t<T>>());
}

/**
 * Implementation of a Parameter field, as specified in ECSS-E-ST-70-41C.
 *
 * @author Gustavo Gonzalez, modified version of Grigoris Pavlakis <grigpavl@ece.auth.gr>
 * @author and Athanasios Theocharis <athatheoc@gmail.com> implementation
 *
 * @section Introduction
 * The Parameter class implements a way of storing and updating system parameters
 * of arbitrary size and type, for GNURadio implementation, we used dynamic memory 
 * allocation.
 * It is split in two distinct parts:
 * 1) an abstract \ref ParameterBase class which provides a
 * common data type used to create any pointers to \ref Parameter objects, as well as
 * virtual functions for accessing the parameter's data part, and
 * 2) a templated \ref Parameter used to store any type-specific parameter information,
 * such as the actual data field where the parameter's value will be stored.
 *
 * @section Architecture Rationale
 * The ST[20] Parameter service is implemented with the need of arbitrary type storage
 * in mind, for GNURadio implementation we use of dynamic memory allocation, the requirement
 * of not used it is based on memory fragmentation avoidance, this implementation is mainly
 * for used in turn on/off instruments or units
 * Furthermore, the \ref ParameterService should provide ID-based access to parameters.
 */
class ParameterBase {
public:

	/**
	 * Given an ECSS message that contains this parameter as its first input, this loads the value from that parameter
	 */
	virtual std::vector<uint8_t> appendValueToVector() = 0;
	virtual void appendValueToMessage(Message& message) = 0;

	/**
	 * Appends the parameter as an ECSS value to an ECSS Message
	 */
	virtual void setValueFromVector(std::vector<uint8_t>& message) = 0;	
	virtual void setValueFromMessage(Message& message) = 0;
	
	/**
	 * Converts the value of a parameter to a double.
	 *
	 * Some precision may be lost in the process. If the value is not arithmetic,
	 * then usually 0 is returned.
	 */
	virtual double getValueAsDouble() = 0;
	
	virtual void appendValueAsTypeToMessage(double value, Message& message) = 0;

	virtual double getValueAsDoubleFromMessage(Message& message) = 0;

	virtual void appendValueAsTypeToVector(double d_value, std::vector<uint8_t>& vector) = 0;

	std::function<void(void*)> cbFunction;
};

/**
 * Implementation of a parameter containing its value. See \ref ParameterBase for more information.
 * @tparam DataType The type of the Parameter value. This is the type used for transmission and reception
 * as per the PUS.
 */
template <typename DataType>
class Parameter : public ParameterBase {
protected:
	DataType currentValue;
	
	DataType parseValue;
	
	inline void callback() {

		if (cbFunction){
			cbFunction(reinterpret_cast<void*>(&currentValue));

		}	
	}
public:
	explicit Parameter(DataType initialValue) : currentValue(initialValue) { }

	inline void setValue(DataType value) {
		currentValue = value;
		callback();
	}

	inline DataType getValue() {
		return currentValue;
	}
		
	inline double getValueAsDouble() override {
		if constexpr (std::is_arithmetic_v<DataType>) {
			return static_cast<double>(currentValue);
		} else {
			return 0;
		}
	}
	
	inline void setValueFromVector(std::vector<uint8_t>& message) override {
		currentValue = read<DataType>(message);
		callback();
	};

	inline void setValueFromMessage(Message& message) override {
		currentValue = read<DataType>(message);
		callback();
	};

	inline std::vector<uint8_t> appendValueToVector() override {
		return append<DataType>(currentValue);
	};
	inline void appendValueToMessage(Message& message) override {
		append<DataType>(message, currentValue);
	};
	
	inline void appendValueAsTypeToMessage(double d_value, Message& message) override {
		parseValue = (DataType)d_value;
		append<DataType>(message, parseValue);
	};

	inline void appendValueAsTypeToVector(double d_value, std::vector<uint8_t>& vector) override {
		parseValue = (DataType)d_value;
		std::vector<uint8_t> value = append<DataType>(parseValue);
		for(size_t i=0; i < value.size(); i++)
			vector.push_back(value[i]);

	};

	inline double getValueAsDoubleFromMessage(Message& message) override {
		parseValue = read<DataType>(message);
		if constexpr (std::is_arithmetic_v<DataType>) {
			return static_cast<double>(parseValue);
		} else {
			return 0;
		}
	};
};

template <>
inline void append(Message& message, uint8_t& value) {
	message.appendUint8(value);
}

template <>
inline void append(Message& message, uint16_t& value) {
	message.appendUint16(value);
}

template <>
inline void append(Message& message, uint32_t& value) {
	message.appendUint32(value);
}

template <>
inline void append(Message& message, uint64_t& value) {
	message.appendUint64(value);
}

template <>
inline void append(Message& message, int8_t& value) {
	message.appendByte(value);
}

template <>
inline void append(Message& message, int16_t& value) {
	message.appendSint16(value);
}

template <>
inline void append(Message& message, int32_t& value) {
	message.appendSint32(value);
}

template <>
inline void append(Message& message, bool& value) {
	message.appendBoolean(value);
}

template <>
inline void append(Message& message, char& value) {
	message.appendByte(value);
}

template <>
inline void append(Message& message, float& value) {
	message.appendFloat(value);
}

template <>
inline void append(Message& message, double& value) {
	message.appendDouble(value);
}

template <>
inline std::vector<uint8_t> append(uint8_t& value) {
	std::vector<uint8_t> message(1);
	message[0] = value;
	return message;
}

template <>
inline std::vector<uint8_t> append(uint16_t& value) {
	std::vector<uint8_t> message(2);
	message[0] = static_cast<uint8_t>((value >> 8) & 0xFF);
	message[1] = static_cast<uint8_t>(value & 0xFF);
	return message;
}

template <>
inline std::vector<uint8_t> append(uint32_t& value) {
	std::vector<uint8_t> message(4);
	message[0] = static_cast<uint8_t>((value >> 24) & 0xFF);
	message[1] = static_cast<uint8_t>((value >> 16) & 0xFF);
	message[2] = static_cast<uint8_t>((value >> 8) & 0xFF);
	message[3] = static_cast<uint8_t>(value & 0xFF);

	return message;
}
template <>
inline std::vector<uint8_t> append(uint64_t& value) {
	std::vector<uint8_t> message(8);
	message[0] = static_cast<uint8_t>((value >> 56) & 0xFF);
	message[1] = static_cast<uint8_t>((value >> 48) & 0xFF);
	message[2] = static_cast<uint8_t>((value >> 40) & 0xFF);
	message[3] = static_cast<uint8_t>((value >> 32) & 0xFF);
	message[4] = static_cast<uint8_t>((value >> 24) & 0xFF);
	message[5] = static_cast<uint8_t>((value >> 16) & 0xFF);
	message[6] = static_cast<uint8_t>((value >> 8) & 0xFF);
	message[7] = static_cast<uint8_t>(value & 0xFF);

	return message;
}

template <>
inline std::vector<uint8_t> append(int8_t& value) {
	std::vector<uint8_t> message(1);
	message[0] = value;
	return message;
}

template <>
inline std::vector<uint8_t> append(int16_t& value) {
	std::vector<uint8_t> message(2);
	message[0] = static_cast<uint8_t>((value >> 8) & 0xFF);
	message[1] = static_cast<uint8_t>(value & 0xFF);

	return message;
}

template <>
inline std::vector<uint8_t> append(int32_t& value) {
	std::vector<uint8_t> message(4);
	message[0] = static_cast<uint8_t>((value >> 24) & 0xFF);
	message[1] = static_cast<uint8_t>((value >> 16) & 0xFF);
	message[2] = static_cast<uint8_t>((value >> 8) & 0xFF);
	message[3] = static_cast<uint8_t>(value & 0xFF);

	return message;
}

template <>
inline std::vector<uint8_t> append(bool& value) {
	std::vector<uint8_t> message(1);
	message[0] = static_cast<uint8_t>(value);
	return message;
}
template <>
inline std::vector<uint8_t> append(char& value) {
	std::vector<uint8_t> message(1);
	message[0] = static_cast<uint8_t>(value);
	return message;

}

template <>
inline std::vector<uint8_t> append(float& value) {
	static_assert(sizeof(uint32_t) == sizeof(value), "Floating point numbers must be 32 bits long");
	std::vector<uint8_t> message(4);
	uint32_t& uint32_value = reinterpret_cast<uint32_t&>(value);
	message[0] = static_cast<uint8_t>((uint32_value >> 24) & 0xFF);
	message[1] = static_cast<uint8_t>((uint32_value >> 16) & 0xFF);
	message[2] = static_cast<uint8_t>((uint32_value >> 8) & 0xFF);
	message[3] = static_cast<uint8_t>(uint32_value & 0xFF);
	return message;
}

template <>
inline std::vector<uint8_t> append(double& value) {
	static_assert(sizeof(uint64_t) == sizeof(value), "Double numbers must be 64 bits long");
	std::vector<uint8_t> message(8);
	uint64_t& uint64_value = reinterpret_cast<uint64_t&>(value);
	message[0] = static_cast<uint8_t>((uint64_value >> 56) & 0xFF);
	message[1] = static_cast<uint8_t>((uint64_value >> 48) & 0xFF);
	message[2] = static_cast<uint8_t>((uint64_value >> 40) & 0xFF);
	message[3] = static_cast<uint8_t>((uint64_value >> 32) & 0xFF);
	message[4] = static_cast<uint8_t>((uint64_value >> 24) & 0xFF);
	message[5] = static_cast<uint8_t>((uint64_value >> 16) & 0xFF);
	message[6] = static_cast<uint8_t>((uint64_value >> 8) & 0xFF);
	message[7] = static_cast<uint8_t>(uint64_value & 0xFF);
	return message;
}

template <>
inline uint8_t read(Message& message) {
	uint8_t value = message.readUint8();
	return value;
}

template <>
inline uint16_t read(Message& message) {
	uint16_t value = message.readUint16();
	return value;
}

template <>
inline uint32_t read(Message& message) {
	uint32_t value = message.readUint32();
	return value;
}

template <>
inline uint64_t read(Message& message) {
	uint64_t value = message.readUint64();
	return value;
}


template <>
inline int8_t read(Message& message) {
	int8_t value = message.readByte();
	return value;
}


template <>
inline int16_t read(Message& message) {
	int16_t value = message.readSint16();
	return value;
}


template <>
inline int32_t read(Message& message) {
	int32_t value = message.readSint32();
	return value;
}


template <>
inline bool read(Message& message) {
	bool value = message.readBoolean();
	return value;
}

template <>
inline float read(Message& message) {
	float value = message.readFloat();
	return value;
}


template <>
inline double read(Message& message) {
	double value = message.readDouble();
	return value;
}

template <>
inline uint8_t read(std::vector<uint8_t> message) {
	uint8_t value;
	if (message.size() < 1)
		return 0;
	value = message[0];
	return value;
}

template <>
inline uint16_t read(std::vector<uint8_t> message) {
	uint16_t value;
	if (message.size() < 2)
		return 0;
	value = ((uint16_t)message[0] << 8) | (uint16_t)message[1];
	return value;
}

template <>
inline uint32_t read(std::vector<uint8_t> message) {
	uint32_t value;
	if (message.size() < 4)
		return 0;
	value = ((uint32_t)message[0] << 24) | ((uint32_t)message[1] << 16) | 
		((uint32_t)message[2] << 8) | (uint32_t)message[3];
	return value;
}

template <>
inline uint64_t read(std::vector<uint8_t> message) {
	uint64_t value;
	if (message.size() < 8)
		return 0;
	value = ((uint64_t)message[0] << 56) | ((uint64_t)message[1] << 48) | 
		((uint64_t)message[2] << 40) | ((uint64_t)message[3] << 32) |
		((uint64_t)message[4] << 24) | ((uint64_t)message[5] << 16) | 
		((uint64_t)message[6] << 8) | (uint64_t)message[7];
	return value;
}

template <>
inline int8_t read(std::vector<uint8_t> message) {
	int8_t value;
	if (message.size() < 1)
		return 0;
	value = message[0];
	return value;
}

template <>
inline int16_t read(std::vector<uint8_t> message) {
	int16_t value;
	if (message.size() < 2)
		return 0;
	value = ((uint16_t)message[0] << 8) | (uint16_t)message[1];
	return value;
}

template <>
inline int32_t read(std::vector<uint8_t> message) {
	int32_t value;
	if (message.size() < 4)
		return 0;
	value = ((uint32_t)message[0] << 24) | ((uint32_t)message[1] << 16) | 
		((uint32_t)message[2] << 8) | (uint32_t)message[3];
	return value;
}

template <>
inline bool read(std::vector<uint8_t> message) {
	if (message.size() < 1)
		return 0;
	return static_cast<bool>(message[0]);
}

template <>
inline float read(std::vector<uint8_t> message) {
	static_assert(sizeof(uint32_t) == sizeof(float), "Floating point numbers must be 32 bits long");
	uint32_t iValue;
	if (message.size() < 4)
		return 0;
	iValue = ((uint32_t)message[0] << 24) | ((uint32_t)message[1] << 16) | 
		((uint32_t)message[2] << 8) | (uint32_t)message[3];
	float fValue = 0;
		
	std::memcpy(&fValue, &iValue, sizeof(float));
	return fValue;
}

template <>
inline double read(std::vector<uint8_t> message) {
	static_assert(sizeof(uint64_t) == sizeof(double), "Double numbers must be 64 bits long");
	uint64_t iValue = 0;
	if (message.size() < 8)
		return 0;
	iValue = ((uint64_t)message[0] << 56) | ((uint64_t)message[1] << 48) | 
		((uint64_t)message[2] << 40) | ((uint64_t)message[3] << 32) |
		((uint64_t)message[4] << 24) | ((uint64_t)message[5] << 16) | 
		((uint64_t)message[6] << 8) | (uint64_t)message[7];

	double dValue = 0;
		
	std::memcpy(&dValue, &iValue, sizeof(double));		
	return dValue;
}
  } // namespace pus
} // namespace gr
#endif // ECSS_PARAMETER_HPP
