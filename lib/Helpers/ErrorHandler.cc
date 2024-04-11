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
#include <gnuradio/pus/Helpers/ErrorHandler.h>

namespace gr {
  namespace pus {

    ErrorHandler* ErrorHandler::inst_errorhandler = NULL;
    
    ErrorHandler::ErrorHandler() 
    {
    }
    
    ErrorHandler* ErrorHandler::getInstance()
    {
       if(inst_errorhandler == NULL)
           inst_errorhandler = new ErrorHandler();
       
       return inst_errorhandler;
    }

    void ErrorHandler::reportInternalError(InternalErrorType errorCode)
    {
       printf("Internal Error: %u\n", (uint16_t)errorCode);	
    }	
    
    void ErrorHandler::reportError(Message& message, AcceptanceErrorType errorCode)
    {
       // 	Services.requestVerification.failAcceptanceVerification(message, errorCode);
       
       printf("Acceptance Error [%u,%u]: %u\n",
                            (uint16_t)message.getMessageServiceType(), (uint16_t)message.getMessageType(),
                             (uint16_t)errorCode);	
    }
    
    void ErrorHandler::reportError(RoutingErrorType errorCode)
    {
       // 	Services.requestVerification.failRoutingVerification(message, errorCode);
       printf("Routing Error: %u\n", (uint16_t)errorCode);	 
    }  
      
    void ErrorHandler::reportError(Message& message, ExecutionStartErrorType errorCode)
    {
       // 	Services.requestVerification.failStartExecutionVerification(message, errorCode);
       printf("Exec. Start Error [%u,%u]: %u \n",
                            (uint16_t)message.getMessageServiceType(), (uint16_t)message.getMessageType(), (uint16_t)errorCode );
    }
 
    void ErrorHandler::reportError(Message& message, ExecutionProgressErrorType errorCode, uint8_t stepID)
    {
       // 	Services.requestVerification.failProgressExecutionVerification(message, errorCode, stepID);
       printf("Exec. Progress Error [%u,%u]: %u on step %u\n",
                            (uint16_t)message.getMessageServiceType(), (uint16_t)message.getMessageType(), (uint16_t)errorCode, (uint16_t)stepID);
    }
	
    void ErrorHandler::reportError(Message& message, ExecutionCompletionErrorType errorCode)
    {
       // 	Services.requestVerification.failCompletionExecutionVerification(message, errorCode);
       printf("Exec. Completion Error [%u,%u]: %u\n",
                            (uint16_t)message.getMessageServiceType(), (uint16_t)message.getMessageType(), (uint16_t) errorCode);
    }    

  } /* namespace pus */
} /* namespace gr */
