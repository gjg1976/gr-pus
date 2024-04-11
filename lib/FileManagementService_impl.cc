/* -*- c++ -*- */
/*
 * Copyright 2024 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/io_signature.h>
#include "FileManagementService_impl.h"
#include <gnuradio/pus/Helpers/AllMessageTypes.h>
#include <gnuradio/pus/Helpers/FilepathValidators.h>

using namespace FilepathValidators;

namespace gr {
  namespace pus {

    FileManagementService::sptr
    FileManagementService::make(const std::string& homePath)
    {
      return gnuradio::make_block_sptr<FileManagementService_impl>(
        homePath);
    }


    /*
     * The private constructor
     */
    FileManagementService_impl::FileManagementService_impl(const std::string& homePath)
      : gr::block("FileManagementService",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)),
              homePath(homePath)
    {
    
        d_message_parser = MessageParser::getInstance();
        d_error_handler = ErrorHandler::getInstance();
        serviceType = ServiceType;
        
        for(size_t i = 0; i < FileManagementService::MessageType::end; i++)
        	counters[i] = 0;
        	
        message_port_register_in(PMT_IN);
        set_msg_handler(PMT_IN,
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
        message_port_register_out(PMT_OUT);
        message_port_register_out(PMT_VER);

        std::vector<uint8_t> STMessages;
        
        for(const auto e : All)
        	STMessages.push_back(e);
        	
	AllMessageTypes::MessagesOfService[ServiceType] = STMessages;

    }

    /*
     * Our virtual destructor.
     */
    FileManagementService_impl::~FileManagementService_impl()
    {
    }

    void FileManagementService_impl::handle_msg(pmt::pmt_t pdu)
    {
        // make sure PDU data is formed properly
        if (!(pmt::is_pair(pdu))) {
            GR_LOG_NOTICE(d_logger, "received unexpected PMT (non-pair)");
            return;
        }

        pmt::pmt_t meta = pmt::car(pdu);
        pmt::pmt_t v_data = pmt::cdr(pdu);

        // extract data
        if (pmt::is_u8vector(v_data)) {
                std::vector<uint8_t> inData = pmt::u8vector_elements(v_data);

                MessageArray in_data(inData.data(), inData.data() + inData.size());                
                Message message  = d_message_parser->ParseMessageCommand(in_data);
          
                if(serviceType == message.getMessageServiceType()){
                    switch (message.getMessageType()) {
                        case CreateFile:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "CreateFile");
#endif
                           createFile(message);
                           break;
                        case DeleteFile:   
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeleteFile");
#endif
                           deleteFile(message);
                           break;                                             
                        case ReportAttributes:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportAttributes");
#endif
                           reportAttributes(message);
                           break;
                        case LockFile:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "LockFile");
#endif
                           lockFile(message);
                           break;
                        case UnlockFile:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "UnlockFile");
#endif
                           unlockFile(message);
                           break;
                        case FindFile:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "FindFile");
#endif
                           findFile(message);
                           break;
                        case CreateDirectory:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "CreateDirectory");
#endif
                           createDirectory(message);
                           break;
                        case DeleteDirectory:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "DeleteDirectory");
#endif
                           deleteDirectory(message);				
                           break;
                        case RenameDirectory:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "RenameDirectory");
#endif
                           renameDirectory(message);				
                           break;
                        case ReportSummaryDirectory:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "ReportSummaryDirectory");
#endif
                           reportSummaryDirectory(message);				
                           break;
                        case CopyFile:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "CopyFile");
#endif
                           copyFile(message);
                           break;
                        case MoveFile:    
#ifdef _PUS_DEBUG
                           GR_LOG_WARN(d_logger, "MoveFile");
#endif
                           moveFile(message);
                           break;
                        default:
#ifdef _PUS_DEBUG
			    GR_LOG_WARN(d_logger, "File Management Service: Wrong serviceSubType");
