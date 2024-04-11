/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 
#include <gnuradio/pus/Helpers/PacketStore.h>

namespace gr {
 namespace pus {
 
	uint16_t PacketStore::calculateSizeInBytes() {
		uint16_t size = 0;
		for (auto& tmPacket : storedTelemetryPackets) {
			size += tmPacket.second.getMessageSize();
		}
		return size;
	}
	
	std::vector<uint16_t> PacketStore::getApplicationsInStore()
	{
		std::vector<uint16_t> appIDList;

		for (auto& definition: definitions) {		
			auto appServicePair = definition.first;

			if (std::find(appIDList.begin(), 
					appIDList.end(), appServicePair.first) ==
	   			 appIDList.end()) {
				appIDList.push_back(appServicePair.first);

			}			
		}
		return appIDList;		
	}
  } // namespace pus
} // namespace gr
