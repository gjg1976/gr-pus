/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_PDU_VECTOR_SOURCE_H
#define INCLUDED_PUS_PDU_VECTOR_SOURCE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
template <class T>  
    class PUS_API pdu_vector_source : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<pdu_vector_source<T>> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of satellite_tools::pdu_vector_source.
       *
       * To avoid accidental use of raw pointers, satellite_tools::pdu_vector_source's
       * constructor is in a private implementation
       * class. satellite_tools::pdu_vector_source::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::vector<T>& data);
    };
typedef pdu_vector_source<std::uint8_t> pdu_vector_source_b;
typedef pdu_vector_source<std::int16_t> pdu_vector_source_s;
typedef pdu_vector_source<std::int32_t> pdu_vector_source_i;
typedef pdu_vector_source<float> pdu_vector_source_f;
typedef pdu_vector_source<gr_complex> pdu_vector_source_c;

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_PDU_VECTOR_SOURCE_H */
