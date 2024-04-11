/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_ALLMESSAGETYPES_H
#define ECSS_ALLMESSAGETYPES_H

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <map>
#include <vector>

namespace gr {
  namespace pus {
/**
 * Namespace containing all the message types for every service type.
 */
    namespace AllMessageTypes {
	/**
	 * Map containing all the message types, per service. The key is the ServiceType and the value,
	 * an etl vector containing the message types.
	 */
	extern std::map<uint8_t, std::vector<uint8_t>> MessagesOfService;

    }// namespace AllMessageTypes
  } /* namespace pus */
} /* namespace gr */
#endif
