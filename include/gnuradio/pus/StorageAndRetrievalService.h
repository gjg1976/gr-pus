/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_STORAGEANDRETRIEVALSERVICE_H
#define INCLUDED_PUS_STORAGEANDRETRIEVALSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/sync_block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API StorageAndRetrievalService : virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 15;

	enum MessageType : uint8_t {
		EnableStorageInPacketStores = 1,
		DisableStorageInPacketStores = 2,
		AddPacketsDefinitionsToPacketStores = 3,
		RemovePacketsDefinitionsFromPacketStores = 4,
		ReportContentAPIDStoreConfig = 5,
		ContentAPIDStoreConfigReport = 6,	
		StartByTimeRangeRetrieval = 9,
		DeletePacketStoreContent = 11,
		ReportContentSummaryOfPacketStores = 12,
		PacketStoreContentSummaryReport = 13,
		ChangeOpenRetrievalStartingTime = 14,
		ResumeOpenRetrievalOfPacketStores = 15,
		SuspendOpenRetrievalOfPacketStores = 16,
		AbortByTimeRangeRetrieval = 17,
		ReportStatusOfPacketStores = 18,
		PacketStoresStatusReport = 19,
		CreatePacketStores = 20,
		DeletePacketStores = 21,
		ReportConfigurationOfPacketStores = 22,
		PacketStoreConfigurationReport = 23,
		CopyPacketsInTimeWindow = 24,
		ResizePacketStores = 25,
		ChangeTypeToCircular = 26,
		ChangeTypeToBounded = 27,
		ChangeVirtualChannel = 28,
		end = 29
	};
	uint8_t All[25] = {
		EnableStorageInPacketStores,
		DisableStorageInPacketStores,
		AddPacketsDefinitionsToPacketStores,
		RemovePacketsDefinitionsFromPacketStores,
		ReportContentAPIDStoreConfig,
		ContentAPIDStoreConfigReport,	
		StartByTimeRangeRetrieval,
		DeletePacketStoreContent,
		ReportContentSummaryOfPacketStores,
		PacketStoreContentSummaryReport,
		ChangeOpenRetrievalStartingTime,
		ResumeOpenRetrievalOfPacketStores,
		SuspendOpenRetrievalOfPacketStores,
		AbortByTimeRangeRetrieval,
		ReportStatusOfPacketStores,
		PacketStoresStatusReport,
		CreatePacketStores,
		DeletePacketStores,
		ReportConfigurationOfPacketStores,
		PacketStoreConfigurationReport,
		CopyPacketsInTimeWindow,
		ResizePacketStores,
		ChangeTypeToCircular,
		ChangeTypeToBounded,
		ChangeVirtualChannel
	 };
	 
      typedef std::shared_ptr<StorageAndRetrievalService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::StorageAndRetrievalService.
       *
       * To avoid accidental use of raw pointers, pus::StorageAndRetrievalService's
       * constructor is in a private implementation
       * class. pus::StorageAndRetrievalService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& init_file, std::vector<uint16_t> vc_list, double samples_per_sec);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_STORAGEANDRETRIEVALSERVICE_H */
