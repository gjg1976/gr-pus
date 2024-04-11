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

class qa_EventReportService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x05, 0x01, 0x01, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x05, 0x01, 0x01, 0xe, 65538, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x05, 0x02, 0x02, 0xe, 65538, 0x19, 0, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x05, 0x03, 0x03, 0xe, 65538, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x05, 0x04, 0x04, 0xe, 65538, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x05, 0x05, 0x00, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x05, 0x05, 0x00, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x05, 0x05, 0x00, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x05, 0x05, 0x00, 0xe, 1, 0x19, 0, 64, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x05, 0x06, 0x00, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x05, 0x06, 0x00, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x05, 0x06, 0x00, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #11
        self.testData.append(test_data(0x05, 0x06, 0x00, 0xe, 1, 0x19, 0, 64, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x05, 0x07, 0x00, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #13
        self.testData.append(test_data(0x05, 0x07, 0x08, -1, 1, 0x19, 15, 1, 0, True, 0, 0)) #14
        self.testData.append(test_data(0x05, 0x01, 0x01, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0))#15
        self.testData.append(test_data(0x05, 0x02, 0x02, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x05, 0x03, 0x03, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #17
        self.testData.append(test_data(0x05, 0x04, 0x04, 0xe, 1, 0x19, 0, 1, 0, True, 0, 0)) #18
        self.testData.append(test_data(0x05, 0x06, 0x00, 0xe, 1, 0x19, 15, 1, 0, True, 0, 0)) #19
        self.testData.append(test_data(0x05, 0x05, 0x00, 0xe, 1, 0x19, 15, 1, 0, True, 0, 0)) #20
                                                                        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.EventReportService("")

    def test_001_S05_RID_no_and_wrong_metadata(self):
        testData = self.testData[0]                        
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([], dtype=numpy.uint8)
        in_pdu_noMeta = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        wrong_meta = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_float(12.1))
        in_pdu_wrongMeta = pmt.cons(wrong_meta, pmt.init_u8vector(packet.size, packet))
        
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(8))
        
        in_pdu_Meta = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_noMeta) 
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_wrongMeta) 
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_Meta)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)

    def test_002_TM05_01_informative_event_report_verification_full_roll_over(self):
        testData = self.testData[1]                        
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x01,0x14], dtype=numpy.uint8)
        
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(0))
        
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0x01,0x14], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(testData.counter, d1, payloads, True, 0, d2, 0, testData, packet))        

    def test_003_TM05_02_low_severity_anomaly_report_verification_full_roll_over(self):
        testData = self.testData[2]                        
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x35,0xdc], dtype=numpy.uint8)
        
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0x35,0xdc], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(testData.counter, d1, payloads, True, 0, d2, 0, testData, packet))    

    def test_004_TM05_03_medium_severity_anomaly_report_verification_full_roll_over(self):
        testData = self.testData[3]                        
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x35,0xdc], dtype=numpy.uint8)
        
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0x35,0xdc], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(testData.counter, d1, payloads, True, 0, d2, 0, testData, packet)) 

    def test_005_TM05_04_high_severity_anomaly_report_verification_full_roll_over(self):
        testData = self.testData[4]                        
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x35,0xdc], dtype=numpy.uint8)
        
        meta = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(6))
        
        in_pdu = pmt.cons(meta, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        for i in range (0, testData.counter):
            eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0x35,0xdc], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(testData.counter, d1, payloads, True, 0, d2, 0, testData, packet))         
        
    def test_006_TC05_05_invalid_numEvents_field_shorter(self):
        testData = self.testData[5]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_TC05_05_invalid_eventID_field_shorter(self):
        testData = self.testData[6]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_TC05_05_invalid_eventID_field_larger(self):
        testData = self.testData[7]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_TC05_05_invalid_eventID_non_exists(self):
        testData = self.testData[8]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x02, 0x00, 0x08], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_010_TC05_06_invalid_numEvents_field_shorter(self):
        testData = self.testData[9]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_011_TC05_06_invalid_eventID_field_shorter(self):
        testData = self.testData[10]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_012_TC05_06_invalid_eventID_field_larger(self):
        testData = self.testData[11]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_013_TC05_06_invalid_eventID_non_exists(self):
        testData = self.testData[12]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x03, 0x00, 0x02, 0x00, 0x05, 0x00, 0x08], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_014_TC05_07_invalid_parameter_longest(self):
        testData = self.testData[13]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_015_TC05_05and06and07_enable_disable_report_test(self):
        
        # Report List of disble Events
        testData = self.testData[14]
                
        eventReportService = pus.EventReportService("../../../examples/init_eventreport.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0, 3, 0, 1, 0, 2, 0, 3], dtype=numpy.uint8)

        payloads = [expected_response_0]
       
        self.assertTrue(checkResults(1, d1, payloads, False, 3, d2, 0, testData, packet))

        # Trigger Event #0
        testData = self.testData[15]           
  
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d3, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d4, 'store'))
        
        packet_event = numpy.array([0x01,0x14], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(0))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0x01,0x14], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d3, payloads, False, 0, d4, 0, testData, packet))  

        # Trigger Event #4
        testData = self.testData[16]           
 
        d5 = blocks.message_debug()
        d6 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d5, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d6, 'store'))
        
        packet_event = numpy.array([0x41,0xf3], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0x41,0xf3], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d5, payloads, False, 0, d6, 0, testData, packet))  

        # Trigger Event #5
        testData = self.testData[17]           
        d7 = blocks.message_debug()
        d8 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d7, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d8, 'store'))
        
        packet_event = numpy.array([0x2f,0x35], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0x2f,0x35], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d7, payloads, False, 0, d8, 0, testData, packet))           

        # Trigger Event #6
        testData = self.testData[18]           
        d9 = blocks.message_debug()
        d10 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d9, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d10, 'store'))
        
        packet_event = numpy.array([0xfe,0xab], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(6))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0xfe,0xab], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d9, payloads, False, 0, d10, 0, testData, packet))  
        
        # Disable Events 0, 5, 6
        testData = self.testData[19]

        d11 = blocks.message_debug()
        d12 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d11, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d12, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x03, 0x00, 0x05, 0x00, 0x00, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        payloads = []
        self.assertTrue(checkResults(0, d11, payloads, False, 3, d12, 0, testData, packet))  

        # Report List of disble Events
        testData = self.testData[14]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0, 6, 0, 0, 0, 1, 0, 2, 0, 3, 0, 5, 0, 6], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        testData.counter_sec_offset = 1
        
        self.assertTrue(checkResults(1, d1, payloads, False, 3, d2, 0, testData, packet))

        # Trigger Event #0
        testData = self.testData[15]           
  
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d3, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d4, 'store'))
        
        packet_event = numpy.array([0x01,0x14], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(0))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d3.num_messages() == 0)
        self.assertTrue(d4.num_messages() == 0)
                
        # Trigger Event #4
        testData = self.testData[16]           
 
        d5 = blocks.message_debug()
        d6 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d5, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d6, 'store'))
        
        packet_event = numpy.array([0x41,0xf3], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        testData.counter_sec_offset = 1
        
        expected_response_0 = numpy.array([0x41,0xf3], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d5, payloads, False, 0, d6, 0, testData, packet))  

        # Trigger Event #5
        testData = self.testData[17]           
        d7 = blocks.message_debug()
        d8 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d7, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d8, 'store'))
        
        packet_event = numpy.array([0x2f,0x35], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d7.num_messages() == 0)
        self.assertTrue(d8.num_messages() == 0)     

        # Trigger Event #6
        testData = self.testData[18]           
        d9 = blocks.message_debug()
        d10 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d9, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d10, 'store'))
        
        packet_event = numpy.array([0xfe,0xab], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(6))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d9.num_messages() == 0)
        self.assertTrue(d10.num_messages() == 0)

        # Enable Events 0, 6
        testData = self.testData[20]

        d11 = blocks.message_debug()
        d12 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d11, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d12, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        payloads = []
        self.assertTrue(checkResults(0, d11, payloads, False, 3, d12, 0, testData, packet))  

        # Report List of disble Events
        testData = self.testData[14]
                
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0, 4, 0, 1, 0, 2, 0, 3, 0, 5], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        testData.counter_sec_offset = 2
        
        self.assertTrue(checkResults(1, d1, payloads, False, 3, d2, 0, testData, packet))

        # Trigger Event #0
        testData = self.testData[15]           
  
        d3 = blocks.message_debug()
        d4 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d3, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d4, 'store'))
        
        packet_event = numpy.array([0x01,0x14], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(0))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        testData.counter_sec_offset = 1
        
        expected_response_0 = numpy.array([0x01,0x14], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d3, payloads, False, 0, d4, 0, testData, packet))  
                
        # Trigger Event #4
        testData = self.testData[16]           
 
        d5 = blocks.message_debug()
        d6 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d5, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d6, 'store'))
        
        packet_event = numpy.array([0x41,0xf3], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        testData.counter_sec_offset = 2
        
        expected_response_0 = numpy.array([0x41,0xf3], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d5, payloads, False, 0, d6, 0, testData, packet))  

        # Trigger Event #5
        testData = self.testData[17]           
        d7 = blocks.message_debug()
        d8 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d7, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d8, 'store'))
        
        packet_event = numpy.array([0x2f,0x35], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d7.num_messages() == 0)
        self.assertTrue(d8.num_messages() == 0)     

        # Trigger Event #6
        testData = self.testData[18]           
        d9 = blocks.message_debug()
        d10 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventReportService, 'out'), (d9, 'store'))
        self.tb.msg_connect((eventReportService, 'ver'), (d10, 'store'))
        
        packet_event = numpy.array([0xfe,0xab], dtype=numpy.uint8)
        
        meta_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(6))
        
        in_pdu_event = pmt.cons(meta_event, pmt.init_u8vector(packet_event.size, packet_event))
        
        self.tb.start()
        eventReportService.to_basic_block()._post(pmt.intern("rid"), in_pdu_event)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        testData.counter_sec_offset = 1
        
        expected_response_0 = numpy.array([0xfe,0xab], dtype=numpy.uint8)

        payloads = [expected_response_0]
        
        self.assertTrue(checkResults(1, d9, payloads, False, 0, d10, 0, testData, packet))  
        
def checkResults(numd1, d1, payloads, repeatPayload, numd2, d2, num_progress, testData, packet):

    if d1.num_messages() != numd1:
        return False
 
    if d2.num_messages() != numd2:
        return False
 
    for i in range (0, testData.counter):
        h = i        
     
        if len(payloads) > 0:
            for j in range (0, len(payloads)):
    
                response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(i))), dtype=numpy.uint8)

                if not checkPrimaryHeader(testData.apid, testData.messageSize, j+i, response, testData.counter_offset):
                    return False           

                if not checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, j+i, response, testData.counter_sec_offset):
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
    gr_unittest.run(qa_EventReportService, "qa_EventReportService.xml" )
