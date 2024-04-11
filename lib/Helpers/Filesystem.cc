/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/pus/Helpers/Filesystem.h>
#include "etl/string_utilities.h"
#include <filesystem> 
#include <fstream>
#include <iostream>
#include <regex>
/**
 * These functions are built on the x86_services target and will never run.
 * To combat undefined function errors, they are defined here.
 * Each function returns the minimum viable option without errors.
 */
namespace Filesystem {

	etl::optional<FileCreationError> createFile(const Path& path) {
		auto repositoryType = Filesystem::getNodeType(path);

		if (repositoryType){
			if (repositoryType.value() == Filesystem::NodeType::File) 
				return FileCreationError::FileAlreadyExists;
			return FileCreationError::UnknownError;
        	}
        	std::ofstream file(path.data(), std::ios::out | std::ios::binary);
        	if (!file)
			return FileCreationError::UnknownError;
			
		file.close();
		
		return etl::nullopt;
	}

	etl::optional<FileDeletionError> deleteFile(const Path& path) {
		auto repositoryType = Filesystem::getNodeType(path);

		if (repositoryType){
			if (repositoryType.value() == Filesystem::NodeType::Directory) 
				return FileDeletionError::PathLeadsToDirectory;
			if (getFileLockStatus(path) == FileLockStatus::Locked)
				return FileDeletionError::FileIsLocked;
    			if (!std::filesystem::remove(path.data()))
				return FileDeletionError::UnknownError;
		}else{
			return FileDeletionError::FileDoesNotExist;
		}
		return etl::nullopt;
	}

	etl::optional<NodeType> getNodeType(const Path& path) {
    		const std::filesystem::path objectPath(path.data()); 
    		std::error_code ec; // For using the non-throwing overloads of functions below.

    		if (std::filesystem::is_directory(objectPath, ec))
    		{ 
        		return NodeType::Directory;
    		}
    		if (std::filesystem::is_regular_file(objectPath, ec) or std::filesystem::is_character_file(objectPath, ec))
   		{
       		return NodeType::File;
    		}
		return etl::nullopt;
	}
	
	FileLockStatus getFileLockStatus(const Path& path) {
		auto repositoryType = Filesystem::getNodeType(path);

		if (repositoryType){
			if (repositoryType.value() == Filesystem::NodeType::File) {
				auto perm = std::filesystem::status(path.data()).permissions();
				if ((perm & std::filesystem::perms::owner_write) != std::filesystem::perms::owner_write and 
					(perm & std::filesystem::perms::group_write) != std::filesystem::perms::group_write)
					return FileLockStatus::Locked;
			}
		}
		return FileLockStatus::Unlocked;
	}

	void lockFile(const Path& path) {

	    std::filesystem::permissions(
       		path.data(),
        		std::filesystem::perms::owner_write | std::filesystem::perms::group_write,
        		// | std::filesystem::perms::owner_exec | std::filesystem::perms::group_exec,
        		std::filesystem::perm_options::remove
    		);
	
	}

	void unlockFile(const Path& path) {
   

	    std::filesystem::permissions(
       		path.data(),
        		std::filesystem::perms::owner_write | std::filesystem::perms::group_write,
        		// | std::filesystem::perms::owner_exec | std::filesystem::perms::group_exec,
        		std::filesystem::perm_options::add
    		);
	}

	etl::optional<FileAttributeError> getFileAttributes(const Path& path, Attributes& attributes) {
		auto repositoryType = Filesystem::getNodeType(path);

		if (repositoryType){
			if (repositoryType.value() == Filesystem::NodeType::Directory) 
				return FileAttributeError::PathLeadsToDirectory;
			else if (repositoryType.value() == Filesystem::NodeType::File) {
				attributes.sizeInBytes = std::filesystem::file_size(path.data());
				attributes.isLocked = (getFileLockStatus(path) == FileLockStatus::Locked);
			}else  return FileAttributeError::UnknownError;
		}else{
			return FileAttributeError::FileDoesNotExist;
		}
		
		return etl::nullopt;
	}

	etl::optional<DirectoryCreationError> createDirectory(const Path& path) {
		auto repositoryType = Filesystem::getNodeType(path);

		if (repositoryType){
			if (repositoryType.value() == Filesystem::NodeType::Directory) 
				return DirectoryCreationError::DirectoryAlreadyExists;
			return DirectoryCreationError::UnknownError;	
		}

		std::filesystem::create_directory(path.data());
		
		return etl::nullopt;
	}

