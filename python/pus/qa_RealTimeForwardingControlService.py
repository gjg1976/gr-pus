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
        
class qa_RealTimeForwardingControlService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x0e, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x0e, 0x01, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x0e, 0x01, 0x00, -1, 1, 0x19, 0, 55, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x0e, 0x02, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x0e, 0x02, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x0e, 0x02, 0x00, -1, 1, 0x19, 0, 57, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x0e, 0x02, 0x00, -1, 1, 0x19, 0, 56, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x0e, 0x02, 0x00, -1, 1, 0x19, 0, 56, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x0e, 0x03, 0x00, -1, 1, 0x19, 0, 1, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x0e, 0x03, 0x04, -1, 1, 0x19, 15, 1, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x0e, 0x01, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #10
        self.testData.append(test_data(0x0e, 0x03, 0x04, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #11
        self.testData.append(test_data(0x0e, 0x02, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x0e, 0x02, 0x00, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #13
                                        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.RealTimeForwardingControlService("")

    def test_001_ST14_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))
        
        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x04, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x0e, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(d3.num_messages() == 0)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST14_01_invalid_num_app_shorter(self):
        testData = self.testData[0]                        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST14_01_invalid_appID_shorter(self):
        testData = self.testData[0]                        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST14_01_invalid_num_services_shorter(self):
        testData = self.testData[0]                        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
              
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST14_01_invalid_services_shorter(self):
        testData = self.testData[0]                        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_006_ST14_01_invalid_num_subtype_shorter(self):
        testData = self.testData[0]                        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x0a, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_ST14_01_invalid_subtype_shorter(self):
        testData = self.testData[0]                        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x0a, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                  
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_ST14_01_invalid_subtype_longer(self):
        testData = self.testData[1]                        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x02, 0x0a, 0x25, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_009_ST14_01_invalid_service_non_exist(self):
        testData = self.testData[2]                        

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x02, 0x03, 0x00, 0x02, 0x0a, 0x25, 0x1f, 0x00, 0x01, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_010_ST14_02_invalid_num_app_shorter(self):
        testData = self.testData[3]                        

        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_011_ST14_02_invalid_appID_shorter(self):
        testData = self.testData[3]                        
 
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_012_ST14_02_invalid_num_services_shorter(self):
        testData = self.testData[3]                        
   
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
              
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_013_ST14_02_invalid_services_shorter(self):
        testData = self.testData[3]                        

        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST14_02_invalid_num_subtype_shorter(self):
        testData = self.testData[3]                        

        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x0a, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_015_ST14_02_invalid_subtype_shorter(self):
        testData = self.testData[3]                        

        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x0a, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                  
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_016_ST14_02_invalid_subtype_longer(self):
        testData = self.testData[4]                        

        realTimeForwardingControlService = pus.RealTimeForwardingControlService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x02, 0x0a, 0x25, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_017_ST14_02_invalid_appID_non_exist(self):
        testData = self.testData[5]                        

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x18, 0x00, 0x02, 0x03, 0x00, 0x02, 0x0a, 0x25, 0x1f, 0x00, 0x01, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_018_ST14_02_invalid_service_non_exist(self):
        testData = self.testData[6]                        

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x1f, 0x00, 0x02, 0x0a, 0x25], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_019_ST14_02_invalid_subservice_non_exist(self):
        testData = self.testData[7]                        

        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x02, 0x0a, 0xef], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_020_ST14_03_invalid_subtype_longer(self):
        testData = self.testData[8]                        
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(d3.num_messages() == 0) 
        
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_021_ST14_03_valid_request(self):
        testData = self.testData[9]                        
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d3.num_messages() == 0) 
    
        expected_response_0 = numpy.array([0, 2, 0, 25, 0, 1, 3, 0, 1, 10, 0, 3, 0, 1, 3, 0, 4, 1, 2, 5, 9], dtype=numpy.uint8)      
        payloads = [expected_response_0]
      
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))

    def test_022_ST14_valid_forward(self):
        testData = self.testData[9]                        
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x08, 0x19, 0xc0 ,0x00, 0x00, 0x32, 0x20, 0x03, 0x0a, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 2, 0, 255, 255, 0, 7, 0, 5, 0, 1, 0, 16, 0, 34, 0, 11, 0, 31, 0, 127, 0, 3, 4, 3, 0, 17, 0, 9, 0, 3, 5, 1, 0, 15, 10, 1, 0, 98, 0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 1) 
    
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
          
        self.assertTrue(numpy.array_equal(response, packet))

    def test_023_ST14_invalid_forward_appID(self):
        testData = self.testData[9]                        
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x08, 0x18, 0xc0 ,0x00, 0x00, 0x0c, 0x20, 0x03, 0x0a, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 2, 0, 255, 255, 0, 7, 0, 5, 0, 1, 0, 16, 0, 34, 0, 11, 0, 31, 0, 127, 0, 3, 4, 3, 0, 17, 0, 9, 0, 3, 5, 1, 0, 15, 10, 1, 0, 98, 0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 0) 

    def test_024_ST14_invalid_forward_service(self):
        testData = self.testData[9]                        
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([8, 25, 192, 0, 1, 16, 32, 13, 1, 0, 0, 0, 0, 82, 213, 50, 140, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5,253, 254, 255, 0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 0) 

    def test_025_ST14_invalid_forward_subtype(self):
        testData = self.testData[9]                        
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x08, 0x19, 0xc0 ,0x00, 0x00, 0x0c, 0x20, 0x03, 0x23, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 2,4,0,0,50,7,1,0,80,0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 0)

    def test_026_ST14_01and02and03and04_add_report_fwd_del(self):
        # ------------------------------------------------------------
        # Add TC[14,01]
        # ------------------------------------------------------------   
        testData = self.testData[10]                        
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        housekeepingService = pus.HousekeepingService("../../../examples/init_hk.json")
        largePacketTransferService = pus.LargePacketTransferService()       
        realTimeForwardingControlService = pus.RealTimeForwardingControlService("../../../examples/init_rtforward.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x02, 0x03, 0x00, 0x01, 0x23, 0x0d, 0x00, 0x01, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
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
        # Report interval TC[14,03] -> TM[14,04]
        # ------------------------------------------------------------   

        testData = self.testData[11]                        
        d2 = blocks.message_debug()

        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d3.num_messages() == 0) 
    
        expected_response_0 = numpy.array([0, 2, 0, 25, 0, 2, 3, 0, 2, 10, 35, 13, 0, 1, 1, 0, 3, 0, 1, 3, 0, 4, 1, 2, 5, 9], dtype=numpy.uint8)      
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Forward TM[13,01]
        # ------------------------------------------------------------   

        packet = numpy.array([8, 25, 192, 0, 0, 25, 32, 13, 1, 0, 0, 0, 0, 82, 213, 50, 140, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5,253, 254, 255, 0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 1) 
    
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
          
        self.assertTrue(numpy.array_equal(response, packet))

        # ------------------------------------------------------------
        # Forward TM[03,35]
        # ------------------------------------------------------------   

        packet = numpy.array([0x08, 0x19, 0xc0 ,0x00, 0x00, 0x15, 0x20, 0x03, 0x23, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 2,4,0,0,50,7,1,0,80,0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 2) 
    
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(1))), dtype=numpy.uint8)
          
        self.assertTrue(numpy.array_equal(response, packet))

        # ------------------------------------------------------------
        # Delete TC[14,02]
        # ------------------------------------------------------------   
        testData = self.testData[12]                        

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x03, 0x00, 0x01, 0x23], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
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
        # Report interval TC[14,03] -> TM[14,04]
        # ------------------------------------------------------------   

        testData = self.testData[11]                        
        d2 = blocks.message_debug()

        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d3.num_messages() == 0) 
    
        expected_response_0 = numpy.array([0, 2, 0, 25, 0, 2, 3, 0, 1, 10, 13, 0, 1, 1, 0, 3, 0, 1, 3, 0, 4, 1, 2, 5, 9], dtype=numpy.uint8)      
        payloads = [expected_response_0]
        
        testData.counter_offset = 1
        testData.counter_sec_offset = counter_sec_offset = 1  
         
        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Forward TM[13,01]
        # ------------------------------------------------------------   

        packet = numpy.array([8, 25, 192, 0, 0, 25, 32, 13, 1, 0, 0, 0, 0, 82, 213, 50, 140, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5,253, 254, 255, 0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 1) 
    
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
          
        self.assertTrue(numpy.array_equal(response, packet))

        # ------------------------------------------------------------
        # Forward TM[03,35]
        # ------------------------------------------------------------   

        packet = numpy.array([0x08, 0x19, 0xc0 ,0x00, 0x00, 0x0c, 0x20, 0x03, 0x23, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 2,4,0,0,50,7,1,0,80,0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 1) 

        # ------------------------------------------------------------
        # Delete TC[14,02]
        # ------------------------------------------------------------   
        testData = self.testData[13]                        

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()

        self.tb.msg_connect((realTimeForwardingControlService, 'out'), (d1, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((realTimeForwardingControlService, 'fwd'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x19, 0x00, 0x01, 0x0d, 0x00, 0x01, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 0)
        self.assertTrue(d3.num_messages() == 0) 
        
        # ------------------------------------------------------------
        # Report interval TC[14,03] -> TM[14,04]
        # ------------------------------------------------------------   

        testData = self.testData[11]                        
        d2 = blocks.message_debug()

        self.tb.msg_connect((realTimeForwardingControlService, 'ver'), (d2, 'store'))
        packet = numpy.array([0x18, 0x03, 0x1b, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                 
        self.assertTrue(d3.num_messages() == 0) 
    
        expected_response_0 = numpy.array([0, 2, 0, 25, 0, 1, 3, 0, 1, 10, 0, 3, 0, 1, 3, 0, 4, 1, 2, 5, 9], dtype=numpy.uint8)      
        payloads = [expected_response_0]
        
        testData.counter_offset = 2
        testData.counter_sec_offset = counter_sec_offset = 2  
         
        self.assertTrue(checkResults(1, d1, payloads, 0, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Forward TM[13,01]
        # ------------------------------------------------------------   

        packet = numpy.array([8, 25, 192, 0, 1, 16, 32, 13, 1, 0, 0, 0, 0, 82, 213, 50, 140, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5,253, 254, 255, 0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 0) 

        # ------------------------------------------------------------
        # Forward TM[03,35]
        # ------------------------------------------------------------   

        packet = numpy.array([0x08, 0x19, 0xc0 ,0x00, 0x00, 0x0c, 0x20, 0x03, 0x23, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xfe, 0xfe, 0xfe, 2,4,0,0,50,7,1,0,80,0xee, 0xaa], dtype=numpy.uint8)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        realTimeForwardingControlService.to_basic_block()._post(pmt.intern("in_msg"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 1) 
        self.assertTrue(d2.num_messages() == 0)                          
        self.assertTrue(d3.num_messages() == 0)     
                                                                                                                        
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
    gr_unittest.run(qa_RealTimeForwardingControlService, "qa_RealTimeForwardingControlService.xml" )
