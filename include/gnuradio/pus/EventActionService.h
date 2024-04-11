/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_EVENTACTIONSERVICE_H
#define INCLUDED_PUS_EVENTACTIONSERVICE_H

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
    class PUS_API EventActionService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 19;

	enum MessageType : uint8_t {
		AddEventAction = 1,
		DeleteEventAction = 2,
		DeleteAllEventAction = 3,
		EnableEventAction = 4,
		DisableEventAction = 5,
		ReportStatusOfEachEventAction = 6,
		EventActionStatusReport = 7,
		EnableEventActionFunction = 8,
		DisableEventActionFunction = 9,
		ReportEventActionDefinitions = 10,
		EventActionDefinitionsReport = 11,
		end = 12
	};
	
	uint8_t All[9] = {
		AddEventAction,
		DeleteEventAction,
		DeleteAllEventAction,
		EnableEventAction,
		DisableEventAction,
		ReportStatusOfEachEventAction,
		EventActionStatusReport,
		EnableEventActionFunction,
		DisableEventActionFunction
	 }; 		
	
      typedef std::shared_ptr<EventActionService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::EventActionService.
       *
       * To avoid accidental use of raw pointers, pus::EventActionService's
       * constructor is in a private implementation
       * class. pus::EventActionService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& filename);  
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_EVENTACTIONSERVICE_H */
