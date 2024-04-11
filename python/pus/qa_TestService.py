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
    def __init__(self, messageType, messageSubTypeTx, messageSubTypeRx, messageSize, counter, apid, ackFlags, crcEnabled):
        self.messageType = messageType
        self.messageSubTypeTx = messageSubTypeTx
        self.messageSubTypeRx = messageSubTypeRx
        self.messageSize = messageSize
        self.counter = counter
        
        self.apid = apid
        bytes_val = bytearray(apid.to_bytes(2, "big", signed = False))
        self.apidArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8)         
        self.ackFlags = ackFlags
        self.crcEnabled = crcEnabled
    
class qa_TestService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 65536, 0x19, 0, True)) 
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 1, True)) 
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 3, True)) 
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 7, True)) 
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 15, True)) 
        self.testData.append(test_data(0x11, 0x03, 0x04, 0x0c, 65536, 2047, 0, False)) 
        self.testData.append(test_data(0x11, 0x03, 0x04, 0x0c, 1, 2047, 1, False)) 
        self.testData.append(test_data(0x11, 0x03, 0x04, 0x0c, 1, 2047, 3, False)) 
        self.testData.append(test_data(0x11, 0x03, 0x04, 0x0c, 1, 2047, 7, False))  
        self.testData.append(test_data(0x11, 0x03, 0x04, 0x0c, 1, 2047, 15, False))                        
                                       
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.TestService()
        
    def test_001_S17_wrong_service_type_subtype_and_size(self):
        testData = self.testData[0]
                
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x10, 0x01, 0x00, 0x00, 0xc8, 0x97], dtype=numpy.uint8)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x11, 0x05, 0x00, 0x00, 0xc8, 0x97], dtype=numpy.uint8)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        testService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        testService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

        packet_17_1 = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet_17_1 = appendCRC(packet_17_1)
        in_pdu_17_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_17_1.size, packet_17_1))

        packet_17_3 = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx+2, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet_17_3 = appendCRC(packet_17_3)
        in_pdu_17_3 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_17_3.size, packet_17_3))
                
        self.tb.start()
        testService.to_basic_block()._post(pmt.intern("in"), in_pdu_17_1) 
        testService.to_basic_block()._post(pmt.intern("in"), in_pdu_17_3) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 4)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(2), packet_17_1, 1))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(3), packet_17_3, 1))
        
    def test_002_S17_01and02_test_response_and_counters_noack(self):
        testData = self.testData[0]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))

        # Testing TC(17,1) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 0, d2, testData, packet))  

    def test_003_S17_01and02_test_response_acceptance_ack(self):
        testData = self.testData[1]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)        
        
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 1, d2, testData, packet))    
         
    def test_004_S17_01and02_test_response_acceptance_and_start_ack(self):
        testData = self.testData[2]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 2, d2, testData, packet))             

    def test_005_S17_01and02_test_response_acceptance_start_and_progress_ack(self):
        testData = self.testData[3]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 2, d2, testData, packet))  

    def test_006_S17_01and02_test_response_acceptance_start_progress_execution_ack(self):
        testData = self.testData[4]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 3, d2, testData, packet))   

    def test_007_S17_03and04_test_response_and_counters_noack(self):
        testData = self.testData[5]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
            
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 0, d2, testData, packet))  

    def test_008_S17_03and04_test_response_acceptance_ack(self):
        testData = self.testData[6]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 1, d2, testData, packet))  
     
    def test_009_S17_03and04_test_response_acceptance_and_start_ack(self):
        testData = self.testData[7]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0xc8, 0x97], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 2, d2, testData, packet))  

    def test_010_S17_03and04_test_response_acceptance_start_and_progress_ack(self):
        testData = self.testData[8]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 2, d2, testData, packet)) 

    def test_011_S17_03and04_test_response_acceptance_start_progress_execution_ack(self):
        testData = self.testData[9]
        testService = pus.TestService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((testService, 'out'), (d1, 'store'))
        self.tb.msg_connect((testService, 'ver'), (d2, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        self.tb.start()
        for i in range (0, testData.counter):
            testService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, 3, d2, testData, packet))

def checkResults(numd1, d1, numd2, d2, testData, packet):
            	
    if d1.num_messages() != numd1:
        return False
    if d2.num_messages() != numd2:
        return False
                
    for i in range (0, testData.counter):
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(i))), dtype=numpy.uint8)
            
        if not checkPrimaryHeader(testData.apid, testData.messageSize, i, response):
            return False
   
        if testData.crcEnabled:
            if not checkCRC(response):
                return False           
        if testData.ackFlags & 0x01:
            if not checkSuccessAcceptanceVerification(d2.get_message(i), packet): 
                return False  
        if testData.ackFlags & 0x02:
            if not checkSuccessStartExecutionVerification(d2.get_message(i+1), packet):
                return False  
        if testData.ackFlags & 0x08:
            if not checkSuccessSuccessCompletionExecutionVerification(d2.get_message(i+2), packet):   
                return False  
    return True
                        
def checkPrimaryHeader(apid, size, counter, message):
    bytes_val = bytearray(apid.to_bytes(2, "big", signed = False))
    apidArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8) 
   
    bytes_val = bytearray(counter.to_bytes(2, "big", signed = False))
    counterArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8)  

    primaryHeader = message[0:6]
    expectedPrimaryHeader = numpy.array([0x08 | apidArray[0], apidArray[1], (counterArray[0] & 0x7f) | 0xc0, counterArray[1], 0x00, size], dtype=numpy.uint8)
    return numpy.array_equal(primaryHeader, expectedPrimaryHeader)

def checkSecondaryHeader(serviceType, messageSubType, counter, message):
    bytes_val = bytearray(counter.to_bytes(2, "big", signed = False))
    counterArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8)  
    secondaryHeader = message[6:13]
    expectedSecondaryHeader = numpy.array([0x20, serviceType, messageSubType, counterArray[0], counterArray[1], 0x00, 0x00], dtype=numpy.uint8)
    return numpy.array_equal(secondaryHeader, expectedSecondaryHeader)

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
    
def checkSuccessProgressExecutionVerification(message, sentMessage):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
        
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))

    if report_req != 5:
        return False
    if pmt.dict_has_key(meta, pmt.intern("error_type")):
        return False
    if pmt.dict_has_key(meta, pmt.intern("step_id")):
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
    gr_unittest.run(qa_TestService, "qa_TestService.xml" )

