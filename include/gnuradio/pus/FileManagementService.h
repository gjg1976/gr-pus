/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */


#ifndef INCLUDED_PUS_FILEMANAGEMENTSERVICE_H
#define INCLUDED_PUS_FILEMANAGEMENTSERVICE_H

#include <gnuradio/pus/api.h>
#include <gnuradio/block.h>
#include <gnuradio/pus/Service.h>
#include <gnuradio/pus/Helpers/MessageParser.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include <gnuradio/pus/Helpers/Filesystem.h>

namespace gr {
  namespace pus {

    /*!
     * \brief <+description of block+>
     * \ingroup pus
     *
     */
    class PUS_API FileManagementService : virtual public gr::block,
    				 virtual public gr::pus::Service
    {
     public:
	inline static const uint8_t ServiceType = 23;

	enum MessageType : uint8_t {
		CreateFile = 1,
		DeleteFile = 2,
		ReportAttributes = 3,
		CreateAttributesReport = 4,
		LockFile = 5,
		UnlockFile = 6,
		FindFile = 7,
		FoundFileReport = 8,
		CreateDirectory = 9,
		DeleteDirectory = 10,
		RenameDirectory = 11,
		ReportSummaryDirectory = 12,
		SummaryDirectoryReport = 13,
		CopyFile = 14,
		MoveFile = 15,
		SuspendFileCopyOperation = 16,
		ResumeFileCopyOperation = 17,
		AbortFileCopyOperation = 18,
		SuspendFileCopyOperationInPath = 19,
		ResumeFileCopyOperationInPath = 20,
		AbortFileCopyOperationInPath = 21,
		EnablePeriodicReportingOfFileCopy = 22,
		FileCopyStatusReport = 23,
		DisablePeriodicReportingOfFileCopy = 24,
		end = 25
	};	

	uint8_t All[24] = {
		CreateFile,
		DeleteFile,
		ReportAttributes,
		CreateAttributesReport,
		LockFile,
		UnlockFile,
		FindFile,
		FoundFileReport,
		CreateDirectory,
		DeleteDirectory,
		RenameDirectory,
		ReportSummaryDirectory,
		SummaryDirectoryReport,
		CopyFile,
		MoveFile,
		SuspendFileCopyOperation,
		ResumeFileCopyOperation,
		AbortFileCopyOperation,
		SuspendFileCopyOperationInPath,
		ResumeFileCopyOperationInPath,
		AbortFileCopyOperationInPath,
		EnablePeriodicReportingOfFileCopy,
		FileCopyStatusReport,
		DisablePeriodicReportingOfFileCopy
	 };

	/**
     * The wildcard character accepted by the service
     */
	inline static constexpr char Wildcard = '*';

	/**
	 * The maximum possible size of a file, in bytes.
	 */
	inline static constexpr size_t MaxPossibleFileSizeBytes = 4096;
	
      typedef std::shared_ptr<FileManagementService> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of pus::FileManagementService.
       *
       * To avoid accidental use of raw pointers, pus::FileManagementService's
       * constructor is in a private implementation
       * class. pus::FileManagementService::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& homePath);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_FILEMANAGEMENTSERVICE_H */
