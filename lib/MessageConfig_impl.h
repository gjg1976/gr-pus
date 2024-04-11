/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_MESSAGECONFIG_IMPL_H
#define INCLUDED_PUS_MESSAGECONFIG_IMPL_H

#include <gnuradio/pus/MessageConfig.h>
#include <gnuradio/pus/Helpers/MessageParser.h>

namespace gr {
  namespace pus {

    class MessageConfig_impl : public MessageConfig
    {
     private:
      MessageParser* d_messageparser;

     public:
      MessageConfig_impl(uint16_t apid, bool crc_enable);
      ~MessageConfig_impl();

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_MESSAGECONFIG_IMPL_H */
