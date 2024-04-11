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
#include "ServicesPool_impl.h"
#include <gnuradio/pus/RequestVerificationService.h>
#include <gnuradio/pus/Helpers/CRCHelper.h>

namespace gr {
  namespace pus {

    ServicesPool::sptr
    ServicesPool::make(std::vector<uint16_t> services_list)
    {
      return gnuradio::make_block_sptr<ServicesPool_impl>(
        services_list);
    }


    /*
     * The private constructor
     */
    ServicesPool_impl::ServicesPool_impl(std::vector<uint16_t> services_list)
      : gr::block("ServicesPool",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_error_handler = ErrorHandler::getInstance();
        
        if(services_list.size() >= ECSSMaxNumberOfServices){
#ifdef _PUS_DEBUG
            GR_LOG_NOTICE(d_logger, "Services list supersedes the maximum allowed");
#endif        
	    return;
        }
        d_services_list = ServicesList(services_list.data(), services_list.data() + services_list.size());
        
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_VER);

        if(d_services_list.size() > 1){
            for(uint16_t i = 0; i < d_services_list.size(); i++){
                message_port_register_out(pmt::intern("out" + std::to_string(i)));
                d_outputservices.insert({d_services_list[i], i});
            }
        }else{
            d_outputservices.clear();
            message_port_register_out(PMT_OUT);
        }
    }

    /*
     * Our virtual destructor.
     */
    ServicesPool_impl::~ServicesPool_impl()
    {
    }

    void ServicesPool_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
#ifdef _PUS_DEBUG
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
#endif
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);

        // extract data
        if (pmt::is_u8vector(v_data)) {
                std::vector<uint8_t> inData = pmt::u8vector_elements(v_data);
                if(inData.size() < (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize)){
                	d_error_handler->reportInternalError(ErrorHandler::UnacceptablePacket);
                	return;
                }

                MessageArray in_data(inData.data(), inData.data() + inData.size());                
                Message message  = Message(in_data);

                if(!d_error_handler->assertInternal(message.getMessageVersion() == 0U, ErrorHandler::UnacceptablePacket))
                	return;
       
                if(!d_error_handler->assertInternal(message.getMessageSecondaryHeaderFlag(), ErrorHandler::UnacceptablePacket))
                	return;

                if(!d_error_handler->assertInternal(message.getMessageSequenceFlags() == 3U, ErrorHandler::UnacceptablePacket))
                	return;

                if(!d_error_handler->assertInternal(message.getMessagePacketDataLength() == (message.getMessageSize() - CCSDSPrimaryHeaderSize - 1),
                					 ErrorHandler::UnacceptablePacket))
                	return;

                if(!d_error_handler->assertRequest(message.getMessagePUSVersion() == 2U, message, ErrorHandler::UnacceptableMessage)){
#ifdef _PUS_DEBUG
                		GR_LOG_WARN(d_logger, "Error: wrong PUS version");
#endif
                	meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::FailedAcceptanceReport));
                	meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(ErrorHandler::IllegalAppData));
                	message_port_pub(PMT_VER, pmt::cons(meta, 
                				pmt::init_u8vector(inData.size(),
                							 inData.data())));          	
                	return;
                }
                in_data.pop_back();
                in_data.pop_back();
		 uint16_t crcField = CRCHelper::calculateMessageCRC(in_data); 
		 uint16_t msgCrcField = message.getMessageCRC();
		 
                if(msgCrcField != crcField ){
#ifdef _PUS_DEBUG
                		GR_LOG_WARN(d_logger, "Error: CRC error");
#endif
                	meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::FailedAcceptanceReport));
                	meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(ErrorHandler::InvalidChecksum));
                	message_port_pub(PMT_VER, pmt::cons(meta, 
                				pmt::init_u8vector(inData.size(),
                							 inData.data())));          	
                	return;               
                }         
               
                uint8_t serviceType = message.getMessageServiceType();
                if(d_services_list.size() > 1){
std::cout << " serviceType " << (uint16_t)  serviceType << std::endl; 
                	if(auto search = d_outputservices.find(serviceType); search != d_outputservices.end()){
                		message_port_pub(pmt::intern("out" + std::to_string(search->second)), pdu);    
                	}else{
#ifdef _PUS_DEBUG
                		GR_LOG_WARN(d_logger, "Error: serviceType not found");
#endif
                		meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::FailedAcceptanceReport));
                		meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(ErrorHandler::IllegalPacketType));
                		message_port_pub(PMT_VER, pmt::cons(meta, 
                				pmt::init_u8vector(inData.size(),
                							 inData.data())));           
                	}	
                }else if(d_services_list.size() == 1){
                	if( d_services_list[0] == serviceType){
                		message_port_pub(PMT_OUT, pmt::cons(meta, 
                				pmt::init_u8vector(inData.size(),
                							 inData.data())));    
                	}else{
#ifdef _PUS_DEBUG
                		GR_LOG_WARN(d_logger, "Error: serviceType not found");
#endif
                		meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::FailedAcceptanceReport));
                		meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(ErrorHandler::IllegalPacketType));
                		message_port_pub(PMT_VER, pmt::cons(meta, 
                				pmt::init_u8vector(inData.size(),
                							 inData.data())));                       		
                	}
                }else{
#ifdef _PUS_DEBUG
                	GR_LOG_WARN(d_logger, "Error: serviceType empty");
#endif
                	meta = pmt::dict_add(meta, PMT_REQ, pmt::from_long(RequestVerificationService::FailedAcceptanceReport));
                	meta = pmt::dict_add(meta, PMT_ERROR_TYPE, pmt::from_long(ErrorHandler::IllegalPacketType));
                	message_port_pub(PMT_VER, pmt::cons(meta, 
                				pmt::init_u8vector(inData.size(),
                							 inData.data())));       
		}
        } else {
#ifdef _PUS_DEBUG
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
#endif
                message_port_pub(PMT_ERROR, pdu);
        }
     }


  } /* namespace pus */
} /* namespace gr */
