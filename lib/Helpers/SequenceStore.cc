/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
 
#include <gnuradio/pus/Helpers/SequenceStore.h>
#include <iostream>

namespace gr {
  namespace pus {
  
uint16_t SequenceStore::calculateSequenceCRC() {
	uint16_t shiftReg = 0xFFFFU;
	for (auto& activity: sequenceActivities) {
		shiftReg = CRCHelper::calculateMessageCRC(activity.request.getMessageData(), shiftReg);
		uint32_t delay = activity.requestDelayTime.formatAsBytes();
		MessageArray delay_vector = {static_cast<uint8_t>((delay >> 24) & 0xFF),
							static_cast<uint8_t>((delay >> 16) & 0xFF),
							static_cast<uint8_t>((delay >> 8) & 0xFF),
							static_cast<uint8_t>(delay & 0xFF)};

		shiftReg = CRCHelper::calculateMessageCRC(delay_vector, shiftReg);
	}	
	return shiftReg;
}

void SequenceStore::activated() 
{
	currentStep = sequenceActivities.begin(); 
	sequenceStatus = Execution; 
	countDown = 0;
}

void SequenceStore::abort() 
{
	currentStep = sequenceActivities.end();
	sequenceStatus = Inactive;
	countDown = 0;
};

SequenceStore::MessageList SequenceStore::step()
{
	MessageList messages_list;
	if(sequenceStatus == Execution){
		while(countDown == 0){
			if(currentStep == sequenceActivities.end()){
				abort();
				break;
			}
			if (messages_list.size() == ECSSMaxNumberOfReleasedSequenceActivities)
				break;
			messages_list.push_back(&(currentStep->request));
			
			static_assert(std::is_same_v<uint32_t, decltype(TimeStamp<4, 0, 1, 1>(currentStep->requestDelayTime.asTAIseconds()).formatAsBytes())>, "The conan-profile timestamp should be 4 bytes");
			countDown = TimeStamp<4, 0, 1, 1>(currentStep->requestDelayTime.asTAIseconds()).formatAsBytes();
			currentStep++;
		}
		if(countDown > 0)
			countDown--;
	}
	return messages_list;
}
  } // namespace pus
} // namespace gr
