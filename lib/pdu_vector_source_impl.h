/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_PDU_VECTOR_SOURCE_IMPL_H
#define INCLUDED_PUS_PDU_VECTOR_SOURCE_IMPL_H

#include <gnuradio/pus/pdu_vector_source.h>

namespace gr {
  namespace pus {

template <class T>
    class pdu_vector_source_impl : public pdu_vector_source<T>
    {
     private:
      std::vector<T> d_data;

      void msg_handler(pmt::pmt_t pmt_msg);
      
     public:
      pdu_vector_source_impl(const std::vector<T>& data);
      ~pdu_vector_source_impl();

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_PDU_VECTOR_SOURCE_IMPL_H */
