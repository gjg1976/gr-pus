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

class qa_TimeBasedSchedulingService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x0b, 0x01, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x0b, 0x02, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x0b, 0x03, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x0b, 0x04, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x0b, 0x04, 0x00, 0x11, 1, 0x19, 15, 7, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x0b, 0x05, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x0b, 0x05, 0x00, 0x11, 1, 0x19, 15, 7, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x0b, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x0b, 0x09, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x0b, 0x0c, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #9        
        self.testData.append(test_data(0x0b, 0x10, 0x0a, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x0b, 0x11, 0x0d, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #11  
        self.testData.append(test_data(0x0b, 0x0f, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x0b, 0x04, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #13
        self.testData.append(test_data(0x0b, 0x0c, 0x0d, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #14  
        self.testData.append(test_data(0x0b, 0x09, 0x0a, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #15  
        self.testData.append(test_data(0x0b, 0x05, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x0b, 0x10, 0x0a, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #17
        self.testData.append(test_data(0x0b, 0x11, 0x0d, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #18 
        self.testData.append(test_data(0x0b, 0x07, 0x00, 0x11, 1, 0x19,  15, 0, 0, True, 0, 0)) #19
        self.testData.append(test_data(0x0b, 0x11, 0x0d, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #20
        self.testData.append(test_data(0x0b, 0x0f, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #21
        self.testData.append(test_data(0x0b, 0x03, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #22
        self.testData.append(test_data(0x0b, 0x10, 0x0a, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #23
        self.testData.append(test_data(0x0b, 0x07, 0x00, 0x11, 1, 0x19, 0, 7, 0, True, 0, 0)) #24
        self.testData.append(test_data(0x0b, 0x0f, 0x00, 0x11, 1, 0x19, 0, 6, 0, True, 0, 0)) #25
        self.testData.append(test_data(0x0b, 0x04, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #26
        self.testData.append(test_data(0x0b, 0x01, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #27
        self.testData.append(test_data(0x0b, 0x02, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #28

                                                                 
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.TimeBasedSchedulingService()

    def test_001_ST12_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x03, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x0b, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST11_01_invalid_paramsSize_fields_longer(self):
        testData = self.testData[0]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST11_02_invalid_paramsSize_fields_longer(self):
        testData = self.testData[1]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST11_03_invalid_paramsSize_fields_longer(self):
        testData = self.testData[2]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST11_04_invalid_numTC_field_shorter(self):
        testData = self.testData[3]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                

    def test_006_ST11_04_invalid_releaseTime_field_shorter(self):
        testData = self.testData[3]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 71, 190, 255], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_007_ST11_04_invalid_TC_field_shorter(self):
        testData = self.testData[3]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 71, 190, 255, 255, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_008_ST11_04_invalid_TC_field_longer(self):
        testData = self.testData[3]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 71, 190, 255, 255, 0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x2f, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00,  71,  191, 0, 0, 0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x2f, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_009_ST11_04_invalid_releaseTime_expires(self):
        testData = self.testData[4]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1980, 1, 6)                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x63, 0x72, 0x4e, 0x00, 0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x2f, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00,  71,  189, 0, 0, 0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x2f, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

    def test_010_ST11_05_invalid_numTC_field_shorter(self):
        testData = self.testData[5]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                

    def test_011_ST11_05_invalid_sourceID_field_shorter(self):
        testData = self.testData[5]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_012_ST11_05_appID_field_shorter(self):
        testData = self.testData[5]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_013_ST11_05_seqCounter_field_shorter(self):
        testData = self.testData[5]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_014_ST11_05_invalid_TC_field_longer(self):
        testData = self.testData[5]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_015_ST11_05_invalid_activity_non_exists(self):
        testData = self.testData[6]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 4)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(2), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(3), packet)) 

    def test_016_ST11_07_invalid_shitTime_field_shorter(self):
        testData = self.testData[7]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))    

    def test_017_ST11_07_invalid_numShf_field_shorter(self):
        testData = self.testData[7]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                

    def test_018_ST11_07_invalid_sourceID_field_shorter(self):
        testData = self.testData[7]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_019_ST11_07_appID_field_shorter(self):
        testData = self.testData[7]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_020_ST11_07_seqCounter_field_shorter(self):
        testData = self.testData[7]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_021_ST11_07_invalid_SeqCounter_field_longer(self):
        testData = self.testData[7]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_022_ST11_09_invalid_numRep_field_shorter(self):
        testData = self.testData[8]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                

    def test_023_ST11_09_invalid_sourceID_field_shorter(self):
        testData = self.testData[8]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_024_ST11_09_invalid_appID_field_shorter(self):
        testData = self.testData[8]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_025_ST11_09_invalid_seqCounter_field_shorter(self):
        testData = self.testData[8]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_026_ST11_09_invalid_seqCounter_field_longer(self):
        testData = self.testData[8]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

 
    def test_027_ST11_12_invalid_numRep_field_shorter(self):
        testData = self.testData[9]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                

    def test_028_ST11_12_invalid_sourceID_field_shorter(self):
        testData = self.testData[9]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_029_ST11_12_appID_field_shorter(self):
        testData = self.testData[9]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_030_ST11_12_invalid_seqCounter_field_shorter(self):
        testData = self.testData[9]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_031_ST11_12_invalid_seqCounter_field_longer(self):
        testData = self.testData[9]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_032_ST11_16_invalid_params_fields_longer(self):
        testData = self.testData[10]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_033_ST11_17_invalid_params_fields_longer(self):
        testData = self.testData[11]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_034_ST11_15_seqCounter_field_shorter(self):
        testData = self.testData[12]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_035_ST11_15_invalid_TC_field_longer(self):
        testData = self.testData[12]
                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_036_ST11_4and12and9and5and16and17and7and17_add_report_delete_shift(self):
        # ------------------------------------------------------------
        # Insert Act TC[11,04]        
        # ------------------------------------------------------------ 

        testData = self.testData[13]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1980, 1, 6)                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))


        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x07, 91,  191, 0, 0, 0x18, 0x19, 0x00, 0x00, 0x00, 0x09, 0x27, 0x03, 0x1b, 0x00, 0x00,  0x02, 0x04, 0x07, 0xff, 0xff, 91,  191, 0, 0, 0x18, 0x19, 0x00, 0x01, 0x00, 0x06, 0x2f, 0x11, 0x01, 0x00, 0x00, 0xff, 0xff, 91,  191, 0, 10, 0x18, 0x19, 0x00, 0x02, 0x00, 0x0c, 0x27, 0x14, 0x01, 0x00, 0x00, 0x00,0x02, 0x00, 0x03, 0x00, 0x09, 0xff, 0xff, 91,  191, 0, 15, 0x18, 0x19, 0x00, 0x03, 0x00, 0x0b, 0x27, 0x13, 0x04, 0x00, 0x00, 0x01, 0x00, 0x14, 0x00, 0x04, 0xff, 0xff, 91,  191, 0, 15, 0x18, 0x19, 0x00, 0x04, 0x00, 0x06, 0x27, 0x0e, 0x03, 0x00, 0x00, 0xff, 0xff, 91,  191, 0, 19, 0x18, 0x19, 0x00, 0x05, 0x00, 0x06, 0x2f, 0x11, 0x03, 0x00, 0x00, 0xff, 0xff, 91,  191, 0, 0, 0x18, 0x19, 0x00, 0x06, 0x00, 0x06, 0x27, 0x0b, 0x03, 0x00, 0x00, 0xff, 0xff], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Summary Report by ID TC[11,12] => TM[11,13]         
        # ------------------------------------------------------------ 

        testData = self.testData[14]
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))   
                     
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x19, 0x00, 0x01, 0x00, 0x00, 0x00, 0x19, 0x00, 0x02], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        expected_response_0 = numpy.array([0, 2, 91, 191, 0, 0, 0, 0, 0, 25, 0, 1, 91, 191, 0, 10, 0, 0, 0, 25, 0, 2], dtype=numpy.uint8)
   
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))
        # ------------------------------------------------------------
        # Detail Report by ID TC[11,09] => TM[11,10]        
        # ------------------------------------------------------------ 
        testData = self.testData[15]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x19, 0x00, 0x00, 0x00, 0x00, 0x00, 0x19, 0x00, 0x05], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        testData.counter_offset = 1
        expected_response_0 = numpy.array([0, 2, 91, 191, 0, 0, 24, 25, 0, 0, 0, 9, 39, 3, 27, 0, 0, 2, 4, 7, 255, 255, 91, 191, 0, 19, 24, 25, 0, 5, 0, 6, 47, 17, 3, 0, 0, 255, 255], dtype=numpy.uint8)
 
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))
        # ------------------------------------------------------------
        # Delete Act TC[11,05]                
        # ------------------------------------------------------------ 
        testData = self.testData[16]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x19, 0x00, 0x01, 0x00, 0x00, 0x00, 0x19, 0x00, 0x05], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 
        # ------------------------------------------------------------
        # Detail Report All TC[11,09] => TM[11,16]        
        # ------------------------------------------------------------ 
        testData = self.testData[17]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        testData.counter_offset = 2
        testData.counter_sec_offset = 1
        expected_response_0 = numpy.array([0, 5, 91, 191, 0, 0, 24, 25, 0, 0, 0, 9, 39, 3, 27, 0, 0, 2, 4, 7, 255, 255, 91, 191, 0, 0, 24, 25, 0, 6, 0, 6, 39, 11, 3, 0, 0, 255, 255, 91, 191, 0, 10, 24, 25, 0, 2, 0, 12, 39, 20, 1, 0, 0, 0, 2, 0, 3, 0, 9, 255, 255, 91, 191, 0, 15, 24, 25, 0, 3, 0, 11, 39, 19, 4, 0, 0, 1, 0, 20, 0, 4, 255, 255, 91, 191, 0, 15, 24, 25, 0, 4, 0, 6, 39, 14, 3, 0, 0, 255, 255], dtype=numpy.uint8)
 
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))
        # ------------------------------------------------------------
        # Summary Report All TC[11,17] => TM[11,13]        
        # ------------------------------------------------------------ 
        testData = self.testData[18]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        testData.counter_offset = 3
        testData.counter_sec_offset = 1
        expected_response_0 = numpy.array([0, 5, 91, 191, 0, 0, 0, 0, 0, 25, 0, 0, 91, 191, 0, 0, 0, 0, 0, 25, 0, 6, 91, 191, 0, 10, 0, 0, 0, 25, 0, 2, 91, 191, 0, 15, 0, 0, 0, 25, 0, 3, 91, 191, 0, 15, 0, 0, 0, 25, 0, 4], dtype=numpy.uint8)
 
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Time shift by ID TC[11,07]                
        # ------------------------------------------------------------ 
        testData = self.testData[19]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0xff, 0xff, 0xff, 0xe7, 0x00, 0x02, 0x00, 0x00, 0x00, 0x19, 0x00, 0x00, 0x00, 0x00, 0x00, 0x19, 0x00, 0x02], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 
        
        # ------------------------------------------------------------
        # Summary Report All TC[11,17] => TM[11,13]        
        # ------------------------------------------------------------ 
        testData = self.testData[20]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        testData.counter_offset = 4
        testData.counter_sec_offset = 2
        expected_response_0 = numpy.array([0, 5, 91, 190, 255, 231, 0, 0, 0, 25, 0, 0, 91, 190, 255, 241, 0, 0, 0, 25, 0, 2, 91, 191, 0, 0, 0, 0, 0, 25, 0, 6, 91, 191, 0, 15, 0, 0, 0, 25, 0, 3, 91, 191, 0, 15, 0, 0, 0, 25, 0, 4], dtype=numpy.uint8)
 
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Time shift all TC[11,15]                
        # ------------------------------------------------------------ 
        testData = self.testData[21]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Summary Report All TC[11,17] => TM[11,13]        
        # ------------------------------------------------------------ 
        testData = self.testData[20]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        testData.counter_offset = 5
        testData.counter_sec_offset = 3
        expected_response_0 = numpy.array([0, 5, 91, 190, 255, 246, 0, 0, 0, 25, 0, 0, 91, 191, 0, 0, 0, 0, 0, 25, 0, 2, 91, 191, 0, 15, 0, 0, 0, 25, 0, 6, 91, 191, 0, 30, 0, 0, 0, 25, 0, 3, 91, 191, 0, 30, 0, 0, 0, 25, 0, 4], dtype=numpy.uint8)
 
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Time shift by ID TC[11,07]                
        # ------------------------------------------------------------ 
        testData = self.testData[24]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0xa4, 0x41, 0x00, 0x20, 0x00, 0x01, 0x00, 0x00, 0x00, 0x19, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error)) 

        # ------------------------------------------------------------
        # Time shift all TC[11,15]                
        # ------------------------------------------------------------ 
        testData = self.testData[25]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0xa4, 0x41, 0x00, 0x20], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error)) 
                
        # ------------------------------------------------------------
        # Reset the time based sch TC[11,3]                
        # ------------------------------------------------------------ 
        testData = self.testData[22]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        # ------------------------------------------------------------
        # Detail Report All TC[11,16] => TM[11,10]        
        # ------------------------------------------------------------ 
        testData = self.testData[23]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        testData.counter_offset = 6
        testData.counter_sec_offset = 2
        expected_response_0 = numpy.array([0, 0], dtype=numpy.uint8)
 
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))  

    def test_037_ST11_1and2_scheduler(self):
        # ------------------------------------------------------------
        # Insert Act TC[11,04]        
        # ------------------------------------------------------------ 

        testData = self.testData[26]
        testData_en = self.testData[27]
        testData_dis = self.testData[28]        
        timeConfig = pus.TimeConfig(0.1, 2, False, 1980, 1, 6)                
        timeBasedSchedulingService = pus.TimeBasedSchedulingService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        now = int(time.time()) - 315964800
        obt_0 = numpy.frombuffer(bytearray((now+60+5).to_bytes(4, "big", signed = False)),dtype=numpy.uint8)
        obt_1 = numpy.frombuffer(bytearray((now+60+10).to_bytes(4, "big", signed = False)),dtype=numpy.uint8)
        obt_2 = numpy.frombuffer(bytearray((now+60+15).to_bytes(4, "big", signed = False)),dtype=numpy.uint8)
        obt_3 = numpy.frombuffer(bytearray((now+60+20).to_bytes(4, "big", signed = False)),dtype=numpy.uint8)        
      
        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x07, obt_0[0],  obt_0[1], obt_0[2], obt_0[3], 0x18, 0x19, 0x00, 0x00, 0x00, 0x09, 0x27, 0x03, 0x1b, 0x00, 0x00,  0x02, 0x04, 0x07, 0xff, 0xff, obt_0[0],  obt_0[1], obt_0[2], obt_0[3], 0x18, 0x19, 0x00, 0x01, 0x00, 0x06, 0x2f, 0x11, 0x01, 0x00, 0x00, 0xff, 0xff, obt_1[0],  obt_1[1], obt_1[2], obt_1[3], 0x18, 0x19, 0x00, 0x02, 0x00, 0x0c, 0x27, 0x14, 0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x03, 0x00, 0x09, 0xff, 0xff, obt_2[0],  obt_2[1], obt_2[2], obt_2[3], 0x18, 0x19, 0x00, 0x03, 0x00, 0x0b, 0x27, 0x13, 0x04, 0x00, 0x00, 0x01, 0x00, 0x14, 0x00, 0x04, 0xff, 0xff, obt_2[0],  obt_2[1], obt_2[2], obt_2[3], 0x18, 0x19, 0x00, 0x04, 0x00, 0x06, 0x27, 0x0e, 0x03, 0x00, 0x00, 0xff, 0xff, obt_3[0],  obt_3[1], obt_3[2], obt_3[3], 0x18, 0x19, 0x00, 0x05, 0x00, 0x06, 0x2f, 0x11, 0x03, 0x00, 0x00, 0xff, 0xff, obt_0[0],  obt_0[1], obt_0[2], obt_0[3], 0x18, 0x19, 0x00, 0x06, 0x00, 0x06, 0x27, 0x0b, 0x03, 0x00, 0x00, 0xff, 0xff], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        packet_en = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_en.ackFlags, testData_en.messageType, testData_en.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet_en = appendCRC(packet_en)
        in_pdu_en = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_en.size, packet_en))

        packet_dis = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_dis.ackFlags, testData_dis.messageType, testData_dis.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet_dis = appendCRC(packet_dis)
        in_pdu_dis = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_dis.size, packet_dis))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(72)
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu_en) 
        time.sleep(5)
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu_dis) 
        time.sleep(5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 6)
        self.assertTrue(d3.num_messages() == 2)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet_en)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet_en)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet_en)) 
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(3), packet_dis)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(4), packet_dis)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(5), packet_dis)) 

        release_0 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        expected_release_0 = numpy.array([24, 25, 0, 3, 0, 11, 39, 19, 4, 0, 0, 1, 0, 20, 0, 4, 255, 255], dtype=numpy.uint8)
        
        release_1 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(1))), dtype=numpy.uint8)
        expected_release_1 = numpy.array([24, 25, 0, 4, 0, 6, 39, 14, 3, 0, 0, 255, 255], dtype=numpy.uint8)

        self.assertTrue(numpy.array_equal(release_0, expected_release_0))       
        self.assertTrue(numpy.array_equal(release_1, expected_release_1))

        # ------------------------------------------------------------
        # Summary Report All TC[11,17] => TM[11,13]        
        # ------------------------------------------------------------ 
        testData = self.testData[20]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((timeBasedSchedulingService, 'out'), (d1, 'store'))
        self.tb.msg_connect((timeBasedSchedulingService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
      
        self.tb.start()
        timeBasedSchedulingService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        expected_response_0 = numpy.array([0, 0], dtype=numpy.uint8)
 
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))
                                                                                                                                                                                                                                                       
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
    gr_unittest.run(qa_TimeBasedSchedulingService, "qa_TimeBasedSchedulingService.xml" )
