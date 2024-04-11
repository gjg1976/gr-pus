#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 Gustavo Gonzalez.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks
try:
    from gnuradio import pus
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    from gnuradio import pus
import numpy
import pmt
import time

class test_data():
    def __init__(self, messageType, messageSubTypeTx, messageSubTypeRx, messageSize, counter, apid, ackFlags, error, step, crcEnabled, counter_offset, counter_sec_offset):
        self.messageType = messageType
        self.messageSubTypeTx = messageSubTypeTx
        self.messageSubTypeRx = messageSubTypeRx
        self.messageSize = messageSize
        self.counter = counter
        
        self.apid = apid
        bytes_val = bytearray(apid.to_bytes(2, "big", signed = False))
        self.apidArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8)         
        self.ackFlags = ackFlags
        self.error = error
        self.step = step
        self.crcEnabled = crcEnabled
        self.counter_offset = counter_offset
        self.counter_sec_offset = counter_sec_offset    
        
class qa_FunctionManagementService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x08, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x08, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x08, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x08, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x08, 0x01, 0x00, -1, 1, 0x19, 0, 62, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x08, 0x01, 0x00, 0x0c, 1, 0x19, 15, 0, 0, True, 0, 0)) #5
                                        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.FunctionManagementService(16, 16)

    def test_001_ST08_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        functionManagementService = pus.FunctionManagementService(16, 16)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((functionManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((functionManagementService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x04, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x08, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        functionManagementService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        functionManagementService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST08_01_invalid_fuctionName_field_shorter(self):
        testData = self.testData[1]
                
        functionManagementService = pus.FunctionManagementService(16, 16)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((functionManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((functionManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        functionManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST08_01_invalid_paramsSize_field_shorter(self):
        testData = self.testData[2]
                
        functionManagementService = pus.FunctionManagementService(16, 16)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((functionManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((functionManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x74, 0x65, 0x73, 0x74, 0x5f, 0x66, 0x75, 0x6e, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        functionManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST08_01_invalid_paramsSize_field_longer(self):
        testData = self.testData[3]
                
        functionManagementService = pus.FunctionManagementService(16, 16)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((functionManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((functionManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x74, 0x65, 0x73, 0x74, 0x5f, 0x66, 0x75, 0x6e, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x00, 0x00, 0x00, 0x70, 0x61, 0x72, 0x61, 0x6d, 0x49, 0x44, 0x20, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        functionManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST08_01_invalid_function_non_exist(self):
        testData = self.testData[4]
        functionInit = pus.FunctionInit(16)        
        functionManagementService = pus.FunctionManagementService(16, 16)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((functionManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((functionManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x65, 0x74, 0x73, 0x74, 0x5f, 0x66, 0x75, 0x6e, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x00, 0x00, 0x00, 0x70, 0x61, 0x72, 0x61, 0x6d, 0x49, 0x44, 0x20, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        functionManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_006_ST08_01_valid_function_call(self):
        testData = self.testData[5]
        functionInit = pus.FunctionInit(16)        
        functionManagementService = pus.FunctionManagementService(16, 16)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((functionManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((functionManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x74, 0x65, 0x73, 0x74, 0x5f, 0x66, 0x75, 0x6e, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x00, 0x00, 0x00, 0x70, 0x61, 0x72, 0x61, 0x6d, 0x49, 0x44, 0x20, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        functionManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))   
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))      
                          
def checkPrimaryHeader(apid, size, counter, message, counter_offset):
    counter += counter_offset
    bytes_val = bytearray(apid.to_bytes(2, "big", signed = False))
    apidArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8) 
   
    bytes_val = bytearray(counter.to_bytes(2, "big", signed = False))
    counterArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8)  

    primaryHeader = message[0:6]
    expectedPrimaryHeader = numpy.array([0x08 | apidArray[0], apidArray[1], (counterArray[0] & 0x7f) | 0xc0, counterArray[1], 0x00, size], dtype=numpy.uint8)
    if size == -1:
        primaryHeader = primaryHeader[0:4]
        expectedPrimaryHeader = expectedPrimaryHeader[0:4]

    return numpy.array_equal(primaryHeader, expectedPrimaryHeader)

def checkSecondaryHeader(serviceType, messageSubType, counter, message, counter_offset):
    counter += counter_offset
    bytes_val = bytearray(counter.to_bytes(2, "big", signed = False))
    counterArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8)  
    secondaryHeader = message[6:13]
    expectedSecondaryHeader = numpy.array([0x20, serviceType, messageSubType, counterArray[0], counterArray[1], 0x00, 0x00], dtype=numpy.uint8)
    return numpy.array_equal(secondaryHeader, expectedSecondaryHeader)


def checkPayload(expectedPayload, message, crcEnabled):
    if crcEnabled:
    	payload = message[17:-2]
    else:
    	payload = message[17:]
    return numpy.array_equal(payload, expectedPayload)
    
       
def checkSuccessAcceptanceVerification(message, sentMessage):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
        
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))

    if report_req != 1:
        return False
    if pmt.dict_has_key(meta, pmt.intern("error_type")):
        return False
    if pmt.dict_has_key(meta, pmt.intern("step_id")):
        return False        
    return True           

def checkFailedAcceptanceVerification(message, sentMessage, error):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
   
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))
    report_error = pmt.to_long(pmt.dict_ref(meta, pmt.intern("error_type"), pmt.PMT_NIL))

    if report_req != 2:
        return False
    if report_error != error:
        return False
    if pmt.dict_has_key(meta, pmt.intern("step_id")):
        return False        
    return True      
    
def checkSuccessStartExecutionVerification(message, sentMessage):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
        
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))

    if report_req != 3:
        return False
    if pmt.dict_has_key(meta, pmt.intern("error_type")):
        return False
    if pmt.dict_has_key(meta, pmt.intern("step_id")):
        return False        
    return True  

def checkFailedStartExecutionVerification(message, sentMessage, error):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
   
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))
    report_error = pmt.to_long(pmt.dict_ref(meta, pmt.intern("error_type"), pmt.PMT_NIL))

    if report_req != 4:
        return False
    if report_error != error:
        return False
    if pmt.dict_has_key(meta, pmt.intern("step_id")):
        return False        
    return True      
    
def checkSuccessProgressExecutionVerification(message, sentMessage, step):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
        
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))
    report_step = pmt.to_long(pmt.dict_ref(meta, pmt.intern("step_id"), pmt.PMT_NIL))
    
    if report_req != 5:
        return False
    if pmt.dict_has_key(meta, pmt.intern("error_type")):
        return False
    if report_step != step:
        return False         
    return True  


def checkFailedProgressExecutionVerification(message, sentMessage, error, step):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
   
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))
    report_error = pmt.to_long(pmt.dict_ref(meta, pmt.intern("error_type"), pmt.PMT_NIL))
    report_step = pmt.to_long(pmt.dict_ref(meta, pmt.intern("step_id"), pmt.PMT_NIL))

    if report_req != 6:
        return False
    if report_error != error:
        return False
    if report_step != step:
        return False        
    return True      
    
def checkSuccessSuccessCompletionExecutionVerification(message, sentMessage):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
        
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))

    if report_req != 7:
        return False
    if pmt.dict_has_key(meta, pmt.intern("error_type")):
        return False
    if pmt.dict_has_key(meta, pmt.intern("step_id")):
        return False        
    return True       

def checkCRC(message):
    crcTail = int.from_bytes(message[-2:], byteorder='big', signed=False)
    message = message[0:-2]
                       
    return getCRC(message) == crcTail  

def appendCRC(message):
    crc : numpy.uint16 = getCRC(message)
    bytes_val = bytearray(int(crc).to_bytes(2, "big", signed = False))
    crcArray = numpy.frombuffer(bytes_val, dtype=numpy.uint8)       
    message = numpy.append(message, crcArray)
    return message  
    
def getCRC(message):
    crc = 0xFFFF
    polynomial = 0x1021

    for i in range(0,len(message)):
        crc ^= message[i] << 8
            
        for j in range(0,8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ polynomial
            else:
                crc = crc << 1                           
    return (crc & 0xffff)  
    
if __name__ == '__main__':
    gr_unittest.run(qa_FunctionManagementService, "qa_FunctionManagementService.xml" )
