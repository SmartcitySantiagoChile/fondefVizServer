# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django_rq import get_worker

from rqworkers.tasks import export_data_job

from elasticsearch_dsl import Search


class RQTest(TestCase):

    def setUp(self):
        pass

    def test_export_job(self):
        """  """
        # init job
        es_query = Search()
        export_data_job(es_query)

        # run worker
        get_worker('data_exporter').work(burst=True)  # Processes all jobs then stop.
