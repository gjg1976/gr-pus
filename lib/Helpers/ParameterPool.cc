/* -*- c++ -*- */
/*
 * Copyright 2023 Gustavo Gonzalez.
 *
 * based on AcubeSAT PUS implementation
 * https://github.com/AcubeSAT/ecss-services
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <gnuradio/pus/Helpers/ParameterPool.h>

 namespace gr {
  namespace pus {

    ParameterPool* ParameterPool::inst_parameterpool = NULL;
    
    ParameterPool::ParameterPool()
    {
    }
    
    ParameterPool* ParameterPool::getInstance()
    {
       if(inst_parameterpool == NULL)
           inst_parameterpool = new ParameterPool();
       
       return inst_parameterpool;
    }

    template <typename DataType>
    bool ParameterPool::setParameter(uint16_t currId, DataType newParamValue) {
	auto parameter = getParameter(currId);
	if (!parameter) {
		return false;
	}
	std::vector<uint8_t> newVectorParamValue(&newParamValue);
	parameter->get().setValueFromVector(newVectorParamValue);
	
	return true;
    }

    bool ParameterPool::initializeParameterMap(const std::string& filename)
    {
        std::ifstream file(filename);
        nlohmann::json json;
		
        if (file) {
            file >> json;
            for (auto& elem : json["parameters"]){
                uint16_t currId = elem["id"];
                std::string type = elem["type"];
		auto parameter = getParameter(currId);
		if (parameter) {
			continue;
		}
                if(type == "uint8"){
                	uint8_t newParamValue = elem["default"];
                	Parameter<uint8_t>* newParameter = new Parameter<uint8_t>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "uint16"){
                	uint16_t newParamValue = elem["default"];
                	Parameter<uint16_t>* newParameter = new Parameter<uint16_t>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "uint32"){
                	uint32_t newParamValue = elem["default"];
                	Parameter<uint32_t>* newParameter = new Parameter<uint32_t>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "uint64"){
                	uint64_t newParamValue = elem["default"];
                	Parameter<uint64_t>* newParameter = new Parameter<uint64_t>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "sint8"){
                	int8_t newParamValue = elem["default"];
                	Parameter<int8_t>* newParameter = new Parameter<int8_t>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "sint16"){
                	int16_t newParamValue = elem["default"];
                	Parameter<int16_t>* newParameter = new Parameter<int16_t>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "sint32"){
                	int32_t newParamValue = elem["default"];
                	Parameter<int32_t>* newParameter = new Parameter<int32_t>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "bool"){
                	bool newParamValue = elem["default"];
                	Parameter<bool>* newParameter = new Parameter<bool>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "float"){
                	float newParamValue = elem["default"];
                	Parameter<float>* newParameter = new Parameter<float>(newParamValue);
			parameters.insert({currId, newParameter[0]});
                }else if(type == "double"){
                	double newParamValue = elem["default"];
                	Parameter<double>* newParameter = new Parameter<double>(newParamValue);
			parameters.insert({currId, newParameter[0]}); 
                }
            }
        } else {
            return false;
        }
        file.close();
        return true;
    }
        
  } // namespace pus
} // namespace gr


