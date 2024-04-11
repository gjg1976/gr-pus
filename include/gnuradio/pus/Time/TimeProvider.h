/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_TIMEPROVIDER_H
#define INCLUDED_PUS_TIMEPROVIDER_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <cstdint>
#include <ctime>
#include <gnuradio/pus/Time/TimeStamp.h>
#include <gnuradio/pus/Time/UTCTimestamp.h>

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <atomic>
#include <etl/vector.h>
#include "etl/map.h"

#define TIME_SIZE 4

namespace gr {
  namespace pus {
class TimeProviderDestroyer;
    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API TimeProvider
    {
     
     private:
      /**
      * @brief Hold the list of timer callbacks
      *
      * @details The callbacks in this list are executed each second.
      */
      etl::map<uint16_t, std::function<void(TimeProvider*)>, ECSSMaxNumberOfCallbackFunctions> handlers;

      static TimeProvider* inst_timeprovider;
      static TimeProviderDestroyer inst_timeproviderdestroyer;
         
      TimeProvider();
      TimeProvider(const TimeProvider&);
      friend class TimeProviderDestroyer;  
      ~TimeProvider();   
       
      TimeProvider& operator=(const TimeProvider&);

      uint8_t d_mode = CUC_LVL1;  
      bool d_p_field = false;
      long d_resolution = 1; 
      long d_newresolution = 1;     

      gr::thread::thread d_thread;
      std::atomic<bool> d_finished;    
      bool d_status;
      bool d_suspend;
    
      void run();
       // Overloading these to start and stop the internal thread that
      // periodically produces the message.
      bool start();
      bool stop();   
     public:

      static TimeProvider* getInstance();
      
      UTCTimestamp getCurrentTimeUTC();  
	/**
	 * Returns the current time as CCSDS 301.0-B-4
	 * @note
	 */
      uint32_t  getCurrentTimeDefaultCUC();
      bool config(float resolution, uint8_t mode, bool p_field, uint16_t epoch_year, uint8_t epoch_month, uint8_t epoch_day);
 
      inline long getTimerResolutionMs() {return d_resolution;};
      
      etl::vector<uint8_t, ECSSMaxTimeField> getCurrentTimeStamp();
            
      uint16_t getTimeSize();
             	  
      enum Modes {
	    CUC_LVL1 = 1,
	    CUC_LVL2 = 2,
	    CDS = 4                
      }; 
      

      
      void addHandler(uint16_t serviceType, std::function<void(TimeProvider*)> handler);
      void removeHandler(uint16_t serviceType);

    };
    

    class TimeProviderDestroyer
    {
     public:
       TimeProviderDestroyer(TimeProvider * = 0);
       ~TimeProviderDestroyer();
       void SetSingleton(TimeProvider *s);

     private:
       TimeProvider *_timeProvider;
    };    
  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_TIMEPARSER_H */
