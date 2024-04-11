/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "EventsInit_impl.h"

namespace gr {
  namespace pus {

    EventsInit::sptr
    EventsInit::make(const std::string& init_file)
    {
      return gnuradio::make_block_sptr<EventsInit_impl>(
        init_file);
    }


    /*
     * The private constructor
     */
    EventsInit_impl::EventsInit_impl(const std::string& init_file)
      : gr::block("EventsInit",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_event_action = EventAction::getInstance();
       
        if (!d_event_action->initializeEventAction(init_file)){
        	GR_LOG_WARN(d_logger, "No Even Action init file found");
        }
    }

    /*
     * Our virtual destructor.
     */
    EventsInit_impl::~EventsInit_impl()
    {
    }

  } /* namespace pus */
} /* namespace gr */
