# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_rq import job

import time


@job('default')
def test_func(a, b):

    time.sleep(60)

    return a + b