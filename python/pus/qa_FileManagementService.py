#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Gustavo Gonzalez.
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
        
class qa_FileManagementService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x17, 0x01, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x17, 0x01, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x17, 0x01, 0x00, 0x11, 1, 0x19, 0, 3, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x17, 0x02, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x17, 0x02, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x17, 0x02, 0x00, 0x11, 1, 0x19, 0, 4, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x17, 0x02, 0x00, 0x11, 1, 0x19, 0, 6, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x17, 0x02, 0x00, 0x11, 1, 0x19, 0, 5, 0, True, 0, 0)) #7        
        self.testData.append(test_data(0x17, 0x03, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x17, 0x03, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x17, 0x03, 0x00, 0x11, 1, 0x19, 0, 4, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x17, 0x03, 0x00, 0x11, 1, 0x19, 0, 8, 0, True, 0, 0)) #11
        self.testData.append(test_data(0x17, 0x05, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x17, 0x05, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #13
        self.testData.append(test_data(0x17, 0x06, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #14
        self.testData.append(test_data(0x17, 0x06, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #15
        self.testData.append(test_data(0x17, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x17, 0x07, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #17
        self.testData.append(test_data(0x17, 0x09, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #18
        self.testData.append(test_data(0x17, 0x09, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #19
        self.testData.append(test_data(0x17, 0x09, 0x00, 0x11, 1, 0x19, 0, 9, 0, True, 0, 0)) #20        
        self.testData.append(test_data(0x17, 0x0a, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #21
        self.testData.append(test_data(0x17, 0x0a, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #22
        self.testData.append(test_data(0x17, 0x0a, 0x00, 0x11, 1, 0x19, 0, 4, 0, True, 0, 0)) #23   
        self.testData.append(test_data(0x17, 0x0b, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #24
        self.testData.append(test_data(0x17, 0x0b, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #25
        self.testData.append(test_data(0x17, 0x0b, 0x00, 0x11, 1, 0x19, 0, 4, 0, True, 0, 0)) #26          
        self.testData.append(test_data(0x17, 0x0b, 0x00, 0x11, 1, 0x19, 0, 9, 0, True, 0, 0)) #27            
        self.testData.append(test_data(0x17, 0x0c, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #28
        self.testData.append(test_data(0x17, 0x0c, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #29
        self.testData.append(test_data(0x17, 0x0c, 0x00, 0x11, 1, 0x19, 0, 4, 0, True, 0, 0)) #30   
               
        self.testData.append(test_data(0x17, 0x0e, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #31
        self.testData.append(test_data(0x17, 0x0e, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #32
        self.testData.append(test_data(0x17, 0x0e, 0x00, 0x11, 1, 0x19, 0, 4, 0, True, 0, 0)) #33          
        self.testData.append(test_data(0x17, 0x0e, 0x00, 0x11, 1, 0x19, 0, 3, 0, True, 0, 0)) #34                  

        self.testData.append(test_data(0x17, 0x0f, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #35
        self.testData.append(test_data(0x17, 0x0f, 0x00, 0x11, 1, 0x19, 0, 83, 0, True, 0, 0)) #36
        self.testData.append(test_data(0x17, 0x0f, 0x00, 0x11, 1, 0x19, 0, 4, 0, True, 0, 0)) #37          
        self.testData.append(test_data(0x17, 0x0f, 0x00, 0x11, 1, 0x19, 0, 3, 0, True, 0, 0)) #38  
        self.testData.append(test_data(0x17, 0x0f, 0x00, 0x11, 1, 0x19, 0, 15, 0, True, 0, 0)) #39  

        self.testData.append(test_data(0x17, 0x09, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #40
        self.testData.append(test_data(0x17, 0x01, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #41
        self.testData.append(test_data(0x17, 0x01, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #42
        self.testData.append(test_data(0x17, 0x09, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #43
        self.testData.append(test_data(0x17, 0x0c, 0x0d, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #44
        self.testData.append(test_data(0x17, 0x03, 0x04, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #45
        self.testData.append(test_data(0x17, 0x07, 0x08, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #46
        self.testData.append(test_data(0x17, 0x05, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #47
        self.testData.append(test_data(0x17, 0x06, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #48
        self.testData.append(test_data(0x17, 0x02, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #49        
        self.testData.append(test_data(0x17, 0x0e, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #50         
        self.testData.append(test_data(0x17, 0x06, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #51
        self.testData.append(test_data(0x17, 0x0f, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #52  
        self.testData.append(test_data(0x17, 0x0b, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #53  
        self.testData.append(test_data(0x17, 0x0a, 0x00, 0x11, 1, 0x19, 15, 16, 0, True, 0, 0)) #54 
        self.testData.append(test_data(0x17, 0x02, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #55    
        self.testData.append(test_data(0x17, 0x0a, 0x00, 0x11, 1, 0x19, 0, 16, 0, True, 0, 0)) #56         
        self.testData.append(test_data(0x17, 0x0a, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #57   
        self.testData.append(test_data(0x17, 0x0a, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #58 
                                                                                                        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.FileManagementService("./")

    def test_001_ST23_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x03, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x17, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST23_01_invalid_repPath_field_shorter(self):
        testData = self.testData[0]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST23_01_invalid_fileName_field_shorter(self):
        testData = self.testData[0]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST23_01_invalid_maxSize_field_shorter(self):
        testData = self.testData[0]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, ], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST23_01_invalid_lock_field_shorter(self):
        testData = self.testData[0]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 0, 0, 255], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_006_ST23_01_invalid_lock_field_longer(self):
        testData = self.testData[0]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 0, 0, 255, 1, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_ST23_01_invalid_wildcards(self):
        testData = self.testData[1]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x2a, 0, 0, 0, 255, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_008_ST23_01_invalid_repPath_non_exists(self):
        testData = self.testData[1]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 0, 0, 255, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_009_ST23_01_invalid_repPath_lead_to_file(self):
        testData = self.testData[1]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 0, 0, 255, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_010_ST23_01_invalid_file_already_exists(self):
        testData = self.testData[2]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 12, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 0, 0, 255, 0], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_011_ST23_02_invalid_repPath_field_shorter(self):
        testData = self.testData[3]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_012_ST23_02_invalid_fileName_field_shorter(self):
        testData = self.testData[3]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_013_ST23_02_invalid_fileName_field_longer(self):
        testData = self.testData[3]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST23_02_invalid_wildcards(self):
        testData = self.testData[4]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x2a], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_015_ST23_02_invalid_repPath_non_exists(self):
        testData = self.testData[4]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_016_ST23_02_invalid_repPath_lead_to_file(self):
        testData = self.testData[4]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_017_ST23_02_invalid_file_non_exists(self):
        testData = self.testData[5]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 12, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x75], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_018_ST23_02_invalid_file_is_a_dir(self):
        testData = self.testData[6]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_019_ST23_02_invalid_file_is_lock(self):
        testData = self.testData[7]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_020_ST23_03_invalid_repPath_field_shorter(self):
        testData = self.testData[8]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_021_ST23_03_invalid_fileName_field_shorter(self):
        testData = self.testData[8]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_022_ST23_03_invalid_fileName_field_longer(self):
        testData = self.testData[8]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_023_ST23_03_invalid_wildcards(self):
        testData = self.testData[9]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x2a], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_024_ST23_03_invalid_repPath_non_exists(self):
        testData = self.testData[9]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_025_ST23_03_invalid_repPath_lead_to_file(self):
        testData = self.testData[9]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_026_ST23_03_invalid_file_non_exists(self):
        testData = self.testData[10]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 12, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x75], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_027_ST23_03_invalid_file_is_a_dir(self):
        testData = self.testData[11]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_028_ST23_05_invalid_repPath_field_shorter(self):
        testData = self.testData[12]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_029_ST23_05_invalid_fileName_field_shorter(self):
        testData = self.testData[12]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_030_ST23_05_invalid_fileName_field_longer(self):
        testData = self.testData[12]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_031_ST23_05_invalid_wildcards(self):
        testData = self.testData[13]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x2a], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_032_ST23_05_invalid_repPath_non_exists(self):
        testData = self.testData[13]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_033_ST23_05_invalid_repPath_lead_to_file(self):
        testData = self.testData[13]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_034_ST23_06_invalid_repPath_field_shorter(self):
        testData = self.testData[14]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_035_ST23_06_invalid_fileName_field_shorter(self):
        testData = self.testData[14]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_036_ST23_06_invalid_fileName_field_longer(self):
        testData = self.testData[14]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_037_ST23_06_invalid_wildcards(self):
        testData = self.testData[15]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x2a], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_038_ST23_06_invalid_repPath_non_exists(self):
        testData = self.testData[15]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_039_ST23_06_invalid_repPath_lead_to_file(self):
        testData = self.testData[15]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_040_ST23_07_invalid_repPath_field_shorter(self):
        testData = self.testData[16]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_041_ST23_07_invalid_fileName_field_shorter(self):
        testData = self.testData[16]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_042_ST23_07_invalid_fileName_field_longer(self):
        testData = self.testData[16]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_043_ST23_07_invalid_repPath_non_exists(self):
        testData = self.testData[17]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_044_ST23_07_invalid_repPath_lead_to_file(self):
        testData = self.testData[17]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_045_ST23_09_invalid_repPath_field_shorter(self):
        testData = self.testData[18]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_046_ST23_09_invalid_dirName_field_shorter(self):
        testData = self.testData[18]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_047_ST23_09_invalid_dirName_field_longer(self):
        testData = self.testData[18]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_048_ST23_09_invalid_wildcards(self):
        testData = self.testData[19]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x2a], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_049_ST23_09_invalid_repPath_non_exists(self):
        testData = self.testData[19]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_050_ST23_09_invalid_repPath_lead_to_file(self):
        testData = self.testData[19]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_051_ST23_09_invalid_dir_already_exists(self):
        testData = self.testData[20]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x65, 0x78, 0x69, 0x73, 0x74, 0x69, 0x6e, 0x67], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))    

    def test_052_ST23_10_invalid_repPath_field_shorter(self):
        testData = self.testData[21]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_053_ST23_10_invalid_dirName_field_shorter(self):
        testData = self.testData[21]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_054_ST23_10_invalid_dirName_field_longer(self):
        testData = self.testData[21]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_055_ST23_10_invalid_wildcards(self):
        testData = self.testData[22]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x2a], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_056_ST23_10_invalid_repPath_non_exists(self):
        testData = self.testData[22]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_057_ST23_10_invalid_repPath_lead_to_file(self):
        testData = self.testData[22]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_058_ST23_10_invalid_dir_non_exists(self):
        testData = self.testData[23]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x65, 0x78, 0x69, 0x73, 0x74, 0x69, 0x6e, 0x69], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))  

    def test_059_ST23_11_invalid_repPath_field_shorter(self):
        testData = self.testData[24]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_060_ST23_11_invalid_srcDirName_field_shorter(self):
        testData = self.testData[24]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_061_ST23_11_invalid_dstDirName_field_shorter(self):
        testData = self.testData[24]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_062_ST23_11_invalid_dstDirName_field_longer(self):
        testData = self.testData[24]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 8, 0x65, 0x78, 0x69, 0x73, 0x74, 0x69, 0x6e, 0x67, 0, 6, 0x72, 0x65, 0x6e, 0x61, 0x6d, 0x65, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_063_ST23_11_invalid_wildcards(self):
        testData = self.testData[25]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x2a, 0x65, 0x73, 0x2f, 0, 8, 0x65, 0x78, 0x69, 0x73, 0x74, 0x69, 0x6e, 0x67, 0, 6, 0x72, 0x65, 0x6e, 0x61, 0x6d, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_064_ST23_11_invalid_repPath_non_exists(self):
        testData = self.testData[25]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f, 0, 8, 0x65, 0x78, 0x69, 0x73, 0x74, 0x69, 0x6e, 0x67, 0, 6, 0x72, 0x65, 0x6e, 0x61, 0x6d, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_065_ST23_11_invalid_repPath_lead_to_file(self):
        testData = self.testData[25]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 8, 0x70, 0x65, 0x70, 0x65, 0x2e, 0x74, 0x78, 0x74, 0, 6, 0x72, 0x65, 0x6e, 0x61, 0x6d, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_066_ST23_11_invalid_srcDir_non_exists(self):
        testData = self.testData[26]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x65, 0x78, 0x69, 0x73, 0x74, 0x6a, 0x6e, 0x69, 0, 6, 0x72, 0x65, 0x6e, 0x61, 0x6d, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))   
        
    def test_067_ST23_11_invalid_dstDir_already_exists(self):
        testData = self.testData[27]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x65, 0x78, 0x69, 0x73, 0x74, 0x69, 0x6e, 0x67, 0, 6, 0x72, 0x65, 0x6e, 0x61, 0x6d, 0x65], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))      

    def test_068_ST23_12_invalid_repPath_field_shorter(self):
        testData = self.testData[28]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_069_ST23_12_invalid_repPath_field_longer(self):
        testData = self.testData[28]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_070_ST23_12_invalid_wildcards(self):
        testData = self.testData[29]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x2a, 0x70, 0x6c, 0x65, 0x73, 0x2f], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_071_ST23_12_invalid_repPath_non_exists(self):
        testData = self.testData[29]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x75, 0x2f], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_072_ST23_12_invalid_repPath_lead_to_file(self):
        testData = self.testData[29]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 39, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
 
    def test_073_ST23_14_invalid_srcPath_field_shorter(self):
        testData = self.testData[31]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_074_ST23_14_invalid_srcFile_field_shorter(self):
        testData = self.testData[31]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_074_ST23_14_invalid_dstPath_field_shorter(self):
        testData = self.testData[31]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_075_ST23_14_invalid_dstFile_field_shorter(self):
        testData = self.testData[31]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_076_ST23_14_invalid_dstFile_field_longer(self):
        testData = self.testData[31]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
                
    def test_077_ST23_14_invalid_wildcards(self):
        testData = self.testData[32]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x2a, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_078_ST23_14_invalid_path_non_exists(self):
        testData = self.testData[32]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x35, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_079_ST23_14_invalid_path_lead_to_file(self):
        testData = self.testData[32]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 43, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_080_ST23_14_invalid_srcFile_non_exists(self):
        testData = self.testData[33]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x75, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))   
        
    def test_081_ST23_14_invalid_dstFile_already_exists(self):
        testData = self.testData[34]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f,  0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))  

    def test_082_ST23_15_invalid_srcPath_field_shorter(self):
        testData = self.testData[35]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_083_ST23_15_invalid_srcFile_field_shorter(self):
        testData = self.testData[35]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_084_ST23_15_invalid_dstPath_field_shorter(self):
        testData = self.testData[35]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_085_ST23_15_invalid_dstFile_field_shorter(self):
        testData = self.testData[35]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_086_ST23_15_invalid_dstFile_field_longer(self):
        testData = self.testData[35]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
                
    def test_087_ST23_15_invalid_wildcards(self):
        testData = self.testData[36]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x2a, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_088_ST23_15_invalid_path_non_exists(self):
        testData = self.testData[36]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x35, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_089_ST23_15_invalid_path_lead_to_file(self):
        testData = self.testData[36]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 43, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_090_ST23_15_invalid_srcFile_non_exists(self):
        testData = self.testData[37]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x75, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x63, 0x6f, 0x70, 0x79, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))   
        
    def test_091_ST23_15_invalid_dstFile_already_exists(self):
        testData = self.testData[38]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f,  0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))  

    def test_092_ST23_15_invalid_srcFile_is_locked(self):
        testData = self.testData[39]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 16, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f,  0, 17, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x6c, 0x6f, 0x63, 0x6b, 0x2e, 0x74, 0x78, 0x74, 0x31], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error))     
                        
    def test_092_ST23_1to15_create_lock_unlock_delete_report_copy_move(self):
        # ------------------------------------------------------------
        # Create a directory TC[04,09]
        # ------------------------------------------------------------   

        testData = self.testData[40]
                
        fileManagementService = pus.FileManagementService("./")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )
        
        # ------------------------------------------------------------
        # Create a file TC[04,01]
        # ------------------------------------------------------------   

        testData = self.testData[41]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x31, 0x2e, 0x64, 0x6f, 0x63, 0, 0, 0, 255, 0], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )
        
        # ------------------------------------------------------------
        # Create a file TC[04,01]
        # ------------------------------------------------------------   

        testData = self.testData[42]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x32, 0x2e, 0x64, 0x6f, 0x63, 0, 0, 0, 255, 1], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

        # ------------------------------------------------------------
        # Create a directory TC[04,09]
        # ------------------------------------------------------------   

        testData = self.testData[43]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 35, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0, 13, 0x6e, 0x65, 0x73, 0x74, 0x5f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

        # ------------------------------------------------------------
        # summary-report the content of a repository TC[04,12] => TM[04,13]
        # ------------------------------------------------------------   

        testData = self.testData[44]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
      
        expected_response_0 = numpy.array([0, 36, 46, 46, 47, 46, 46, 47, 46, 46, 47, 101, 120, 97, 109, 112, 108, 101, 115, 47, 84, 101, 115, 116, 83, 84, 50, 51, 47, 110, 101, 119, 95, 116, 101, 115, 116, 47, 0, 3, 0, 0, 13, 110, 101, 115, 116, 95, 110, 101, 119, 95, 116, 101, 115, 116, 1, 0, 10, 116, 101, 115, 116, 35, 50, 46, 100, 111, 99, 1, 0, 10, 116, 101, 115, 116, 35, 49, 46, 100, 111, 99], dtype=numpy.uint8)        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Report the attributes of a file TC[04,03] => TM[04,04]
        # ------------------------------------------------------------   

        testData = self.testData[45]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 12, 0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6c, 0x65, 0x2e, 0x74, 0x78, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
      
        expected_response_0 = numpy.array([0, 27, 46, 46, 47, 46, 46, 47, 46, 46, 47, 101, 120, 97, 109, 112, 108, 101, 115, 47, 84, 101, 115, 116, 83, 84, 50, 51, 47, 0, 12, 116, 101, 115, 116, 102, 105, 108, 101, 46, 116, 120, 116, 0, 0, 1, 184, 0], dtype=numpy.uint8)        
        payloads = [expected_response_0]
        
        testData.counter_offset = 1
      
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Find files TC[04,07] => TM[04,08]
        # ------------------------------------------------------------   

        testData = self.testData[46]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 5, 0x74, 0x65, 0x73, 0x74, 0x2a], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
      
        expected_response_0 = numpy.array([0, 36, 46, 46, 47, 46, 46, 47, 46, 46, 47, 101, 120, 97, 109, 112, 108, 101, 115, 47, 84, 101, 115, 116, 83, 84, 50, 51, 47, 110, 101, 119, 95, 116, 101, 115, 116, 47, 0, 5, 116, 101, 115, 116, 42, 0, 2, 0, 10, 116, 101, 115, 116, 35, 50, 46, 100, 111, 99, 0, 10, 116, 101, 115, 116, 35, 49, 46, 100, 111, 99], dtype=numpy.uint8)        
        payloads = [expected_response_0]
        
        testData.counter_offset = 2
        
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))


        # ------------------------------------------------------------
        # Lock a file TC[04,05]
        # ------------------------------------------------------------   

        testData = self.testData[47]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x31, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )

        # ------------------------------------------------------------
        # Unlock a file TC[04,06]
        # ------------------------------------------------------------   

        testData = self.testData[48]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x32, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )

        # ------------------------------------------------------------
        # Delete a file TC[04,02]
        # ------------------------------------------------------------   

        testData = self.testData[49]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x32, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )        

        # ------------------------------------------------------------
        # Copy a file TC[04,14]
        # ------------------------------------------------------------   

        testData = self.testData[50]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 1, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x31, 0x2e, 0x64, 0x6f, 0x63, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x32, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )

        # ------------------------------------------------------------
        # Unlock a file TC[04,06]
        # ------------------------------------------------------------   

        testData = self.testData[51]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x31, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

        # ------------------------------------------------------------
        # Move a file TC[04,15]
        # ------------------------------------------------------------   

        testData = self.testData[52]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 2, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x31, 0x2e, 0x64, 0x6f, 0x63, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x33, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )

        # ------------------------------------------------------------
        # Rename a directory TC[04,11]
        # ------------------------------------------------------------   

        testData = self.testData[53]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74, 0, 8, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )
        
        # ------------------------------------------------------------
        # Delete a directory TC[04,10]
        # ------------------------------------------------------------   

        testData = self.testData[54]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(2), packet, testData.error) )        

        # ------------------------------------------------------------
        # Unlock a file TC[04,06]
        # ------------------------------------------------------------   

        testData = self.testData[51]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x32, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

        # ------------------------------------------------------------
        # Delete a file TC[04,06]
        # ------------------------------------------------------------   

        testData = self.testData[55]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x32, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

        # ------------------------------------------------------------
        # Delete a file TC[04,06]
        # ------------------------------------------------------------   

        testData = self.testData[55]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'out'), (d1, 'store'))
        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 36, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74, 0x2f, 0, 10, 0x74, 0x65, 0x73, 0x74, 0x23, 0x33, 0x2e, 0x64, 0x6f, 0x63], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

        # ------------------------------------------------------------
        # Delete a directory TC[04,10]
        # ------------------------------------------------------------   

        testData = self.testData[56]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedSuccessCompletionExecutionVerification(d2.get_message(0), packet, testData.error) )  

        # ------------------------------------------------------------
        # Delete a directory TC[04,10]
        # ------------------------------------------------------------   

        testData = self.testData[57]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 35, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74, 0, 13, 0x6e, 0x65, 0x73, 0x74, 0x5f, 0x6e, 0x65, 0x77, 0x5f, 0x74, 0x65, 0x73, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )


        # ------------------------------------------------------------
        # Delete a directory TC[04,10]
        # ------------------------------------------------------------   

        testData = self.testData[58]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((fileManagementService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0, 27, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0x54, 0x65, 0x73, 0x74, 0x53, 0x54, 0x32, 0x33, 0x2f, 0, 8, 0x6f, 0x6c, 0x64, 0x5f, 0x74, 0x65, 0x73, 0x74], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        fileManagementService.to_basic_block()._post(pmt.intern("in"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        
def checkResults(numd1, d1, payloads, numd2, d2, num_progress, testData, packet):

  
    if d1.num_messages() != numd1:
        return False

    if d2.num_messages() != numd2:
        return False

    for i in range (0, testData.counter):
        h = i        
     
        if len(payloads) > 0:
            for j in range (0, len(payloads)):
 
               response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(j))), dtype=numpy.uint8)
     
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

def checkFailedSuccessCompletionExecutionVerification(message, sentMessage, error):
    responseVerification =  numpy.array(pmt.u8vector_elements(pmt.cdr(message)), dtype=numpy.uint8)

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
        
    meta = pmt.car(message)

    report_req = pmt.to_long(pmt.dict_ref(meta, pmt.intern("req"), pmt.PMT_NIL))
    report_error = pmt.to_long(pmt.dict_ref(meta, pmt.intern("error_type"), pmt.PMT_NIL))

    if report_req != 8:
        return False
    if report_error != error:
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
    gr_unittest.run(qa_FileManagementService, "qa_FileManagementService.xml" )
