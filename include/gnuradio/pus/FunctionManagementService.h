/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_FUNCTIONMANAGEMENTSERVICE_H
#define INCLUDED_PUS_FUNCTIONMANAGEMENTSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API FunctionManagementService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 8;

	enum MessageType : uint8_t {
		PerformFunction = 1,
		end = 2
	};
	uint8_t All[1] = {
		PerformFunction
	 }; 	
      typedef std::shared_ptr<FunctionManagementService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::FunctionManagementService.
       *
       * To avoid accidental use of raw pointers, pus::FunctionManagementService's
       * constructor is in a private implementation
       * class. pus::FunctionManagementService::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint16_t funcNameSize, uint16_t funcParamSize);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_FUNCTIONMANAGEMENTSERVICE_H */
