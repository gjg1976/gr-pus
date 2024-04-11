#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 MessageParser::sptr message_parser, ErrorHandler::sptr error_handler.
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
    from gnuradio.pus import RequestVerificationService
import numpy
import pmt
import time

class test_data():
    def __init__(self, messageType, messageSubType, messageSize, counter, apid, error, step, crcEnabled):
        self.messageType = messageType
        self.messageSubType = messageSubType
        self.messageSize = messageSize
        self.counter = counter
        
        self.apid = apid
        bytes_val = bytearray(apid.to_bytes(2, "big", signed = False))
        self.apidArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8)         
        self.error = error
        self.step = step 
        self.crcEnabled = crcEnabled
        
class qa_RequestVerificationService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x01, 0x01, 0x10, 1, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x01, 0x10,65540, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x01, 0x10, 1, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x01, 0x10, 1, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x01, 0x10, 1, 0x19, 0, 0, True))         
        self.testData.append(test_data(0x01, 0x01, 0x10, 1, 0x19, 0, 0, True))   
        self.testData.append(test_data(0x01, 0x02, 0x12, 65540, 0x19, 2, 0, True)) 
        self.testData.append(test_data(0x01, 0x02, 0x12, 1, 0x19, 2, 0, True)) 
        self.testData.append(test_data(0x01, 0x02, 0x12, 1, 0x19, 2, 0, True))                        
        self.testData.append(test_data(0x01, 0x02, 0x12, 1, 0x19, 2, 0, True))
        self.testData.append(test_data(0x01, 0x03, 0x10, 65540, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x03, 0x10, 1, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x03, 0x10, 1, 0x19, 0, 0, True))    
        self.testData.append(test_data(0x01, 0x04, 0x12, 65540, 0x19, 4, 0, True)) 
        self.testData.append(test_data(0x01, 0x04, 0x12, 1, 0x19, 4, 0, True)) 
        self.testData.append(test_data(0x01, 0x04, 0x12, 1, 0x19, 4, 0, True))                        
        self.testData.append(test_data(0x01, 0x04, 0x12, 1, 0x19, 4, 0, True))
        self.testData.append(test_data(0x01, 0x05, 0x11, 65540, 0x19, 0, 1, True)) 
        self.testData.append(test_data(0x01, 0x05, 0x11, 1, 0x19, 0, 9, True)) 
        self.testData.append(test_data(0x01, 0x05, 0x11, 1, 0x19, 0, 9, True))                        
        self.testData.append(test_data(0x01, 0x05, 0x11, 1, 0x19, 0, 9, True))                
        self.testData.append(test_data(0x01, 0x06, 0x13, 65540, 0x19, 5, 1, True)) 
        self.testData.append(test_data(0x01, 0x06, 0x13, 1, 0x19, 6, 9, True)) 
        self.testData.append(test_data(0x01, 0x06, 0x13, 1, 0x19, 6, 9, True))                        
        self.testData.append(test_data(0x01, 0x06, 0x13, 1, 0x19, 6, 9, True))   
        self.testData.append(test_data(0x01, 0x07, 0x10, 65540, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x07, 0x10, 1, 0x19, 0, 0, True)) 
        self.testData.append(test_data(0x01, 0x07, 0x10, 1, 0x19, 0, 0, True))         
        self.testData.append(test_data(0x01, 0x08, 0x12, 65540, 0x19, 8, 0, True)) 
        self.testData.append(test_data(0x01, 0x08, 0x12, 1, 0x19, 7, 0, True)) 
        self.testData.append(test_data(0x01, 0x08, 0x12, 1, 0x19, 6, 0, True))                        
        self.testData.append(test_data(0x01, 0x08, 0x12, 1, 0x19, 6, 0, True))
        self.testData.append(test_data(0x01, 0x0a, 0x12, 65540, 0x19, 9, 0, True)) 
        self.testData.append(test_data(0x01, 0x0a, 0x12, 1, 0x19, 12, 0, True)) 
        self.testData.append(test_data(0x01, 0x0a, 0x12, 1, 0x19, 12, 0, True))                        
        self.testData.append(test_data(0x01, 0x0a, 0x12, 1, 0x19, 12, 0, True))
        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.RequestVerificationService()

    def test_001_S01_no_and_wrong_metadata(self):
        testData = self.testData[0]
                
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20, 0x10, 0x01, 0x00, 0x00, 0xc8, 0x97], dtype=numpy.uint8)
        in_pdu_noMeta = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(0))

        in_pdu_Meta = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu_noMeta) 
        requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu_Meta)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)

    def test_002_TM01_01_acceptance_report_verification_full_rollover(self):
        testData = self.testData[1]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,1) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  
        
    def test_003_TM01_01_acceptance_report_packet_sequence_verification(self):
        testData = self.testData[2]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,1) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  

    def test_004_TM01_01_acceptance_non_response_to_wrong_message_size(self):
        testData = self.testData[3]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,1) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def est_005_TM01_01_acceptance_response_verification_with_non_related_metadata_verification_error_type(self):
        testData = self.testData[4]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,1) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error"), pmt.from_long(3));
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  

    def test_006_TM01_01_acceptance_response_verification_with_non_related_metadata_verification_step_id(self):
        testData = self.testData[5]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,1) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("step"), pmt.from_long(4));
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))          

    def test_007_TM01_02_failed_acceptance_report_verification_full_rollover(self):
        testData = self.testData[6]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error));
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
  
        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 

    def test_008_TM01_03_failed_acceptance_report_packet_sequence_verification(self):
        testData = self.testData[7]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error));
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
  
        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 

    def test_009_TM01_03_failed_acceptance_wrong_message_size(self):
        testData = self.testData[8]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()

        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,1) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error));
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_010_TM01_02_failed_acceptance_response_verification_with_not_metadata_verification_error(self):
        testData = self.testData[9]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,2) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0) 

    def test_011_TM01_03_startexec_report_verification_full_rollover(self):
        testData = self.testData[10]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,3) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  
        
    def test_012_TM01_03_startexec_report_packet_sequence_verification(self):
        testData = self.testData[11]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,3) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  

    def test_013_TM01_03_startexec_non_response_to_wrong_message_size(self):
        testData = self.testData[12]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,3) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_014_TM01_04_failed_startexec_report_verification_full_rollover(self):
        testData = self.testData[13]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
  
        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 

    def test_015_TM01_04_failed_startexec_report_packet_sequence_verification(self):
        testData = self.testData[14]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()

        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 
        
    def test_016_TM01_04_failed_startexec_wrong_message_size(self):
        testData = self.testData[15]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_017_TM01_04_failed_startexec_response_verification_with_not_metadata_verification_error(self):
        testData = self.testData[16]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0) 

    def test_018_TM01_05_progexec_report_verification_full_rollover(self):
        testData = self.testData[17]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,5) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("step_id"), pmt.from_long(testData.step))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  
        
    def test_019_TM01_05_progexec_report_packet_sequence_verification(self):
        testData = self.testData[18]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,5) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("step_id"), pmt.from_long(testData.step))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  

    def test_020_TM01_05_progexec_wrong_message_size(self):
        testData = self.testData[19]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,3) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("step_id"), pmt.from_long(testData.step))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_021_TM01_05_progexec_with_non_related_metadata_verification_step_id(self):
        testData = self.testData[20]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,3) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)   

    def test_022_TM01_06_failed_progexec_report_verification_full_rollover(self):
        testData = self.testData[21]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("step_id"), pmt.from_long(testData.step))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  
        
    def test_023_TM01_06_failed_progexec_report_packet_sequence_verification(self):
        testData = self.testData[22]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("step_id"), pmt.from_long(testData.step))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  

    def test_024_TM01_06_failed_progexec_wrong_message_size(self):
        testData = self.testData[23]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("step_id"), pmt.from_long(testData.step))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_025_TM01_06_failed_progexec_with_non_related_metadata_verification_step_id(self):
        testData = self.testData[24]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)   

    def test_026_TM01_07_exec_report_verification_full_rollover(self):
        testData = self.testData[25]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  
        
    def test_027_TM01_07_exec_report_packet_sequence_verification(self):
        testData = self.testData[26]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,5) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet))  

    def test_028_TM01_07_exec_non_response_to_wrong_message_size(self):
        testData = self.testData[27]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_029_TM01_08_failed_exec_report_verification_full_rollover(self):
        testData = self.testData[28]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
  
        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 

    def test_030_TM01_08_failed_exec_report_packet_sequence_verification(self):
        testData = self.testData[29]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()

        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 
        
    def test_031_TM01_08_failed_exec_wrong_message_size(self):
        testData = self.testData[30]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_032_TM01_08_failed_exec_response_verification_with_not_metadata_verification_error(self):
        testData = self.testData[31]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0) 

    def test_033_TM01_10_failed_routing_report_verification_full_rollover(self):
        testData = self.testData[32]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
  
        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 

    def test_034_TM01_10_failed_routing_report_packet_sequence_verification(self):
        testData = self.testData[33]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()

        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(checkResults(testData.counter, d1, testData, packet)) 
        
    def test_035_TM01_10_failed_routing_wrong_message_size(self):
        testData = self.testData[34]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        meta = pmt.dict_add(meta, pmt.intern("error_type"), pmt.from_long(testData.error))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)  

    def test_036_TM01_10_failed_routing_response_verification_with_not_metadata_verification_error(self):
        testData = self.testData[35]
        requestVerificationService = pus.RequestVerificationService()
        d1 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        
        self.tb.msg_connect((requestVerificationService, 'out'), (d1, 'store'))

        # Testing TC(17,4) 
        packet = numpy.array([0x18, 0x03, 0xc1, 0xa5, 0x00, 0x06, 0x23, 0x11, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        
        packet = appendCRC(packet)
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("req"), pmt.from_long(testData.messageSubType))
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
  
        self.tb.start()
        for i in range (0, testData.counter):
            requestVerificationService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)                                                                                            
