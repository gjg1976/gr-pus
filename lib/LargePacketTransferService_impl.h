/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_LARGEPACKETTRANSFERSERVICE_IMPL_H
#define INCLUDED_PUS_LARGEPACKETTRANSFERSERVICE_IMPL_H

#include <gnuradio/pus/LargePacketTransferService.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/vector.h"

#define LARGE_PACKET_TRANS_ID_SIZE	2
#define LARGE_PACKET_TRANS_COUNTER_SIZE	2

namespace gr {
  namespace pus {

    class LargePacketTransferService_impl : public LargePacketTransferService
    {
     private:
       TimeProvider* d_time_provider;
       uint16_t downlinkLargeMessageTransactionIdentifier;
       uint16_t counters[LargePacketTransferService::MessageType::end];

	typedef etl::map<uint16_t, MessageArray, ECSSLargeUplinkStoreMaxParts> uplinkMessageParts;

	typedef std::pair<uint16_t, uplinkMessageParts> uplinkMessageEntry;
	
	etl::map<uint16_t, uplinkMessageEntry, ECSSLargeUplinkStoreSize> uplinkMessagesList;

     public:
      LargePacketTransferService_impl();
      ~LargePacketTransferService_impl();

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);
	/**
	 * It is responsible to extract the data from large packets and call the split function
	 *
	 */
      void handle_large_in_msg(pmt::pmt_t pdu);
	/**
	 * timer Tick hook, each time is called, it will search for all Uplink Messages
	 * and increase a timeout counter, when the counter reach ECSSLargeUplinkReceptiontimeOut
	 * then a abort message is generated and the Uplink Message discarted.
	 * @param p TimeProvider singleton
	 * @return void
	 */
      void timerTick(TimeProvider *p) ;
	/**
	 * TM[13,1] Function that handles the first part of the download report
	 * @param largeMessageTransactionIdentifier The identifier of the large packet
	 * @param partSequenceNumber The identifier of the part of the large packet
	 * @param string The data contained in this part of the large packet
	 */
	void firstDownlinkPartReport(uint16_t largeMessageTransactionIdentifier, uint16_t partSequenceNumber,
	                             MessageArray& data);

	/**
	 * TM[13,2] Function that handles the n-2 parts of tbe n-part download report
	 * @param largeMessageTransactionIdentifier The identifier of the large packet
	 * @param partSequenceNumber The identifier of the part of the large packet
	 * @param string The data contained in this part of the large packet
	 */
	void intermediateDownlinkPartReport(uint16_t largeMessageTransactionIdentifier, uint16_t partSequenceNumber,
	                                    MessageArray& data);

	/**
	 * TM[13,3] Function that handles the last part of the download report
	 * @param largeMessageTransactionIdentifier The identifier of the large packet
	 * @param partSequenceNumber The identifier of the part of the large packet
	 * @param string The data contained in this part of the large packet
	 */
	void lastDownlinkPartReport(uint16_t largeMessageTransactionIdentifier, uint16_t partSequenceNumber,
	                            MessageArray& data);
	
	/**
	 * TC[13,9] Function that handles the first part of the uplink message
	 * @param request The uplink message contained the first part of the message
	 */
	void firstUplinkPartMessage(Message& request);

	/**
	 * TC[13,10] Function that handles the n-2 parts of the n-part download message
	 * @param request The uplink message contained the n-part of the message
	 */
	void intermediateUplinkPartMessage(Message& request);

	/**
	 * TC[13,11] Function that handles the last part of the n-part download message
	 * @param request The uplink message contained the n-part of the message
	 */
	void lastUplinkPartMessage(Message& request);	

	/**
	 * TM[13,16] Function that handles the uplink failure report
	 * @param largeMessageTransactionIdentifier The identifier of the large packet
	 * @param failureIdentification The identifier of the failure causing to abort the uplink
	 */
	void uplinkAbortReport(uint16_t largeMessageTransactionIdentifier, uint8_t failureIdentification);
	
	/**
	 * Function that splits large messages
	 * @param message that is exceeds the standards and has to be split down
	 * @param largeMessageTransactionIdentifier that is a value we assign to this splitting of the large message
	 */
	void split(std::vector<uint8_t>& message, uint16_t largeMessageTransactionIdentifier);

	/**
	 * Function that joint and releases large messages
	 * @param largeMessageTransactionIdentifier that is a value we assign to the store message parts to join
	 */
	void joint(uint16_t largeMessageTransactionIdentifier, uint16_t numParts);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_LARGEPACKETTRANSFERSERVICE_IMPL_H */
