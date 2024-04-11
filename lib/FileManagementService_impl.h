/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_PUS_FILEMANAGEMENTSERVICE_IMPL_H
#define INCLUDED_PUS_FILEMANAGEMENTSERVICE_IMPL_H

#include <gnuradio/pus/FileManagementService.h>
#include "etl/string_utilities.h"

#define FILE_MAN_STR_SIZE 2
#define FILE_MAN_MAX_FILE_SIZE 4
#define FILE_MAN_LOCK_SIZE 1
#define FILE_MAN_COPY_ID_SIZE 2
#define FILE_MAN_MOVE_ID_SIZE 2

namespace gr {
  namespace pus {

    class FileManagementService_impl : public FileManagementService
    {
     private:
      uint16_t counters[FileManagementService::MessageType::end];
      std::string homePath = "./";

	using ObjectPath = Filesystem::ObjectPath;
	using Path = Filesystem::Path;

	/**
	 * Returns the full filesystem path for an object given the repository path and the file path
	 * @param repositoryPath The repository path
	 * @param filePath The file path
	 * @return The full path, where the repository path and file path are separated by a single '/' (slash)
	 *
	 * @note All leading and trailing slashes are removed from the repositoryPath and filePath objects.
	 */
	inline Path getFullPath(ObjectPath& repositoryPath, ObjectPath& filePath) {
		etl::trim_from_left(repositoryPath, "/");
		etl::trim_from_right(repositoryPath, "/");

		etl::trim_from_left(filePath, "/");
		etl::trim_from_right(filePath, "/");

		Path fullPath = (homePath.data());
		fullPath.append(repositoryPath);
		fullPath.append("/");
		fullPath.append(filePath);
		return fullPath;
	}
	
     public:
      FileManagementService_impl(const std::string& homePath);
      ~FileManagementService_impl();

 	/**
	 * It is responsible to call the suitable function that execute the proper subservice. The
	 * way that the subservices are selected is for the time being based on the messageType(class
	 * member of class Message) of the param message
	 *
	 */
       void handle_msg(pmt::pmt_t pdu);

	/**
     * TC[23,1] Create a file at the provided repository path, give it the provided file name and file size
     * Checks done prior to creating a file:
     * - The size of the file is below the maximum allowed file size
     * - The path is valid, meaning it leads to an existing repository
     * - The repository's path and file's name do not contain a wildcard
     * - The file does not already exist
     * - The object type at the repository path is nothing but a directory (LFS_TYPE_DIR)
     * - The object path size is less than ECSSMaxStringSize
     *
     * @note Apart from the above checks, the _maximum file size_ telecommand argument is currently ignored.
     */
	void createFile(Message& message);

	/**
     * TC[23,2] Delete the file at the provided repository path, with the provided file name
     * Checks done prior to deleting a file:
     * - The path is valid, meaning it leads to an existing file
     * - The repository's path and file's name do not contain a wildcard
     * - The object type at the repository path is nothing but a directory (LFS_TYPE_REG)
     * - The object path size is less than ECSSMaxStringSize
     */
	void deleteFile(Message& message);

	/**
     * TC[23,3] Report attributes of a file at the provided repository path and file name
     * Checks done prior to reporting a file:
     * - The path is valid, meaning it leads to an existing file
     * - The repository's path and file's name do not contain a wildcard
     * - The object type at the repository path is nothing but a directory (LFS_TYPE_REG)
     * - The object path size is less than ECSSMaxStringSize
     */
	void reportAttributes(Message& message);

	/**
     * TM[23,4] Create a report with the attributes from a file at the provided object path
     */
	void fileAttributeReport(Filesystem::ObjectPath& repositoryPath, Filesystem::ObjectPath& fileName, const  Filesystem::Attributes& attributes);
	/**
     * TC[23,5] Lock a file from the filesystem
     */
	void lockFile(Message& message);

	/**
     * TC[23,6] Unlock a file from the filesystem
     */
	void unlockFile(Message& message);

	/**
     * TC[23,7] Find file pattern on the filesystem
     */	
	void findFile(Message& message);

	/**
     * TM[23,8] Create a report with the file found
     */
	void foundFileReport(Filesystem::ObjectPath& repositoryPath, Filesystem::ObjectPath& fileName);
	/**
     * TC[23,9] Create a directory on the filesystem
     */
	void createDirectory(Message& message);

	/**
     * TC[23,10] Delete a directory from the filesystem
     */
	void deleteDirectory(Message& message);

	/**
     * TC[23,11] Rename a directory from the filesystem
     */
	void renameDirectory(Message& message);
	
	/**
     * TC[23,12] Report a directory content summary from the filesystem
     */
	void reportSummaryDirectory(Message& message);
	
	/**
     * TM[23,13] Create a report with a directory content
     */
	void summaryDirectoryReport(Filesystem::ObjectPath& repositoryPath);
	
	/**
     * TC[23,14] Copy a file from the filesystem
     */
	void copyFile(Message& message);
	
	/**
     * TC[23,15] Move a file from the filesystem
     */
	void moveFile(Message& message);
    };

  } // namespace pus
} // namespace gr

#endif /* INCLUDED_PUS_FILEMANAGEMENTSERVICE_IMPL_H */