	SearchContent findFile(const ObjectPath& path, const ObjectPath& pattern) {
		std::regex searchPattern(pattern.data());
		SearchContent searchContent;
		auto repositoryType = Filesystem::getNodeType(path);
		if (repositoryType){
			if (repositoryType.value() == Filesystem::NodeType::Directory) {
				for (const auto & entry : std::filesystem::recursive_directory_iterator(path.data())){
        				if(searchContent.size() < ECSSMaxNumberOfDirectoryContentList/2){
    						std::error_code ec; 
    						if (std::filesystem::is_regular_file(entry.path(), ec) or
    								std::filesystem::is_character_file(entry.path(), ec))
   						{
                					if (std::regex_search(entry.path().filename().string(), searchPattern)) {
  		              					ObjectPath fileName(entry.path().string().data());
	                    					etl::right_n(fileName, fileName.length() - path.length());
                   						searchContent.push_back(fileName);
                					}
    						}
    					}
		        	}
			}
		}
		return searchContent;
	}	
	
	etl::optional<DirectoryDeletionError> deleteDirectory(const Path& path) {
		auto repositoryType = Filesystem::getNodeType(path);

		if (repositoryType){
			if (repositoryType.value() != Filesystem::NodeType::Directory) 
				return DirectoryDeletionError::DirectoryDoesNotExist;
			if (!std::filesystem::is_empty(path.data())) 
				return DirectoryDeletionError::DirectoryIsNotEmpty;
			std::filesystem::remove(path.data());
		}else{
			return DirectoryDeletionError::DirectoryDoesNotExist;
		}

		return etl::nullopt;
	}

	etl::optional<DirectoryRenameError> renameDirectory(const Path& srcPath, const Path& dstPath) {
		auto srcRepositoryType = Filesystem::getNodeType(srcPath);
		auto dstRepositoryType = Filesystem::getNodeType(dstPath);

		if (!srcRepositoryType)
			return DirectoryRenameError::SrcDirectoryDoesNotExist;
		else if(srcRepositoryType.value() != Filesystem::NodeType::Directory) 
			return DirectoryRenameError::SrcDirectoryDoesNotExist;
				
		if(dstRepositoryType)
			return DirectoryRenameError::DstDirectoryDoesExist;
		std::filesystem::rename(srcPath.data(), dstPath.data());
		return etl::nullopt;
	}
	
	DirContent getDirContent(const ObjectPath& path) {
		DirContent dirContent;
		auto repositoryType = Filesystem::getNodeType(path);

		if (repositoryType){
			if (repositoryType.value() == Filesystem::NodeType::Directory) {
				for (const auto & entry : std::filesystem::directory_iterator(path.data())){
        				if(dirContent.size() < ECSSMaxNumberOfDirectoryContentList){
    						std::error_code ec; // For using the non-throwing overloads of functions below.
    						if (std::filesystem::is_directory(entry.path(), ec))
    						{ 
        						ContentEntry content(NodeType::Directory, entry.path().filename().string().data());
        						dirContent.push_back(content);
    						}
    						if (std::filesystem::is_regular_file(entry.path(), ec) or
    								std::filesystem::is_character_file(entry.path(), ec))
   						{
	
        						ContentEntry content(NodeType::File, entry.path().filename().string().data());
        						dirContent.push_back(content);
      						}
    					}
		        	}
			}
		}
		return dirContent;
	}	

	etl::optional<FileCopyError> copyFile(const Path& srcPath, const Path& dstPath) {
		auto srcRepositoryType = Filesystem::getNodeType(srcPath);
		auto dstRepositoryType = Filesystem::getNodeType(dstPath);

		if (srcRepositoryType){
			if (not srcRepositoryType)
				return FileCopyError::SrcFileDoesNotExist;
			if (srcRepositoryType.value() != Filesystem::NodeType::File) 
				return FileCopyError::SrcFileDoesNotExist;
			if (dstRepositoryType)
				return FileCopyError::DstFileAlreadyExists;
			std::filesystem::copy(srcPath.data(), dstPath.data());
		}else{
			return FileCopyError::SrcFileDoesNotExist;
		}

		return etl::nullopt;
	}	    	

	etl::optional<FileMoveError> moveFile(const Path& srcPath, const Path& dstPath) {
		auto srcRepositoryType = Filesystem::getNodeType(srcPath);
		auto dstRepositoryType = Filesystem::getNodeType(dstPath);

		if (srcRepositoryType){
			if (not srcRepositoryType)
				return FileMoveError::SrcFileDoesNotExist;
			if (srcRepositoryType.value() != Filesystem::NodeType::File) 
				return FileMoveError::SrcFileDoesNotExist;
			if (dstRepositoryType)
				return FileMoveError::DstFileAlreadyExists;
			if (getFileLockStatus(srcPath) == FileLockStatus::Locked)
				return FileMoveError::SrcFileIsLocked;
			std::filesystem::rename(srcPath.data(), dstPath.data());
		}else{
			return FileMoveError::SrcFileDoesNotExist;
		}

		return etl::nullopt;
	}
} // namespace Filesystem
