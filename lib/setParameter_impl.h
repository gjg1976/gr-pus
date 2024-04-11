/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_SETPARAMETER_IMPL_H
#define INCLUDED_PUS_SETPARAMETER_IMPL_H

#include <gnuradio/pus/setParameter.h>
#include <gnuradio/pus/Helpers/ParameterPool.h>

namespace gr {
  namespace pus {
template <class T>
    class setParameter_impl : public setParameter<T>
    {
     private:
    gr::thread::thread d_thread;

      uint16_t d_parameterID;
      ParameterPool* d_parameter_pool;
      
      void callBackParameter(void *value);
    void run();
    
     public:
      setParameter_impl(uint16_t parameterID);
      ~setParameter_impl();

      void setParameterValue(T newValue) override;
    bool start() override;
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_SETPARAMETER_IMPL_H */
