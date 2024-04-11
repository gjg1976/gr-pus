/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_MEMORYMANAGER_H
#define ECSS_MEMORYMANAGER_H

#include <gnuradio/pus/Helpers/ErrorHandler.h>


namespace gr {
 namespace pus {

   class MemoryManager {
     private:
      static MemoryManager* inst_memorymanager;
      
      MemoryManager();
      MemoryManager(const MemoryManager&);
      
      MemoryManager& operator=(const MemoryManager&);
      std::vector<uint8_t> simulatedMem{std::vector<uint8_t>(1024,0)};
        
    public:
	// Memory type ID's
	enum MemoryID {
		DTCMRAM = 0,
		RAM_D1,
		RAM_D2,
		RAM_D3,
		ITCMRAM,
		FLASH_MEMORY,
		EEPROM_MEMORY,
		EXTERNAL,
		END
	};
	
        static MemoryManager* getInstance();

	bool allowedWritting(MemoryID memoryID);
	bool addressValidator(MemoryID memoryID, uint64_t startAddress);	
	bool writeData(MemoryID memoryID, uint64_t startAddress, MessageArray& writeData);
	MessageArray dump(MemoryID memoryID, uint64_t startAddress, uint16_t readLength);
   };
  } /* namespace pus */
} /* namespace gr */  

#endif // ECSS_MEMORYMANAGER_H
