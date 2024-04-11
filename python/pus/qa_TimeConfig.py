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
import os

class qa_TimeConfig(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()
        self.epoch_diff = 315964800

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = pus.TimeConfig(0.1, 2, False, 1986, 1, 6)

    def test_001_timeConfig_test(self):
        timeConfig = pus.TimeConfig(0.1, 2, True, 1986, 1, 6)

        self.tb.start()
        time.sleep(.5)
        self.tb.stop()
        self.tb.wait()

        #print("getCurrentTimeUTC()")
        #print(timeConfig.getCurrentTimeUTC())
        #print("")
        print("getCurrentTimeDefaultCUC")
        print(timeConfig.getCurrentTimeDefaultCUC())
        print("")
        print("getCurrentTimeStamp()")  
        print([hex(x) for x in timeConfig.getCurrentTimeStampAsVector()])                
        print("")
        print("System OBT")
        print(int(os.popen('date +%s').read()) - self.epoch_diff)
 
        self.assertTrue(True)

if __name__ == '__main__':
    gr_unittest.run(qa_TimeConfig, "qa_TimeConfig.xml" )