#endif
			    reportAcceptanceError(message, ErrorHandler::IllegalPacketSubType);			   
                    }
               }else{
#ifdef _PUS_DEBUG
		    GR_LOG_WARN(d_logger, "File Management Service: Wrong serviceType");
#endif
		    reportAcceptanceError(message, ErrorHandler::IllegalPacketType);

               }

        } else {
                GR_LOG_WARN(d_logger, "Error: the input data is not a u8vector");
        }
     }

void FileManagementService_impl::createFile(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::CreateFile)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);

 	if(tcSize < FILE_MAN_STR_SIZE * 2 + FILE_MAN_MAX_FILE_SIZE + FILE_MAN_LOCK_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto fileName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or fileName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
		
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + fileName.length() + FILE_MAN_STR_SIZE + FILE_MAN_MAX_FILE_SIZE + FILE_MAN_LOCK_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	
	
	auto fullPath = getFullPath(repositoryPath, fileName);

	if (findWildcardPosition(fullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	uint32_t maxFileSizeBytes = request.readUint32();
	if (maxFileSizeBytes > MaxPossibleFileSizeBytes) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::SizeOfFileIsOutOfBounds);
		return;
	}

	bool isFileLocked = request.readBoolean();

	reportSuccessStartExecutionVerification(request);
	
	if (auto fileCreationError = Filesystem::createFile(fullPath)) {
		switch (fileCreationError.value()) {
			case Filesystem::FileCreationError::FileAlreadyExists: {
				reportExecutionCompletionError(request,
				                          ErrorHandler::ExecutionCompletionErrorType::FileAlreadyExists);
				return;
			}
			default: {
				reportExecutionCompletionError(request,
				                          ErrorHandler::ExecutionCompletionErrorType::UnknownExecutionCompletionError);
				return;
			}
		}
	}

	if (isFileLocked) {
		Filesystem::lockFile(fullPath);
	}
		
	reportSuccessCompletionExecutionVerification(request);	
}

void FileManagementService_impl::deleteFile(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::DeleteFile)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (2 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto fileName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or fileName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + fileName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	
		
	auto fullPath = getFullPath(repositoryPath, fileName);

	if (findWildcardPosition(fullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	
	reportSuccessStartExecutionVerification(request);
	
	if (auto fileDeletionError = Filesystem::deleteFile(fullPath)) {
		using Filesystem::FileDeletionError;
		switch (fileDeletionError.value()) {
			case FileDeletionError::FileDoesNotExist:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::ObjectDoesNotExist);
				break;
			case FileDeletionError::PathLeadsToDirectory:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AttemptedDeleteOnDirectory);
				break;
			case FileDeletionError::FileIsLocked:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AttemptedDeleteOnLockedFile);
				break;
			default:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::UnknownFileDeleteError);
				break;
		}
	}else{
		reportSuccessCompletionExecutionVerification(request);
	}	
}

void FileManagementService_impl::reportAttributes(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::ReportAttributes)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (2 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto fileName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or fileName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + fileName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	
	
	auto fullPath = getFullPath(repositoryPath, fileName);
	if (findWildcardPosition(fullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	reportSuccessStartExecutionVerification(request);
	Filesystem::Attributes attributes;	
	if (auto fileAttributeError = Filesystem::getFileAttributes(fullPath, attributes)) {
		using Filesystem::FileAttributeError;
		switch (fileAttributeError.value()) {
			case FileAttributeError::FileDoesNotExist:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::ObjectDoesNotExist);
				break;
			case FileAttributeError::PathLeadsToDirectory:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AttemptedReportAttributesOnDirectory);
				break;
			default:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::UnknownFileAttributeError);
				break;
		}
	}else{
		repositoryPath.append("/");
		fileAttributeReport(repositoryPath, fileName, attributes);
		reportSuccessCompletionExecutionVerification(request);
	}	
}

