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
    def __init__(self, messageType, messageSubTypeTx, messageSubTypeRx, messageSize, counter, apid, ackFlags, error, crcEnabled):
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
        self.crcEnabled = crcEnabled
    
class qa_ServicesPool(gr_unittest.TestCase):
    servicesList = (3,4,5,6,8,11,12,13,14,15,17,19,20)    
    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 0, 5, True))                
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 0, 2, True))                
        self.testData.append(test_data(0x31, 0x01, 0x02, 0x0c, 1, 0x19, 0, 3, True))
        self.testData.append(test_data(0x03, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x04, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x05, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x06, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x08, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x0b, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x0c, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))  
        self.testData.append(test_data(0x0d, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x0e, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x0f, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x11, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x13, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))  
        self.testData.append(test_data(0x14, 0x01, 0x02, 0x0c, 1, 0x19, 0, 0, True))  
                                                                                                                       
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.ServicesPool(self.servicesList)
        
    def test_001_ServicePool_primary_header_invalid(self):
        testData = self.testData[0]
                
        servicePool = pus.ServicesPool(self.servicesList)
        
        d1 = []
        for i in range(0,len(self.servicesList)):
            d1.insert(i, blocks.message_debug())
            self.tb.msg_connect((servicePool, 'out' + str(i)), (d1[i], 'store'))
            
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)


        self.tb.msg_connect((servicePool, 'ver'), (d2, 'store'))

        packetWrongMinSize = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00], dtype=numpy.uint8)
        packetWrongMinSize = appendCRC(packetWrongMinSize)
        in_pduWrongMinSize = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetWrongMinSize.size, packetWrongMinSize))

        packetWrongVersion = numpy.array([0x98, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packetWrongVersion = appendCRC(packetWrongVersion)
        in_pduWrongVersion = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetWrongVersion.size, packetWrongVersion))

        packetNoSecondaryHeader = numpy.array([0x10, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packetNoSecondaryHeader = appendCRC(packetNoSecondaryHeader)
        in_pduNoSecondaryHeader = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetNoSecondaryHeader.size, packetNoSecondaryHeader))
        
        packetWrongSeqFlags = numpy.array([0x18, 0x03, 0xa0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packetWrongSeqFlags = appendCRC(packetWrongSeqFlags)
        in_pduWrongSeqFlags = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetWrongSeqFlags.size, packetWrongSeqFlags))

        packetSizeMismatch = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packetSizeMismatch = appendCRC(packetSizeMismatch)
        in_pduSizeMismatch = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSizeMismatch.size, packetSizeMismatch))

        self.tb.start()
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pduWrongMinSize) 
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pduWrongVersion) 
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pduNoSecondaryHeader)         
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pduWrongSeqFlags) 
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pduSizeMismatch) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        for i in range(0,len(self.servicesList)):     
            self.assertTrue(d1[i].num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

    def test_002_ServicePool_secondary_header_invalid(self):
        testData = self.testData[1]
                
        servicePool = pus.ServicesPool(self.servicesList)
        
        d1 = []
        for i in range(0,len(self.servicesList)):
            d1.insert(i, blocks.message_debug())
            self.tb.msg_connect((servicePool, 'out' + str(i)), (d1[i], 'store'))
            
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)


        self.tb.msg_connect((servicePool, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x10 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        for i in range(0,len(self.servicesList)):     
            self.assertTrue(d1[i].num_messages() == 0)
            
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ServicePool_crc_invalid(self):
        testData = self.testData[2]
                
        servicePool = pus.ServicesPool(self.servicesList)
        
        d1 = []
        for i in range(0,len(self.servicesList)):
            d1.insert(i, blocks.message_debug())
            self.tb.msg_connect((servicePool, 'out' + str(i)), (d1[i], 'store'))
            
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)


        self.tb.msg_connect((servicePool, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        packet[len(packet)-2]=packet[len(packet)-2]+1
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        for i in range(0,len(self.servicesList)):     
            self.assertTrue(d1[i].num_messages() == 0)
            
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_004_ServicePool_service_type_non_exists(self):
        testData = self.testData[3]
             
        servicePool = pus.ServicesPool(self.servicesList)
        
        d1 = []
        for i in range(0,len(self.servicesList)):
            d1.insert(i, blocks.message_debug())
            self.tb.msg_connect((servicePool, 'out' + str(i)), (d1[i], 'store'))
            
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)


        self.tb.msg_connect((servicePool, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20  | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        for i in range(0,len(self.servicesList)):     
            self.assertTrue(d1[i].num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ServicePool_Service_ST03_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[4]))

    def test_006_ServicePool_Service_ST04_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[5]))
        
    def test_007_ServicePool_Service_ST05_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[6]))

    def test_008_ServicePool_Service_ST06_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[7]))

    def test_009_ServicePool_Service_ST08_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[8]))

    def test_010_ServicePool_Service_ST11_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[9]))
        
    def test_011_ServicePool_Service_ST12_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[10]))

    def test_012_ServicePool_Service_ST13_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[11]))

    def test_013_ServicePool_Service_ST14_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[12]))

    def test_014_ServicePool_Service_ST15_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[13]))
        
    def test_015_ServicePool_Service_ST17_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[14]))

    def test_016_ServicePool_Service_ST19_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[15]))

    def test_017_ServicePool_Service_ST20_verify_forward_message(self):
        self.assertTrue(self.forward_verification(self.testData[16]))
                           
    def forward_verification(self, testData):
        servicePool = pus.ServicesPool(self.servicesList)
        
        d1 = []
        for i in range(0,len(self.servicesList)):
            d1.insert(i, blocks.message_debug())
            self.tb.msg_connect((servicePool, 'out' + str(i)), (d1[i], 'store'))
            
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)


        self.tb.msg_connect((servicePool, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20  | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        servicePool.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        for i in range(0,len(self.servicesList)):     
            if self.servicesList[i] == testData.messageType:
                self.assertTrue(d1[i].num_messages() == 1)
                print(d1[i].get_message(0))
                print(packet)
                response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1[i].get_message(0))), dtype=numpy.uint8)   
                if not numpy.array_equal(response, packet):
                    return False             
            else:
                if d1[i].num_messages() != 0:
                    return False             
        if d2.num_messages() != 0:
                return False         
        return True
        
def checkFailedAcceptanceVerification(message, sentMessage, error):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)
        
    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))
    error_type = pmt.to_long(pmt.dict_ref(meta, pmt.intern("error_type"), pmt.PMT_NIL))

    if report_req != 2:
        return False
    if error_type != error:
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
    gr_unittest.run(qa_ServicesPool, "qa_ServicesPool.xml" )

