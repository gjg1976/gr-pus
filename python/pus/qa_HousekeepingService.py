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
        
class qa_HousekeepingService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x11, 1, 0x19, 15, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 15, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 15, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1d, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 28, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 9, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 28, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 9, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x03, 0x01, 0x00, 0x1b, 1, 0x19, 0, 26, 0, True, 0, 0)) #11
        
        self.testData.append(test_data(0x03, 0x03, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x03, 0x03, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #13
        self.testData.append(test_data(0x03, 0x03, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #14
        self.testData.append(test_data(0x03, 0x03, 0x00, 0x1b, 1, 0x19, 0, 25, 0, True, 0, 0)) #15
        self.testData.append(test_data(0x03, 0x03, 0x00, 0x1b, 1, 0x19, 0, 27, 0, True, 0, 0)) #16
        
        self.testData.append(test_data(0x03, 0x09, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #17  
        self.testData.append(test_data(0x03, 0x09, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #18
        self.testData.append(test_data(0x03, 0x09, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #19
        self.testData.append(test_data(0x03, 0x09, 0x00, 0x1b, 1, 0x19, 0, 25, 0, True, 0, 0)) #20
        self.testData.append(test_data(0x03, 0x09, 0x0a, -1, 1, 0x19, 15, 25, 0, True, 0, 0)) #21
        
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #22
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #23
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #24        
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1d, 1, 0x19, 0, 1, 0, True, 0, 0)) #25
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #26
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #27
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #28
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 28, 0, True, 0, 0)) #29
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 9, 0, True, 0, 0)) #30
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 28, 0, True, 0, 0)) #31
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 9, 0, True, 0, 0)) #32
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 25, 0, True, 0, 0)) #33
        self.testData.append(test_data(0x03, 0x1d, 0x00, 0x1b, 1, 0x19, 0, 29, 0, True, 0, 0)) #34
        
        self.testData.append(test_data(0x03, 0x05, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #35
        self.testData.append(test_data(0x03, 0x05, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #36
        self.testData.append(test_data(0x03, 0x05, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #37
        self.testData.append(test_data(0x03, 0x05, 0x00, 0x1b, 1, 0x19, 0, 25, 0, True, 0, 0)) #38
        
        self.testData.append(test_data(0x03, 0x06, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #39
        self.testData.append(test_data(0x03, 0x06, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #40
        self.testData.append(test_data(0x03, 0x06, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #41
        self.testData.append(test_data(0x03, 0x06, 0x00, 0x1b, 1, 0x19, 0, 25, 0, True, 0, 0)) #42
        
        self.testData.append(test_data(0x03, 0x1f, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #43
        self.testData.append(test_data(0x03, 0x1f, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #44
        self.testData.append(test_data(0x03, 0x1f, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #45        
        self.testData.append(test_data(0x03, 0x1f, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #46
        self.testData.append(test_data(0x03, 0x1f, 0x00, 0x1b, 1, 0x19, 0, 25, 0, True, 0, 0)) #47

        self.testData.append(test_data(0x03, 0x01, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #48   
        self.testData.append(test_data(0x03, 0x09, 0x0a, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #49
        self.testData.append(test_data(0x03, 0x1d, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #50        
        self.testData.append(test_data(0x03, 0x09, 0x0a, -1, 1, 0x19, 15, 0, 0, True, 1, 1)) #51        
        self.testData.append(test_data(0x03, 0x05, 0x00, 0x1b, 1, 0x19, 15, 0, 0, True, 0, 0)) #52
        self.testData.append(test_data(0x03, 0x09, 0x0a, -1, 1, 0x19, 15, 0, 0, True, 2, 2)) #53
        self.testData.append(test_data(0x03, 0x06, 0x00, 0x1b, 1, 0x19, 15, 0, 0, True, 0, 0)) #54                                
        self.testData.append(test_data(0x03, 0x09, 0x0a, -1, 1, 0x19, 15, 0, 0, True, 3, 3)) #55
        self.testData.append(test_data(0x03, 0x1f, 0x00, 0x1b, 1, 0x19, 15, 0, 0, True, 0, 0)) #56        
        self.testData.append(test_data(0x03, 0x09, 0x0a, -1, 1, 0x19, 15, 0, 0, True, 4, 4)) #57
        self.testData.append(test_data(0x03, 0x03, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #58       
        self.testData.append(test_data(0x03, 0x09, 0x0a, -1, 1, 0x19, 0, 25, 0, True, 0, 0)) #59

        self.testData.append(test_data(0x03, 0x21, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #60
        self.testData.append(test_data(0x03, 0x21, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #61
        self.testData.append(test_data(0x03, 0x21, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #62
        self.testData.append(test_data(0x03, 0x21, 0x23, 0x0d, 1, 0x19, 0, 25, 0, True, 0, 0)) #63
        self.testData.append(test_data(0x03, 0x21, 0x23, 0x15, 1, 0x19, 15, 25, 0, True, 0, 0)) #64

        self.testData.append(test_data(0x03, 0x1b, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #65
        self.testData.append(test_data(0x03, 0x1b, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #66
        self.testData.append(test_data(0x03, 0x1b, 0x00, 0x1b, 1, 0x19, 0, 1, 0, True, 0, 0)) #67
        self.testData.append(test_data(0x03, 0x1b, 0x00, 0x0d, 1, 0x19, 0, 25, 0, True, 0, 0)) #68
        self.testData.append(test_data(0x03, 0x1b, 0x19, -1, 1, 0x19, 15, 25, 0, True, 0, 0)) #69

        self.testData.append(test_data(0x03, 0x05, 0x19, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #70
                                                                                                                                                              
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.HousekeepingService("")

    def test_001_ST03_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x04, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x03, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))       

    def test_002_ST03_01_invalid_numParams_field_shorter(self):
        testData = self.testData[0]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 0x0a, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST03_01_invalid_paramsID_fields_shorter(self):
        testData = self.testData[1]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST03_01_invalid_numSuperStruct_field_shorter(self):
        testData = self.testData[2]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST03_01_invalid_numSuperStruct_field_longer(self):
        testData = self.testData[3]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))            

    def test_006_ST03_01_invalid_superStructs_fields_shorter(self):
        testData = self.testData[4]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))   
         
    def test_007_ST03_01_invalid_superStructParamIDs_fields_shorter(self):
        testData = self.testData[5]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_008_ST03_01_invalid_superStructParamIDs_fields_longer(self):
        testData = self.testData[6]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                                    

    def test_009_ST03_01_invalid_superStructParamIDs_fields_ParamIDs_duplicated(self):
        testData = self.testData[7]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_010_ST03_01_invalid_superStructParamIDs_fields_ParamIDs_non_existing(self):
        testData = self.testData[8]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x33, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_011_ST03_01_invalid_ParamIDs_duplicated(self):
        testData = self.testData[9]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x04, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_012_ST03_01_invalid_ParamID_non_existing(self):
        testData = self.testData[10]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x33, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_013_ST03_01_invalid_create_struct_already_exist(self):
        testData = self.testData[11]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x04, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST03_03_invalid_numStructs_field_shorter(self):
        testData = self.testData[12]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_015_ST03_03_invalid_structID_fields_shorter(self):
        testData = self.testData[13]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_016_ST03_03_invalid_structID_fields_longer(self):
        testData = self.testData[14]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_017_ST03_03_invalid_structID_non_exists(self):
        testData = self.testData[15]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_018_ST03_03_invalid_structID_struct_enabled(self):
        testData = self.testData[16]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_019_ST03_09_invalid_numStructs_field_shorter(self):
        testData = self.testData[17]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_020_ST03_09_invalid_structID_fields_shorter(self):
        testData = self.testData[18]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_021_ST03_09_invalid_structID_fields_longer(self):
        testData = self.testData[19]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_022_ST03_09_invalid_structID_non_exists(self):
        testData = self.testData[20]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_023_ST03_09and10_report_valid_structIDs(self):
        testData = self.testData[21]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x04, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(1))), dtype=numpy.uint8)
        expected_response_0 = numpy.array([4,0,0,50,0,6,0,5,0,1,0,16,0,34,0,11,0,31,0,2,4,3,0,17,0,9,0,3,5,1,0,15], dtype=numpy.uint8)
        expected_response_1 = numpy.array([7,1,0,80,0,3,0,65,0,49,0,98,0,0], dtype=numpy.uint8)

        payloads = [expected_response_0,expected_response_1]
        
        self.assertTrue(checkResults(2, d1, payloads, 3, d2, 0, testData, packet))

    def test_024_ST03_29_invalid_numParams_field_shorter(self):
        testData = self.testData[22]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_025_ST03_29_invalid_paramsID_fields_shorter(self):
        testData = self.testData[23]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_026_ST03_29_invalid_numSuperStruct_field_shorter(self):
        testData = self.testData[24]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_027_ST03_29_invalid_numSuperStruct_field_longer(self):
        testData = self.testData[25]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))            

    def test_028_ST03_29_invalid_superStructs_fields_shorter(self):
        testData = self.testData[26]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01,  0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))   
         
    def test_029_ST03_29_invalid_superStructParamIDs_fields_shorter(self):
        testData = self.testData[27]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01,  0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_030_ST03_29_invalid_superStructParamIDs_fields_longer(self):
        testData = self.testData[28]
                
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01, 0x00, 0x05, 0x00, 0x01, 0x00, 0x04, 0x00, 0x05, 0x00, 0x16, 0x00, 0x7f, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x01, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                                    

    def test_031_ST03_29_invalid_superStructParamIDs_fields_ParamIDs_duplicated(self):
        testData = self.testData[29]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01, 0x00, 0x02, 0x00, 0x22, 0x00, 0x31, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x41, 0x00, 0x41], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_032_ST03_29_invalid_superStructParamIDs_fields_ParamIDs_non_existing(self):
        testData = self.testData[30]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01, 0x00, 0x02, 0x00, 0x22, 0x00, 0x31, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x43, 0x00, 0x41], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_033_ST03_29_invalid_ParamIDs_duplicated(self):
        testData = self.testData[31]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01, 0x00, 0x02, 0x00, 0x31, 0x00, 0x31, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x22, 0x00, 0x41], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_034_ST03_29_invalid_ParamID_non_existing(self):
        testData = self.testData[32]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x01, 0x00, 0x02, 0x00, 0x22, 0x00, 0x43, 0x00, 0x01, 0x0a, 0x02, 0x00, 0x22, 0x00, 0x41], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
        
    def test_035_ST03_29_invalid_append_struct_non_existing(self):
        testData = self.testData[33]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x02, 0x00, 0x02, 0x00, 0x22, 0x00, 0x31, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
    
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_036_ST03_29_invalid_append_struct_is_enabled(self):
        testData = self.testData[34]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x01, 0x30, 0x07, 0x00, 0x02, 0x00, 0x22, 0x00, 0x31, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_037_ST03_05_invalid_numStructs_field_shorter(self):
        testData = self.testData[35]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_038_ST03_05_invalid_structID_fields_shorter(self):
        testData = self.testData[36]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_039_ST03_05_invalid_structID_fields_longer(self):
        testData = self.testData[37]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_040_ST03_05_invalid_structID_non_exists(self):
        testData = self.testData[38]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_041_ST03_06_invalid_numStructs_field_shorter(self):
        testData = self.testData[39]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x06, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_042_ST03_06_invalid_structID_fields_shorter(self):
        testData = self.testData[40]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x06, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_043_ST03_06_invalid_structID_fields_longer(self):
        testData = self.testData[41]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_044_ST03_06_invalid_structID_non_exists(self):
        testData = self.testData[42]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_045_ST03_31_invalid_numStructs_field_shorter(self):
        testData = self.testData[43]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1f, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_046_ST03_31_invalid_structID_fields_shorter(self):
        testData = self.testData[44]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1f, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_047_ST03_31_invalid_interval_fields_shorter(self):
        testData = self.testData[45]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x00, 0x0a, 0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_048_ST03_31_invalid_interval_fields_longer(self):
        testData = self.testData[46]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x00, 0x0a, 0x04, 0x00, 0x10, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  
        
    def test_049_ST03_31_invalid_structID_non_exists(self):
        testData = self.testData[47]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x00, 0x0a, 0x02, 0x00, 0x10], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))
             
    def test_050_ST03_01and03and29and05and06and31and9and10_create_report_append_report_enable_report_disble_report_modify_report_delete_report_valid_structID(self):
        # ------------------------------------------------------------
        # Create TC[03,01]
        # ------------------------------------------------------------
        testData = self.testData[48]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02,0,50,0,6,0,5,0,1,0,16,0,34,0,11,0,31,0,2,4,3,0,17,0,9,0,3,5,1,0,15], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        payloads = []
                
        self.assertTrue(checkResults(0, d1, payloads, 3, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Report creation TC[03,09] -> TM[03,10]
        # ------------------------------------------------------------           
        testData = self.testData[49]

        d3 = blocks.message_debug()
        d4 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d3, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d4, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        expected_response_0 = numpy.array([2,0,0,50,0,6,0,5,0,1,0,16,0,34,0,11,0,31,0,2,4,3,0,17,0,9,0,3,5,1,0,15], dtype=numpy.uint8)

        payloads = [expected_response_0]
    
        self.assertTrue(checkResults(1, d3, payloads, 3, d4, 0, testData, packet))
        # ------------------------------------------------------------
        # Append TC[03,29]        
        # ------------------------------------------------------------
        testData = self.testData[50]

        d5 = blocks.message_debug()
        d6 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d5, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d6, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0, 1, 0, 127, 0, 1, 10, 1, 0, 98], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        payloads = []
                                                    
        self.assertTrue(checkResults(0, d5, payloads, 3, d6, 0, testData, packet))
        # ------------------------------------------------------------
        # Report append TC[03,09] -> TM[03,10]
        # ------------------------------------------------------------   
        testData = self.testData[51]

        d7 = blocks.message_debug()
        d8 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d7, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d8, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        expected_response_0 = numpy.array([2,0,0,50,0,7,0,5,0,1,0,16,0,34,0,11,0,31,0,127,0,3,4,3,0,17,0,9,0,3,5,1,0,15,10,1,0,98], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d7, payloads, 3, d8, 0, testData, packet))

        # ------------------------------------------------------------
        # Enable TC[03,05]        
        # ------------------------------------------------------------
        testData = self.testData[52]

        d9 = blocks.message_debug()
        d10 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d9, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d10, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        payloads = []
                
        self.assertTrue(checkResults(0, d9, payloads, 3, d10, 0, testData, packet))        
        # ------------------------------------------------------------
        # Report enable TC[03,09] -> TM[03,10]
        # ------------------------------------------------------------   
        testData = self.testData[53]

        d11 = blocks.message_debug()
        d12 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d11, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d12, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([2,1,0,50,0,7,0,5,0,1,0,16,0,34,0,11,0,31,0,127,0,3,4,3,0,17,0,9,0,3,5,1,0,15,10,1,0,98], dtype=numpy.uint8)

        payloads = [expected_response_0]
                
        self.assertTrue(checkResults(1, d11, payloads, 3, d12, 0, testData, packet))
        # ------------------------------------------------------------
        # Disable TC[03,06]        
        # ------------------------------------------------------------
        testData = self.testData[54]


        d13 = blocks.message_debug()
        d14 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d13, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d14, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        payloads = []
                
        self.assertTrue(checkResults(0, d13, payloads, 3, d14, 0, testData, packet))     
        # ------------------------------------------------------------
        # Report disable TC[03,09] -> TM[03,10]
        # ------------------------------------------------------------   
        testData = self.testData[55]

        d15 = blocks.message_debug()
        d16 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d15, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d16, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        expected_response_0 = numpy.array([2,0,0,50,0,7,0,5,0,1,0,16,0,34,0,11,0,31,0,127,0,3,4,3,0,17,0,9,0,3,5,1,0,15,10,1,0,98], dtype=numpy.uint8)

        payloads = [expected_response_0]
                
        self.assertTrue(checkResults(1, d15, payloads, 3, d16, 0, testData, packet))
        # ------------------------------------------------------------
        # Update interval TC[03,05]        
        # ------------------------------------------------------------
        testData = self.testData[56]

        d17 = blocks.message_debug()
        d18 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d17, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d18, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02, 0xff, 0xff], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        payloads = []
                
        self.assertTrue(checkResults(0, d17, payloads, 3, d18, 0, testData, packet))  
        # ------------------------------------------------------------
        # Report interval TC[03,09] -> TM[03,10]
        # ------------------------------------------------------------   
        testData = self.testData[57]       

        d19 = blocks.message_debug()
        d20 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d19, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d20, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        expected_response_0 = numpy.array([2,0,255,255,0,7,0,5,0,1,0,16,0,34,0,11,0,31,0,127,0,3,4,3,0,17,0,9,0,3,5,1,0,15,10,1,0,98], dtype=numpy.uint8)

        payloads = [expected_response_0]
                
        self.assertTrue(checkResults(1, d19, payloads, 3, d20, 0, testData, packet))
        # ------------------------------------------------------------
        # Delete TC[03,03]        
        # ------------------------------------------------------------                
        testData = self.testData[58]

        d21 = blocks.message_debug()
        d22 = blocks.message_debug()

        self.tb.msg_connect((housekeepingService, 'out'), (d21, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d22, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        payloads = []
                
        self.assertTrue(checkResults(0, d21, payloads, 3, d22, 0, testData, packet))

        # ------------------------------------------------------------
        # Report delete TC[03,09] -> TM[03,10]
        # ------------------------------------------------------------  
        testData = self.testData[59]
                
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d23 = blocks.message_debug()
        d24 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d23, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d24, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d23.num_messages() == 0)
        self.assertTrue(d24.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d24.get_message(0), packet, testData.error))
        
    def test_051_ST03_33_invalid_numStructs_field_shorter(self):
        testData = self.testData[60]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_052_ST03_33_invalid_structID_fields_shorter(self):
        testData = self.testData[61]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_053_ST03_33_invalid_structID_fields_longer(self):
        testData = self.testData[62]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_054_ST03_33_invalid_structID_non_exists(self):
        testData = self.testData[63]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_055_ST03_33and35_valid_structIDs_generation(self):
        testData = self.testData[64]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x04, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
       
        expected_response_0 = numpy.array([2, 4, 0, 0, 50, 7, 1, 0, 80], dtype=numpy.uint8)

        payloads = [expected_response_0]

        testData.ackFlags = 0x0f
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))
        
    def test_056_ST03_27_invalid_numStructs_field_shorter(self):
        testData = self.testData[65]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_057_ST03_27_invalid_structID_fields_shorter(self):
        testData = self.testData[66]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_058_ST03_27_invalid_structID_fields_longer(self):
        testData = self.testData[67]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x01, 0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_059_ST03_27_invalid_structID_non_exists(self):
        testData = self.testData[68]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        expected_response_0 = numpy.array([0], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_060_ST03_27and25_report_valid_structs_params(self):
        testData = self.testData[69]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1d, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x04, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        expected_response_0 = numpy.array([4,64,70,153,153,153,153,153,154,8,222,153,242,61,255, 178,1,65,222,153,242,61,66,2,0,0,243,222,153,242,61,66,2,0,0,243,222,153,242,61,66,2,0,0, 243,222,153,242,61,66,2,0,0,243,0,0,0,0,0], dtype=numpy.uint8)
        expected_response_1 = numpy.array([7,0,78,0,154,68,155,112,0], dtype=numpy.uint8)        
        payloads = [expected_response_0, expected_response_1]

        self.assertTrue(checkResults(2, d1, payloads, 3, d2, 0, testData, packet))

    def test_061_ST03_25_automatic_report_valid_structs_params(self):
        testData = self.testData[70]

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        
        setParameter_9 = pus.setParameter_f(9)
        setParameter_17 = pus.setParameter_i(17)


        self.tb.msg_connect((housekeepingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((housekeepingService, 'ver'), (d2, 'store'))
        
        packet_enable = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x04], dtype=numpy.uint8)
        packet_enable = appendCRC(packet_enable)
        in_pdu_enable = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_enable.size, packet_enable))
        
        packet_disable = numpy.array([0x18, 0x03, 0x05, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx+1, 0x00, 0x00, 0x01, 0x07], dtype=numpy.uint8)
        packet_disable = appendCRC(packet_disable)
        in_pdu_disable = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_disable.size, packet_disable))
                
        self.tb.start()
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu_disable) 
        housekeepingService.to_basic_block()._post(pmt.intern("in"), in_pdu_enable) 
        time.sleep(1.1)
        setParameter_9.setParameterValue(535.75)
        setParameter_17.setParameterValue(5432)                
        time.sleep(1.1)
        setParameter_9.setParameterValue(2054.1)
        setParameter_17.setParameterValue(100)    
        time.sleep(1.1)  
        setParameter_9.setParameterValue(876.0)
        setParameter_17.setParameterValue(65421)   
        time.sleep(11)       
        self.tb.stop()
        self.tb.wait()
        
        expected_response_0 = numpy.array([4, 64, 70, 153, 153, 153, 153, 153, 154, 8, 222, 153, 242, 61, 255, 178, 1, 65, 0, 0, 21, 56, 68, 5, 240, 0, 243, 0, 0, 0, 100, 69, 0, 97, 154, 243, 0, 0, 255, 141, 68, 91, 0, 0, 243, 0, 0, 255, 141, 68, 91, 0, 0, 243, 0, 0, 0, 0, 0], dtype=numpy.uint8)

        expected_response_1 = numpy.array([4, 64, 70, 153, 153, 153, 153, 153, 154, 8, 222, 153, 242, 61, 255, 178, 1, 65, 0, 0, 255, 141, 68, 91, 0, 0, 243, 0, 0, 255, 141, 68, 91, 0, 0, 243, 0, 0, 255, 141, 68, 91, 0, 0, 243, 0, 0, 255, 141, 68, 91, 0, 0, 243, 0, 0, 0, 0, 0], dtype=numpy.uint8)      
        payloads = [expected_response_0, expected_response_1]

        self.assertTrue(checkResults(2, d1, payloads, 0, d2, 0, testData, packet_disable))
                                                                                                        
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
    gr_unittest.run(qa_HousekeepingService, "qa_HousekeepingService.xml" )