def checkResults(numd1, d1, testData, packet):

    if d1.num_messages() != numd1:
        return False

    for i in range (0, testData.counter):
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(i))), dtype=numpy.uint8)

        if not checkPrimaryHeader(testData.apid, testData.messageSize, i, response):
            return False

        if testData.crcEnabled:
            if not checkCRC(response):
                return False           

        if testData.messageSubType == 0x01:
            if not checkSuccessAcceptanceVerification(response, packet):
                return False  

        if testData.messageSubType == 0x02:
            if not checkFailedAcceptanceVerification(response, packet, testData.error):
                return False    

        if testData.messageSubType == 0x03:
            if not checkSuccessStartExecutionVerification(response, packet):
                return False  

        if testData.messageSubType == 0x04:
            if not checkFailedStartExecutionVerification(response, packet, testData.error):
                return False 

        if testData.messageSubType == 0x05:
            if not checkSuccessProgressExecutionVerification(response, packet, testData.step):
                return False  

        if testData.messageSubType == 0x06:
            if not checkFailedProgressExecutionVerification(response, packet, testData.error, testData.step):
                return False 

        if testData.messageSubType == 0x07:
            if not checkSuccessSuccessCompletionExecutionVerification(response, packet):
                return False  

        if testData.messageSubType == 0x08:
            if not checkFailedSuccessCompletionExecutionVerification(response, packet, testData.error):
                return False  

        if testData.messageSubType == 0x09:
            print(response)
            if not checkFailedRoutingVerification(response, packet, testData.error):
                return False  

    return True

