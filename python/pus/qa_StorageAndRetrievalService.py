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
        
class qa_StorageAndRetrievalService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x0f, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x0f, 0x01, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x0f, 0x02, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x0f, 0x02, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x0f, 0x03, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x0f, 0x03, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x0f, 0x03, 0x00, -1, 1, 0x19, 0, 51, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x0f, 0x03, 0x00, -1, 1, 0x19, 0, 55, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x0f, 0x04, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x0f, 0x04, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x0f, 0x04, 0x00, -1, 1, 0x19, 0, 56, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x0f, 0x04, 0x00, -1, 1, 0x19, 0, 55, 0, True, 0, 0)) #11
        self.testData.append(test_data(0x0f, 0x05, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x0f, 0x05, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #13
        self.testData.append(test_data(0x0f, 0x05, 0x06, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #14
        self.testData.append(test_data(0x0f, 0x09, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #15
        self.testData.append(test_data(0x0f, 0x09, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x0f, 0x09, 0x00, -1, 1, 0x19, 0, 21, 0, True, 0, 0)) #17
        self.testData.append(test_data(0x0f, 0x0b, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #18
        self.testData.append(test_data(0x0f, 0x0b, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #19
        self.testData.append(test_data(0x0f, 0x0c, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #20
        self.testData.append(test_data(0x0f, 0x0c, 0x0d, -1, 1, 0x19, 15, 10, 0, True, 0, 0)) #21
        self.testData.append(test_data(0x0f, 0x0e, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #22
        self.testData.append(test_data(0x0f, 0x0e, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #23
        self.testData.append(test_data(0x0f, 0x0f, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #24
        self.testData.append(test_data(0x0f, 0x0f, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #25
        self.testData.append(test_data(0x0f, 0x10, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #26
        self.testData.append(test_data(0x0f, 0x10, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #27
        self.testData.append(test_data(0x0f, 0x11, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #28
        self.testData.append(test_data(0x0f, 0x11, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #29        
        self.testData.append(test_data(0x0f, 0x12, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #30
        self.testData.append(test_data(0x0f, 0x12, 0x13, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #31
        self.testData.append(test_data(0x0f, 0x14, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #32
        self.testData.append(test_data(0x0f, 0x14, 0x00, -1, 1, 0x19, 0, 16, 0, True, 0, 0)) #33
        self.testData.append(test_data(0x0f, 0x14, 0x00, -1, 1, 0x19, 0, 34, 0, True, 0, 0)) #34
        self.testData.append(test_data(0x0f, 0x15, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #35
        self.testData.append(test_data(0x0f, 0x15, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #36 
        self.testData.append(test_data(0x0f, 0x16, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #37
        self.testData.append(test_data(0x0f, 0x16, 0x17, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #38
        self.testData.append(test_data(0x0f, 0x18, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #39
        self.testData.append(test_data(0x0f, 0x18, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #40 
        self.testData.append(test_data(0x0f, 0x19, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #41
        self.testData.append(test_data(0x0f, 0x19, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #42 
        self.testData.append(test_data(0x0f, 0x1a, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #43
        self.testData.append(test_data(0x0f, 0x1a, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #44 
        self.testData.append(test_data(0x0f, 0x1b, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #45
        self.testData.append(test_data(0x0f, 0x1b, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #46         
        self.testData.append(test_data(0x0f, 0x1c, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #47
        self.testData.append(test_data(0x0f, 0x1c, 0x00, -1, 1, 0x19, 0, 10, 0, True, 0, 0)) #48  
        self.testData.append(test_data(0x0f, 0x1c, 0x00, -1, 1, 0x19, 0, 34, 0, True, 0, 0)) #49 
        self.testData.append(test_data(0x0f, 0x14, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #50
        self.testData.append(test_data(0x0f, 0x16, 0x17, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #51
        self.testData.append(test_data(0x0f, 0x05, 0x06, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #52
        self.testData.append(test_data(0x0f, 0x03, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #53
        self.testData.append(test_data(0x0f, 0x04, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #54
        self.testData.append(test_data(0x0f, 0x15, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #55
        self.testData.append(test_data(0x0f, 0x03, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #56
        self.testData.append(test_data(0x0f, 0x12, 0x13, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #57 
        self.testData.append(test_data(0x0f, 0x0c, 0x0d, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #58        
        self.testData.append(test_data(0x0f, 0x01, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #59
        self.testData.append(test_data(0x0f, 0x02, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #60
        self.testData.append(test_data(0x0f, 0x1c, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #61
        self.testData.append(test_data(0x0f, 0x0e, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #62
        self.testData.append(test_data(0x0f, 0x0c, 0x0d, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #63  
        self.testData.append(test_data(0x0f, 0x0f, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #64
        self.testData.append(test_data(0x0f, 0x1c, 0x00, -1, 1, 0x19, 0, 14, 0, True, 0, 0)) #65
        self.testData.append(test_data(0x0f, 0x01, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #66
        self.testData.append(test_data(0x0f, 0x10, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #67        
        self.testData.append(test_data(0x0f, 0x0f, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #68
        self.testData.append(test_data(0x0f, 0x09, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #69
        self.testData.append(test_data(0x0f, 0x12, 0x13, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #70
        self.testData.append(test_data(0x0f, 0x0b, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #71
                                                                                                                                 
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        #instance = pus.StorageAndRetrievalService("", [1,2], 32000)

    def test_001_ST15_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))
        
        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x04, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x0f, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  
        
    def test_002_ST15_01_invalid_num_stores_shorter(self):
        testData = self.testData[0]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST15_01_invalid_pktStoreID_shorter(self):
        testData = self.testData[0]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST15_01_invalid_pktStoreID_longer(self):
        testData = self.testData[0]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01,0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST15_01_invalid_pktStoreID_non_exists(self):
        testData = self.testData[1]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01,0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_006_ST15_02_invalid_num_stores_shorter(self):
        testData = self.testData[2]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_ST15_02_invalid_pktStoreID_shorter(self):
        testData = self.testData[2]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_ST15_02_invalid_pktStoreID_longer(self):
        testData = self.testData[2]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01,0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_009_ST15_02_invalid_pktStoreID_non_exists(self):
        testData = self.testData[3]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01,0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_010_ST15_03_invalid_pktStoreID_shorter(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_011_ST15_03_invalid_n1_shorter(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_012_ST15_03_invalid_appID_shorter(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_013_ST15_03_invalid_n2_shorter(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST15_03_invalid_srvID_shorter(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_015_ST15_03_invalid_n3_shorter(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_016_ST15_03_invalid_subtypeID_shorter(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_017_ST15_03_invalid_subtypeID_longer(self):
        testData = self.testData[4]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01, 0x0a, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_018_ST15_03_invalid_pktStoreID_non_exists(self):
        testData = self.testData[5]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01, 0x0a], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_019_ST15_03_invalid_appID_non_exists(self):
        testData = self.testData[6]

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        requestVerificationService = pus.RequestVerificationService()  
                    
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x04, 0x00, 0x01, 0x03, 0x00, 0x01, 0x0a], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_020_ST15_03_invalid_subTypeID_non_exists(self):
        testData = self.testData[7]

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
     
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01, 0x5a], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_021_ST15_04_invalid_pktStoreID_shorter(self):
        testData = self.testData[8]
  
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_022_ST15_04_invalid_n1_shorter(self):
        testData = self.testData[8]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_023_ST15_04_invalid_appID_shorter(self):
        testData = self.testData[8]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_024_ST15_04_invalid_n2_shorter(self):
        testData = self.testData[8]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_025_ST15_04_invalid_srvID_shorter(self):
        testData = self.testData[8]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_026_ST15_04_invalid_n3_shorter(self):
        testData = self.testData[8]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_027_ST15_04_invalid_subtypeID_shorter(self):
        testData = self.testData[8]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_028_ST15_04_invalid_subtypeID_longer(self):
        testData = self.testData[8]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01, 0x0a, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_029_ST15_04_invalid_pktStoreID_non_exists(self):
        testData = self.testData[9]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01, 0x0a], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_030_ST15_04_invalid_appID_non_exists(self):
        testData = self.testData[10]

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x04, 0x00, 0x01, 0x03, 0x00, 0x01, 0x0a], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_031_ST15_04_invalid_subTypeID_non_exists(self):
        testData = self.testData[11]

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01, 0x5a], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_032_ST15_05_invalid_pktStoreID_shorter(self):
        testData = self.testData[12]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_033_ST15_05_invalid_pktStoreID_longer(self):
        testData = self.testData[12]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_034_ST15_05_invalid_pktStoreID_non_exists(self):
        testData = self.testData[13]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x66, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))


    def test_035_ST15_05_valid_report(self):
        testData = self.testData[14]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        onBoardMonitoringService = pus.OnBoardMonitoringService("")               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        expected_response_0 = numpy.array([104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 2, 0, 3, 0, 1, 1, 0, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 25, 0, 2, 3, 0, 1, 10, 12, 0, 2, 10, 11], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))   

    def test_036_ST19_09_invalid_num_stores_shorter(self):
        testData = self.testData[15]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_037_ST15_09_invalid_pktStoreID_shorter(self):
        testData = self.testData[15]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_038_ST15_09_invalid_fromTime_shorter(self):
        testData = self.testData[15]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_039_ST15_09_invalid_toTime_shorter(self):
        testData = self.testData[15]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_040_ST15_09_invalid_toTime_longer(self):
        testData = self.testData[15]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_041_ST15_09_invalid_pktStoreID_non_exists(self):
        testData = self.testData[16]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x67, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_042_ST15_09_invalid_timeWindows(self):
        testData = self.testData[17]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0xa0, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_043_ST15_11_invalid_time_shorter(self):
        testData = self.testData[18]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_044_ST15_11_invalid_num_stores_shorter(self):
        testData = self.testData[18]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_045_ST15_11_invalid_pktStoreID_shorter(self):
        testData = self.testData[18]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_046_ST15_11_invalid_pktStoreID_longer(self):
        testData = self.testData[18]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_047_ST15_11_invalid_pktStoreID_non_exists(self):
        testData = self.testData[19]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_048_ST15_12_invalid_num_stores_shorter(self):
        testData = self.testData[20]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_049_ST15_12_invalid_pktStoreID_shorter(self):
        testData = self.testData[20]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_050_ST15_12_invalid_pktStoreID_longer(self):
        testData = self.testData[20]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_051_ST15_12_invalid_pktStoreID_non_exists(self):
        testData = self.testData[21]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x68, 0x6f, 0x75, 0x73, 0x67, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))

        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)

        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response)) 
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))

    def test_052_ST15_14_invalid_time_shorter(self):
        testData = self.testData[22]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_053_ST15_14_invalid_num_stores_shorter(self):
        testData = self.testData[22]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_054_ST15_14_invalid_pktStoreID_shorter(self):
        testData = self.testData[22]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_055_ST15_14_invalid_pktStoreID_longer(self):
        testData = self.testData[22]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_056_ST15_14_invalid_pktStoreID_non_exists(self):
        testData = self.testData[23]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_057_ST15_15_invalid_num_stores_shorter(self):
        testData = self.testData[24]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_058_ST15_15_invalid_pktStoreID_shorter(self):
        testData = self.testData[24]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_059_ST15_15_invalid_pktStoreID_longer(self):
        testData = self.testData[24]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_060_ST15_15_invalid_pktStoreID_non_exists(self):
        testData = self.testData[25]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x68, 0x6f, 0x75, 0x73, 0x67, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
  
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))


    def test_061_ST15_16_invalid_num_stores_shorter(self):
        testData = self.testData[26]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_062_ST15_16_invalid_pktStoreID_shorter(self):
        testData = self.testData[26]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_063_ST15_16_invalid_pktStoreID_longer(self):
        testData = self.testData[26]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_064_ST15_16_invalid_pktStoreID_non_exists(self):
        testData = self.testData[27]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x68, 0x6f, 0x75, 0x73, 0x67, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
  
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_065_ST15_17_invalid_num_stores_shorter(self):
        testData = self.testData[28]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_066_ST15_17_invalid_pktStoreID_shorter(self):
        testData = self.testData[28]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_067_ST15_17_invalid_pktStoreID_longer(self):
        testData = self.testData[28]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_068_ST15_17_invalid_pktStoreID_non_exists(self):
        testData = self.testData[29]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x68, 0x6f, 0x75, 0x73, 0x67, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
  
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_069_ST15_18_invalid_params_longer(self):
        testData = self.testData[30]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_070_ST15_18_valid_pktStoreID(self):
        testData = self.testData[31]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)

        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))   


    def test_071_ST15_18_invalid_num_stores_shorter(self):
        testData = self.testData[32]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_072_ST15_18_invalid_pktStoreID_shorter(self):
        testData = self.testData[32]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))


    def test_073_ST15_18_invalid_pktStoreSize_shorter(self):
        testData = self.testData[32]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_074_ST15_18_invalid_pktStoreType_shorter(self):
        testData = self.testData[32]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_075_ST15_18_invalid_pktStoreVC_shorter(self):
        testData = self.testData[32]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_076_ST15_18_invalid_pktStoreVC_longer(self):
        testData = self.testData[32]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x01, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_077_ST15_18_invalid_pktStoreID_exists(self):
        testData = self.testData[33]
                 
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x01], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_078_ST15_18_invalid_pktStoreVC(self):
        testData = self.testData[34]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x0f], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_079_ST15_21_invalid_num_stores_shorter(self):
        testData = self.testData[35]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_080_ST15_21_invalid_pktStoreID_shorter(self):
        testData = self.testData[35]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_081_ST15_21_invalid_pktStoreID_longer(self):
        testData = self.testData[35]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_082_ST15_21_invalid_pktStoreID_non_exists(self):
        testData = self.testData[36]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x68, 0x6f, 0x75, 0x73, 0x67, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
  
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_083_ST15_22_invalid_params_longer(self):
        testData = self.testData[37]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_084_ST15_22_valid_pktStoreID(self):
        testData = self.testData[38]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)

        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 2, 0, 0, 1], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))   

    def test_085_ST15_24_invalid_type_shorter(self):
        testData = self.testData[39]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_086_ST15_24_invalid_time1Tag_shorter(self):
        testData = self.testData[39]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_087_ST15_24_invalid_time2Tag_shorter(self):
        testData = self.testData[39]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_088_ST15_24_invalid_fromPktStore_shorter(self):
        testData = self.testData[39]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00, 0xf0, 0x00, 0x52], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_089_ST15_24_invalid_toPktStore_shorter(self):
        testData = self.testData[39]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00, 0xf0, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_090_ST15_24_invalid_toPktStore_longer(self):
        testData = self.testData[39]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00, 0xf0, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_091_ST15_24_invalid_fromPktStore_non_exists(self):
        testData = self.testData[40]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00, 0xf0, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_092_ST15_24_invalid_toPktStore_non_exists(self):
        testData = self.testData[40]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x00, 0x00, 0xf0, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_093_ST15_25_invalid_num_stores_shorter(self):
        testData = self.testData[41]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_094_ST15_25_invalid_pktStoreID_shorter(self):
        testData = self.testData[41]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_095_ST15_25_invalid_pktStoreSize_shorter(self):
        testData = self.testData[41]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01,0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_096_ST15_25_invalid_pktStoreSize_longer(self):
        testData = self.testData[41]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01,0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x1f, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_097_ST15_25_invalid_pktStoreID_non_exists(self):
        testData = self.testData[42]
                
        storageAndRetrievalService = pus.StorageAndRetrievalService("", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01,0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x1f], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_098_ST15_26_invalid_pktStoreID_shorter(self):
        testData = self.testData[43]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_099_ST15_26_invalid_pktStoreID_longer(self):
        testData = self.testData[43]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_100_ST15_26_invalid_pktStoreID_non_exists(self):
        testData = self.testData[44]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x66, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_101_ST15_27_invalid_pktStoreID_shorter(self):
        testData = self.testData[45]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_102_ST15_27_invalid_pktStoreID_longer(self):
        testData = self.testData[45]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_103_ST15_27_invalid_pktStoreID_non_exists(self):
        testData = self.testData[46]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x66, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_104_ST15_28_invalid_pktStoreID_shorter(self):
        testData = self.testData[47]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_105_ST15_28_invalid_pktStoreVC_shorter(self):
        testData = self.testData[47]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_106_ST15_28_invalid_pktStoreVC_longer(self):
        testData = self.testData[47]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_107_ST15_27_invalid_pktStoreID_non_exists(self):
        testData = self.testData[48]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x66, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_108_ST15_27_invalid_pktStoreVC(self):
        testData = self.testData[49]
  
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
               
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x10], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_109_ST15_20and22and5and4and3and21_create_report_add_remove_delete_pktStore(self):
        # ------------------------------------------------------------
        # Create PktStore TC[15,20]
        # ------------------------------------------------------------   

        testData = self.testData[50]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        requestVerificationService = pus.RequestVerificationService()  
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        parameterStatisticsService = pus.ParameterStatisticsService("../../../examples/init_paramstats.json")        
                   
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x02], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report Configuration of PktStore TC[15,22]
        # ------------------------------------------------------------   

        testData = self.testData[51]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
                
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)

        expected_response_0 = numpy.array([0, 2, 82, 101, 112, 111, 114, 116, 115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 0, 2, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 2, 0, 0, 1], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report Content of PktStore TC[15,05] "Housekeeping"
        # ------------------------------------------------------------   

        testData = self.testData[52]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 1                

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        expected_response_0 = numpy.array([104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 2, 0, 3, 0, 1, 1, 0, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 25, 0, 2, 3, 0, 1, 10, 12, 0, 2, 10, 11], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet)) 

        # ------------------------------------------------------------
        # Report Content of PktStore TC[15,05] "Reports"
        # ------------------------------------------------------------   

        testData = self.testData[52]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 2
        testData.counter_sec_offset = 1        

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        expected_response_0 = numpy.array([82, 101, 112, 111, 114, 116, 115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet)) 

        # ------------------------------------------------------------
        # Add PktStore TC[15,3]
        # ------------------------------------------------------------   

        testData = self.testData[53]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19,0x00, 0x01, 0x01, 0x00, 0x08, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  


        # ------------------------------------------------------------
        # Add PktStore TC[15,3]
        # ------------------------------------------------------------   

        testData = self.testData[53]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report Content of PktStore TC[15,05] "Housekeeping"
        # ------------------------------------------------------------   

        testData = self.testData[52]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 3
        testData.counter_sec_offset = 2             

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
 
        expected_response_0 = numpy.array([104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 2, 0, 3, 0, 1, 1, 0, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 25, 0, 5, 1, 0, 9, 1, 2, 3, 4, 5, 6, 7, 8, 10, 3, 0, 12, 10, 1, 3, 5, 6, 9, 25, 27, 29, 31, 33, 35, 4, 0, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 0, 14, 10, 11, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 0, 25, 1, 2, 3, 4, 5, 6, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet)) 

        # ------------------------------------------------------------
        # Report Content of PktStore TC[15,05] "Reports"
        # ------------------------------------------------------------   

        testData = self.testData[52]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 4
        testData.counter_sec_offset = 3        
   
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        expected_response_0 = numpy.array([82, 101, 112, 111, 114, 116, 115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 25, 0, 1, 1, 0, 8, 1, 2, 3, 4, 5, 6, 7, 8], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet)) 

        # ------------------------------------------------------------
        # Remove PktStore TC[15,4]
        # ------------------------------------------------------------   

        testData = self.testData[54]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19,0x00, 0x01, 0x01, 0x00, 0x02, 0x05, 0x06], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report Content of PktStore TC[15,05] "Reports"
        # ------------------------------------------------------------   

        testData = self.testData[52]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 5
        testData.counter_sec_offset = 4        
  
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        expected_response_0 = numpy.array([82, 101, 112, 111, 114, 116, 115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 25, 0, 1, 1, 0, 6, 1, 2, 3, 4, 7, 8], dtype=numpy.uint8)  
    
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet)) 

        # ------------------------------------------------------------
        # Remove PktStore TC[15,4]
        # ------------------------------------------------------------   

        testData = self.testData[54]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x01, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report Content of PktStore TC[15,05] "Reports"
        # ------------------------------------------------------------   

        testData = self.testData[52]
       
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 6
        testData.counter_sec_offset = 5        
        
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        expected_response_0 = numpy.array([82, 101, 112, 111, 114, 116, 115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        result1 = checkResults(1, d1, payloads, 0, d2, 0, testData, packet)
        
        testData.counter_offset = 7
        testData.counter_sec_offset = 5  

        result2 = checkResults(1, d1, payloads, 0, d2, 0, testData, packet)  
            
        self.assertTrue(result1 or result2)

        # ------------------------------------------------------------
        # Delete PktStore TC[15,21]
        # ------------------------------------------------------------   

        testData = self.testData[55]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x52, 0x65, 0x70, 0x6f, 0x72, 0x74, 0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report Configuration of PktStore TC[15,22]
        # ------------------------------------------------------------   

        testData = self.testData[51]
          
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
                
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)

        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 2, 0, 0, 1], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        testData.counter_offset = 7
        testData.counter_sec_offset = 1  

        result1 = checkResults(1, d1, payloads, 0, d2, 0, testData, packet)
        
        testData.counter_offset = 8
        testData.counter_sec_offset = 1  

        result2 = checkResults(1, d1, payloads, 0, d2, 0, testData, packet)  
              
        self.assertTrue(result1 or result2)

    def test_110_ST15_1and2and18and28and14_add_report_enable_change_retrieval_disable_pktStore(self):
        # ------------------------------------------------------------
        # Add PktStore TC[15,3]
        # ------------------------------------------------------------   

        testData = self.testData[56]
                
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        requestVerificationService = pus.RequestVerificationService()  
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        parameterStatisticsService = pus.ParameterStatisticsService("../../../examples/init_paramstats.json")        
                   
        storageAndRetrievalService = pus.StorageAndRetrievalService("../../../examples/init_stgandret.json", [1,2], 32000)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (storageAndRetrievalService, 'in_msg'))
        self.tb.msg_connect((housekeepingService, 'ver'), (requestVerificationService, 'in'))
        self.tb.msg_connect((parameterStatisticsService, 'out'), (storageAndRetrievalService, 'in_msg'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (requestVerificationService, 'in'))
        self.tb.msg_connect((requestVerificationService, 'out'), (storageAndRetrievalService, 'in_msg'))
        self.tb.msg_connect((storageAndRetrievalService, 'out'), (storageAndRetrievalService, 'in_msg'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (requestVerificationService, 'in'))
        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(15)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 0, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report status of PktStore TC[15,18] => TM[15,19]
        # ------------------------------------------------------------   

        testData = self.testData[57]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]
        testData.counter_offset = 2

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet)) 
         
        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[58]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 6

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)

        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet)) 

        # ------------------------------------------------------------
        # Report Content of PktStore TC[15,05] "Housekeeping"
        # ------------------------------------------------------------   

        testData = self.testData[52]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        testData.counter_offset = 10
          

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
 
        expected_response_0 = numpy.array([104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 0, 2, 0, 3, 0, 1, 1, 0, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 25, 0, 5, 1, 0, 9, 1, 2, 3, 4, 5, 6, 7, 8, 10, 3, 0, 12, 10, 1, 3, 5, 6, 9, 25, 27, 29, 31, 33, 35, 4, 0, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 0, 14, 10, 11, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 0, 25, 1, 2, 3, 4, 5, 6, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet)) 
        
        # ------------------------------------------------------------
        # Enable PktStore TC[15,1]
        # ------------------------------------------------------------   

        testData = self.testData[59]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(15)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report status of PktStore TC[15,18] => TM[15,19]
        # ------------------------------------------------------------   

        testData = self.testData[57]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 1, 0, 0], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]
  
        testData.counter_offset = 17
        testData.counter_sec_offset = 1
        
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet, False)) 
         
        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[58]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([0, 0, 0, 0, 0, 20, 0, 20], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        testData.counter_offset = 21
        testData.counter_sec_offset = 1

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
                  
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        telemetry =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
   
        self.assertTrue(numpy.array_equal(telemetry[17:34], expected_response_0))       
        self.assertTrue(numpy.array_equal(telemetry[42:50], expected_response_1))            

        start_time_value = int.from_bytes(telemetry[38:42], "big", signed=True) - 2
        # ------------------------------------------------------------
        # Disable PktStore TC[15,2]
        # ------------------------------------------------------------   

        testData = self.testData[60]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(15)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  
        # ------------------------------------------------------------
        # change VC PktStore TC[15,28]
        # ------------------------------------------------------------   
        testData = self.testData[61]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # change Start time PktStore TC[15,14]
        # ------------------------------------------------------------   

        testData = self.testData[62]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        obt_array = bytearray(start_time_value.to_bytes(4, "big", signed = False))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, obt_array[0], obt_array[1], obt_array[2], obt_array[3], 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(15)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
        
        payloads = []

        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[63]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0], dtype=numpy.uint8)  
        #expected_response_1 = numpy.array([0, 28, 0, 18], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        testData.counter_offset = 21
        testData.counter_sec_offset = 1

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)

        telemetry =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
   
        self.assertTrue(numpy.array_equal(telemetry[17:34], expected_response_0))       
        self.assertTrue(telemetry[47] > telemetry[49])             

        # ------------------------------------------------------------
        # Resume retrieval PktStore TC[15,15]
        # ------------------------------------------------------------   
        testData = self.testData[64]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 7)
        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[63]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 7)
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([0, 28, 0, 18], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        testData.counter_offset = 21
        testData.counter_sec_offset = 1

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)

        telemetry =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
   
        self.assertTrue(numpy.array_equal(telemetry[17:34], expected_response_0))       
        self.assertTrue(telemetry[47] > telemetry[49]) 

        # ------------------------------------------------------------
        # change VC PktStore TC[15,28]
        # ------------------------------------------------------------   
        testData = self.testData[65]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
        # ------------------------------------------------------------
        # Enable PktStore TC[15,1]
        # ------------------------------------------------------------   

        testData = self.testData[66]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(15)
        self.tb.stop()
        self.tb.wait()
            
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)                
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 2)
        
        payloads = []


        #self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[63]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 2)
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([0, 36, 0, 26], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        testData.counter_offset = 21
        testData.counter_sec_offset = 1

        telemetry =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
   
        self.assertTrue(numpy.array_equal(telemetry[17:34], expected_response_0))       
        self.assertTrue(telemetry[47] > telemetry[49])  

        # ------------------------------------------------------------
        # Suspend retrieval PktStore TC[15,15]
        # ------------------------------------------------------------   
        testData = self.testData[67]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(15)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 2)
        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))         

        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[63]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 2)
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0], dtype=numpy.uint8)  
        #expected_response_1 = numpy.array([0, 36, 0, 26], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        testData.counter_offset = 21
        testData.counter_sec_offset = 1

        telemetry =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
   
        self.assertTrue(numpy.array_equal(telemetry[17:34], expected_response_0))       
        self.assertTrue(telemetry[47] > telemetry[49])  

        # ------------------------------------------------------------
        # Resume retrieval PktStore TC[15,15]
        # ------------------------------------------------------------   
        testData = self.testData[68]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
         
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 3)

        # ------------------------------------------------------------
        # Suspend retrieval PktStore TC[15,15]
        # ------------------------------------------------------------   
        testData = self.testData[67]

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
       
        # ------------------------------------------------------------
        # change Start time PktStore TC[15,14]
        # ------------------------------------------------------------   
        testData = self.testData[62]

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, obt_array[0], obt_array[1], obt_array[2], obt_array[3], 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(15)
        self.tb.stop()
        self.tb.wait()

        # ------------------------------------------------------------
        # Resume retrieval PktStore TC[15,15]
        # ------------------------------------------------------------   
        testData = self.testData[68]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 20)

        # ------------------------------------------------------------
        # Suspend retrieval PktStore TC[15,15]
        # ------------------------------------------------------------   
        testData = self.testData[67]

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        # ------------------------------------------------------------
        # Retrieve by time window PktStore TC[15,09]
        # ------------------------------------------------------------   
        testData = self.testData[69]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        obt_array = bytearray((start_time_value - 2).to_bytes(4, "big", signed = False))
        obt_array2 = bytearray((start_time_value + 15 ).to_bytes(4, "big", signed = False))
                
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00, obt_array[0], obt_array[1], obt_array[2], obt_array[3], obt_array2[0], obt_array2[1], obt_array2[2], obt_array2[3]], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() > 0)
        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))          
        # ------------------------------------------------------------
        # Report status of PktStore TC[15,18] => TM[15,19]
        # ------------------------------------------------------------   

        testData = self.testData[70]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0, 1, 0, 0], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]
  
        testData.counter_offset = 17
        testData.counter_sec_offset = 1
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        
        self.assertTrue(numpy.array_equal(response[17:-2], expected_response_0))  
        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[63]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)

 
        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([0, 84, 0, 74], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        telemetry =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
   
        self.assertTrue(numpy.array_equal(telemetry[17:34], expected_response_0))       
        self.assertTrue(telemetry[47] > telemetry[49])  
          
        # ------------------------------------------------------------
        # Delete content of PktStore TC[15,11]
        # ------------------------------------------------------------   
        testData = self.testData[71]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()

        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc0'), (d3, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'vc1'), (d4, 'store'))

        obt_array = bytearray((start_time_value + 50).to_bytes(4, "big", signed = False))
                
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, obt_array[0], obt_array[1], obt_array[2], obt_array[3], 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
          
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))          

        # ------------------------------------------------------------
        # Report summary of PktStore TC[15,12] "Housekeeping" => TM[15,13]
        # ------------------------------------------------------------   

        testData = self.testData[63]
        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((storageAndRetrievalService, 'out'), (d1, 'store'))
        self.tb.msg_connect((storageAndRetrievalService, 'ver'), (d2, 'store'))

        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x68, 0x6f, 0x75, 0x73, 0x65, 0x6b, 0x65, 0x65, 0x70, 0x69, 0x6e, 0x67, 0x00, 0x00, 0x00], dtype=numpy.uint8)
       
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        storageAndRetrievalService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)

        expected_response_0 = numpy.array([0, 1, 104, 111, 117, 115, 101, 107, 101, 101, 112, 105, 110, 103, 0, 0, 0], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([0, 58, 0, 58], dtype=numpy.uint8)  
        
        payloads = [expected_response_0]

        telemetry =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
 
        self.assertTrue(numpy.array_equal(telemetry[17:34], expected_response_0))       
        self.assertTrue(telemetry[47] == telemetry[49])  

                                                                                                                                                                                                      
def checkResults(numd1, d1, payloads, numd2, d2, num_progress, testData, packet, primaryHeader = True):

    if d1.num_messages() != numd1:
        return False

    if d2.num_messages() != numd2:
        return False

    for i in range (0, testData.counter):
        h = i        
     
        if len(payloads) > 0:
            for j in range (0, len(payloads)):

               response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(j))), dtype=numpy.uint8)

               if primaryHeader:
                  if not checkPrimaryHeader(testData.apid, testData.messageSize, j, response, testData.counter_offset):
                     return False           

               if not checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, j, response, testData.counter_sec_offset):
                  return False          
                                             
               if testData.crcEnabled:
                  if not checkCRC(response):
                     return False           
                   
               if not checkPayload(payloads[j], response, testData.crcEnabled):
                  return False  

        if testData.ackFlags & 0x01:
            if not checkSuccessAcceptanceVerification(d2.get_message(h), packet): 
                return False  
            h+=1
 
        if testData.ackFlags & 0x02:
            if not checkSuccessStartExecutionVerification(d2.get_message(h), packet):
                return False  
            h+=1        

        if testData.ackFlags & 0x04:
            for j in range (0, num_progress):

               if not checkSuccessProgressExecutionVerification(d2.get_message(h), packet, j):
                  return False  
               h+=1       
 
        if testData.ackFlags & 0x08:

            if not checkSuccessSuccessCompletionExecutionVerification(d2.get_message(h), packet):   
                return False  
            h+=1

    return True
                                                                                                            
def checkPrimaryHeader(apid, size, counter, message, counter_offset):
    counter += counter_offset
    bytes_val = bytearray(apid.to_bytes(2, "big", signed = False))
    apidArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8) 
    counter = counter & 0xffff   
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
    counter = counter & 0xffff  
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
    gr_unittest.run(qa_StorageAndRetrievalService, "qa_StorageAndRetrievalService.xml" )
