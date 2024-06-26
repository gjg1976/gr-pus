/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 #include <gnuradio/pus/Helpers/CRCHelper.h>

namespace gr {
  namespace pus {
  

uint16_t CRCHelper::calculateMessageCRC(MessageArray& message) {
	// shift register contains all 1's initially (ECSS-E-ST-70-41C, Annex B - CRC and ISO checksum)
	uint16_t shiftReg = 0xFFFFU;

	// CRC16-CCITT generator polynomial (as specified in standard)
	uint16_t polynomial = 0x1021U;

	for (uint32_t i = 0; i < message.size(); i++) {
		// "copy" (XOR w/ existing contents) the current msg bits into the MSB of the shift register
		shiftReg ^= (message[i] << 8U);

		for (int j = 0; j < 8; j++) {
			// if the MSB is set, the bitwise AND gives 1
			if ((shiftReg & 0x8000U) != 0U) {
				// toss out of the register the MSB and divide (XOR) its content with the generator
				shiftReg = ((shiftReg << 1U) ^ polynomial);
			} else {
				// just toss out the MSB and make room for a new bit
				shiftReg <<= 1U;
			}
		}
	}
	return shiftReg;
}

uint16_t CRCHelper::calculateMessageCRC(MessageArray& message, uint16_t shiftReg) {

	// CRC16-CCITT generator polynomial (as specified in standard)
	uint16_t polynomial = 0x1021U;

	for (uint32_t i = 0; i < message.size(); i++) {
		// "copy" (XOR w/ existing contents) the current msg bits into the MSB of the shift register
		shiftReg ^= (message[i] << 8U);

		for (int j = 0; j < 8; j++) {
			// if the MSB is set, the bitwise AND gives 1
			if ((shiftReg & 0x8000U) != 0U) {
				// toss out of the register the MSB and divide (XOR) its content with the generator
				shiftReg = ((shiftReg << 1U) ^ polynomial);
			} else {
				// just toss out the MSB and make room for a new bit
				shiftReg <<= 1U;
			}
		}
	}

	return shiftReg;
}

uint16_t CRCHelper::validateMessageCRC(MessageArray& message) {
	return calculateMessageCRC(message);
	// CRC result of a correct msg w/checksum appended is 0
}

  } // namespace pus
} // namespace gr