def checkPrimaryHeader(apid, size, counter, message):
    bytes_val = bytearray(apid.to_bytes(2, "big", signed = False))
    apidArray = numpy.frombuffer(bytes_val,dtype=numpy.uint8) 
    counter = counter & 0xffff
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
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
     
    return True           

def checkFailedAcceptanceVerification(message, sentMessage, error):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
    errorRx = int.from_bytes(message[13+9], byteorder='big', signed=False) 
    if errorRx != error:
        return False
             
    return True    

def checkSuccessStartExecutionVerification(message, sentMessage):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
     
    return True  

def checkFailedStartExecutionVerification(message, sentMessage, error):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
    errorRx = int.from_bytes(message[13+9], byteorder='big', signed=False) 
    if errorRx != error:
        return False
             
    return True     
    
def checkSuccessProgressExecutionVerification(message, sentMessage, step):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False

    if message[13+8] != step:    
        return False              
  
    return True  

def checkFailedProgressExecutionVerification(message, sentMessage, error, step):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False

    if message[13+8] != step:    
        return False              

    errorRx = int.from_bytes(message[13+10], byteorder='big', signed=False) 
    if errorRx != error:
        return False  
        
    return True  


def checkSuccessSuccessCompletionExecutionVerification(message, sentMessage):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
             
    return True  

def checkFailedSuccessCompletionExecutionVerification(message, sentMessage, error):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
 
    errorRx = int.from_bytes(message[13+9], byteorder='big', signed=False) 
    if errorRx != error:
        return False  
        
    return True  

def checkFailedRoutingVerification(message, sentMessage, error):
    responseVerification = message[13+4:13+8]
    sentMessage = sentMessage[0:4]

    if (not numpy.array_equal(responseVerification, sentMessage)):
        return False
 
    errorRx = int.from_bytes(message[13+9], byteorder='big', signed=False) 
    if errorRx != error:
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
    gr_unittest.run(qa_RequestVerificationService, "qa_RequestVerificationService.xml" )
