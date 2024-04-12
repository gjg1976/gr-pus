/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 
#include <gnuradio/pus/Helpers/MemoryManager.h>
#include <iostream>

namespace gr {
 namespace pus {


    MemoryManager* MemoryManager::inst_memorymanager = NULL;
    
    MemoryManager::MemoryManager() 
    {
    	//simulatedMem.resize(1024);
    	//std::fill(simulatedMem.begin(), simulatedMem.end(), 0);
    }
    
    MemoryManager* MemoryManager::getInstance()
    {
       if(inst_memorymanager == NULL)
           inst_memorymanager = new MemoryManager();
       
       return inst_memorymanager;
    }


    bool MemoryManager::allowedWritting(MemoryID memID) {

	if (memID < EEPROM_MEMORY) { 
		return true;
	} else {
		return false;
	}
    }
    
    bool MemoryManager::addressValidator(MemoryID memoryID, uint64_t address)
    {
	switch (memoryID){
		case MemoryID::EEPROM_MEMORY:
			if (address < (uint64_t)(simulatedMem.size()/2))
				return true;
			break;
		default:	
			if (address < (uint64_t)simulatedMem.size() and address >= (uint64_t)(simulatedMem.size()/2))
				return true;	
	}
	return false;	
    }   
    
    MessageArray MemoryManager::dump(MemoryID memoryID, uint64_t startAddress, uint16_t readLength)
    {
    	MessageArray dumpData;
    	if (addressValidator(memoryID, startAddress) &&
		    addressValidator(memoryID, startAddress + readLength)) {
		for(int i = 0; i < readLength; i++){
			dumpData.push_back(simulatedMem[startAddress+i]);
		}
	}
	return dumpData;
    }
    
    bool MemoryManager::writeData(MemoryID memoryID, uint64_t startAddress, MessageArray& writeData)   
    {
    	if (addressValidator(memoryID, startAddress) &&
		    addressValidator(memoryID, startAddress + writeData.size())) {
		for(size_t i = 0; i < writeData.size(); i++){
			simulatedMem[startAddress+i] = writeData[i];
		}
		return true;
	}
	return false;
    }         
  } /* namespace pus */
} /* namespace gr */


