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
        
class qa_ParameterStatisticsService(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.testData = []
        self.testData.append(test_data(0x04, 0x01, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #0
        self.testData.append(test_data(0x04, 0x01, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #1
        self.testData.append(test_data(0x04, 0x03, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #2
        self.testData.append(test_data(0x04, 0x04, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #3
        self.testData.append(test_data(0x04, 0x04, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #4
        self.testData.append(test_data(0x04, 0x04, 0x00, 0x11, 1, 0x19, 0, 32, 0, True, 0, 0)) #5
        self.testData.append(test_data(0x04, 0x05, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #6
        self.testData.append(test_data(0x04, 0x06, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #7
        self.testData.append(test_data(0x04, 0x06, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #8
        self.testData.append(test_data(0x04, 0x06, 0x00, 0x11, 1, 0x19, 0, 8, 1, True, 0, 0)) #9        
        self.testData.append(test_data(0x04, 0x06, 0x00, 0x11, 1, 0x19, 0, 32, 1, True, 0, 0)) #10
        self.testData.append(test_data(0x04, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #11
        self.testData.append(test_data(0x04, 0x07, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #12
        self.testData.append(test_data(0x04, 0x07, 0x00, 0x11, 1, 0x19, 0, 9, 0, True, 0, 0)) #13  
        self.testData.append(test_data(0x04, 0x08, 0x00, 0x11, 1, 0x19, 0, 1, 0, True, 0, 0)) #14  
        self.testData.append(test_data(0x04, 0x08, 0x09, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #15 
        self.testData.append(test_data(0x04, 0x06, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #16
        self.testData.append(test_data(0x04, 0x08, 0x09, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #17                
        self.testData.append(test_data(0x04, 0x07, 0x00, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #18 
        self.testData.append(test_data(0x04, 0x08, 0x09, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #19                
        self.testData.append(test_data(0x04, 0x01, 0x02, -1, 1, 0x19, 15, 0, 0, True, 0, 0)) #20
        self.testData.append(test_data(0x04, 0x05, 0x00, 0x11, 1, 0x19, 0, 0, 0, True, 0, 0)) #21
        self.testData.append(test_data(0x04, 0x03, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #22
        self.testData.append(test_data(0x04, 0x01, 0x02, -1, 1, 0x19, 0, 0, 0, True, 0, 0)) #23
        self.testData.append(test_data(0x04, 0x04, 0x00, 0x11, 1, 0x19, 15, 0, 0, True, 0, 0)) #24
                                                         
    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.ParameterStatisticsService("")

    def test_001_ST04_wrong_service_type_subtype(self):
        testData = self.testData[0]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packetType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x03, 0x01, 0x00, 0x00], dtype=numpy.uint8)
        packetType = appendCRC(packetType)
        in_pduType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetType.size, packetType))

        packetSubType = numpy.array([0x18, 0x03, 0xc0, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, 0x04, 0x2d, 0x00, 0x00], dtype=numpy.uint8)
        packetSubType = appendCRC(packetSubType)
        in_pduSubType = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packetSubType.size, packetSubType))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pduType) 
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pduSubType)
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 2)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packetType, 3))
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(1), packetSubType, 4))  

    def test_002_ST04_01_invalid_reset_flag_field_shorter(self):
        testData = self.testData[0]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_003_ST04_01_invalid_reset_flag_field_longer(self):
        testData = self.testData[1]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))

    def test_004_ST04_03_invalid_field_longer(self):
        testData = self.testData[2]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_005_ST04_04_invalid_interval_field_shorter(self):
        testData = self.testData[3]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                       
        
    def test_006_ST04_04_invalid_interval_field_longer(self):
        testData = self.testData[4]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))         

    def test_006_ST04_04_invalid_interval_shorter_than_min(self):
        testData = self.testData[5]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))      

    def test_008_ST04_05_invalid_fields_longer(self):
        testData = self.testData[6]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))   

    def test_009_ST04_06_invalid_numDef_field_shorter(self):
        testData = self.testData[7]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                       

    def test_010_ST04_06_invalid_ParamID_field_shorter(self):
        testData = self.testData[7]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_011_ST04_06_invalid_interval_field_shorter(self):
        testData = self.testData[7]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  
        
    def test_012_ST04_06_invalid_interval_field_longer(self):
        testData = self.testData[8]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x05, 0x00, 0x02, 0x00, 0x00, 0x00, 0x05, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  
                        
    def test_013_ST04_06_invalid_paramID_non_exists(self):
        testData = self.testData[9]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                
        parameterStatisticsService = pus.ParameterStatisticsService("../../../examples/init_paramstats.json")

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x20, 0x00, 0x06, 0x00, 0x00, 0x00, 0x20], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))    
                                
    def test_014_ST04_06_invalid_interval_shorter_than_min(self):
        testData = self.testData[10]
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                
        parameterStatisticsService = pus.ParameterStatisticsService("../../../examples/init_paramstats.json")

        d1 = blocks.message_debug()
        d2 = blocks.message_debug()

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x20, 0x00, 0x02, 0x00, 0x00, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))    

    def test_015_ST04_07_invalid_numDef_field_shorter(self):
        testData = self.testData[11]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))                       

    def test_016_ST04_07_invalid_ParamID_field_shorter(self):
        testData = self.testData[11]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  
        
    def test_017_ST04_07_invalid_ParamID_field_longer(self):
        testData = self.testData[12]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x05, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  
                        
    def test_018_ST04_07_invalid_paramID_non_exists(self):
        testData = self.testData[13]
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x06, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
   
        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)
        self.assertTrue(checkFailedStartExecutionVerification(d2.get_message(0), packet, testData.error))    

    def test_019_ST04_08_invalid_fields_longer(self):
        testData = self.testData[14]
                
        parameterStatisticsService = pus.ParameterStatisticsService("")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 0)
        self.assertTrue(d2.num_messages() == 1)

        self.assertTrue(checkFailedAcceptanceVerification(d2.get_message(0), packet, testData.error))  

    def test_020_ST04_06and07and08and09_report_add_report_delete_stats_def(self):
        # ------------------------------------------------------------
        # Report def TC[04,08] -> TM[04,09]
        # ------------------------------------------------------------   
        testData = self.testData[21]
        packet_dis = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet_dis = appendCRC(packet_dis)
        in_pdu_dis = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_dis.size, packet_dis))
        
        testData = self.testData[15]
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        parameterStatisticsService = pus.ParameterStatisticsService("../../../examples/init_paramstats.json")
        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu_dis) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        expected_response_0 = numpy.array([0, 0, 0, 5, 0, 2, 0, 1, 0, 0, 0, 10, 0, 9, 0, 0, 0, 5], dtype=numpy.uint8)        
        payloads = [expected_response_0]

        self.assertTrue(checkResults(1, d1, payloads, 3, d2, 0, testData, packet))

        # ------------------------------------------------------------
        # Add/Mod def TC[04,06]
        # ------------------------------------------------------------   
        testData = self.testData[16]
        d2 = blocks.message_debug()
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))
                
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x20, 0x00, 0x02, 0x00, 0x00, 0x00, 0x40], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
 
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
  
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )

        # ------------------------------------------------------------
        # Report def TC[04,08] -> TM[04,09]
        # ------------------------------------------------------------   
        
        testData = self.testData[17]

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()


        self.assertTrue(d1.num_messages() == 2)
        self.assertTrue(d2.num_messages() == 3)
        
        expected_response = numpy.array([0, 0, 0, 0, 0, 3, 0, 1, 0, 0, 0, 32, 0, 2, 0, 0, 0, 64, 0, 9, 0, 0, 0, 5], dtype=numpy.uint8)        
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(1))), dtype=numpy.uint8)
                    
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 1, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 1, response, testData.counter_sec_offset))
                                              
        if testData.crcEnabled:
            self.assertTrue(checkCRC(response))
                
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled))

        # ------------------------------------------------------------
        # Del def TC[04,07]
        # ------------------------------------------------------------   
        testData = self.testData[18]
        d2 = blocks.message_debug()
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))
                
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x01, 0x00, 0x09], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
       
        self.assertTrue(d1.num_messages() == 2 or d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 3)
  
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )

        # ------------------------------------------------------------
        # Report def TC[04,08] -> TM[04,09]
        # ------------------------------------------------------------   
        
        testData = self.testData[19]

        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        self.assertTrue(d1.num_messages() == 3 or d1.num_messages() == 4)
        self.assertTrue(d2.num_messages() == 3)
        
        expected_response = numpy.array([0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 32, 0, 2, 0, 0, 0, 64], dtype=numpy.uint8)        
        if d1.num_messages() == 3:
            response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(2))), dtype=numpy.uint8)
        else:
            response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(3))), dtype=numpy.uint8)   
            testData.counter_offset = 1  
               
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 2, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 2, response, testData.counter_sec_offset))
                                              
        if testData.crcEnabled:
            self.assertTrue(checkCRC(response))
                
        self.assertTrue(checkPayload(expected_response, response, testData.crcEnabled))

    def test_021_ST04_01and02and03_report_reset_report_stats(self):
        # ------------------------------------------------------------
        # Report def TC[04,01] -> TM[04,02]
        # ------------------------------------------------------------   
        
        testData = self.testData[21]
        packet_dis = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet_dis = appendCRC(packet_dis)
        in_pdu_dis = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet_dis.size, packet_dis))
        
        testData = self.testData[20]   
        timeConfig = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)
        parametersInit = pus.ParametersInit("../../../examples/init_param.json")                 
        parameterStatisticsService = pus.ParameterStatisticsService("../../../examples/init_paramstats.json")
        setParameter_1 = pus.setParameter_b(1)
        setParameter_9 = pus.setParameter_f(9)


        d1 = blocks.message_debug()
        d2 = blocks.message_debug()
        messageConfig =  pus.MessageConfig(testData.apid, testData.crcEnabled)

        self.tb.msg_connect((parameterStatisticsService, 'out'), (d1, 'store'))
        self.tb.msg_connect((parameterStatisticsService, 'ver'), (d2, 'store'))
     
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
           
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu_dis) 
        time.sleep(1)
        setParameter_1.setParameterValue(9)
        setParameter_9.setParameterValue(10.5)
        time.sleep(1)
        setParameter_1.setParameterValue(10)
        setParameter_9.setParameterValue(21)
        time.sleep(1)
        setParameter_1.setParameterValue(11)
        setParameter_9.setParameterValue(33.75)
        time.sleep(1)
        setParameter_1.setParameterValue(12)
        setParameter_9.setParameterValue(45.9)
        time.sleep(1)
        setParameter_1.setParameterValue(13)
        time.sleep(1)
        setParameter_1.setParameterValue(14)
        time.sleep(1)
        setParameter_1.setParameterValue(15)
        time.sleep(1)
        setParameter_1.setParameterValue(16)
        time.sleep(1)
        setParameter_1.setParameterValue(17)
        time.sleep(1)
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        expected_response = numpy.array([0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 10, 0, 9, 0, 0, 0, 5], dtype=numpy.uint8)        

        expected_response_0 = numpy.array([0, 2, 0, 1, 0, 9, 17], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([9], dtype=numpy.uint8)  
        expected_response_2_0 = numpy.array([13, 2, 0, 9, 0, 16, 66, 55, 153, 154], dtype=numpy.uint8)  
        expected_response_2_1 = numpy.array([13, 2, 0, 9, 0, 17, 66, 55, 153, 154], dtype=numpy.uint8)  
        expected_response_3 = numpy.array([65, 40, 0, 0], dtype=numpy.uint8)  
        expected_response_4_0 = numpy.array([66, 19, 16, 0, 65, 81, 82, 242], dtype=numpy.uint8)  
        expected_response_4_1 = numpy.array([66, 18, 90, 91, 65, 75, 100, 39], dtype=numpy.uint8)  
        expected_response_4_2 = numpy.array([66, 22, 64,  0, 65, 71, 142, 87], dtype=numpy.uint8)  
  
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(0))), dtype=numpy.uint8)
        
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 3)
  
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(0), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(1), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(2), packet) )
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 0, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 0, response, testData.counter_sec_offset))
        time.sleep(0.3)

        self.assertTrue(numpy.array_equal(response[25:32], expected_response_0))
        self.assertTrue(numpy.array_equal(response[36:37], expected_response_1))
        self.assertTrue(numpy.array_equal(response[41:51], expected_response_2_0) or numpy.array_equal(response[41:51], expected_response_2_1))
        self.assertTrue(numpy.array_equal(response[55:59], expected_response_3))
        self.assertTrue(numpy.array_equal(response[63:71], expected_response_4_0) or numpy.array_equal(response[63:71], expected_response_4_1) or numpy.array_equal(response[63:71], expected_response_4_2))  

        # ------------------------------------------------------------
        # Reset stats TC[04,03]
        # ------------------------------------------------------------   
        testData = self.testData[22]
                
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
        
        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
       
        self.assertTrue(d1.num_messages() == 1)
        self.assertTrue(d2.num_messages() == 6)
  
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(3), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(4), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(5), packet) )

        # ------------------------------------------------------------
        # Report def TC[04,01] -> TM[04,02]
        # ------------------------------------------------------------   
        
        testData = self.testData[23]   
     
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x01], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))
           
        self.tb.start()
        time.sleep(11)
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
        
        expected_response = numpy.array([0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 10, 0, 9, 0, 0, 0, 5], dtype=numpy.uint8)        

        expected_response_0 = numpy.array([0, 2, 0, 1, 0, 10, 17], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([17], dtype=numpy.uint8)  
        expected_response_2 = numpy.array([17, 0, 0, 9, 0, 19, 66, 55, 153, 154], dtype=numpy.uint8)  
        expected_response_3 = numpy.array([66, 55, 153, 154], dtype=numpy.uint8)  
        expected_response_4 = numpy.array([66, 55, 153, 154, 0, 0, 0, 0], dtype=numpy.uint8)  
   
        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(1))), dtype=numpy.uint8)
        
        self.assertTrue(d1.num_messages() == 2)
        self.assertTrue(d2.num_messages() == 6)
  
        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 1, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 1, response, testData.counter_sec_offset))
        self.assertTrue(numpy.array_equal(response[25:32], expected_response_0))
        self.assertTrue(numpy.array_equal(response[36:37], expected_response_1))
        self.assertTrue(numpy.array_equal(response[41:51], expected_response_2))
        self.assertTrue(numpy.array_equal(response[55:59], expected_response_3))
        self.assertTrue(numpy.array_equal(response[63:71], expected_response_4))                                

        # ------------------------------------------------------------
        # Enable rep stats TC[04,04]
        # ------------------------------------------------------------   
        
        testData = self.testData[24]
        packet = numpy.array([0x18, 0x03, 0x11, 0x00, 0x00, 0x06, 0x20 | testData.ackFlags, testData.messageType, testData.messageSubTypeTx, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a], dtype=numpy.uint8)
        packet = appendCRC(packet)
        in_pdu = pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(packet.size, packet))

        self.tb.start()
        parameterStatisticsService.to_basic_block()._post(pmt.intern("in"), in_pdu) 
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()
       

        self.assertTrue(d1.num_messages() == 2)
        self.assertTrue(d2.num_messages() == 9)
  
        self.assertTrue(checkSuccessAcceptanceVerification(d2.get_message(6), packet)) 
        self.assertTrue(checkSuccessStartExecutionVerification(d2.get_message(7), packet)) 
        self.assertTrue(checkSuccessSuccessCompletionExecutionVerification(d2.get_message(8), packet) )        


        # ------------------------------------------------------------
        # Report def TM[04,02]
        # ------------------------------------------------------------   
        
        testData = self.testData[23]   
           
        self.tb.start()
        time.sleep(1)
        setParameter_1.setParameterValue(9)
        setParameter_9.setParameterValue(10.5)
        time.sleep(1)
        setParameter_1.setParameterValue(10)
        setParameter_9.setParameterValue(21)
        time.sleep(1)
        setParameter_1.setParameterValue(11)
        setParameter_9.setParameterValue(33.75)
        time.sleep(1)
        setParameter_1.setParameterValue(12)
        setParameter_9.setParameterValue(45.9)
        time.sleep(1)
        setParameter_1.setParameterValue(13)
        time.sleep(1)
        setParameter_1.setParameterValue(14)
        time.sleep(1)
        setParameter_1.setParameterValue(15)
        time.sleep(1)
        setParameter_1.setParameterValue(16)
        time.sleep(1)
        setParameter_1.setParameterValue(17)
        time.sleep(1)
        self.tb.stop()
        self.tb.wait()
        
        expected_response = numpy.array([0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 10, 0, 9, 0, 0, 0, 5], dtype=numpy.uint8)        

        expected_response_0 = numpy.array([0, 2, 0, 1, 0, 9, 17], dtype=numpy.uint8)  
        expected_response_1 = numpy.array([9], dtype=numpy.uint8)  
        expected_response_2_0 = numpy.array([13, 2, 0, 9, 0, 18, 66, 55, 153, 154], dtype=numpy.uint8)  
        expected_response_2_1 = numpy.array([13, 2, 0, 9, 0, 17, 66, 55, 153, 154], dtype=numpy.uint8) 
        expected_response_3 = numpy.array([65, 40, 0, 0], dtype=numpy.uint8)  
        expected_response_4_0 = numpy.array([66, 31, 68, 69, 65, 45, 188, 36], dtype=numpy.uint8)
        expected_response_4_1 = numpy.array([66, 27, 93, 94, 65, 68, 230, 32], dtype=numpy.uint8) 

        response =  numpy.array(pmt.u8vector_elements(pmt.cdr(d1.get_message(2))), dtype=numpy.uint8)

        self.assertTrue(d1.num_messages() == 3)
        self.assertTrue(d2.num_messages() == 9)

        self.assertTrue(checkPrimaryHeader(testData.apid, testData.messageSize, 2, response, testData.counter_offset))
        self.assertTrue(checkSecondaryHeader(testData.messageType, testData.messageSubTypeRx, 2, response, testData.counter_sec_offset))

        self.assertTrue(numpy.array_equal(response[25:32], expected_response_0))
        self.assertTrue(numpy.array_equal(response[36:37], expected_response_1))
        self.assertTrue(numpy.array_equal(response[41:51], expected_response_2_0) or numpy.array_equal(response[41:51], expected_response_2_1))
        self.assertTrue(numpy.array_equal(response[55:59], expected_response_3))
        self.assertTrue(numpy.array_equal(response[63:71], expected_response_4_0) or numpy.array_equal(response[63:71], expected_response_4_1))
                  
                                                                                                                                                                           
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
    gr_unittest.run(qa_ParameterStatisticsService, "qa_ParameterStatisticsService.xml" )
