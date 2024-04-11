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
#include "setParameter_impl.h"

namespace gr {
  namespace pus {

template <>
    void
    setParameter_impl<std::uint8_t>::callBackParameter(void *value)    {
        uint8_t newValue = *reinterpret_cast<uint8_t *>(value);
        GR_LOG_WARN(d_logger, 
                         boost::format("Parameter %1%: changed to %2%") % 
                            d_parameterID %
                            (uint16_t) newValue);
    }
    
template <>
    void
    setParameter_impl<std::int16_t>::callBackParameter(void *value)    {
        int16_t newValue = *reinterpret_cast<int16_t *>(value);
        GR_LOG_WARN(d_logger, 
                         boost::format("Parameter %1%: changed to %2%") %  
                            d_parameterID %
                            newValue);
    }  

template <>
    void
    setParameter_impl<std::int32_t>::callBackParameter(void *value)    {
        int32_t newValue = *reinterpret_cast<int32_t *>(value);
        GR_LOG_WARN(d_logger, 
                         boost::format("Parameter %1%: changed to %2%") % 
                            d_parameterID %
                            newValue);
    }  
    
template <>
    void
    setParameter_impl<float>::callBackParameter(void *value)    {
        float newValue = *reinterpret_cast<float *>(value);
         GR_LOG_WARN(d_logger, 
                         boost::format("Parameter %1%: changed to %2%") % 
                            d_parameterID %
                            newValue);
    }           

template <>
    void
    setParameter_impl<double>::callBackParameter(void *value)    {
        double newValue = *reinterpret_cast<double *>(value);
            GR_LOG_WARN(this->d_logger,
                        boost::format("Parameter %1%: changed to %2%") % 
                            d_parameterID%
                            newValue);
    }   

template <class T>
typename setParameter<T>::sptr
    setParameter<T>::make(uint16_t parameterID)
    {
      return gnuradio::make_block_sptr<setParameter_impl<T>>(
        parameterID);
    }


    /*
     * The private constructor
     */
template <class T>
    setParameter_impl<T>::setParameter_impl(uint16_t parameterID)
      : gr::block("setParameter",
                     gr::io_signature::make(0, 0, 0),
                     gr::io_signature::make(0, 0, 0)),
                     d_parameterID(parameterID)
    {
    	d_parameter_pool = ParameterPool::getInstance();

	start(); // Callback function are seted 1 sec later in order to give time to init Parameters
    }

    /*
     * Our virtual destructor.
     */
template <class T>
    setParameter_impl<T>::~setParameter_impl()
    {
    	if (auto parameter = d_parameter_pool->getParameter(d_parameterID)){
	        parameter->get().cbFunction = nullptr;
	}
	
    }

template <class T>
bool setParameter_impl<T>::start()
{
    d_thread = gr::thread::thread([this] { run(); });

    return block::start();
}

template <class T>
void setParameter_impl<T>::run()
{
    boost::this_thread::sleep(
            boost::posix_time::milliseconds(static_cast<long>(1000)));
    if (auto parameter = d_parameter_pool->getParameter(d_parameterID)){
        	parameter->get().cbFunction = std::bind(
                	&setParameter_impl<T>::callBackParameter,
                	this,
                	std::placeholders::_1
            	);
    }
}


template <class T>
    void
    setParameter_impl<T>::setParameterValue(T newValue)
    {
    }
    
template <>
    void
    setParameter_impl<std::uint8_t>::setParameterValue(uint8_t newValue)
    {
        //printf("Set Parameter %u = %u\n", d_parameterID, (uint16_t)newValue);
        auto parameter = d_parameter_pool->getParameter(d_parameterID);
        static_cast<Parameter<uint8_t>*>(&parameter->get())->setValue(newValue);
    }    

template <>
    void
    setParameter_impl<std::int16_t>::setParameterValue(int16_t newValue)
    {
        //printf("Set Parameter %u = %d\n", d_parameterID, newValue);
        auto parameter = d_parameter_pool->getParameter(d_parameterID);
        static_cast<Parameter<int16_t>*>(&parameter->get())->setValue(newValue);
    } 
    
template <>
    void
    setParameter_impl<std::int32_t>::setParameterValue(int32_t newValue)
    {
        //printf("Set Parameter %u = %d\n", d_parameterID, newValue);
        auto parameter = d_parameter_pool->getParameter(d_parameterID);
        static_cast<Parameter<int32_t>*>(&parameter->get())->setValue(newValue);
    } 
    
template <>
    void
    setParameter_impl<float>::setParameterValue(float newValue)
    {
       // printf("Set Parameter %u = %f\n", d_parameterID, newValue);
        auto parameter = d_parameter_pool->getParameter(d_parameterID);
        static_cast<Parameter<float>*>(&parameter->get())->setValue(newValue);
    }         

template <>
    void
    setParameter_impl<double>::setParameterValue(double newValue)
    {
        auto parameter = d_parameter_pool->getParameter(d_parameterID);
        static_cast<Parameter<double>*>(&parameter->get())->setValue(newValue);
    }  
    
template class setParameter<std::uint8_t>;
template class setParameter<std::int16_t>;
template class setParameter<std::int32_t>;
template class setParameter<float>;
template class setParameter<double>;
  } /* namespace pus */
} /* namespace gr */
