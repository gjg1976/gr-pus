/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_SERVICES_HOUSEKEEPINGSTRUCTURE_H
#define ECSS_SERVICES_HOUSEKEEPINGSTRUCTURE_H

#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Helpers/ErrorHandler.h>
#include "etl/map.h"
#include "etl/vector.h"
#include "etl/list.h"

namespace gr {
  namespace pus {
/**
 * Implementation of the super conmutated housekeeping report arrays used by the Housekeeping Reporting Subservice (ST[03]). 
 */
    struct HousekeepingSuperConmutatedArrays {

    /**
     * Defined as integer multiples of the minimum sampling interval as per 6.3.3.2.c.5 #NOTE-2.
     */
      uint8_t superConmutatedInterval = 0;

      uint8_t counterSuperConmutatedInterval = 0;

	/**
	 * Vector containing the Report Type definitions. Each definition has its unique name of type uint8. For
	 * example, a Report Type definition could be 'ReportHousekeepingStructures'.
	 */
	typedef std::vector<uint8_t> superConmutatedVector;
    /**
     * Vector containing the IDs of the simply commutated parameters, contained in the housekeeping structure.
     */
      etl::vector<uint16_t, ECSSMaxSuperCommutatedParameters>  superCommutatedParameterIds;

    /**
     * queue containing the historic super conmutated data arrays to be copy into the housekeepings parameters reports up to 
     * size = superConmutatedInterval.
     */
      etl::list<superConmutatedVector, ECSSMaxSuperCommutatedArraySize>  superCommutatedDataArray;
      	
      HousekeepingSuperConmutatedArrays() = default;
    };

/**
 * Implementation of the Housekeeping report structure used by the Housekeeping Reporting Subservice (ST[03]). The
 * current version includes only simply commutated parameters, i.e. parameters that contain a single sampled value.
 *
 * @author Petridis Konstantinos <petridkon@gmail.com>
 */
    struct HousekeepingStructure {
      uint8_t structureId;

    /**
     * Defined as integer multiples of the minimum sampling interval as per 6.3.3.2.c.5 #NOTE-2.
     */
      uint16_t collectionInterval = 0;

      uint16_t counterInterval = 0;
    /**
     * Indicates whether the periodic generation of housekeeping reports is enabled.
     */
      bool periodicGenerationActionStatus = false;

    /**
     * Vector containing the IDs of the simply commutated parameters, contained in the housekeeping structure.
     */
      etl::vector<uint16_t, ECSSMaxSimplyCommutatedParameters> simplyCommutatedParameterIds;

      etl::map<uint8_t, HousekeepingSuperConmutatedArrays, ECSSMaxSuperCommutatedArrays> superCommutatedArrays;

      HousekeepingStructure() = default;
    };
    
  } // namespace pus
} // namespace gr

#endif
