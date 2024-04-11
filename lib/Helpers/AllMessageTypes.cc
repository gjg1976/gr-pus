/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/pus/Helpers/AllMessageTypes.h>
namespace gr {
  namespace pus {
    namespace AllMessageTypes {
	std::map<uint8_t, std::vector<uint8_t>> MessagesOfService;

    } // namespace AllMessageTypes
  } /* namespace pus */
} /* namespace gr */
