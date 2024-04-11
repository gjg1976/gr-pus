/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_TIMEBASEDSCHEDULINGSERVICE_H
#define INCLUDED_PUS_TIMEBASEDSCHEDULINGSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API TimeBasedSchedulingService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 11;

	enum MessageType : uint8_t {
		EnableTimeBasedScheduleExecutionFunction = 1,
		DisableTimeBasedScheduleExecutionFunction = 2,
		ResetTimeBasedSchedule = 3,
		InsertActivities = 4,
		DeleteActivitiesById = 5,
		TimeShiftActivitiesById = 7,
		DetailReportActivitiesById = 9,
		TimeBasedScheduleReportById = 10,
		ActivitiesSummaryReportById = 12,
		TimeBasedScheduledSummaryReport = 13,
		TimeShiftAllScheduledActivities = 15,
		DetailReportAllScheduledActivities = 16,
		SummaryReportAllScheduledActivities = 17,
		end = 18
	};
 	uint8_t All[13] = {
		EnableTimeBasedScheduleExecutionFunction,
		DisableTimeBasedScheduleExecutionFunction,
		ResetTimeBasedSchedule,
		InsertActivities,
		DeleteActivitiesById,
		TimeShiftActivitiesById,
		DetailReportActivitiesById,
		TimeBasedScheduleReportById,
		ActivitiesSummaryReportById,
		TimeBasedScheduledSummaryReport,
		TimeShiftAllScheduledActivities,
		DetailReportAllScheduledActivities,
		SummaryReportAllScheduledActivities,
	 };    
	 
      typedef std::shared_ptr<TimeBasedSchedulingService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::TimeBasedSchedulingService.
       *
       * To avoid accidental use of raw pointers, pus::TimeBasedSchedulingService's
       * constructor is in a private implementation
       * class. pus::TimeBasedSchedulingService::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_TIMEBASEDSCHEDULINGSERVICE_H */
