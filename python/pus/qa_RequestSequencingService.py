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

class qa_RequestSequencingService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x15, 0x01, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x15, 0x02, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x15, 0x02, 0x00, 0x11, 1, 0x19, 0, 79, 0, True, 0, 0)) #2        
        self.testData.append(test_data(0x15, 0x03, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #3   
        self.testData.append(test_data(0x15, 0x03, 0x00, 0x11, 1, 0x19, 0, 77, 0, True, 0, 0)) #4           
        self.testData.append(test_data(0x15, 0x04, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #5   
        self.testData.append(test_data(0x15, 0x04, 0x00, 0x11, 1, 0x19, 0, 77, 0, True, 0, 0)) #6  
        self.testData.append(test_data(0x15, 0x05, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #7   
        self.testData.append(test_data(0x15, 0x05, 0x00, 0x11, 1, 0x19, 0, 77, 0, True, 0, 0)) #8  
        self.testData.append(test_data(0x15, 0x06, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x15, 0x08, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x15, 0x08, 0x00, 0x11, 1, 0x19, 0, 79, 0, True, 0, 0)) #11 
        self.testData.append(test_data(0x15, 0x09, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #12  
        self.testData.append(test_data(0x15, 0x09, 0x00, 0x11, 1, 0x19, 0, 77, 0, True, 0, 0)) #13  
        self.testData.append(test_data(0x15, 0x0b, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #14  
        self.testData.append(test_data(0x15, 0x0b, 0x00, 0x11, 1, 0x19, 0, 77, 0, True, 0, 0)) #15  
        self.testData.append(test_data(0x15, 0x0d, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #16  
        self.testData.append(test_data(0x15, 0x01, 0x00, 0x11, 1, 0x19, 0, 74, 0, True, 0, 0)) #17
        self.testData.append(test_data(0x15, 0x01, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #18
        self.testData.append(test_data(0x15, 0x02, 0x00, 0x11, 1, 0x19, 0, 74, 0, True, 0, 0)) #19
        self.testData.append(test_data(0x15, 0x02, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #20
        self.testData.append(test_data(0x15, 0x06, 0x07, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #21
        self.testData.append(test_data(0x15, 0x0b, 0x0c, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #22
        self.testData.append(test_data(0x15, 0x0b, 0x0c, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #23     
        self.testData.append(test_data(0x15, 0x03, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #24  
        self.testData.append(test_data(0x15, 0x06, 0x07, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #25
        self.testData.append(test_data(0x15, 0x08, 0x00, 0x11, 1, 0x19, 0, 74, 0, True, 0, 0)) #26
        self.testData.append(test_data(0x15, 0x08, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #27        
        self.testData.append(test_data(0x15, 0x05, 0x00, 0x11, 1, 0x19, 0, 81, 0, True, 0, 0)) #28   
        self.testData.append(test_data(0x15, 0x05, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #29 
        self.testData.append(test_data(0x15, 0x04, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #30  
        self.testData.append(test_data(0x15, 0x04, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #31          
        self.testData.append(test_data(0x15, 0x0d, 0x0e, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #32  
        self.testData.append(test_data(0x15, 0x09, 0x0a, 0x1d, 1, 0x19, 15, 0, 0, True, 0, 0)) #33
        self.testData.append(test_data(0x15, 0x08, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #34
        self.testData.append(test_data(0x15, 0x05, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #35 
                                               
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.RequestSequencingService("")

    def test_001_ST21_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x03, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x15, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST21_01_invalid_seqID_fields_shorter(self):
        testData = self.testData[0]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST21_01_invalid_numActivities_fields_shorter(self):
        testData = self.testData[0]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST21_01_invalid_activities_fields_shorter(self):
        testData = self.testData[0]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST21_01_invalid_activities_delay_shorter(self):
        testData = self.testData[0]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x18, 0x19, 0x00, 0x03, 0x00, 0x0b, 0x27, 0x13, 0x04, 0x00, 0x00, 0x01, 0x00, 0x14, 0x00, 0x04, 0xff, 0xff, 0x00, 0x00, 0x00, 0x0a, 0x18, 0x19, 0x00, 0x06, 0x00, 0x06, 0x27, 0x0b, 0x03, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_006_ST21_01_invalid_activities_delay_longer(self):
        testData = self.testData[0]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x18, 0x19, 0x00, 0x03, 0x00, 0x0b, 0x27, 0x13, 0x04, 0x00, 0x00, 0x01, 0x00, 0x14, 0x00, 0x04, 0xff, 0xff, 0x00, 0x00, 0x00, 0x0a, 0x18, 0x19, 0x00, 0x06, 0x00, 0x06, 0x27, 0x0b, 0x03, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_ST21_02_invalid_seqID_fields_shorter(self):
        testData = self.testData[1]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_ST21_02_invalid_filename_non_exists(self):
        testData = self.testData[2]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 16, 0x69, 0x6e, 0x69, 0x74, 0x5f, 0x72, 0x65, 0x71, 0x73, 0x65, 0x71, 0x32, 0x2e, 0x6a, 0x73, 0x6f], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_009_ST21_03_invalid_seqID_fields_shorter(self):
        testData = self.testData[3]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_010_ST21_03_invalid_seqID_non_exists(self):
        testData = self.testData[4]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_011_ST21_04_invalid_seqID_fields_shorter(self):
        testData = self.testData[5]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_012_ST21_04_invalid_seqID_non_exists(self):
        testData = self.testData[6]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_013_ST21_05_invalid_seqID_fields_shorter(self):
        testData = self.testData[7]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST21_05_invalid_seqID_non_exists(self):
        testData = self.testData[8]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_015_ST21_06_invalid_params_fields_longer(self):
        testData = self.testData[9]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_016_ST21_08_invalid_seqID_fields_shorter(self):
        testData = self.testData[10]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_017_ST21_08_invalid_filename_non_exists(self):
        testData = self.testData[11]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 16, 0x69, 0x6e, 0x69, 0x74, 0x5f, 0x72, 0x65, 0x71, 0x73, 0x65, 0x71, 0x32, 0x2e, 0x6a, 0x73, 0x6f], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_018_ST21_09_invalid_seqID_fields_shorter(self):
        testData = self.testData[12]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_019_ST21_09_invalid_seqID_non_exists(self):
        testData = self.testData[13]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_020_ST21_11_invalid_seqID_fields_shorter(self):
        testData = self.testData[14]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_021_ST21_11_invalid_seqID_non_exists(self):
        testData = self.testData[15]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_022_ST21_13_invalid_params_fields_longer(self):
        testData = self.testData[16]
                
        requestSequencingService = pus.RequestSequencingService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_023_ST21_01to13_load_unload_execute_abort_report_checksum(self):
        # ------------------------------------------------------------
        # Direct load a sequence TC[21,1]                
        # ------------------------------------------------------------ 
        testData = self.testData[17]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1980, 1, 6)                       
        requestSequencingService = pus.RequestSequencingService("../../../examples/init_reqseq.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x18, 0x19, 0x00, 0x03, 0x00, 0x0b, 0x27, 0x13, 0x04, 0x00, 0x00, 0x01, 0x00, 0x14, 0x00, 0x04, 0xff, 0xff, 0x00, 0x00, 0x00, 0x0a, 0x18, 0x19, 0x00, 0x06, 0x00, 0x06, 0x27, 0x0b, 0x03, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

        # ------------------------------------------------------------
        # Direct load a sequence TC[21,1]                
        # ------------------------------------------------------------ 

        testData = self.testData[18]
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x18, 0x19, 0x00, 0x03, 0x00, 0x0b, 0x27, 0x13, 0x04, 0x00, 0x00, 0x01, 0x00, 0x14, 0x00, 0x04, 0xff, 0xff, 0x00, 0x00, 0x00, 0x0a, 0x18, 0x19, 0x00, 0x06, 0x00, 0x06, 0x27, 0x0b, 0x03, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))        

        # ------------------------------------------------------------
        # Load a sequence by Reference TC[21,2]                
        # ------------------------------------------------------------ 
        testData = self.testData[19]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 17, 0x69, 0x6e, 0x69, 0x74, 0x5f, 0x72, 0x65, 0x71, 0x73, 0x65, 0x71, 0x32, 0x2e, 0x6a, 0x73, 0x6f, 0x6e], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

        # ------------------------------------------------------------
        # Load a sequence by Reference TC[21,2]                
        # ------------------------------------------------------------ 
        testData = self.testData[20]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 00, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 17, 0x69, 0x6e, 0x69, 0x74, 0x5f, 0x72, 0x65, 0x71, 0x73, 0x65, 0x71, 0x32, 0x2e, 0x6a, 0x73, 0x6f, 0x6e], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Report status of each sequence TC[21,6] => TM[21,7]                
        # ------------------------------------------------------------ 

        testData = self.testData[21]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
       
        expected_response_0 = numpy.array([0, 5, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 53, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)      
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))
                        
        # ------------------------------------------------------------
        # Report Content of a sequence TC[21,11] => TM[21,12]                
        # ------------------------------------------------------------ 
        testData = self.testData[22]
        testData_noack = self.testData[23]               
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet_1 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)

        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))

        packet_2 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_noack.ackFlags, testData_noack.messageType, testData_noack.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x32, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)

        packet_2 = appendCRC(packet_2)
        in_pdu_2 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_2.size, packet_2))
        
        packet_3 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_noack.ackFlags, testData_noack.messageType, testData_noack.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)

        packet_3 = appendCRC(packet_3)
        in_pdu_3 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_3.size, packet_3))

        packet_4 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_noack.ackFlags, testData_noack.messageType, testData_noack.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)

        packet_4 = appendCRC(packet_4)
        in_pdu_4 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_4.size, packet_4))

        packet_5 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_noack.ackFlags, testData_noack.messageType, testData_noack.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)

        packet_5 = appendCRC(packet_5)
        in_pdu_5 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_5.size, packet_5))
                                        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        time.sleep(.5)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_2) 
        time.sleep(.5)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_3) 
        time.sleep(.5)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_4) 
        time.sleep(.5)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_5) 
        time.sleep(.5)                        
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d3.num_messages() == 0)

        expected_response_0 = numpy.array([84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 0, 6, 24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 4, 0, 0, 0, 2, 24, 23, 192, 0, 0, 7, 32, 3, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 23, 192, 0, 0, 7, 32, 3, 31, 0, 0, 2, 1, 4, 0, 0, 0, 0, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 4, 0, 0, 0, 5, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 4, 0, 0, 0, 10, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 4, 0, 0, 0, 0], dtype=numpy.uint8)   
        expected_response_1 = numpy.array([84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 6, 24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 5, 0, 0, 0, 12, 24, 23, 192, 0, 0, 7, 32, 3, 25, 0, 0, 0, 0, 1, 0, 0, 0, 10, 24, 23, 192, 0, 0, 7, 32, 3, 31, 0, 0, 2, 1, 5, 0, 0, 0, 10, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 5, 0, 0, 0, 8, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 5, 0, 0, 0, 11, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 5, 0, 0, 0, 14], dtype=numpy.uint8)   
        expected_response_2 = numpy.array([84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 0, 6, 24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 6, 0, 0, 0, 0, 24, 23, 192, 0, 0, 7, 32, 3, 25, 0, 0, 0, 0, 2, 0, 0, 0, 1, 24, 23, 192, 0, 0, 7, 32, 3, 31, 0, 0, 2, 1, 6, 0, 0, 0, 1, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 6, 0, 0, 0, 1, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 6, 0, 0, 0, 1, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 6, 0, 0, 0, 1], dtype=numpy.uint8)   
        expected_response_3 = numpy.array([84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 2, 24, 25, 0, 3, 0, 11, 39, 19, 4, 0, 0, 1, 0, 20, 0, 4, 255, 255, 0, 0, 0, 10, 24, 25, 0, 6, 0, 6, 39, 11, 3, 0, 0, 255, 255, 0, 0, 0, 1], dtype=numpy.uint8)
        expected_response_4 = numpy.array([84, 101, 115, 116, 83, 101, 113, 35, 53, 0, 0, 0, 0, 0, 0, 0, 6, 24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 5, 0, 0, 0, 12, 24, 23, 192, 0, 0, 7, 32, 3, 25, 0, 0, 0, 0, 1, 0, 0, 0, 10, 24, 23, 192, 0, 0, 7, 32, 3, 31, 0, 0, 2, 1, 5, 0, 0, 0, 10, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 5, 0, 0, 0, 8, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 5, 0, 0, 0, 11, 24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 5, 0, 0, 0, 14], dtype=numpy.uint8)   

        payloads = [expected_response_0, expected_response_1, expected_response_2, expected_response_3, expected_response_4]
        testData_noack.counter_offset = 1
        self.assertTrue(checkResults(5, d1, payloads, 3, d2, 0, testData_noack, packet_1))
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet_1))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet_1))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet_1)) 

        # ------------------------------------------------------------
        # Upload a sequence TC[21,3]                
        # ------------------------------------------------------------ 

        testData = self.testData[24]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))

        # ------------------------------------------------------------
        # Report status of each sequence TC[21,6] => TM[21,7]                
        # ------------------------------------------------------------ 

        testData = self.testData[25]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
                
        expected_response_0 = numpy.array([0, 4, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)      
        payloads = [expected_response_0]
        testData.counter_offset = 6
        testData.counter_sec_offset = 1 

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Load a sequence by Reference and activated TC[21,8]                
        # ------------------------------------------------------------ 
        testData = self.testData[26]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 18, 0x69, 0x6e, 0x69, 0x74, 0x5f, 0x72, 0x65, 0x71, 0x73, 0x65, 0x71, 0x32, 0x2e, 0x6a, 0x73, 0x6f, 0x6e], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

        # ------------------------------------------------------------
        # Load a sequence by Reference and activated TC[21,8]                 
        # ------------------------------------------------------------ 
        testData = self.testData[27]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x36, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 17, 0x69, 0x6e, 0x69, 0x74, 0x5f, 0x72, 0x65, 0x71, 0x73, 0x65, 0x71, 0x32, 0x2e, 0x6a, 0x73, 0x6f, 0x6e], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(3)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() > 0)
        expected_response_d3_0 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 5], dtype=numpy.uint8)         

        response_d3 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)

        self.assertTrue(numpy.array_equal(expected_response_d3_0, response_d3))
                       
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Report status of each sequence TC[21,6] => TM[21,7]                
        # ------------------------------------------------------------ 

        testData = self.testData[25]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(0.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 1)
       
        expected_response_0 = numpy.array([0, 5, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 54, 0, 0, 0, 0, 0, 0, 1], dtype=numpy.uint8)      


        payloads = [expected_response_0]
        testData.counter_offset = 7
        testData.counter_sec_offset = 2 

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))
                        
        # ------------------------------------------------------------
        # Abort a sequence TC[21,5]                
        # ------------------------------------------------------------ 

        testData = self.testData[28]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

        # ------------------------------------------------------------
        # Abort a sequence TC[21,5]                
        # ------------------------------------------------------------ 

        testData = self.testData[29]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x36, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Report status of each sequence TC[21,6] => TM[21,7]                
        # ------------------------------------------------------------ 

        testData = self.testData[25]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
       
        expected_response_0 = numpy.array([0, 5, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 54, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)      


        payloads = [expected_response_0]
        testData.counter_offset = 8
        testData.counter_sec_offset = 3 

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))
        # ------------------------------------------------------------
        # Activate a sequence TC[21,4]               
        # ------------------------------------------------------------ 

        testData = self.testData[30]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(1.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() > 0)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Activate a sequence TC[21,4]                
        # ------------------------------------------------------------ 

        testData = self.testData[31]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(1.5)
        self.tb.stop()
        self.tb.wait()
 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() > 0)
        
          
        # ------------------------------------------------------------
        # Report status of each sequence TC[21,6] => TM[21,7]                
        # ------------------------------------------------------------ 

        testData = self.testData[25]
                
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() > 0)
       
        expected_response_0 = numpy.array([0, 5, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 1, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 1, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 54, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)      


        payloads = [expected_response_0]
        testData.counter_offset = 9
        testData.counter_sec_offset = 4

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Abort and report TC[21,13] => TM[21,14]                
        # ------------------------------------------------------------ 

        testData = self.testData[32]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)

        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() > 0)
       
        expected_response_0 = numpy.array([0, 2, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)      


        payloads = [expected_response_0]
        testData.counter_offset = 10

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))   

        # ------------------------------------------------------------
        # Checksum a sequence TC[21,9] => TM[21,10]                
        # ------------------------------------------------------------ 

        testData = self.testData[33]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
        expected_response_0 = numpy.array([84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 113, 199], dtype=numpy.uint8)      
        payloads = [expected_response_0]
        testData.counter_offset = 11
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))        

        # ------------------------------------------------------------
        # Activate two sequences TC[21,4]
        # Load a sequence by Reference and activated TC[21,8]                 
        # Report status of each sequence TC[21,6] => TM[21,7]                
        # Abort a sequence TC[21,5]                
        # ------------------------------------------------------------ 

        testData_activated = self.testData[31]
        testData_load = self.testData[34]
        testData_status = self.testData[25]
        testData_abort = self.testData[35]
                        
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()

        self.tb.msg_connect((requestSequencingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((requestSequencingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((requestSequencingService, 'release'), (d3, 'store'))
        
        packet_seq1 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_activated.ackFlags, testData_activated.messageType, testData_activated.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet_seq1 = appendCRC(packet_seq1)
        in_pdu_seq1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_seq1.size, packet_seq1))                


        packet_seq3 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_activated.ackFlags, testData_activated.messageType, testData_activated.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet_seq3 = appendCRC(packet_seq3)
        in_pdu_seq3 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_seq3.size, packet_seq3))

        packet_seq7 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_load.ackFlags, testData_load.messageType, testData_load.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x37, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 18, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x2e, 0x2e, 0x2f, 0x65, 0x78, 0x61, 0x6d, 0x70, 0x6c, 0x65, 0x73, 0x2f, 0, 17, 0x69, 0x6e, 0x69, 0x74, 0x5f, 0x72, 0x65, 0x71, 0x73, 0x65, 0x71, 0x32, 0x2e, 0x6a, 0x73, 0x6f, 0x6e], dtype=numpy.uint8)

        packet_seq7 = appendCRC(packet_seq7)
        in_pdu_seq7 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_seq7.size, packet_seq7))

        packet_status = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_status.ackFlags, testData_status.messageType, testData_status.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)

        packet_status = appendCRC(packet_status)
        in_pdu_status = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_status.size, packet_status))

        packet_abort_seq1 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_abort.ackFlags, testData_abort.messageType, testData_abort.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet_abort_seq1 = appendCRC(packet_abort_seq1)
        in_pdu_abort_seq1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_abort_seq1.size, packet_abort_seq1))

        packet_abort_seq7 = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_abort.ackFlags, testData_abort.messageType, testData_abort.messageSubTypeTx, 0x00, 0x00, 0x54, 0x65, 0x73, 0x74, 0x53, 0x65, 0x71, 0x23, 0x37, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, ], dtype=numpy.uint8)
        
        packet_abort_seq7 = appendCRC(packet_abort_seq7)
        in_pdu_abort_seq7 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_abort_seq7.size, packet_abort_seq7))
                
        self.tb.start()
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_seq1) 
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_seq3) 
        time.sleep(1.1)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_seq7) 
        time.sleep(1)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_status)
        time.sleep(7)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_status)
        time.sleep(1)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_abort_seq1)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_abort_seq7)
        time.sleep(1)
        requestSequencingService.to_basic_block()._post(pmt.intern("in"), in_pdu_status)
        time.sleep(1)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d2.num_messages() == 0)

        expected_response_0 = numpy.array([0, 6, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 1, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 1, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 54, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 55, 0, 0, 0, 0, 0, 0, 1], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([0, 6, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 1, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 54, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 55, 0, 0, 0, 0, 0, 0, 1], dtype=numpy.uint8)  
        expected_response_2 = numpy.array([0, 6, 84, 101, 115, 116, 83, 101, 113, 35, 49, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 50, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 51, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 52, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 54, 0, 0, 0, 0, 0, 0, 0, 84, 101, 115, 116, 83, 101, 113, 35, 55, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.uint8)  

        payloads = [expected_response_0, expected_response_1, expected_response_2]

        testData_status.counter_offset = 12
        testData_status.counter_sec_offset = 5
                
        self.assertTrue(checkResults(3, d1, payloads, 0, d2, 0, testData_status, packet_status))                      

        self.assertTrue(d3.num_messages() == 12)
        
        expected_release_0 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 4], dtype=numpy.uint8)  
        release_0 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        expected_release_1 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 6], dtype=numpy.uint8)  
        release_1 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(1))), dtype=numpy.uint8)
        expected_release_2 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 25, 0, 0, 0, 0, 2], dtype=numpy.uint8)  
        release_2 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(2))), dtype=numpy.uint8)
        expected_release_3 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 31, 0, 0, 2, 1, 6], dtype=numpy.uint8)  
        release_3 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(3))), dtype=numpy.uint8)
        expected_release_4 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 9, 0, 0, 2, 1, 5], dtype=numpy.uint8)  
        release_4 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(4))), dtype=numpy.uint8)
        expected_release_5 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 25, 0, 0, 0, 0, 0], dtype=numpy.uint8)  
        release_5 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(5))), dtype=numpy.uint8)
        expected_release_6 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 31, 0, 0, 2, 1, 4], dtype=numpy.uint8)  
        release_6 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(6))), dtype=numpy.uint8)
        expected_release_7 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 4], dtype=numpy.uint8)  
        release_7 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(7))), dtype=numpy.uint8)
        expected_release_8 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 6], dtype=numpy.uint8)  
        release_8 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(8))), dtype=numpy.uint8)
        expected_release_9 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 6], dtype=numpy.uint8)  
        release_9 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(9))), dtype=numpy.uint8)
        expected_release_10 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 6], dtype=numpy.uint8)  
        release_10 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(10))), dtype=numpy.uint8)
        expected_release_11 = numpy.array([24, 23, 192, 0, 0, 7, 32, 3, 27, 0, 0, 2, 1, 4], dtype=numpy.uint8)  
        release_11 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(11))), dtype=numpy.uint8)
        
        self.assertTrue(numpy.array_equal(release_0, expected_release_0))
        self.assertTrue(numpy.array_equal(release_1, expected_release_1))                     
        self.assertTrue(numpy.array_equal(release_2, expected_release_2))
        self.assertTrue(numpy.array_equal(release_3, expected_release_3))  
        self.assertTrue(numpy.array_equal(release_4, expected_release_4))
        self.assertTrue(numpy.array_equal(release_5, expected_release_5))  
        self.assertTrue(numpy.array_equal(release_6, expected_release_6))
        self.assertTrue(numpy.array_equal(release_7, expected_release_7))                     
        self.assertTrue(numpy.array_equal(release_8, expected_release_8))
        self.assertTrue(numpy.array_equal(release_9, expected_release_9))  
        self.assertTrue(numpy.array_equal(release_10, expected_release_10))
        self.assertTrue(numpy.array_equal(release_11, expected_release_11))  
                                
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
    gr_unittest.run(qa_RequestSequencingService, "qa_RequestSequencingService.xml" )
