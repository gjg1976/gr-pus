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
        
class qa_LargePacketTransferService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x0d, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x0d, 0x01, 0x01, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x0d, 0x02, 0x02, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x0d, 0x01, 0x03, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x0d, 0x09, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x0d, 0x09, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x0d, 0x09, 0x00, -1, 1, 0x19, 0, 59, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x0d, 0x09, 0x00, -1, 1, 0x19, 0, 61, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x0d, 0x0a, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x0d, 0x0a, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x0d, 0x0a, 0x00, -1, 1, 0x19, 0, 60, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x0d, 0x0a, 0x00, -1, 1, 0x19, 0, 61, 0, True, 0, 0)) #11
        self.testData.append(test_data(0x0d, 0x0b, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x0d, 0x0b, 0x10, -1, 1, 0x19, 0, 60, 0, True, 0, 0)) #13
        self.testData.append(test_data(0x0d, 0x0b, 0x00, -1, 1, 0x19, 0, 61, 0, True, 0, 0)) #14
        self.testData.append(test_data(0x0d, 0x09, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #15        
        self.testData.append(test_data(0x0d, 0x0a, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x0d, 0x0b, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #17
                                        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.LargePacketTransferService()

    def test_001_ST13_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))
        
        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x04, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x0d, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST13_in_packet_short(self):
        testData = self.testData[0]
                
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packetType = numpy.fromfile("../../../examples/test_one_pattern.bin", dtype=numpy.uint8)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("large"), in_pduType) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)

    def test_003_ST13_in_packet_two_parts(self):
        testData = self.testData[0]
                
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packetType = numpy.fromfile("../../../examples/test_two_pattern.bin", dtype=numpy.uint8)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("large"), in_pduType) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

              
        self.assertTrue(d1.num_messages() == 2)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)     
        
        testData = self.testData[1]
        
        expected_response = numpy.array([0, 0, 0, 0], dtype=numpy.uint8)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, i & 0xff)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled))     

        testData = self.testData[3]

        expected_response = numpy.array([0, 0, 0, 1], dtype=numpy.uint8)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, (255 - i) & 0xff)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(1))), dtype=numpy.uint8)
        testData.counter_offset = 1;
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled)) 
        
    def test_004_ST13_in_packet_four_parts(self):
        testData = self.testData[0]
                
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packetType = numpy.fromfile("../../../examples/test_four_pattern.bin", dtype=numpy.uint8)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("large"), in_pduType) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 4)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0) 

        testData = self.testData[1]
        
        expected_response = numpy.array([0, 0, 0, 0], dtype=numpy.uint8)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, i & 0xff)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled))     

        testData = self.testData[2]

        expected_response = numpy.array([0, 0, 0, 1], dtype=numpy.uint8)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, (255 - i) & 0xff)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(1))), dtype=numpy.uint8)
        testData.counter_offset = 1;
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled)) 

        
        expected_response = numpy.array([0, 0, 0, 2], dtype=numpy.uint8)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, i & 0xff)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(2))), dtype=numpy.uint8)
        testData.counter_offset = 2;
        testData.counter_sec_offset = 1;
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled)) 

        testData = self.testData[3]

        expected_response = numpy.array([0, 0, 0, 3], dtype=numpy.uint8)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, (255 - i) & 0xff)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(3))), dtype=numpy.uint8)
        testData.counter_offset = 3;
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled)) 

    def test_005_ST13_09_invalid_trans_ID_shorter(self):
        testData = self.testData[4]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_006_ST13_09_invalid_trans_counter_shorter(self):
        testData = self.testData[4]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_ST13_09_invalid_payload_shorter(self):
        testData = self.testData[4]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 255):
            packet = numpy.append(packet, i & 0xff)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_ST13_09_invalid_payload_longer(self):
        testData = self.testData[5]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet = numpy.append(packet, i & 0xff)
        packet = numpy.append(packet, 0x00)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_009_ST13_09_invalid_trans_id_already_used(self):
        testData = self.testData[6]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet_0 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_0 = numpy.append(packet_0, i & 0xff)
        packet_0 = appendCRC(packet_0)
        in_pdu_0 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_0.size, packet_0))

        packet_1 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x1a, 0xff, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_1 = numpy.append(packet_1, i & 0xff)
        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))
                
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_0) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet_1, testData.error))

    def test_010_ST13_09_invalid_trans_counter_wrong(self):
        testData = self.testData[7]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01], dtype=numpy.uint8)
        for i in range(0, 256):
            packet = numpy.append(packet, i & 0xff)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_011_ST13_10_invalid_trans_ID_shorter(self):
        testData = self.testData[8]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_012_ST13_10_invalid_trans_counter_shorter(self):
        testData = self.testData[8]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_013_ST13_10_invalid_payload_shorter(self):
        testData = self.testData[8]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 255):
            packet = numpy.append(packet, i & 0xff)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST13_10_invalid_payload_longer(self):
        testData = self.testData[9]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet = numpy.append(packet, i & 0xff)
        packet = numpy.append(packet, 0x00)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_015_ST13_10_invalid_trans_id_non_exist(self):
        testData = self.testData[6]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))
        
        packet_0 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_0 = numpy.append(packet_0, i & 0xff)
        packet_0 = appendCRC(packet_0)
        in_pdu_0 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_0.size, packet_0))

        testData = self.testData[10]         
        packet_1 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_1 = numpy.append(packet_1, i & 0xff)
        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_0) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
  
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet_1, testData.error))

    def test_016_ST13_10_invalid_trans_counter_wrong(self):
        testData = self.testData[6]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))
        
        packet_0 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_0 = numpy.append(packet_0, i & 0xff)
        packet_0 = appendCRC(packet_0)
        in_pdu_0 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_0.size, packet_0))

        testData = self.testData[11]         
        packet_1 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_1 = numpy.append(packet_1, i & 0xff)
        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_0) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet_1, testData.error))

    def test_017_ST13_11_invalid_trans_ID_shorter(self):
        testData = self.testData[12]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_018_ST13_11_invalid_trans_counter_shorter(self):
        testData = self.testData[12]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_019_ST13_11_invalid_trans_id_non_exist(self):
        testData = self.testData[6]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))
        
        packet_0 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_0 = numpy.append(packet_0, i & 0xff)
        packet_0 = appendCRC(packet_0)
        in_pdu_0 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_0.size, packet_0))

        testData = self.testData[13]         
        packet_1 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_1 = numpy.append(packet_1, i & 0xff)
        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_0) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
  
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet_1, testData.error))

    def test_020_ST13_11_invalid_trans_counter_wrong(self):
        testData = self.testData[6]                        
        largePacketTransferService = pus.LargePacketTransferService()
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))
        
        packet_0 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_0 = numpy.append(packet_0, i & 0xff)
        packet_0 = appendCRC(packet_0)
        in_pdu_0 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_0.size, packet_0))

        testData = self.testData[14]         
        packet_1 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_1 = numpy.append(packet_1, i & 0xff)
        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_0) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet_1, testData.error))

    def test_021_ST13_9and10and11and16_uplink_timeout(self):
        testData = self.testData[6]                        
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        largePacketTransferService = pus.LargePacketTransferService()

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))
        
        packet_0 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_0 = numpy.append(packet_0, i & 0xff)
        packet_0 = appendCRC(packet_0)
        in_pdu_0 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_0.size, packet_0))

        testData = self.testData[9]         
        packet_1 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_1 = numpy.append(packet_1, (255 - i) & 0xff)
        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))
        
        testData = self.testData[13]         
        packet_2 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_2 = numpy.append(packet_2, i & 0xff)
        packet_2 = appendCRC(packet_2)
        in_pdu_2 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_2.size, packet_2))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_0) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        time.sleep(12)
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_2) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet_2, testData.error))
        
        expected_response = numpy.array([0, 1, 1], dtype=numpy.uint8)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled)) 

    def test_022_ST13_9and10and11_uplink_packet(self):
        testData = self.testData[15]                        
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        largePacketTransferService = pus.LargePacketTransferService()

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((largePacketTransferService, 'out'), (d1, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((largePacketTransferService, 'release'), (d3, 'store'))
        
        packet_0 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_0 = numpy.append(packet_0, i & 0xff)
        packet_0 = appendCRC(packet_0)
        in_pdu_0 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_0.size, packet_0))

        testData = self.testData[16]         
        packet_1 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_1 = numpy.append(packet_1, (255 - i) & 0xff)
        packet_1 = appendCRC(packet_1)
        in_pdu_1 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_1.size, packet_1))
        
        testData = self.testData[17]         
        packet_2 = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02], dtype=numpy.uint8)
        for i in range(0, 256):
            packet_2 = numpy.append(packet_2, i & 0xff)
        packet_2 = appendCRC(packet_2)
        in_pdu_2 = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_2.size, packet_2))
        
        self.tb.start()
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_0) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_1) 
        largePacketTransferService.to_basic_block()._post(pmt.intern("in"), in_pdu_2) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 9)
        self.assertTrue(d3.num_messages() == 1) 

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet_0))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet_0))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet_0))
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(3), packet_1))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(4), packet_1))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(5), packet_1))        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(6), packet_2))
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(7), packet_2))
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(8), packet_2))

        expected_response = numpy.array([], dtype=numpy.uint8)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, i & 0xff)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, (255 - i) & 0xff)
        for i in range(0, 256):
            expected_response = numpy.append(expected_response, i & 0xff)
            
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(response, expected_response))
                                                         
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
    gr_unittest.run(qa_LargePacketTransferService, "qa_LargePacketTransferService.xml" )
