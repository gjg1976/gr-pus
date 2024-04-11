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
        
class qa_EventActionService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x13, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x13, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x13, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x13, 0x01, 0x00, -1, 1, 0x19, 15, 2, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x13, 0x02, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x13, 0x02, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x13, 0x02, 0x00, -1, 1, 0x19, 15, 4, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x13, 0x02, 0x00, -1, 1, 0x19, 15, 3, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x13, 0x03, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x13, 0x04, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x13, 0x04, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x13, 0x04, 0x00, -1, 1, 0x19, 15, 4, 0, True, 0, 0)) #11
        self.testData.append(test_data(0x13, 0x04, 0x00, -1, 1, 0x19, 15, 4, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x13, 0x05, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #13
        self.testData.append(test_data(0x13, 0x05, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #14
        self.testData.append(test_data(0x13, 0x05, 0x00, -1, 1, 0x19, 15, 4, 0, True, 0, 0)) #15
        self.testData.append(test_data(0x13, 0x05, 0x00, -1, 1, 0x19, 15, 4, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x13, 0x08, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #17
        self.testData.append(test_data(0x13, 0x09, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #18        
        self.testData.append(test_data(0x13, 0x06, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #19     
        self.testData.append(test_data(0x13, 0x06, 0x07, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #20           
        self.testData.append(test_data(0x13, 0x0a, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #21
        self.testData.append(test_data(0x13, 0x0a, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #22
        self.testData.append(test_data(0x13, 0x0a, 0x0b, -1, 1, 0x19, 15, 4, 0, True, 0, 0)) #23
        self.testData.append(test_data(0x13, 0x0a, 0x0b, -1, 1, 0x19, 15, 4, 0, True, 0, 0)) #24
        self.testData.append(test_data(0x13, 0x06, 0x07, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #25  
        self.testData.append(test_data(0x13, 0x04, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #26
        self.testData.append(test_data(0x13, 0x05, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #27
        self.testData.append(test_data(0x13, 0x09, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #28
        self.testData.append(test_data(0x13, 0x08, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #29
        self.testData.append(test_data(0x13, 0x06, 0x07, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #30  
        self.testData.append(test_data(0x13, 0x03, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #31
        self.testData.append(test_data(0x13, 0x06, 0x07, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #32 
        self.testData.append(test_data(0x13, 0x01, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #33
        self.testData.append(test_data(0x13, 0x04, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #34
        self.testData.append(test_data(0x13, 0x0a, 0x0b, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #35
        self.testData.append(test_data(0x13, 0x02, 0x00, -1, 1, 0x19, 0, 3, 0, True, 0, 0)) #36
        self.testData.append(test_data(0x13, 0x05, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #37
        self.testData.append(test_data(0x13, 0x02, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #38
        self.testData.append(test_data(0x13, 0x0a, 0x0b, -1, 1, 0x19, 0, 4, 0, True, 0, 0)) #39
                                                                                                                                                        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.EventActionService("")

    def test_001_ST19_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        eventActionService = pus.EventActionService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x04, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x13, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4)) 

    def test_002_ST19_Event_no_and_wrong_metadata(self):
        testData = self.testData[0]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([], dtype=numpy.uint8)
        in_pdu_noMeta = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        wrong_meta_type = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_float(12.1))
        in_pdu_wrongMetaType = pmt.cons(wrong_meta_type, pmt.init_u8vector(packet.size, packet))

        wrong_meta_data = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(8))
        in_pdu_wrongMetaData = pmt.cons(wrong_meta_data, pmt.init_u8vector(packet.size, packet))
                
        packet = numpy.array([0x00, 0x08], dtype=numpy.uint8)
        meta_non_existing_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        in_pdu_MetaNonExistingEvent = pmt.cons(meta_non_existing_event, pmt.init_u8vector(packet.size, packet))

        packet = numpy.array([0x00, 0x01], dtype=numpy.uint8)
        meta_disable_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        in_pdu_MetaDisableEvent = pmt.cons(meta_disable_event, pmt.init_u8vector(packet.size, packet))

        packet = numpy.array([0x00, 0x07], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(0))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_noMeta) 
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_wrongMetaType) 
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_wrongMetaData)
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaNonExistingEvent)
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaDisableEvent)
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)

    def test_003_ST19_low_severity_execute_Action(self):
        testData = self.testData[0]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x00, 0x07], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 1)

        expectedEventAction = numpy.array([0x18,0x14,0xc0,0x00,0x00,0x07,0x20,0x03,0x1b,0x00,0x00,0x02,0x01,0x04], dtype=numpy.uint8)

        responseEventAction =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(expectedEventAction, responseEventAction))

    def test_004_ST19_medium_severity_execute_Action(self):
        testData = self.testData[0]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x00, 0x07], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 1)

        expectedEventAction = numpy.array([0x18,0x14,0xc0,0x00,0x00,0x07,0x20,0x03,0x1b,0x00,0x00,0x02,0x01,0x04], dtype=numpy.uint8)

        responseEventAction =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(expectedEventAction, responseEventAction))

    def test_005_ST19_high_severity_execute_Action(self):
        testData = self.testData[0]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x00, 0x0f], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(6))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 1)

        expectedEventAction = numpy.array([0x18,0x14,0xc0,0x00,0x00,0x07,0x20,0x03,0x1b,0x00,0x00,0x02,0x01,0x04], dtype=numpy.uint8)
        responseEventAction =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(expectedEventAction, responseEventAction))


    def test_006_ST19_01_invalid_numEvents_field_shorter(self):
        testData = self.testData[1]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_ST19_01_invalid_appID_field_shorter(self):
        testData = self.testData[1]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_ST19_01_invalid_eventID_field_shorter(self):
        testData = self.testData[1]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_009_ST19_01_invalid_request_field_shorter(self):
        testData = self.testData[1]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x07, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_010_ST19_01_invalid_request_field_longer(self):
        testData = self.testData[2]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x07, 0x18,0x17,0xc0,0x00,0x00,0x07,0x20,0x03,0x1b,0x00,0x00,0x02,0x01,0x04, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  
            
    def test_011_ST19_01_invalid_event_enabled(self):
        testData = self.testData[3]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 0x19, 0x00, 0x03, 0x18,0x17, 0xc0, 0x00, 0x00, 0x07,0x20,0x03,0x1b,0x00,0x00,0x02,0x01,0x04, 0x00, 0x19, 0x00, 0x07, 0x18,0x17,0xc0,0x00,0x00,0x07,0x20,0x03,0x19,0x00,0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))                       

    def test_012_ST19_02_invalid_numEvents_field_shorter(self):
        testData = self.testData[4]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_013_ST19_02_invalid_appID_field_shorter(self):
        testData = self.testData[4]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST19_02_invalid_eventID_field_shorter(self):
        testData = self.testData[4]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_015_ST19_02_invalid_request_field_longer(self):
        testData = self.testData[5]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x07, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error)) 

    def test_016_ST19_02_invalid_appID_non_exist(self):
        testData = self.testData[6]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x06, 0x00, 0x19, 0x00, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    
        
    def test_017_ST19_02_invalid_eventID_non_exist(self):
        testData = self.testData[6]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x04, 0x00, 20, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    

    def test_018_ST19_02_invalid_event_enabled(self):
        testData = self.testData[7]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x07, 0x00, 20, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    
        
    def test_019_ST19_03_invalid_field_longer(self):
        testData = self.testData[8]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_020_ST19_04_invalid_numEvents_field_shorter(self):
        testData = self.testData[9]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_021_ST19_04_invalid_appID_field_shorter(self):
        testData = self.testData[9]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_022_ST19_04_invalid_eventID_field_shorter(self):
        testData = self.testData[9]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_023_ST19_04_invalid_request_field_longer(self):
        testData = self.testData[10]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x07, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error)) 

    def test_024_ST19_04_invalid_appID_non_exist(self):
        testData = self.testData[11]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x06, 0x00, 0x19, 0x00, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))       

    def test_025_ST19_04_invalid_eventID_non_exist(self):
        testData = self.testData[12]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x04, 0x00, 20, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    
        
    def test_026_ST19_05_invalid_numEvents_field_shorter(self):
        testData = self.testData[13]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_027_ST19_05_invalid_appID_field_shorter(self):
        testData = self.testData[13]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_028_ST19_05_invalid_eventID_field_shorter(self):
        testData = self.testData[13]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_029_ST19_05_invalid_request_field_longer(self):
        testData = self.testData[14]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x07, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error)) 

    def test_030_ST19_05_invalid_appID_non_exist(self):
        testData = self.testData[15]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x06, 0x00, 0x19, 0x00, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    

    def test_031_ST19_05_invalid_eventID_non_exist(self):
        testData = self.testData[16]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x04, 0x00, 20, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    

    def test_032_ST19_08_invalid_field_longer(self):
        testData = self.testData[17]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_033_ST19_09_invalid_field_longer(self):
        testData = self.testData[18]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_034_ST19_06_invalid_field_longer(self):
        testData = self.testData[19]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_035_ST19_06_valid_request(self):
        testData = self.testData[20]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,6,0,20,0,1,0,0,20,0,3,0,0,20,0,6,0,0,20,0,7,1,0,20,0,10,1,0,20,0,15,1], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 1, 3, d2, 0, testData, packet))

    def test_036_ST19_10_invalid_numEvents_field_shorter(self):
        testData = self.testData[21]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_037_ST19_10_invalid_appID_field_shorter(self):
        testData = self.testData[21]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_038_ST19_10_invalid_eventID_field_shorter(self):
        testData = self.testData[21]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_039_ST19_10_invalid_request_field_longer(self):
        testData = self.testData[22]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x07, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error)) 

    def test_040_ST19_10_invalid_appID_non_exist(self):
        testData = self.testData[23]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x06, 0x00, 0x19, 0x00, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    

    def test_041_ST19_10_invalid_eventID_non_exist(self):
        testData = self.testData[24]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x02, 0x00, 20, 0x00, 0x04, 0x00, 20, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    

    def test_042_ST19_06and04and05_report_trigger_enable_disable(self):
        #------------------------------------
        #   report event status
        #------------------------------------  
        testData = self.testData[25]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,6,0,20,0,1,0,0,20,0,3,0,0,20,0,6,0,0,20,0,7,1,0,20,0,10,1,0,20,0,15,1], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 1, 0, d2, 0, testData, packet))

        #------------------------------------
        #   trigger medium disable Event
        #------------------------------------        
        
        packet = numpy.array([0x00, 0x06], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)

        #------------------------------------
        #   Enable Event
        #------------------------------------  

        testData = self.testData[26]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))    
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        #------------------------------------
        #   report event status
        #------------------------------------  
        testData = self.testData[25]                        
        d4 = blocks.message_debug()
        d5 = blocks.message_debug()
        self.tb.msg_connect((eventActionService, 'out'), (d4, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d5, 'store'))
                        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,6,0,20,0,1,0,0,20,0,3,0,0,20,0,6,1,0,20,0,7,1,0,20,0,10,1,0,20,0,15,1], dtype=numpy.uint8)

        payloads = [expected_response_0]
        testData.counter_sec_offset = 1 
        testData.counter_offset = 1   

        self.assertTrue(checkResults(1, d4, payloads, 1, 0, d5, 0, testData, packet))

        #------------------------------------
        #   trigger medium disable Event
        #------------------------------------        
        
        packet = numpy.array([0x00, 0x06], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 2)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 1)

        expectedEventAction = numpy.array([0x18,0x14,0xc0,0x00,0x00,0x07,0x20,0x03,0x1f,0x00,0x00,0x02,0x01,0x04], dtype=numpy.uint8)
        responseEventAction =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(expectedEventAction, responseEventAction))

        #------------------------------------
        #   Disable Event
        #------------------------------------  

        testData = self.testData[27]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x06], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 2)
        self.assertTrue(d2.num_messages() == 6)
        self.assertTrue(d3.num_messages() == 1)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(3), packet))    
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(4), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(5), packet)) 

        #------------------------------------
        #   report event status
        #------------------------------------  
        testData = self.testData[25]                        

        d6 = blocks.message_debug()
        d7 = blocks.message_debug()
        self.tb.msg_connect((eventActionService, 'out'), (d6, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d7, 'store'))  
              
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,6,0,20,0,1,0,0,20,0,3,0,0,20,0,6,0,0,20,0,7,1,0,20,0,10,1,0,20,0,15,1], dtype=numpy.uint8)

        payloads = [expected_response_0]
        testData.counter_sec_offset = 2 
        testData.counter_offset = 2

        self.assertTrue(checkResults(1, d6, payloads, 1, 0, d7, 0, testData, packet))

        #------------------------------------
        #   trigger medium disable Event
        #------------------------------------        
        
        packet = numpy.array([0x00, 0x06], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(5))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 6)
        self.assertTrue(d3.num_messages() == 1)

    def test_043_ST19_08and09_enable_disable_service(self):
        #------------------------------------
        #   Disable Service
        #------------------------------------  

        testData = self.testData[28]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))    
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        #------------------------------------
        #   trigger low disable Event
        #------------------------------------        
        
        packet = numpy.array([0x00, 0x07], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)

        #------------------------------------
        #   Enable Service
        #------------------------------------  

        testData = self.testData[29]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 6)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(3), packet))    
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(4), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(5), packet)) 

        #------------------------------------
        #   trigger low disable Event
        #------------------------------------        
        
        packet = numpy.array([0x00, 0x07], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(4))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 6)
        self.assertTrue(d3.num_messages() == 1)

        expectedEventAction = numpy.array([0x18,0x14,0xc0,0x00,0x00,0x07,0x20,0x03,0x1b,0x00,0x00,0x02,0x01,0x04], dtype=numpy.uint8)
        responseEventAction =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(expectedEventAction, responseEventAction))

    def test_044_ST19_06and03_report_delete_all(self):
        #------------------------------------
        #   report event status
        #------------------------------------  
        testData = self.testData[30]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,6,0,20,0,1,0,0,20,0,3,0,0,20,0,6,0,0,20,0,7,1,0,20,0,10,1,0,20,0,15,1], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 1, 0, d2, 0, testData, packet))

        #------------------------------------
        #   Delete All
        #------------------------------------  

        testData = self.testData[31]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 0)
                        
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))    
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet)) 

        #------------------------------------
        #   report event status
        #------------------------------------  
        testData = self.testData[30]                        
  
        d4 = blocks.message_debug()
        d5 = blocks.message_debug()
        self.tb.msg_connect((eventActionService, 'out'), (d4, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d5, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,0], dtype=numpy.uint8)

        payloads = [expected_response_0]
        testData.counter_sec_offset = 1 
        testData.counter_offset = 1   

        self.assertTrue(checkResults(1, d4, payloads, 1, 0, d5, 0, testData, packet))

    def test_045_ST19_06and01and10_report_add_delete(self):
        #------------------------------------
        #   report event status
        #------------------------------------  
        testData = self.testData[32]                        
        eventActionService = pus.EventActionService("../../../examples/init_eventaction.json")    
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((eventActionService, 'out'), (d1, 'store'))
        self.tb.msg_connect((eventActionService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((eventActionService, 'action'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,6,0,20,0,1,0,0,20,0,3,0,0,20,0,6,0,0,20,0,7,1,0,20,0,10,1,0,20,0,15,1], dtype=numpy.uint8)

        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 1, 0, d2, 0, testData, packet))

        #------------------------------------
        #   Add definition
        #------------------------------------  

        testData = self.testData[33]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x04, 0x18,0x17, 0xc0, 0x00, 0x00, 0x07,0x20,0x03,0xaf,0x00,0x00,0x02,0x01,0x04 ], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)

        #------------------------------------
        #   Enable Event
        #------------------------------------  

        testData = self.testData[34]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x04], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)
                        
        #------------------------------------
        #   report event status
        #------------------------------------  
        testData = self.testData[32]                        
  
        d4 = blocks.message_debug()
        self.tb.msg_connect((eventActionService, 'out'), (d4, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0,7,0,20,0,1,0,0,20,0,3,0,0,20,0,4,1,0,20,0,6,0,0,20,0,7,1,0,20,0,10,1,0,20,0,15,1], dtype=numpy.uint8)

        payloads = [expected_response_0]
        testData.counter_sec_offset = 1 
        testData.counter_offset = 1
        self.assertTrue(checkResults(1, d4, payloads, 1, 0, d2, 0, testData, packet))

        #------------------------------------
        #   report event definition
        #------------------------------------  
        
        testData = self.testData[35]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x04], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0)

        expected_response_0 = numpy.array([1,0,20,0,4, 1, 0x18,0x14, 0xc0, 0x00, 0x00, 0x07,0x20,0x03,0xaf,0x00,0x00,0x02,0x01,0x04], dtype=numpy.uint8)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(2))), dtype=numpy.uint8)

        testData.counter_offset = 2
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkCRC(response))
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))                     

        #------------------------------------
        #   trigger high disable Event
        #------------------------------------        
        
        packet = numpy.array([0x00, 0x04], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(6))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 1)

        expectedEventAction = numpy.array([0x18,0x14, 0xc0, 0x00, 0x00, 0x07,0x20,0x03,0xaf,0x00,0x00,0x02,0x01,0x04], dtype=numpy.uint8)
        responseEventAction =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(expectedEventAction, responseEventAction))
        
        #------------------------------------
        #   Delete Event
        #------------------------------------          
        testData = self.testData[36]                        

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x04], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 1)
                        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error)) 

        #------------------------------------
        #   Disable Event
        #------------------------------------  

        testData = self.testData[37]                        
        
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x04], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 1)
        
        #------------------------------------
        #   Delete Event
        #------------------------------------          
        testData = self.testData[38]                        

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x04], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 1)
                        
        #------------------------------------
        #   report event definition
        #------------------------------------  
        testData = self.testData[39]                        
      
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01, 0x00, 20, 0x00, 0x04], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 4)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(d3.num_messages() == 1)

        expectedEventAction = numpy.array([0x00], dtype=numpy.uint8)
        responseEventAction =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(3))), dtype=numpy.uint8)

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error)) 

        self.assertTrue(checkPayload(expectedEventAction, responseEventAction, testData.crcEnabled))
                                       
        #------------------------------------
        #   trigger high disable Event
        #------------------------------------        
        
        packet = numpy.array([0x00, 0x04], dtype=numpy.uint8)
        meta_info_event = pmt.dict_add(pmt.make_dict(), pmt.intern("event"), pmt.from_long(6))
        in_pdu_MetaInfoEvent = pmt.cons(meta_info_event, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        eventActionService.to_basic_block()._post(pmt.intern("rid"), in_pdu_MetaInfoEvent)        
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 4)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(d3.num_messages() == 1)
   
                                                                                        
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
    gr_unittest.run(qa_EventActionService, "qa_EventActionService.xml" )