void FileManagementService_impl::fileAttributeReport(ObjectPath& repositoryPath, ObjectPath& fileName, const Filesystem::Attributes& attributes) {
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			FileManagementService::MessageType::CreateAttributesReport, 
			counters[FileManagementService::MessageType::CreateAttributesReport], 0);

	report.appendOctetString(repositoryPath);
	report.appendOctetString(fileName);
	report.appendUint32(attributes.sizeInBytes);
	report.appendBoolean(attributes.isLocked);
		
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[FileManagementService::MessageType::CreateAttributesReport]++;	
}

void FileManagementService_impl::lockFile(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::LockFile)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (2 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto fileName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or fileName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + fileName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	auto fullPath = getFullPath(repositoryPath, fileName);

	if (findWildcardPosition(fullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	reportSuccessStartExecutionVerification(request);

	Filesystem::lockFile(fullPath);

	reportSuccessCompletionExecutionVerification(request);	
}

void FileManagementService_impl::unlockFile(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::UnlockFile)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (2 * FILE_MAN_STR_SIZE)){        
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto fileName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or fileName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + fileName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);	
		
	auto fullPath = getFullPath(repositoryPath, fileName);

	if (findWildcardPosition(fullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	reportSuccessStartExecutionVerification(request);

	Filesystem::unlockFile(fullPath);

	reportSuccessCompletionExecutionVerification(request);	
}

void FileManagementService_impl::findFile(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::FindFile)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (2 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto searchPattern = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or searchPattern.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}	
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + searchPattern.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	if (findWildcardPosition(repositoryPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	reportSuccessStartExecutionVerification(request);
		
	foundFileReport(repositoryPath, searchPattern);
	
	reportSuccessCompletionExecutionVerification(request);
}

void FileManagementService_impl::foundFileReport(Filesystem::ObjectPath& repositoryPath, Filesystem::ObjectPath& searchPattern)
{
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			FileManagementService::MessageType::FoundFileReport, 
			counters[FileManagementService::MessageType::FoundFileReport], 0);

	Filesystem::SearchContent searchContent = Filesystem::findFile(repositoryPath, searchPattern);
	
	report.appendOctetString(repositoryPath);
	report.appendOctetString(searchPattern);
	report.appendUint16(searchContent.size());
	for(auto& content: searchContent){
		report.appendOctetString(content);
	}
	
			
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[FileManagementService::MessageType::FoundFileReport]++;
}

void FileManagementService_impl::createDirectory(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::CreateDirectory)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (2 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto dirName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or dirName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}		
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + dirName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	auto fullPath = getFullPath(repositoryPath, dirName);

	if (findWildcardPosition(fullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	reportSuccessStartExecutionVerification(request);
	
	if (auto dirCreationError = Filesystem::createDirectory(fullPath)) {
		switch (dirCreationError.value()) {

			using Filesystem::DirectoryCreationError;
			case DirectoryCreationError::DirectoryAlreadyExists: {
				reportExecutionCompletionError(request,
				                          ErrorHandler::ExecutionCompletionErrorType::DirAlreadyExists);
				return;
			}
			default: {
				reportExecutionCompletionError(request,
				                          ErrorHandler::ExecutionCompletionErrorType::UnknownExecutionCompletionError);
				return;
			}
		}
	}
		
	reportSuccessCompletionExecutionVerification(request);	
}

void FileManagementService_impl::deleteDirectory(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::DeleteDirectory)) {
		return;
	}
 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (2 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto dirName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 or dirName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + dirName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	auto fullPath = getFullPath(repositoryPath, dirName);

	if (findWildcardPosition(fullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	reportSuccessStartExecutionVerification(request);
	if (auto dirDeletionError = Filesystem::deleteDirectory(fullPath)) {
		switch (dirDeletionError.value()) {
			using Filesystem::DirectoryDeletionError;
			case DirectoryDeletionError::DirectoryDoesNotExist:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::ObjectDoesNotExist);
				break;
			case DirectoryDeletionError::DirectoryIsNotEmpty:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AttemptedDeleteANonEmptyDir);
				break;				
				
			default:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::UnknownDirDeleteError);
				break;
		}
	}else{
		reportSuccessCompletionExecutionVerification(request);
	}	
}

void FileManagementService_impl::renameDirectory(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::RenameDirectory)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (3 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto srcDirName = request.readOctetString<Filesystem::ObjectPathSize>();
	auto dstDirName = request.readOctetString<Filesystem::ObjectPathSize>();
	
	if(repositoryPath.length() == 0 or srcDirName.length() == 0 or dstDirName.length() == 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE + srcDirName.length() + FILE_MAN_STR_SIZE + dstDirName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);	
		
	auto srcFullPath = getFullPath(repositoryPath, srcDirName);
	auto dstFullPath = getFullPath(repositoryPath, dstDirName);
	
	if (findWildcardPosition(srcFullPath) or findWildcardPosition(dstFullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	reportSuccessStartExecutionVerification(request);
	if (auto dirRenameError = Filesystem::renameDirectory(srcFullPath, dstFullPath)) {
		switch (dirRenameError.value()) {
			using Filesystem::DirectoryRenameError;
			case DirectoryRenameError::SrcDirectoryDoesNotExist:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::ObjectDoesNotExist);
				break;
			case DirectoryRenameError::DstDirectoryDoesExist:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::DirAlreadyExists);
				break;				
			default:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::UnknownDirRenameError);
				break;
		}
	}else{
		reportSuccessCompletionExecutionVerification(request);
	}
}
	
