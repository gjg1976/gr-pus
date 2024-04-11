/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_MESSAGEPARSER_H
#define INCLUDED_PUS_MESSAGEPARSER_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Time/TimeProvider.h>
#include <gnuradio/pus/Helpers/Message.h>
#include <gnuradio/pus/Time/TimeProvider.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API MessageParser
    {
     private:
      static MessageParser* inst_messageparser;
      
      MessageParser();
      MessageParser(const MessageParser&);
      
      MessageParser& operator=(const MessageParser&);

      bool d_crc_enable;
      uint16_t d_counter;
      uint16_t d_apid;

      TimeProvider* d_timeprovider;
      
      void counter_inc() { d_counter++; if(d_counter > 16383) d_counter = 0;};
      
     public:
      static MessageParser* getInstance();

      bool config(uint16_t apid, bool crc_enable);

/***************************************************************************************/

      Message ParseMessageCommand(MessageArray& in_data);
      Message CreateMessageReport(uint8_t scTimeRef, uint8_t serviceType, 
			uint8_t messageType, uint16_t messageTypeCounter,
			uint16_t destinationId, MessageArray& payload); 	
      Message CreateEmptyMessageReport(uint8_t scTimeRef, uint8_t serviceType, 
			uint8_t messageType, uint16_t messageTypeCounter,
			uint16_t destinationId);
      Message CreateMessageReport(uint16_t apid,
    			uint16_t packetSequenceCounter, uint8_t scTimeRef, uint8_t serviceType, 
			uint8_t messageType, uint16_t messageTypeCounter,
			uint16_t destinationId, MessageArray& payload);
			
			
      void closeMessage(Message& message);
    
      MessageArray parseTCfromMessage(Message& message);

      MessageArray parseUpToEndfromMessage(Message& message);						 
/***************************************************************************************/
			
      uint16_t getApplicationId() { return d_apid;};	
      
     // void closeMessage(Message& message);	
      
     // std::vector<uint8_t> parseTCfromMessage(Message& message);
      
     // std::vector<uint8_t> parseUpToEndfromMessage(Message& message);
          
      bool assertTC(Message request, uint8_t expectedServiceType, uint8_t expectedMessageType)  {
		return request.assertType(Message::TC, expectedServiceType, expectedMessageType);
	}


      bool assertTM(Message request, uint8_t expectedServiceType, uint8_t expectedMessageType)  {
		return request.assertType(Message::TM, expectedServiceType, expectedMessageType);
	}
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_MESSAGEPARSER_H */
