/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/pus/Time/Time.h>

namespace gr {
  namespace pus {
	namespace Time {
		struct epoch Epoch{
	    		1980,
	    		1,
	    		6,
		};
    }    
  } /* namespace pus */
} /* namespace gr */
