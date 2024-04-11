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

#include <cstdint>
#include <etl/optional.h>
#include <gnuradio/pus/FileManagementService.h>

namespace FilepathValidators {
	/**
     * If a wildcard is encountered, then it returns its position in the string (starting from 0).
     * @param path The path passed as a String.
     * @return Optionally, the position of the wildcard.
     */
	etl::optional<size_t> findWildcardPosition(const Filesystem::Path& path);
} //namespace FilepathValidators
