/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#pragma once

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include "etl/optional.h"
#include "etl/result.h"
#include "etl/string.h"
#include <etl/vector.h>

namespace Filesystem {
	constexpr size_t FullPathSize = ECSSMaxStringSize;
	using Path = etl::string<FullPathSize>;

	/**
	 * ObjectPathSize is half the maximum size, minus one character for the '/' delimiter between the
	 * repository and file paths.
	 */
	constexpr size_t ObjectPathSize = (FullPathSize / 2) - 1;
	using ObjectPath = etl::string<ObjectPathSize>;

	/**
	 * The available metadata for a file
	 */
	struct Attributes {
		size_t sizeInBytes;
		bool isLocked;
	};

	/**
	 * The type of a node in the file system
	 */
	enum class NodeType : uint8_t {
		Directory = 0,
		File = 1
	};

	/**
	 * Possible errors returned by the filesystem during file creation
	 */
	enum class FileCreationError : uint8_t {
		FileAlreadyExists = 0,
		UnknownError = 255
	};

	/**
	 * Possible errors returned by the filesystem during file deletion
	 */
	enum class FileDeletionError : uint8_t {
		FileDoesNotExist = 0,
		PathLeadsToDirectory = 1,
		FileIsLocked = 2,
		UnknownError = 255
	};

	/**
	 * Possible errors returned by the filesystem during directory creation
	 */
	enum class DirectoryCreationError : uint8_t {
		DirectoryAlreadyExists = 0,
		UnknownError = 255
	};

	/**
	 * Possible errors returned by the filesystem during directory deletion
	 */
	enum class DirectoryDeletionError : uint8_t {
		DirectoryDoesNotExist = 0,
		DirectoryIsNotEmpty = 1,
		UnknownError = 255
	};

	/**
	 * Possible errors returned by the filesystem during directory rename
	 */
	enum class DirectoryRenameError : uint8_t {
		SrcDirectoryDoesNotExist = 0,
		DstDirectoryDoesExist = 1,
		UnknownError = 255
	};
	/**
	 * The current file lock status
	 */
	enum class FileLockStatus : uint8_t {
		Unlocked = 0,
		Locked = 1,
	};

	/**
	 * Possible errors returned by the filesystem during a file attribute check
	 */
	enum class FileAttributeError : uint8_t {
		PathLeadsToDirectory = 0,
		FileDoesNotExist = 1,
		UnknownError = 255
	};


	/**
	 * Possible errors returned by the filesystem during file copy
	 */
	enum class FileCopyError : uint8_t {
		SrcFileDoesNotExist = 0,
		DstFileAlreadyExists = 1,
		UnknownError = 255
	};

	/**
	 * Possible errors returned by the filesystem during file move
	 */
	enum class FileMoveError : uint8_t {
		SrcFileDoesNotExist = 0,
		DstFileAlreadyExists = 1,
		SrcFileIsLocked = 2,
		UnknownError = 255
	};


	typedef std::pair<NodeType, ObjectPath> ContentEntry; 
	typedef etl::vector<ContentEntry, ECSSMaxNumberOfDirectoryContentList> DirContent;
	typedef etl::vector<ObjectPath, ECSSMaxNumberOfDirectoryContentList/2> SearchContent;			
	/**
	 * Creates a file using platform specific filesystem functions
	 * @param path A String representing the path on the filesystem
	 * @return Optionally, a file creation error. If no errors occur, returns etl::nullopt
	 */
	etl::optional<FileCreationError> createFile(const Path& path);

	/**
	 * Deletes a file using platform specific filesystem functions
	 * @param path A String representing the path on the filesystem
	 * @return Optionally, a file deletion error. If no errors occur, returns etl::nullopt
	 */
	etl::optional<FileDeletionError> deleteFile(const Path& path);

	/**
	 * Creates a directory using platform specific filesystem functions
	 * @param path A String representing the path on the filesystem
	 * @return Optionally, a directory creation error. If no errors occur, returns etl::nullopt
	 */
	etl::optional<DirectoryCreationError> createDirectory(const Path& path);

	/**
	 * Deletes a directory using platform specific filesystem functions
	 * @param path A String representing the path on the filesystem
	 * @return Optionally, a directory deletion error. If no errors occur, returns etl::nullopt
	 */
	etl::optional<DirectoryDeletionError> deleteDirectory(const Path& path);

	/**
	 * Rename a directory using platform specific filesystem functions
	 * @param srcPath A String representing the source path on the filesystem
	 * @param dstPath A String representing the destination path on the filesystem
	 * @return Optionally, a directory rename error. If no errors occur, returns etl::nullopt
	 */
	etl::optional<DirectoryRenameError> renameDirectory(const Path& srcPath, const Path& dstPath);

	/**
	 * Gets the file metadata
	 * @param path A String representing the path on the filesystem
	 * @param attributes A Attributes struct to be filled with the file attributes
	 * @return Optionally, a get attributes error. If no errors occur, returns etl::nullopt
	 */
	etl::optional<FileAttributeError> getFileAttributes(const Path& path, Attributes& attributes);

	/**
	 * Gets the type of node in the filesystem
	 * @param path A String representing the path on the filesystem
	 * @return A NodeType value, or nothing if the file can't be accessed
	 */
	etl::optional<NodeType> getNodeType(const Path& path);


	/**
	 * Gets a directory content
	 * @param objectPath A String representing the path on the filesystem
	 * @param searchPattern A String representing the file search pattern
	 * @return A vector with the filenames as search results 
	 */		
	SearchContent findFile(const ObjectPath& objectPath, const ObjectPath& searchPattern);
	
	/**
	 * An overloaded function providing support for getNodeType on repository objects.
	 * @param objectPath A String representing a path on the filesystem
	 * @return A NodeType value
	 */
	inline etl::optional<NodeType> getNodeType(const ObjectPath& objectPath) {
		const Path path = objectPath.data();
		return getNodeType(path);
	}

	/**
	 * Locks a file using the filesystem functions.
	 * @param path A String representing the path on the filesystem
	 */
	void lockFile(const Path& path);

	/**
	 * Unlocks a file using the filesystem functions.
	 * @param path A String representing the path on the filesystem
	 */
	void unlockFile(const Path& path);

	/**
	 * Gets the current file lock status
	 * @param path A String representing the path on the filesystem
	 * @return The FileLockStatus value
	 */
	FileLockStatus getFileLockStatus(const Path& path);

	/**
	 * Gets a directory content
	 * @param path A String representing the path on the filesystem
	 * @return A vector with the directory content as pair <type, name>
	 */		
	DirContent getDirContent(const ObjectPath& path);

	/**
	 * Copy a file in the filesystem
	 * @param srcPath The source file to copy
	 * @param dstPath The destination file to copy
	 * @return A NodeType value, or nothing if the file can't be accessed
	 */	
	etl::optional<FileCopyError> copyFile(const Path& srcPath, const Path& dstPath);	

	/**
	 * Move a file in the filesystem
	 * @param srcPath The source file to move
	 * @param dstPath The destination file moved
	 * @return A NodeType value, or nothing if the file can't be accessed
	 */	
	etl::optional<FileMoveError> moveFile(const Path& srcPath, const Path& dstPath);		
} // namespace Filesystem
