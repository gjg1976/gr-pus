/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_MEMORYMANAGEMENTSERVICE_H
#define INCLUDED_PUS_MEMORYMANAGEMENTSERVICE_H

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
    class PUS_API MemoryManagementService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 6;

	enum MessageType : uint8_t {
		LoadRawMemoryDataAreas = 2,
		DumpRawMemoryData = 5,
		DumpRawMemoryDataReport = 6,
		CheckRawMemoryData = 9,
		CheckRawMemoryDataReport = 10,
		end = 11
	};
	uint8_t All[5] = {
		LoadRawMemoryDataAreas,
		DumpRawMemoryData,
		DumpRawMemoryDataReport,
		CheckRawMemoryData,
		CheckRawMemoryDataReport
	 }; 

	
      typedef std::shared_ptr<MemoryManagementService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::MemoryManagementService.
       *
       * To avoid accidental use of raw pointers, pus::MemoryManagementService's
       * constructor is in a private implementation
       * class. pus::MemoryManagementService::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_MEMORYMANAGEMENTSERVICE_H */