void FileManagementService_impl::reportSummaryDirectory(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::ReportSummaryDirectory)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < FILE_MAN_STR_SIZE){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	auto repositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	if(repositoryPath.length() == 0 ){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
  	tcSize -= repositoryPath.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	reportSuccessAcceptanceVerification(request);	
	
	if (findWildcardPosition(repositoryPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto repositoryType = Filesystem::getNodeType(repositoryPath);
	if (not repositoryType) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	
	reportSuccessStartExecutionVerification(request);
	
	if (repositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	
	summaryDirectoryReport(repositoryPath);
	
	reportSuccessCompletionExecutionVerification(request);
}
	
void FileManagementService_impl::summaryDirectoryReport(Filesystem::ObjectPath& repositoryPath)
{
        Message report = d_message_parser->CreateEmptyMessageReport(0, serviceType, 
			FileManagementService::MessageType::SummaryDirectoryReport, 
			counters[FileManagementService::MessageType::SummaryDirectoryReport], 0);

	Filesystem::DirContent dirContent = Filesystem::getDirContent(repositoryPath);
	
	report.appendOctetString(repositoryPath);
	report.appendUint16(dirContent.size());
	for(auto& content: dirContent){
		report.appendUint8((uint8_t)content.first);
		report.appendOctetString(content.second);
	}
	d_message_parser->closeMessage(report);
			
        message_port_pub(PMT_OUT, pmt::cons(pmt::PMT_NIL, 
                				pmt::init_u8vector(report.getMessageData().size(), report.getMessageRawData())));

        counters[FileManagementService::MessageType::SummaryDirectoryReport]++;

}
	
void FileManagementService_impl::copyFile(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::CopyFile)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (4 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	uint16_t operationID =  request.readUint16();
	
	auto srcRepositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto srcFileName = request.readOctetString<Filesystem::ObjectPathSize>();
	auto dstRepositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto dstFileName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(srcRepositoryPath.length() == 0 or srcFileName.length() == 0 or dstRepositoryPath.length() == 0 or dstFileName.length() == 0){
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
  	tcSize -= FILE_MAN_COPY_ID_SIZE + srcRepositoryPath.length() + FILE_MAN_STR_SIZE + srcFileName.length() + FILE_MAN_STR_SIZE + dstRepositoryPath.length() + FILE_MAN_STR_SIZE + dstFileName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	
		
	auto srcFullPath = getFullPath(srcRepositoryPath, srcFileName);
	auto dstFullPath = getFullPath(dstRepositoryPath, dstFileName);

	if (findWildcardPosition(srcFullPath) or findWildcardPosition(dstFullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto srcRepositoryType = Filesystem::getNodeType(srcRepositoryPath);
	auto dstRepositoryType = Filesystem::getNodeType(dstRepositoryPath);
	if ((not srcRepositoryType) or (not dstRepositoryType)) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	if (srcRepositoryType.value() != Filesystem::NodeType::Directory or dstRepositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	
	reportSuccessStartExecutionVerification(request);
	
	if (auto fileCopyError = Filesystem::copyFile(srcFullPath, dstFullPath)) {
		switch (fileCopyError.value()) {
			using Filesystem::FileCopyError;
			case FileCopyError::SrcFileDoesNotExist:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::ObjectDoesNotExist);
				break;
			case FileCopyError::DstFileAlreadyExists:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::FileAlreadyExists);
				break;	
			default:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AttemptedMoveALockedFile);
				break;
		}
	}else{
		reportSuccessCompletionExecutionVerification(request);
	}

}
	
void FileManagementService_impl::moveFile(Message& request) {
	if (!d_message_parser->assertTC(request, serviceType, 
			FileManagementService::MessageType::MoveFile)) {
		return;
	}

 	uint16_t tcSize = request.getMessageSize() - (CCSDSPrimaryHeaderSize + ECSSSecondaryTCHeaderSize + ECSSSecondaryTCCRCSize);
	
 	if(tcSize < (4 * FILE_MAN_STR_SIZE)){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}

	uint16_t operationID =  request.readUint16();

	
	auto srcRepositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto srcFileName = request.readOctetString<Filesystem::ObjectPathSize>();
	auto dstRepositoryPath = request.readOctetString<Filesystem::ObjectPathSize>();
	auto dstFileName = request.readOctetString<Filesystem::ObjectPathSize>();
	if(srcRepositoryPath.length() == 0 or srcFileName.length() == 0 or dstRepositoryPath.length() == 0 or dstFileName.length() == 0){
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
  	tcSize -= FILE_MAN_MOVE_ID_SIZE + srcRepositoryPath.length() + FILE_MAN_STR_SIZE + srcFileName.length() + FILE_MAN_STR_SIZE + dstRepositoryPath.length() + FILE_MAN_STR_SIZE + dstFileName.length() + FILE_MAN_STR_SIZE;

	if(tcSize != 0){     
		reportAcceptanceError(request, ErrorHandler::InvalidLength);
		return;
	}
	
	reportSuccessAcceptanceVerification(request);	
		
	auto srcFullPath = getFullPath(srcRepositoryPath, srcFileName);
	auto dstFullPath = getFullPath(dstRepositoryPath, dstFileName);
	
	if (findWildcardPosition(srcFullPath) or findWildcardPosition(dstFullPath)) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}

	auto srcRepositoryType = Filesystem::getNodeType(srcRepositoryPath);
	auto dstRepositoryType = Filesystem::getNodeType(dstRepositoryPath);
	if ((not srcRepositoryType) or (not dstRepositoryType)) {
		reportExecutionStartError(request,
		                          ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	


	if (srcRepositoryType.value() != Filesystem::NodeType::Directory or dstRepositoryType.value() != Filesystem::NodeType::Directory) {
		reportExecutionStartError(request, ErrorHandler::ExecutionStartErrorType::ObjectPathIsInvalid);
		return;
	}
	
	reportSuccessStartExecutionVerification(request);

	if (auto fileMoveError = Filesystem::moveFile(srcFullPath, dstFullPath)) {
		switch (fileMoveError.value()) {
			using Filesystem::FileMoveError;
			case FileMoveError::SrcFileDoesNotExist:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::ObjectDoesNotExist);
				break;
			case FileMoveError::DstFileAlreadyExists:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::FileAlreadyExists);
				break;				
			case FileMoveError::SrcFileIsLocked:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::AttemptedMoveALockedFile);
				break;		
			default:
				reportExecutionCompletionError(request, ErrorHandler::ExecutionCompletionErrorType::UnknownFileMoveError);
				break;
		}
	}else{
		reportSuccessCompletionExecutionVerification(request);
	}	
}


  } /* namespace pus */
} /* namespace gr */
