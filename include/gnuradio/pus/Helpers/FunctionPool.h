/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_FUNCTIONPOOL_H
#define ECSS_FUNCTIONPOOL_H

#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <string>
#include <map>
/**
 * Implementation of ST[19] event-action Service
 *
 * ECSS 8.19 && 6.19
 *
 * @ingroup Services
 *
 * @note The application ID was decided to be abolished as an identifier of the event-action
 * definition
 * @attention Every event action definition ID should be different, regardless of the application ID
 */
namespace gr {
 namespace pus {

typedef std::string functionName;
typedef std::map<functionName, void (*)(std::vector<uint8_t>)> FunctionMap;

   class FunctionPool {

     private:
      static FunctionPool* inst_functionpool;
      
      FunctionPool();
      FunctionPool(const FunctionPool&);
      
      FunctionPool& operator=(const FunctionPool&);
	
      uint16_t d_funcNameSize;
      uint16_t d_funcParamSize;
        
    public:

        static FunctionPool* getInstance();

	/**
	 * Map of the function names to their respective pointers. Size controlled by FUNC_MAP_SIZE
	 */
	FunctionMap funcPtrIndex;
	
	inline void setFuncNameSize(uint16_t funcNameSize) { d_funcNameSize = funcNameSize;};
	inline uint16_t getFuncNameSize() { return d_funcNameSize;};
	
	void include(std::string funcName, void (*ptr)(std::vector<uint8_t>));
   };
  } /* namespace pus */
} /* namespace gr */  

#endif // ECSS_SERVICES_EVENTACTIONSERVICE_HPP
