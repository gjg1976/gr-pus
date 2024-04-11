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
#include "MessageConfig_impl.h"

namespace gr {
  namespace pus {

    MessageConfig::sptr
    MessageConfig::make(uint16_t apid, bool crc_enable)
    {
      return gnuradio::make_block_sptr<MessageConfig_impl>(
        apid, crc_enable);
    }


    /*
     * The private constructor
     */
    MessageConfig_impl::MessageConfig_impl(uint16_t apid, bool crc_enable)
      : gr::block("MessageConfig",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
         d_messageparser = MessageParser::getInstance();
         d_messageparser->config(apid, crc_enable);
         ApplicationId = apid;
    }

    /*
     * Our virtual destructor.
     */
    MessageConfig_impl::~MessageConfig_impl()
    {
    }


  } /* namespace pus */
} /* namespace gr */
