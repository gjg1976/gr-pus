/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef ECSS_SERVICES_SERVICE_HPP
#define ECSS_SERVICES_SERVICE_HPP

#include <cstdint>
#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>

/**
 * @defgroup Services Services
 * ECSS Services implementations, as defined in ECSS-E-ST-70-41C. These services receive TC Messages, and output TM
 * Messages.
 */

/**
 * A spacecraft service, as defined in ECSS-E-ST-70-41C
 *
 * A member of the Service class should be used as a singleton, i.e. must be created only once in
 * the code
 */
 namespace gr {
  namespace pus {
   
   class Service : virtual public gr::block
   {
    private:
	uint16_t messageTypeCounter = 0;

    protected:	
	
	MessageParser* d_message_parser;
	ErrorHandler* d_error_handler;

	/**
	 * TM[1,1] successful acceptance verification report
	 */     
    void reportSuccessAcceptanceVerification(Message& request);
    
	/**
	 * TM[1,2] failed acceptance verification report
	 */
    void reportAcceptanceError(Message& request, ErrorHandler::AcceptanceErrorType errorCode);   
     
	/**
	 * TM[1,3] successful start of execution verification report
	 */
    void reportSuccessStartExecutionVerification(Message& request);
    
	/**
	 * TM[1,4] failed start of execution verification report
	 */             
    void reportExecutionStartError(Message& request, ErrorHandler::ExecutionStartErrorType errorCode);   

	/**
	 * TM[1,5] successful progress of execution verification report
	 */
    void reportSuccessProgressExecutionVerification(Message& request, uint8_t stepID);
    
	/**
	 * TM[1,6] failed progress of execution verification report
	 */        
    void reportExecutionProgressError(Message& request, ErrorHandler::ExecutionProgressErrorType errorCode, uint8_t stepID);    


	/**
	 * TM[1,7] successful completion of execution verification report
	 */
    void reportSuccessCompletionExecutionVerification(Message& request);
 
	/**
	 * TM[1,8] failed completion of execution verification report
	 */        
    void reportExecutionCompletionError(Message& request, ErrorHandler::ExecutionCompletionErrorType errorCode);    

	/**
	 * TM[1,10] failed routing verification report
 	 */            
    void failRoutingVerification(Message& request, ErrorHandler::RoutingErrorType errorCode); 

	/**
	 * The service type of this Service. For example, ST[12]'s serviceType is `12`.
	 * Specify this value in the constructor of your service.
	 */
	uint8_t serviceType{};

	/**
	 * Creates a new empty telemetry package originating from this service
	 *
	 * @param messageType The ID of the message type, as specified in the standard. For example,
	 *                    the TC[17,3] message has `messageType = 3`.
	 * @todo See if the Message must be returned by reference
	 */
	Message createTM(uint8_t messageType) const {
		return Message();//serviceType, messageType, Message::TM);
	}

	/**
	 * Stores a message so that it can be transmitted to the ground station
	 *
	 * Note: For now, since we don't have any mechanisms to queue messages and send them later,
	 * we just print the message to the screen
	 */
	void storeMessage(Message& message);

	/**
	 * This function declared only to remind us that every service must have a function like
	 * this, but this particular function does actually nothing.
	 */
	void execute(Message& message);

	/**
	 * Default protected constructor for this Service
	 */
	Service() = default;

    public:
	/**
	 * @brief Unimplemented copy constructor
	 *
	 * Does not allow Services should be copied. There should be only one instance for each Service.
	 */
	Service(Service const&) = delete;

	/**
	 * Unimplemented assignment operation
	 *
	 * Does not allow changing the instances of Services, as Services are singletons.
	 */
	void operator=(Service const&) = delete;

	/**
	 * Default destructor
	 */
	~Service() = default;

	/**
	 * Default move constructor
	 */
	Service(Service&& service) noexcept = default;

	/**
	 * Default move assignment operator
	 */
	Service& operator=(Service&& service) noexcept = default;
   };

  } // namespace pus
} // namespace gr
#endif // ECSS_SERVICES_SERVICE_HPP
