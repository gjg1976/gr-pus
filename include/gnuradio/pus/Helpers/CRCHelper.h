/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_SERVICES_CRCHELPER_HPP
#define ECSS_SERVICES_CRCHELPER_HPP

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <vector>
#include <cstdint>
#include <etl/vector.h>

namespace gr {
  namespace pus { 
  
   typedef etl::vector<uint8_t, ECSSMaxMessageSize> MessageArray; 
     
   class CRCHelper {
	/**
	 * CRC16 calculation helper class
	 * This class declares a function which calculates the CRC16 checksum of the given data.
	 *
	 * For now the actual implementation is the CRC16/CCITT variant (ECSS-E-ST-70-41C, pg.615)
	 * (polynomial 0x1021, normal input), but this can change at any time
	 * (even to a hardware CRC implementation, if available)
	 *
	 * Please report all found bugs.
	 *
	 * @author (CRC explanation) http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
	 * @author (class code & dox) Grigoris Pavlakis <grigpavl@ece.auth.gr>
	 */

	// TODO: Change this to hardware implementation or a trusted software one
    public:

	/**
	 * Actual CRC calculation function.
	 * @param  message (pointer to the data to be checksummed)
	 * @return the CRC16 checksum of the input data
	 */
	static uint16_t calculateMessageCRC(MessageArray& message);

	/**
	 * Actual CRC calculation function with init register option.
	 * @param  message (pointer to the data to be checksummed)
	 * @param  shiftReg (initial value)
	 * @return the CRC16 checksum of the input data
	 */
	static uint16_t calculateMessageCRC(MessageArray& message, uint16_t shiftReg) ;
	
	/**
	 * CRC validation function. Make sure the passed message actually contains a CRC checksum
	 * appended at the very end!
	 * @param  message (pointer to the data to be validated)
	 * @param  length (in bytes, plus 2 bytes for the CRC checksum)
	 * @return 0 when the data is valid, a nonzero uint16 when the data is corrupted
	 */
	static uint16_t validateMessageCRC(MessageArray& message);

   };
  } // namespace pus
} // namespace gr
#endif // ECSS_SERVICES_CRCHELPER_HPP
