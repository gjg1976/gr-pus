/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_LARGEMESSAGEDETECTOR_IMPL_H
#define INCLUDED_PUS_LARGEMESSAGEDETECTOR_IMPL_H

#include <gnuradio/pus/LargeMessageDetector.h>
#include <gnuradio/pus/Definitions/pmt_constants.h>
#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include "etl/vector.h"
namespace gr {
  namespace pus {

    class LargeMessageDetector_impl : public LargeMessageDetector
    {
     private:
      // Nothing to declare in this block.

     public:
      LargeMessageDetector_impl();
      ~LargeMessageDetector_impl();

	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
      void handle_msg(pmt::pmt_t pdu);

    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_LARGEMESSAGEDETECTOR_IMPL_H */
