/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "pdu_vector_source_impl.h"

namespace gr {
  namespace pus {

template <class T>
typename pdu_vector_source<T>::sptr
    pdu_vector_source<T>::make(const std::vector<T>& data)
    {
      return gnuradio::make_block_sptr<pdu_vector_source_impl<T>>(
        data);
    }


    /*
     * The private constructor
     */
template <class T>
    pdu_vector_source_impl<T>::pdu_vector_source_impl(const std::vector<T>& data)
      : gr::block("pdu_vector_source",
                     gr::io_signature::make(0, 0, 0),
                     gr::io_signature::make(0, 0, 0)),
                     d_data(data)
    {
    
        // register message ports
      this->message_port_register_out(pmt::mp("pdu_out"));
      this->message_port_register_in(pmt::mp("trg"));

      this->set_msg_handler(pmt::mp("trg"), [this](pmt::pmt_t msg) { this->msg_handler(msg); });
    
    }

    /*
     * Our virtual destructor.
     */
template <class T>
    pdu_vector_source_impl<T>::~pdu_vector_source_impl()
    {
    }

template <class T>
    void
    pdu_vector_source_impl<T>::msg_handler(pmt::pmt_t pmt_msg)
    {
    }

template <>
    void
    pdu_vector_source_impl<std::uint8_t>::msg_handler(pmt::pmt_t pmt_msg)
    {
        this->message_port_pub(
            pmt::mp("pdu_out"),
            pmt::cons(pmt::PMT_NIL, pmt::init_u8vector(d_data.size(), d_data)));
                              
    }
 template <>
    void
    pdu_vector_source_impl<std::int16_t>::msg_handler(pmt::pmt_t pmt_msg)
    {
        this->message_port_pub(
            pmt::mp("pdu_out"),
            pmt::cons(pmt::PMT_NIL, pmt::init_s16vector(d_data.size(), d_data)));
                              
    }   

template<>
    void
    pdu_vector_source_impl<std::int32_t>::msg_handler(pmt::pmt_t pmt_msg)
    {
        this->message_port_pub(
            pmt::mp("pdu_out"),
            pmt::cons(pmt::PMT_NIL, pmt::init_s32vector(d_data.size(), d_data)));
    }
    
template<>
    void
    pdu_vector_source_impl<float>::msg_handler(pmt::pmt_t pmt_msg)
    {
        this->message_port_pub(
            pmt::mp("pdu_out"),
            pmt::cons(pmt::PMT_NIL, pmt::init_f32vector(d_data.size(), d_data)));
    }
    
template<>
    void
    pdu_vector_source_impl<gr_complex>::msg_handler(pmt::pmt_t pmt_msg)
    {
        this->message_port_pub(
            pmt::mp("pdu_out"),
            pmt::cons(pmt::PMT_NIL, pmt::init_c32vector(d_data.size(), d_data)));
    } 

template class pdu_vector_source<std::uint8_t>;
template class pdu_vector_source<std::int16_t>;
template class pdu_vector_source<std::int32_t>;
template class pdu_vector_source<float>;
template class pdu_vector_source<gr_complex>;
  } /* namespace pus */
} /* namespace gr */
