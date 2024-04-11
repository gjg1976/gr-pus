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
        
class qa_OnBoardMonitoringService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x0c, 0x01, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x0c, 0x01, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x0c, 0x01, 0x00, 0x11, 1, 0x19, 15, 46, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x0c, 0x02, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x0c, 0x02, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x0c, 0x02, 0x00, 0x11, 1, 0x19, 15, 46, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x0c, 0x03, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x0c, 0x04, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x0c, 0x04, 0x00, 0x11, 1, 0x19, 0, 38, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x0c, 0x05, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #9
        self.testData.append(test_data(0x0c, 0x05, 0x00, 0x11, 1, 0x19, 0, 66, 0, True, 0, 0)) #10  
        self.testData.append(test_data(0x0c, 0x05, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #11  
        self.testData.append(test_data(0x0c, 0x05, 0x00, 0x11, 1, 0x19, 0, 9, 0, True, 0, 0)) #12  
        self.testData.append(test_data(0x0c, 0x05, 0x00, 0x11, 1, 0x19, 0, 68, 0, True, 0, 0)) #13  
        self.testData.append(test_data(0x0c, 0x06, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #14
        self.testData.append(test_data(0x0c, 0x06, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #15
        self.testData.append(test_data(0x0c, 0x06, 0x00, 0x11, 1, 0x19, 15, 46, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #17
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 0, 66, 0, True, 0, 0)) #18
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #19
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #20
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #21
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #22         
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #23
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #24        
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #25
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 0, 70, 0, True, 0, 0)) #26
        self.testData.append(test_data(0x0c, 0x08, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #27
        self.testData.append(test_data(0x0c, 0x08, 0x00, 0x11, 1, 0x19, 15, 46, 0, True, 0, 0)) #28
        self.testData.append(test_data(0x0c, 0x0d, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #29  
        self.testData.append(test_data(0x0c, 0x0a, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #30          
        self.testData.append(test_data(0x0c, 0x08, 0x09, -1, 1, 0x19, 15, 1, 0, True, 0, 0)) #31
        self.testData.append(test_data(0x0c, 0x0d, 0x0e, -1, 1, 0x19, 15, 1, 0, True, 0, 0)) #32  
        self.testData.append(test_data(0x0c, 0x06, 0x00, 0x11, 1, 0x19, 15, 69, 0, True, 0, 0)) #33
        self.testData.append(test_data(0x0c, 0x02, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #34
        self.testData.append(test_data(0x0c, 0x08, 0x09, -1, 1, 0x19, 15, 46, 0, True, 0, 0)) #35
        self.testData.append(test_data(0x0c, 0x06, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #36
        self.testData.append(test_data(0x0c, 0x01, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #37
        self.testData.append(test_data(0x0c, 0x08, 0x09, -1, 1, 0x19, 15, 46, 0, True, 0, 0)) #38
        self.testData.append(test_data(0x0c, 0x10, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #39
        self.testData.append(test_data(0x0c, 0x04, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #40
        self.testData.append(test_data(0x0c, 0x05, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #41  
        self.testData.append(test_data(0x0c, 0x08, 0x09, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #42
        self.testData.append(test_data(0x0c, 0x07, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #43
        self.testData.append(test_data(0x0c, 0x0f, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #44
        self.testData.append(test_data(0x0c, 0x04, 0x00, 0x11, 1, 0x19, 15, 38, 0, True, 0, 0)) #45
        self.testData.append(test_data(0x0c, 0x0a, 0x0b, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #46
        self.testData.append(test_data(0x0c, 0x00, 0x0c, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #47
        self.testData.append(test_data(0x0c, 0x03, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #48
        self.testData.append(test_data(0x0c, 0x03, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #49
                                                                                                        
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.OnBoardMonitoringService("")

    def test_001_ST12_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x03, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x0c, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST12_01_invalid_numPMON_field_shorter(self):
        testData = self.testData[0]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST12_01_invalid_PMON_field_shorter(self):
        testData = self.testData[0]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST12_01_invalid_PMON_field_longer(self):
        testData = self.testData[1]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_005_ST12_01_invalid_PMON_field_non_exists(self):
        testData = self.testData[2]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x02, 0x00, 0x05], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error))        
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))      
                      
    def test_006_ST12_02_invalid_numPMON_field_shorter(self):
        testData = self.testData[3]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_007_ST12_02_invalid_PMON_field_shorter(self):
        testData = self.testData[3]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_008_ST12_02_invalid_PMON_field_longer(self):
        testData = self.testData[4]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_009_ST12_02_invalid_PMON_field_non_exists(self):
        testData = self.testData[5]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x05, 0x00, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 4)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error))        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(2), packet, testData.error))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(3), packet))     

 
    def test_010_ST12_03_invalid_transistion_field_shorter(self):
        testData = self.testData[6]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_011_ST12_03_invalid_transistion_field_longer(self):
        testData = self.testData[6]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_012_ST12_04_invalid_data_field_longer(self):
        testData = self.testData[7]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_013_ST12_04_invalid_PMON_enabled(self):
        testData = self.testData[8]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json")

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_014_ST12_05_invalid_numDef_field_shorter(self):
        testData = self.testData[9]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))


    def test_015_ST12_05_invalid_PMONID_field_shorter(self):
        testData = self.testData[9]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_016_ST12_05_invalid_paramID_field_shorter(self):
        testData = self.testData[9]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_017_ST12_05_invalid_interval_field_shorter(self):
        testData = self.testData[9]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_018_ST12_05_invalid_repNum_field_shorter(self):
        testData = self.testData[9]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00, 0x0a, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_019_ST12_05_invalid_defType_field_unk(self):
        testData = self.testData[10]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00, 0x0a, 0x00, 0x05, 0x03], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_020_ST12_05_invalid_type0_data_field_shorter(self):
        testData = self.testData[11]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
    
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_021_ST12_05_invalid_type0_data_field_longer(self):
        testData = self.testData[11]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x00, 0xff, 0xff, 0xff, 0xff, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_022_ST12_05_invalid_type0_paramID_non_exist(self):
        testData = self.testData[12]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x07, 0x00, 0x0a, 0x00, 0x05, 0x00, 0xff, 0xff, 0xff, 0xff, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))      

    def test_023_ST12_05_invalid_type0_monDef_already_exist(self):
        testData = self.testData[13]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x00, 0x0a, 0x00, 0x05, 0x00, 0xff, 0xa0, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error)) 
        
    def test_024_ST12_05_invalid_type1_data_field_shorter(self):
        testData = self.testData[11]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_025_ST12_05_invalid_type1_data_field_longer(self):
        testData = self.testData[11]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x01, 0xff, 0xff, 0xff, 0xff, 0x00, 0x02, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))        

    def test_026_ST12_05_invalid_type1_monDef_already_exist(self):
        testData = self.testData[13]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x00, 0x0a, 0x00, 0x05, 0x01, 0xff, 0x00, 0x02, 0xa0, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))     
        
    def test_027_ST12_05_invalid_type2_data_field_shorter(self):
        testData = self.testData[11]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_028_ST12_05_invalid_type2_data_field_longer(self):
        testData = self.testData[11]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x02, 0xff, 0xff, 0xff, 0xff, 0x00, 0x02, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))      

    def test_029_ST12_05_invalid_type2_monDef_already_exist(self):
        testData = self.testData[13]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x05, 0x00, 0x05, 0x00, 0x0a, 0x00, 0x05, 0x02, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x02, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x05], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))    

    def test_030_ST12_06_invalid_numPMON_field_shorter(self):
        testData = self.testData[14]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_031_ST12_06_invalid_PMON_field_shorter(self):
        testData = self.testData[14]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_032_ST12_06_invalid_PMON_field_longer(self):
        testData = self.testData[15]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_033_ST12_06_invalid_PMON_field_non_exists(self):
        testData = self.testData[16]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x03, 0x00, 0x02, 0x00, 0x05, 0x00, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 4)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, 69))        
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(2), packet, testData.error))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(3), packet))     

    def test_034_ST12_07_invalid_numDef_field_shorter(self):
        testData = self.testData[17]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))


    def test_035_ST12_07_invalid_PMONID_field_shorter(self):
        testData = self.testData[17]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_036_ST12_07_invalid_paramID_field_shorter(self):
        testData = self.testData[17]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_037_ST12_07_invalid_repNum_field_shorter(self):
        testData = self.testData[17]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_038_ST12_07_invalid_defType_field_unk(self):
        testData = self.testData[18]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x01, 0x00, 0x05, 0x03], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_039_ST12_07_invalid_type0_data_field_shorter(self):
        testData = self.testData[19]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x09, 0x00, 0x05, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
    
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_040_ST12_07_invalid_type0_data_field_longer(self):
        testData = self.testData[20]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x09, 0x00, 0x05, 0x00, 0xff, 0xff, 0xff, 0xff, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))
        
    def test_041_ST12_07_type0_monDef_already_exist(self):
        testData = self.testData[21]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x00, 0x05, 0x00, 0xff, 0xa0, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))  
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))  
            
    def test_042_ST12_07_invalid_type1_data_field_shorter(self):
        testData = self.testData[22]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x09, 0x00, 0x05, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_043_ST12_07_invalid_type1_data_field_longer(self):
        testData = self.testData[22]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x09, 0x00, 0x05, 0x01, 0xff, 0xff, 0xff, 0xff, 0x00, 0x02, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))        

    def test_044_ST12_07_type1_monDef_already_exist(self):
        testData = self.testData[23]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x01, 0x00, 0x05, 0x01, 0xa0, 0x00, 0x02, 0xff, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))  
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))  
        
    def test_045_ST12_07_invalid_type2_data_field_shorter(self):
        testData = self.testData[24]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x02, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_046_ST12_07_invalid_type2_data_field_longer(self):
        testData = self.testData[24]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x05, 0x02, 0xff, 0xff, 0xff, 0xff, 0x00, 0x02, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))      

    def test_047_ST12_07_type2_monDef_already_exist(self):
        testData = self.testData[25]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x05, 0x00, 0x05, 0x00, 0x05, 0x02, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x02, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x05], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet))  
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))     

    def test_048_ST12_07_invalid_type0_monDef_already_exist(self):
        testData = self.testData[26]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                     
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02, 0x00, 0x03, 0x00, 0x05, 0x00, 0xff, 0xa0, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error)) 
        
    def test_049_ST12_08_invalid_numPMON_field_shorter(self):
        testData = self.testData[27]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_050_ST12_08_invalid_PMON_field_shorter(self):
        testData = self.testData[27]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_051_ST12_08_invalid_PMON_field_longer(self):
        testData = self.testData[27]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_052_ST12_08_invalid_PMON_field_non_exists(self):
        testData = self.testData[28]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x03, 0x00, 0x02, 0x00, 0x05, 0x00, 0x07], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
                                
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))     

    def test_053_ST12_13_invalid_data_field_longer(self):
        testData = self.testData[29]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_054_ST12_10_invalid_data_field_longer(self):
        testData = self.testData[30]
                
        onBoardMonitoringService = pus.OnBoardMonitoringService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))        

    def test_055_ST12_08and13and06and01and02and08and15and16_PMON_reports(self):
        # ------------------------------------------------------------
        # Report Def TC[12,08] -> TM[12,9]        
        # ------------------------------------------------------------      
        testData = self.testData[31]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        #parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        expected_response_0 = numpy.array([1, 44, 0, 5, 0, 2, 0, 1, 0, 10, 0, 0, 10, 0, 255, 10, 0, 1, 0, 3, 0, 1, 0, 20, 0, 0, 10, 1, 10, 0, 1, 15, 0, 2, 0, 5, 0, 5, 0, 10, 1, 0, 5, 2, 192, 65, 64, 0, 0, 0, 0, 0, 0, 7, 64, 49, 204, 204, 204, 204, 204, 205, 0, 6, 0, 3, 0, 6, 0, 5, 0, 10, 1, 0, 5, 1, 192, 68, 0, 0, 0, 0, 0, 0, 0, 7, 64, 49, 204, 204, 204, 204, 204, 205, 0, 6, 0, 34, 0, 34, 0, 10, 1, 0, 5, 1, 255, 246, 0, 15, 0, 15, 0, 25], dtype=numpy.uint8)

        payloads = [expected_response_0]
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))  

        # ------------------------------------------------------------
        # Report Def Status TC[12,13] -> TM[12,14]        
        # ------------------------------------------------------------ 
        
        testData = self.testData[32]
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0, 5, 0, 2, 0, 0, 3, 0, 0, 5, 1, 0, 6, 1, 0, 34, 1], dtype=numpy.uint8)

        payloads = [expected_response_0]
        testData.counter_offset = 1
        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))        

        # ------------------------------------------------------------
        # Delete Def TC[12,06]        
        # ------------------------------------------------------------ 
 
        testData = self.testData[33]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x05, 0x00, 0x03], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))      

        # ------------------------------------------------------------
        # Disable Def TC[12,06]        
        # ------------------------------------------------------------ 
        testData = self.testData[34]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x05], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))        
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))      
            
        # ------------------------------------------------------------
        # Report Def TC[12,08] -> TM[12,9]        
        # ------------------------------------------------------------      
        
        testData = self.testData[35]
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x05], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
            
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(1), packet, testData.error))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))   

        expected_response_0 = numpy.array([1, 44, 0, 1, 0, 5, 0, 5, 0, 10, 0, 0, 0, 2, 192, 65, 64, 0, 0, 0, 0, 0, 0, 7, 64, 49, 204, 204, 204, 204, 204, 205, 0, 6, 0, 3], dtype=numpy.uint8)

        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        testData.counter_offset = 2

        testData.counter_sec_offset = 1        
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))  
        # ------------------------------------------------------------
        # Delete Def TC[12,06]        
        # ------------------------------------------------------------ 
 
        testData = self.testData[33]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x05], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))      

        # ------------------------------------------------------------
        # Enable Def TC[12,01]        
        # ------------------------------------------------------------ 
        testData = self.testData[37]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))        
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))     


        # ------------------------------------------------------------
        # Report Def Status TC[12,13] -> TM[12,14]        
        # ------------------------------------------------------------ 
        
        testData = self.testData[32]
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0, 3, 0, 2, 1, 0, 6, 1, 0, 34, 1], dtype=numpy.uint8)

        payloads = [expected_response_0]
        testData.counter_offset = 3
        testData.counter_sec_offset = 1      

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))    

        # ------------------------------------------------------------
        # Disable Function TC[12,16]        
        # ------------------------------------------------------------ 
        testData = self.testData[39]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))        
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    

        # ------------------------------------------------------------
        # Delete All Def TC[12,04]        
        # ------------------------------------------------------------ 
 
        testData = self.testData[40]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))
        # ------------------------------------------------------------
        # Report Def TC[12,08] -> TM[12,9]        
        # ------------------------------------------------------------      
        
        testData = self.testData[42]
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
            
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)

        expected_response_0 = numpy.array([1, 44, 0, 0], dtype=numpy.uint8)
                                           
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        testData.counter_offset = 4
        testData.counter_sec_offset = 2        
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))  

        
        # ------------------------------------------------------------
        # Add Def TC[12,05]        
        # ------------------------------------------------------------ 
        
        testData = self.testData[41]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x05, 0x00, 0x05, 0x00, 0x0a, 0x00, 0x05, 0x02, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x02, 0xa0, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x05, 0x00, 0x01, 0x00, 32, 0x00, 0x0a, 0x00, 0x05, 0x00, 0xff, 0xff, 0x01, 0xef, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))

        # ------------------------------------------------------------
        # Report Def TC[12,08] -> TM[12,9]        
        # ------------------------------------------------------------      
        
        testData = self.testData[42]
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
            
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)

        expected_response_0 = numpy.array([1, 44, 0, 2, 0, 1, 0, 32, 0, 10, 0, 0, 5, 0, 255, 255, 1, 239, 0, 2, 0, 5, 0, 5, 0, 10, 0, 0, 5, 2, 255, 255, 255, 255, 255, 255, 255, 255, 0, 2, 160, 16, 0, 0, 0, 0, 0, 0, 0, 2, 0, 5], dtype=numpy.uint8)
                                                         
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        testData.counter_offset = 5
        testData.counter_sec_offset = 3        

        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))  

        # ------------------------------------------------------------
        # Mod Def TC[12,05]        
        # ------------------------------------------------------------ 
        
        testData = self.testData[43]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()


        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 32, 0x00, 0x0f, 0x01, 0x00, 0xa0, 0x00, 0x01, 0x0f, 0x00, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))   
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))

        # ------------------------------------------------------------
        # Report Def TC[12,08] -> TM[12,9]        
        # ------------------------------------------------------------      
        
        testData = self.testData[42]
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
            
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 0)

        expected_response_0 = numpy.array([1, 44, 0, 2, 0, 1, 0, 32, 0, 10, 0, 0, 15, 1, 0, 160, 0, 1, 15, 0, 0, 2, 0, 5, 0, 5, 0, 10, 0, 0, 5, 2, 255, 255, 255, 255, 255, 255, 255, 255, 0, 2, 160, 16, 0, 0, 0, 0, 0, 0, 0, 2, 0, 5], dtype=numpy.uint8)
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        testData.counter_offset = 6
        testData.counter_sec_offset = 4        
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))  

        # ------------------------------------------------------------
        # Enable Function TC[12,15]        
        # ------------------------------------------------------------ 
        testData = self.testData[44]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 3)

        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))        
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    

        # ------------------------------------------------------------
        # Delete All Def TC[12,04]        
        # ------------------------------------------------------------ 
        testData = self.testData[8]

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))

    def test_056_ST12_10and11_PMON_checks(self):
        testData_chg_trans = self.testData[49]
        testData = self.testData[46]
        testData_en = self.testData[37]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        setParameter_1 = pus.setParameter_b(1)
        setParameter_5 = pus.setParameter_d(5)
        setParameter_34 = pus.setParameter_s(34)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'rid'), (d3, 'store'))
        
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        packet_noAck = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet_noAck = appendCRC(packet_noAck)
        in_pdu_noAck = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_noAck.size, packet_noAck))

        packet_en = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20, testData_en.messageType, testData_en.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x02, 0x00, 0x03], dtype=numpy.uint8)
        packet_en = appendCRC(packet_en)
        in_pdu_en = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_en.size, packet_en))

        packet_trans = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_chg_trans.ackFlags, testData_chg_trans.messageType, testData_chg_trans.messageSubTypeTx, 0x00, 0x00, 0xff, 0xff], dtype=numpy.uint8)
        packet_trans = appendCRC(packet_trans)
        in_pdu_trans = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_trans.size, packet_trans))
                
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_trans) 
        setParameter_1.setParameterValue(10)
        time.sleep(10)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        setParameter_5.setParameterValue(15.0)
        setParameter_34.setParameterValue(-3)        
        time.sleep(10)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_noAck) 
        time.sleep(.5)
        setParameter_34.setParameterValue(16)     
        time.sleep(10)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_noAck) 
        time.sleep(.5)
        setParameter_34.setParameterValue(-11) 
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_en) 
        time.sleep(.5)
        setParameter_1.setParameterValue(30) 
        time.sleep(25)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_noAck) 
        time.sleep(.5)
        setParameter_1.setParameterValue(10) 
        setParameter_34.setParameterValue(0) 
        time.sleep(25)
        setParameter_1.setParameterValue(11) 
        setParameter_34.setParameterValue(-20) 
        time.sleep(3)        
        setParameter_34.setParameterValue(40) 
        time.sleep(3)   
        setParameter_1.setParameterValue(10) 
        setParameter_34.setParameterValue(0) 
        time.sleep(25)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_noAck) 
        time.sleep(.5)
        setParameter_5.setParameterValue(-35.0)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*2)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*3)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*4)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*5)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*6)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*7)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*8)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*9)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*10)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*11)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*12)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*13)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*14)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*15)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*16)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*17)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*18)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*19)
        time.sleep(1)
        setParameter_5.setParameterValue(-35.0*20)                                                                        
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_noAck) 
        time.sleep(.5)
        increase = -35.0*20 + 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 20
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 28
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 20
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 28
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 20
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 28
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 20
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 28
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 20
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 28
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6                                               
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 20
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 28
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 20
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 28
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6        
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_noAck) 
        time.sleep(.5)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 10
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 14
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 10
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 14
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 18
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 18
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 18
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 14
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 10
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 18
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6                                               
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 10
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 14
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 10
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 18
        setParameter_5.setParameterValue(increase)
        time.sleep(1)
        increase += 6        
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_noAck) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        expected_response_0 = numpy.array([0, 2, 0, 6, 0, 5, 1, 64, 70, 153, 153, 153, 153, 153, 154, 64, 49, 204, 204, 204, 204, 204, 205, 1, 7], dtype=numpy.uint8)
        
        expected_response_1 = numpy.array([0, 34, 0, 34, 1, 255, 178, 255, 246, 1, 6], dtype=numpy.uint8)       
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet))        
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet))    
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        
        rid_0 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        expected_rid_0 = numpy.array([0, 6], dtype=numpy.uint8)
        rid_1 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(1))), dtype=numpy.uint8)
        expected_rid_1 = numpy.array([0, 15], dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0))
        self.assertTrue(numpy.array_equal(response[46:57], expected_response_1))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0))
        self.assertTrue(numpy.array_equal(rid_0, expected_rid_0))
        self.assertTrue(numpy.array_equal(rid_1, expected_rid_1))

        expected_response_0 = numpy.array([0, 0], dtype=numpy.uint8)       
        testData.counter_offset = 1
        testData.counter_sec_offset = 1   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(1))), dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))        
          
        expected_response_0 = numpy.array([0, 1, 0, 34, 0, 34, 1, 0, 16, 0, 15, 5, 7], dtype=numpy.uint8)       
        testData.counter_offset = 2
        testData.counter_sec_offset = 2  

        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(2))), dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkPayload(expected_response_0, response[:-6], False)) 
        rid_2 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(2))), dtype=numpy.uint8)
        expected_rid_2 = numpy.array([0, 25], dtype=numpy.uint8)
        self.assertTrue(numpy.array_equal(rid_2, expected_rid_2))

        expected_response_0 = numpy.array([0, 3, 0, 2, 0, 1, 0, 255, 30, 10, 1, 4], dtype=numpy.uint8)
        expected_response_1 = numpy.array([0, 3, 0, 1, 1, 30, 15, 1, 7], dtype=numpy.uint8)       
        expected_response_2 = numpy.array([0, 34, 0, 34, 1, 255, 245, 255, 246, 7, 6], dtype=numpy.uint8) 
        testData.counter_offset = 3
        testData.counter_sec_offset = 3  
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(3))), dtype=numpy.uint8)
        rid_3 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(3))), dtype=numpy.uint8)
        expected_rid_3 = numpy.array([0, 15], dtype=numpy.uint8)
        rid_4 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(4))), dtype=numpy.uint8)
        expected_rid_4 = numpy.array([0, 1], dtype=numpy.uint8)
        rid_5 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(5))), dtype=numpy.uint8)
        expected_rid_5 = numpy.array([0, 2], dtype=numpy.uint8)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:29], expected_response_0))
        self.assertTrue(numpy.array_equal(response[33:42], expected_response_1))
        self.assertTrue(numpy.array_equal(response[46:57], expected_response_2))
        self.assertTrue(numpy.array_equal(rid_3, expected_rid_3))
        self.assertTrue(numpy.array_equal(rid_4, expected_rid_4)) 
        self.assertTrue(numpy.array_equal(rid_5, expected_rid_5))             

        expected_response_0 = numpy.array([0, 0], dtype=numpy.uint8)       
        testData.counter_offset = 4
        testData.counter_sec_offset = 4   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(4))), dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled))  


        expected_response_0 = numpy.array([0,2,0,5,0,5,2,192,65,128,0,0,0,0,0,192,65,64,0,0,0,0,0,8,9], dtype=numpy.uint8)
        expected_response_1 = numpy.array([0,6,0,5,1,192,110,160,0,0,0,0,0,192,68,0,0,0,0,0,0,5,6], dtype=numpy.uint8)
        testData.counter_offset = 5
        testData.counter_sec_offset = 5  
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(5))), dtype=numpy.uint8)
        rid_6 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(6))), dtype=numpy.uint8)
        expected_rid_6 = numpy.array([0, 7], dtype=numpy.uint8)
        rid_7 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(7))), dtype=numpy.uint8)
        expected_rid_7 = numpy.array([0, 7], dtype=numpy.uint8)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0))
        self.assertTrue(numpy.array_equal(response[46:69], expected_response_1))
        self.assertTrue(numpy.array_equal(rid_6, expected_rid_6))
        self.assertTrue(numpy.array_equal(rid_7, expected_rid_7)) 

        expected_response_0_0 = numpy.array([0,2,0,5,0,5,2,64,50,0,0,0,0,0,0,64,49,204,204,204,204,204,205,9,10], dtype=numpy.uint8)
        expected_response_0_1 = numpy.array([0,2,0,5,0,5,2,64,52,0,0,0,0,0,0,64,49,204,204,204,204,204,205,9,10], dtype=numpy.uint8)
        expected_response_0_2 = numpy.array([0, 2, 0, 5, 0, 5, 2, 64, 59, 85, 85, 85, 85, 85, 85, 64, 49, 204, 204, 204, 204, 204, 205, 9, 10], dtype=numpy.uint8)
        expected_response_1 = numpy.array([0,6,0,5,1,192,110,160,0,0,0,0,0,192,68,0,0,0,0,0,0,5,6], dtype=numpy.uint8)          

        testData.counter_offset = 6
        testData.counter_sec_offset = 6  
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(6))), dtype=numpy.uint8)
 
        rid_8 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(8))), dtype=numpy.uint8)
        expected_rid_8 = numpy.array([0, 6], dtype=numpy.uint8)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0_0) or numpy.array_equal(response[17:42], expected_response_0_1) or numpy.array_equal(response[17:42], expected_response_0_2))
        self.assertTrue(numpy.array_equal(response[46:69], expected_response_1))
        self.assertTrue(numpy.array_equal(rid_8, expected_rid_8))

        testData.counter_offset = 7
        testData.counter_sec_offset = 7  
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(7))), dtype=numpy.uint8)
        expected_response_0 = numpy.array([0,1,0,6,0,5,1,192,110,160,0,0,0,0,0,192,68,0,0,0,0,0,0,5,6], dtype=numpy.uint8)  
        
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0))
         
        self.assertTrue(d1.num_messages() == 8)
        self.assertTrue(d2.num_messages() == 3)
        self.assertTrue(d3.num_messages() == 9)


    def test_057_ST12_12_PMON_check_transition_report(self):        
        testData = self.testData[46]
        testData_trans = self.testData[47]
        testData_en = self.testData[37]
        testData_chg_trans = self.testData[48]
        
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        onBoardMonitoringService = pus.OnBoardMonitoringService("../../../examples/init_onboardmon.json") 
        setParameter_1 = pus.setParameter_b(1)
        setParameter_5 = pus.setParameter_d(5)
        setParameter_34 = pus.setParameter_s(34)
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        d3 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((onBoardMonitoringService, 'out'), (d1, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'ver'), (d2, 'store'))
        self.tb.msg_connect((onBoardMonitoringService, 'rid'), (d3, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        packet_en = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20, testData_en.messageType, testData_en.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x02, 0x00, 0x03], dtype=numpy.uint8)
        packet_en = appendCRC(packet_en)
        in_pdu_en = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_en.size, packet_en))

        packet_trans = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_chg_trans.ackFlags, testData_chg_trans.messageType, testData_chg_trans.messageSubTypeTx, 0x00, 0x00, 0x00, 0x32], dtype=numpy.uint8)
        packet_trans = appendCRC(packet_trans)
        in_pdu_trans = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_trans.size, packet_trans))

        packet_trans_out = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData_chg_trans.ackFlags, testData_chg_trans.messageType, testData_chg_trans.messageSubTypeTx, 0x00, 0x00, 0xff, 0xff], dtype=numpy.uint8)
        packet_trans_out = appendCRC(packet_trans_out)
        in_pdu_trans_out = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_trans_out.size, packet_trans_out))
        
        self.tb.start()
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_trans_out) 
        setParameter_1.setParameterValue(10)
        time.sleep(1)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_en) 
        setParameter_1.setParameterValue(16)
        setParameter_5.setParameterValue(-40.0)
        setParameter_34.setParameterValue(-11)        
        time.sleep(12)
        setParameter_5.setParameterValue(20.0)
        setParameter_34.setParameterValue(16)        
        time.sleep(12)
        setParameter_1.setParameterValue(10)
        setParameter_5.setParameterValue(-40.0)
        setParameter_34.setParameterValue(-11)        
        time.sleep(12)
        setParameter_1.setParameterValue(0)
        setParameter_5.setParameterValue(20.0)
        setParameter_34.setParameterValue(16)  
        time.sleep(12)
        setParameter_1.setParameterValue(10)
        setParameter_5.setParameterValue(-40.0)
        setParameter_34.setParameterValue(-11)        
        time.sleep(12)
        setParameter_1.setParameterValue(0)
        setParameter_5.setParameterValue(20.0)
        setParameter_34.setParameterValue(16)  
        time.sleep(12)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu_trans) 
        time.sleep(.5)
        setParameter_1.setParameterValue(10)
        time.sleep(17)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        setParameter_5.setParameterValue(0.0)
        setParameter_34.setParameterValue(0) 
        time.sleep(17)
        onBoardMonitoringService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
            
        expected_response_0 = numpy.array([0, 13, 0, 6, 0, 5, 1, 64, 52, 0, 0, 0, 0, 0, 0, 64, 49, 204, 204, 204, 204, 204, 205, 5, 7], dtype=numpy.uint8)
        expected_response_1 = numpy.array([0, 34, 0, 34, 1, 0, 16, 0, 15, 6, 7], dtype=numpy.uint8)
        expected_response_2 = numpy.array([0, 6, 0, 5, 1, 192, 68, 0, 0, 0, 0, 0, 0, 64, 49, 204, 204, 204, 204, 204, 205, 7, 5], dtype=numpy.uint8)
        expected_response_3 = numpy.array([0, 34, 0, 34, 1, 255, 245, 255, 246, 7, 6], dtype=numpy.uint8)
        expected_response_4 = numpy.array([0, 2, 0, 1, 0, 255, 10, 10, 4, 3], dtype=numpy.uint8)
        expected_response_5 = numpy.array([0, 6, 0, 5, 1, 64, 52, 0, 0, 0, 0, 0, 0, 64, 49, 204, 204, 204, 204, 204, 205, 5, 7], dtype=numpy.uint8)
        expected_response_6 = numpy.array([0, 34, 0, 34, 1, 0, 16, 0, 15, 6, 7], dtype=numpy.uint8)
        expected_response_7 = numpy.array([0, 2, 0, 1, 0, 255, 0, 10, 3, 4], dtype=numpy.uint8)
        expected_response_8 = numpy.array([0, 6, 0, 5, 1, 192, 68, 0, 0, 0, 0, 0, 0, 64, 49, 204, 204, 204, 204, 204, 205, 7, 5], dtype=numpy.uint8)
        expected_response_9 = numpy.array([0, 34, 0, 34, 1, 255, 245, 255, 246, 7, 6], dtype=numpy.uint8)
        expected_response_10 = numpy.array([0, 2, 0, 1, 0, 255, 10, 10, 4, 3], dtype=numpy.uint8)
        expected_response_11 = numpy.array([0, 6, 0, 5, 1, 64, 52, 0, 0, 0, 0, 0, 0, 64, 49, 204, 204, 204, 204, 204, 205, 5, 7], dtype=numpy.uint8)
        expected_response_12 = numpy.array([0, 34, 0, 34, 1, 0, 16, 0, 15, 6, 7], dtype=numpy.uint8)

        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
            
        self.assertTrue(checkPrimaryHeader(testData_trans.apid, testData_trans.messageSize, 0, response, testData_trans.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData_trans.messageType, testData_trans.messageSubTypeRx, 0, response, testData_trans.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0))
        self.assertTrue(numpy.array_equal(response[46:57], expected_response_1)) 
        self.assertTrue(numpy.array_equal(response[61:84], expected_response_2))
        self.assertTrue(numpy.array_equal(response[88:99], expected_response_3))
        self.assertTrue(numpy.array_equal(response[103:113], expected_response_4)) 
        self.assertTrue(numpy.array_equal(response[117:140], expected_response_5))
        self.assertTrue(numpy.array_equal(response[144:155], expected_response_6)) 
        
        self.assertTrue(numpy.array_equal(response[159:169], expected_response_7))
        self.assertTrue(numpy.array_equal(response[173:196], expected_response_8)) 
        self.assertTrue(numpy.array_equal(response[200:211], expected_response_9)) 
        self.assertTrue(numpy.array_equal(response[215:225], expected_response_10)) 
        self.assertTrue(numpy.array_equal(response[229:252], expected_response_11))
        self.assertTrue(numpy.array_equal(response[256:267], expected_response_12))  
                      
        expected_response_0 = numpy.array([0, 0], dtype=numpy.uint8)       
        testData.counter_offset = 1
        testData.counter_sec_offset = 0   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(1))), dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled)) 

        expected_response_0 = numpy.array([0, 2, 0, 6, 0, 5, 1, 64, 52, 0, 0, 0, 0, 0, 0, 64, 49, 204, 204, 204, 204, 204, 205, 1, 7], dtype=numpy.uint8)
        expected_response_1 = numpy.array([0, 34, 0, 34, 1, 0, 16, 0, 15, 1, 7], dtype=numpy.uint8)     
        testData.counter_offset = 2
        testData.counter_sec_offset = 1   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(2))), dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0))
        self.assertTrue(numpy.array_equal(response[46:57], expected_response_1)) 

        expected_response_0 = numpy.array([0, 2, 0, 6, 0, 5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 64, 49, 204, 204, 204, 204, 204, 205, 7, 5], dtype=numpy.uint8)
        expected_response_1 = numpy.array([0, 34, 0, 34, 1, 0, 0, 0, 15, 7, 5], dtype=numpy.uint8)     
        testData_trans.counter_offset = 3
        testData_trans.counter_sec_offset = 1   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(3))), dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData_trans.apid, testData_trans.messageSize, 0, response, testData_trans.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData_trans.messageType, testData_trans.messageSubTypeRx, 0, response, testData_trans.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[17:42], expected_response_0))
        self.assertTrue(numpy.array_equal(response[46:57], expected_response_1)) 
        
        expected_response_0 = numpy.array([0, 0], dtype=numpy.uint8)       
        testData.counter_offset = 4
        testData.counter_sec_offset = 2   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(4))), dtype=numpy.uint8)
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        self.assertTrue(checkPayload(expected_response_0, response, testData.crcEnabled)) 


        rid_0 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(0))), dtype=numpy.uint8)
        expected_rid_0 = numpy.array([0, 15], dtype=numpy.uint8)
        rid_1 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(1))), dtype=numpy.uint8)
        expected_rid_1 = numpy.array([0, 1], dtype=numpy.uint8)
        rid_2 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(2))), dtype=numpy.uint8)
        expected_rid_2 = numpy.array([0, 6], dtype=numpy.uint8)
        rid_3 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(3))), dtype=numpy.uint8)
        expected_rid_3 = numpy.array([0, 25], dtype=numpy.uint8)
        rid_4 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(4))), dtype=numpy.uint8)
        expected_rid_4 = numpy.array([0, 2], dtype=numpy.uint8)
        rid_5 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(5))), dtype=numpy.uint8)
        expected_rid_5 = numpy.array([0, 15], dtype=numpy.uint8)        
        rid_6 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(6))), dtype=numpy.uint8)
        expected_rid_6 = numpy.array([0, 6], dtype=numpy.uint8)
        rid_7 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(7))), dtype=numpy.uint8)
        expected_rid_7 = numpy.array([0, 25], dtype=numpy.uint8)
        rid_8 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(8))), dtype=numpy.uint8)
        expected_rid_8 = numpy.array([0, 1], dtype=numpy.uint8)
        rid_9 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(9))), dtype=numpy.uint8)
        expected_rid_9 = numpy.array([0, 15], dtype=numpy.uint8)
        rid_10 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(10))), dtype=numpy.uint8)
        expected_rid_10 = numpy.array([0, 6], dtype=numpy.uint8)
        rid_11 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(11))), dtype=numpy.uint8)
        expected_rid_11 = numpy.array([0, 25], dtype=numpy.uint8)                                  
        rid_12 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(12))), dtype=numpy.uint8)
        expected_rid_12 = numpy.array([0, 6], dtype=numpy.uint8)
        rid_13 =  numpy.array(pmt.u8vector_elements(pmt.cdr(d3.get_message(13))), dtype=numpy.uint8)
        expected_rid_13 = numpy.array([0, 25], dtype=numpy.uint8) 
     
        self.assertTrue(numpy.array_equal(rid_0, expected_rid_0))                
        self.assertTrue(numpy.array_equal(rid_1, expected_rid_1))      
        self.assertTrue(numpy.array_equal(rid_2, expected_rid_2))                
        self.assertTrue(numpy.array_equal(rid_3, expected_rid_3))  
        self.assertTrue(numpy.array_equal(rid_4, expected_rid_4))                
        self.assertTrue(numpy.array_equal(rid_5, expected_rid_5))  
        self.assertTrue(numpy.array_equal(rid_6, expected_rid_6))                
        self.assertTrue(numpy.array_equal(rid_7, expected_rid_7))      
        self.assertTrue(numpy.array_equal(rid_8, expected_rid_8))                
        self.assertTrue(numpy.array_equal(rid_9, expected_rid_9))  
        self.assertTrue(numpy.array_equal(rid_10, expected_rid_10))                
        self.assertTrue(numpy.array_equal(rid_11, expected_rid_11))  
        self.assertTrue(numpy.array_equal(rid_12, expected_rid_12))  
        self.assertTrue(numpy.array_equal(rid_13, expected_rid_13))                

                                                                                                                                                                                                                          
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
    gr_unittest.run(qa_OnBoardMonitoringService, "qa_OnBoardMonitoringService.xml" )
