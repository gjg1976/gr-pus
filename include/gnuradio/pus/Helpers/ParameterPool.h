/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef ECSS_PARAMETERPOOL_H
#define ECSS_PARAMETERPOOL_H

#include <map>
#include <functional>
#include <optional>
#include <gnuradio/pus/Definitions/ECSS_Definitions.h>
#include <gnuradio/pus/Helpers/Parameter.h>
#include <nlohmann/json.hpp>
#include <fstream>
#include "etl/map.h"

 namespace gr {
  namespace pus {

   class ParameterPool 
   {
     private:
	typedef etl::map<uint16_t, std::reference_wrapper<ParameterBase>, ECSSParameterCount> ParameterMap;

	/**
	 * Map storing the IDs and references to each parameter
	 * of the \ref PlatformParameters namespace.
	 * The key of the map is the ID of the parameter as specified in PUS.
	 * The parameters here are under the responsibility of \ref ParameterService.
	 */
	ParameterMap parameters;
	
       void parse_json(const std::string& filename);

      static ParameterPool* inst_parameterpool;
      
      ParameterPool();
      ParameterPool(const ParameterPool&);
      
      ParameterPool& operator=(const ParameterPool&);
      
     public:
	static ParameterPool* getInstance();

	bool initializeParameterMap(const std::string& filename);

	/**
	 * Checks if \var parameters contains a reference to a parameter with
	 * the given parameter ID as key
	 *
	 * @param parameterId the given ID
	 * @return True if there is a reference to a parameter with the given ID, False otherwise
	 */
	bool parameterExists(uint16_t parameterId) {
		return parameters.find(parameterId) != parameters.end();
	}

	/**
	 * This is a simple getter function, which returns a reference to
	 * a specified parameter, from the \var parameters.
	 *
	 * @param parameterId the id of the parameter, whose reference is to be returned.
	 */
	std::optional<std::reference_wrapper<ParameterBase>> getParameter(uint16_t parameterId) {
		auto parameter = parameters.find(parameterId);

		if (parameter != parameters.end()) {
			return parameter->second;
		} else {
			return {};
		}
	}

	/**
	 * This function receives a TC[20, 3] message and after checking whether its type is correct,
	 * iterates over all contained parameter IDs and replaces the settings for each valid parameter,
	 * while ignoring all invalid IDs.
	 *
	 * @param newParamValues: a valid TC[20, 3] message carrying parameter ID and replacement value
	 */	
	template <typename DataType>
	bool setParameter(uint16_t currId, DataType newParamValue) ; 

    };
  } // namespace pus
} // namespace gr
#endif // ECSS_PARAMETERPOOL_H
