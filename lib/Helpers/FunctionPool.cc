/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 
#include <gnuradio/pus/Helpers/FunctionPool.h>
#include <iostream>

namespace gr {
 namespace pus {


    FunctionPool* FunctionPool::inst_functionpool = NULL;
    
    FunctionPool::FunctionPool() 
    {
    }
    
    FunctionPool* FunctionPool::getInstance()
    {
       if(inst_functionpool == NULL)
           inst_functionpool = new FunctionPool();
       
       return inst_functionpool;
    }


    void FunctionPool::include(std::string funcName,
                                        void (*ptr)(std::vector<uint8_t>)) {

	if (funcPtrIndex.size() < ECSSFunctionMapSize) { 
		funcPtrIndex.insert(std::make_pair(funcName, ptr));
	} else {
		ErrorHandler::getInstance()->reportInternalError(ErrorHandler::InternalErrorType::MapFull);
	}
    }    
  } /* namespace pus */
} /* namespace gr */


