/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_PARAMETERSERVICE_H
#define INCLUDED_PUS_PARAMETERSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"
namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API ParameterService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 20;

	enum MessageType : uint8_t {
		ReportParameterValues = 1,
		ParameterValuesReport = 2,
		SetParameterValues = 3,
		end = 4
	};

	uint8_t All[3] = {
		ReportParameterValues,
		ParameterValuesReport,
		SetParameterValues
	 }; 	
      typedef std::shared_ptr<ParameterService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::ParameterService.
       *
       * To avoid accidental use of raw pointers, pus::ParameterService's
       * constructor is in a private implementation
       * class. pus::ParameterService::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_PARAMETERSERVICE_H */
