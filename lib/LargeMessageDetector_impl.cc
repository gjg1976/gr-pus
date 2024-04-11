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
#include "LargeMessageDetector_impl.h"

namespace gr {
  namespace pus {

    LargeMessageDetector::sptr
    LargeMessageDetector::make()
    {
      return gnuradio::make_block_sptr<LargeMessageDetector_impl>(
        );
    }


    /*
     * The private constructor
     */
    LargeMessageDetector_impl::LargeMessageDetector_impl()
      : gr::block("LargeMessageDetector",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
    
        this->message_port_register_in(PMT_IN);
        this->set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });

        this->message_port_register_out(PMT_OUT);
        this->message_port_register_out(PMT_LARGE);
    }

    /*
     * Our virtual destructor.
     */
    LargeMessageDetector_impl::~LargeMessageDetector_impl()
    {
    }

    void LargeMessageDetector_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);

        // extract data
        if (pmt::is_u8vector(v_data)) {
                std::vector<uint8_t> in_data = pmt::u8vector_elements(v_data);
		if(in_data.size() > ECSSMaxFixedOctetMessageSize)
		        message_port_pub(PMT_LARGE, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(in_data.size(), in_data)));
		else
		        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(in_data.size(), in_data)));
        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

  } /* namespace pus */
} /* namespace gr */
