/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_LARGEPACKETTRANSFERSERVICE_H
#define INCLUDED_PUS_LARGEPACKETTRANSFERSERVICE_H

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
    class PUS_API LargePacketTransferService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 13;


	enum MessageType : uint8_t {
		FirstDownlinkPartReport = 1,
		InternalDownlinkPartReport = 2,
		LastDownlinkPartReport = 3,
		FirstUplinkPartMessage = 9,
		IntermediateUplinkPartMessage = 10,
		LastUplinkPartMessage = 11,
		UplinkAbortReport = 16,		
		end = 17
	};
	uint8_t All[7] = {
		FirstDownlinkPartReport,
		InternalDownlinkPartReport,
		LastDownlinkPartReport,
		FirstUplinkPartMessage,
		IntermediateUplinkPartMessage,
		LastUplinkPartMessage,
		UplinkAbortReport
	 }; 	
      typedef std::shared_ptr<LargePacketTransferService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::LargePacketTransferService.
       *
       * To avoid accidental use of raw pointers, pus::LargePacketTransferService's
       * constructor is in a private implementation
       * class. pus::LargePacketTransferService::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_LARGEPACKETTRANSFERSERVICE_H */
