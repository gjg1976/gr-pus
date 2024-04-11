/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_EVENTSINIT_IMPL_H
#define INCLUDED_PUS_EVENTSINIT_IMPL_H

#include <gnuradio/pus/EventsInit.h>
#include <gnuradio/pus/Helpers/EventAction.h>

namespace gr {
  namespace pus {

    class EventsInit_impl : public EventsInit
    {
     private:
      EventAction* d_event_action;

     public:
      EventsInit_impl(const std::string& init_file);
      ~EventsInit_impl();

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_EVENTSINIT_IMPL_H */
