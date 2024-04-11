/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/pus/Time/TimeProvider.h>

namespace gr {
  namespace pus {

    TimeProvider* TimeProvider::inst_timeprovider = NULL;
    TimeProviderDestroyer TimeProvider::inst_timeproviderdestroyer;
    
    TimeProvider::TimeProvider() :
    	d_mode(CUC_LVL1) 
    {
    	d_resolution = d_newresolution = 1000;
    	start();
    }

    TimeProvider::~TimeProvider()
    {
       stop();
    }
        
    TimeProvider* TimeProvider::getInstance()
    {
       if(inst_timeprovider == NULL){
           inst_timeprovider = new TimeProvider();
           inst_timeproviderdestroyer.SetSingleton(inst_timeprovider);           
       }
       return inst_timeprovider;
    }

    UTCTimestamp TimeProvider::getCurrentTimeUTC() {
	time_t timeInSeconds = static_cast<time_t>(time(nullptr));
	
	tm* UTCTimeStruct = std::gmtime(&timeInSeconds);

	UTCTimestamp currentTime(UTCTimeStruct->tm_year, UTCTimeStruct->tm_mon,
	                         UTCTimeStruct->tm_mday, UTCTimeStruct->tm_hour,
	                         UTCTimeStruct->tm_min, UTCTimeStruct->tm_sec);
	

	return currentTime;
    }

    bool TimeProvider::config(float resolution, uint8_t mode, bool p_field, uint16_t epoch_year, uint8_t epoch_month, uint8_t epoch_day)
    {

        d_mode = mode;
        d_p_field = p_field;
        d_newresolution = (long)(resolution * 1000);

    	if(d_mode == CUC_LVL1){
    		Time::Epoch.year = 1958;
		Time::Epoch.month = 1;
		Time::Epoch.day = 1;
	}else if(d_mode == CUC_LVL2){
		if(epoch_year > 2019 || epoch_month > 11 || epoch_day > Time::DaysOfMonth[epoch_month]){
	            return false;
		}else{	
		    Time::Epoch.year = epoch_year;
		    Time::Epoch.month = epoch_month;
		    Time::Epoch.day = epoch_day;
		}
	}
        return true;
    }

    uint32_t  TimeProvider::getCurrentTimeDefaultCUC() {
	UTCTimestamp timeUTC = getCurrentTimeUTC();
	return Time::DefaultCUC(timeUTC).formatAsBytes();
    }

    etl::vector<uint8_t, ECSSMaxTimeField> TimeProvider::getCurrentTimeStamp() {
	etl::vector<uint8_t, ECSSMaxTimeField>  stamp;
   
        if(d_p_field)
		stamp.push_back(Time::buildShortCUCHeader<4,0>()) ;

	uint32_t ticks = TimeProvider::getInstance()->getCurrentTimeDefaultCUC();
	stamp.push_back((ticks >> 24) & 0xffU);
	stamp.push_back((ticks >> 16) & 0xffU);
	stamp.push_back((ticks >> 8) & 0xffU);
	stamp.push_back((ticks) & 0xffU);	
	
	return stamp;
    } 
    
    	
    bool TimeProvider::start()
    {
        d_finished = false;
        d_thread = gr::thread::thread([this] { run(); });

        return true;
    }

    bool TimeProvider::stop()
    {
        // Shut down the thread
        d_finished = true;
        d_thread.interrupt();
        d_thread.join();

        return true;
    }        

    void TimeProvider::run()
    {
	auto start = std::chrono::high_resolution_clock::now().time_since_epoch();
	auto waitMilliseconds = 1000 - std::chrono::duration_cast<std::chrono::milliseconds>(start).count() % 1000;

	boost::this_thread::sleep(
            		boost::posix_time::milliseconds(static_cast<long>(waitMilliseconds)));

        start = std::chrono::high_resolution_clock::now().time_since_epoch();	

        while (!d_finished) {
            auto finish = std::chrono::high_resolution_clock::now().time_since_epoch();
             auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(finish - start).count();

            if( diff >= d_resolution)
            {
            	start += std::chrono::milliseconds(d_resolution);
            
            	for (auto const& entry : handlers) {
                	entry.second(this);
            	}
            	if (d_newresolution != d_resolution)
            		d_resolution = d_newresolution;

            }
            boost::this_thread::sleep(
            		boost::posix_time::milliseconds(static_cast<long>(1)));
        }
    }

    //add handler to list --> works fine
    void TimeProvider::addHandler(uint16_t serviceType, std::function<void(TimeProvider*)> handler) {
        handlers[serviceType] = handler;
    }

    void TimeProvider::removeHandler(uint16_t serviceType) {
        handlers.erase(serviceType);
    }  
    
    uint16_t TimeProvider::getTimeSize()
    {
     	return TIME_SIZE;
    }    
    
    TimeProviderDestroyer::TimeProviderDestroyer(TimeProvider *s)
    {
     _timeProvider = s;
    }

    TimeProviderDestroyer::~TimeProviderDestroyer()
    {
     delete _timeProvider;
    }

    void TimeProviderDestroyer::SetSingleton(TimeProvider *s)
    {
     _timeProvider = s;
    }  
  } /* namespace pus */
} /* namespace gr */
