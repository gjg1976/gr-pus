#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 Gustavo Gonzalez.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
from gnuradio import gr
import serial
from threading import Thread
from threading import Event
import pmt

class serial_transceiver(gr.basic_block):
    """
    docstring for block serial_transceiver
    """
    def __init__(self, serial_port,serial_baud, serial_data_bits, serial_parity, serial_stop_bits, depth):
        gr.basic_block.__init__(self,
            name="serial_transceiver",
            in_sig=[],
            out_sig=[])
        self.instrument_id = 0
        self.depth = depth
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

        self.message_port_register_out(pmt.intern('out'))
        self.serial_port = serial.Serial(port=serial_port, baudrate=serial_baud, bytesize=serial_data_bits,
                         parity = 'N', stopbits=serial_stop_bits, timeout=0)
        self.thread = Thread(target=self.uart_handler_rx, args=(self.serial_port, self.instrument_id))
        self.event = Event()
        self.thread.start()   

    def stop(self):
        self.event.set()
        self.thread.join()
        return super().stop()

    def uart_handler_rx(self, serial_port, instrument_id):
        b_data_in = numpy.empty(0, dtype=numpy.uint8)
        b_processing_status = False 
        
        while True:
            if self.event.is_set():
                break
            while serial_port.inWaiting() > 0:
                for b in serial_port.read():
                    b_data_in = numpy.insert(b_data_in, b_data_in.size, b)
            if len(b_data_in) > 1:   
                packet = pmt.cons(pmt.PMT_NIL,pmt.init_u8vector(b_data_in.size, b_data_in))
                self.message_port_pub(pmt.intern('out'), packet)
                b_data_in = numpy.empty(0, dtype=numpy.uint8)
                                        
    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print("[ERROR] Received invalid message type. Expected u8vector")
            return
        tele_command = numpy.array(pmt.u8vector_elements(msg), dtype=numpy.uint8)
        self.serial_port.write(numpy.frombuffer(tele_command, dtype=numpy.uint8))

