/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_SERVICESPOOL_IMPL_H
#define INCLUDED_PUS_SERVICESPOOL_IMPL_H

#include <gnuradio/pus/ServicesPool.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <etl/vector.h>
#include <etl/map.h>

namespace gr {
  namespace pus {

    class ServicesPool_impl : public ServicesPool
    {
     private:
      typedef etl::map<uint16_t, uint16_t, ECSSMaxNumberOfServices> OutputServices;
      typedef etl::vector<uint16_t, ECSSMaxNumberOfServices> ServicesList;

      OutputServices d_outputservices;
      ServicesList d_services_list;
      
      ErrorHandler* d_error_handler;
            
     public:
      ServicesPool_impl(std::vector<uint16_t> services_list);
      ~ServicesPool_impl();


    /**
     * @brief
     *
     * @param msg
     */
      void handle_msg(pmt::pmt_t pdu);

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_SERVICESPOOL_IMPL_H */
