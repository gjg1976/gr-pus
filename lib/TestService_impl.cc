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
#include "TestService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {

    TestService::sptr
    TestService::make()
    {
      return gnuradio::make_block_sptr<TestService_impl>();
    }


    /*
     * The private constructor
     */
    TestService_impl::TestService_impl()
      : gr::block("TestService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        serviceType = ServiceType;
        for(size_t i = 0; i < TestService::MessageType::end; i++)
        	counters[i] = 0;
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;

    }

    /*
     * Our virtual destructor.
     */
    TestService_impl::~TestService_impl()
    {
    }
    
    void TestService_impl::storeMessage(Message& report)
    {
	message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
               	pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
    }

    void TestService_impl::areYouAlive(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, TestService::MessageType::AreYouAliveTest)) {
		return;
	}
  	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}  	       
	reportSuccessAcceptanceVerification(request);
	reportSuccessStartExecutionVerification(request);
	
        counters[TestService::MessageType::AreYouAliveTest]++;
	areYouAliveReport();

	reportSuccessCompletionExecutionVerification(request);
    }

    void TestService_impl::areYouAliveReport() {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			TestService::MessageType::AreYouAliveTestReport, 
			counters[TestService::MessageType::AreYouAliveTestReport], 0);

        d_message_parser->closeMessage(report);
        	
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));
        
        counters[TestService::MessageType::AreYouAliveTestReport]++;
    }

    void TestService_impl::onBoardConnection(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, TestService::MessageType::OnBoardConnectionTest)) {
		return;
	}
  	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
 	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}           
	reportSuccessAcceptanceVerification(request);
        counters[TestService::MessageType::OnBoardConnectionTest]++;
	uint16_t applicationProcessId = d_message_parser->getApplicationId();

	reportSuccessStartExecutionVerification(request);

	onBoardConnectionReport(applicationProcessId);
	
	reportSuccessCompletionExecutionVerification(request);
    }

    void TestService_impl::onBoardConnectionReport(uint16_t applicationProcessId) {
       
         Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			TestService::MessageType::OnBoardConnectionTestReport, 
			counters[TestService::MessageType::OnBoardConnectionTestReport], 0);
			
 	 report.appendUint16(applicationProcessId);
 	 
        d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[TestService::MessageType::OnBoardConnectionTestReport]++;
    }

    void TestService_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);

        // extract data
        if (pmt::is_u8vector(v_data)) {

                std::vector<uint8_t> inData = pmt::u8vector_elements(v_data);

                MessageArray in_data(inData.data(), inData.data() + inData.size());                
                Message message  = d_message_parser->ParseMessageCommand(in_data);

                if(serviceType == message.getMessageServiceType()){

                    switch (message.getMessageType()) {
                        case AreYouAliveTest:
  
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "AreYouAliveTest");
#endif
			   areYouAlive(message);
			   break;
                        case OnBoardConnectionTest:

#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "OnBoardConnectionTest");
#endif
			   onBoardConnection(message);
			   break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "Test Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "Test Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);
               }

        } else {
#ifdef _PUS_DEBUG
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
#endif
        }
     }
  } /* namespace pus */
} /* namespace gr */
