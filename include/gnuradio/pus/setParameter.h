/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_SETPARAMETER_H
#define INCLUDED_PUS_SETPARAMETER_H

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
    class PUS_API setParameter : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<setParameter<T>> sptr;

      virtual void setParameterValue(T newValue) = 0;
      /*!
       * \brief Return a shared_ptr to a new instance of pus::setParameter.
       *
       * To avoid accidental use of raw pointers, pus::setParameter's
       * constructor is in a private implementation
       * class. pus::setParameter::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint16_t parameterID);
    };
    
typedef setParameter<std::uint8_t> setParameter_b;
typedef setParameter<std::int16_t> setParameter_s;
typedef setParameter<std::int32_t> setParameter_i;
typedef setParameter<float> setParameter_f;
typedef setParameter<double> setParameter_d;
  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_SETPARAMETER_H */
