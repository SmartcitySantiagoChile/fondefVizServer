# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import os

loader = unittest.TestLoader()
start_dir = os.path.dirname(__file__)
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)
