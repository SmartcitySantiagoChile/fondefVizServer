import os
import uuid
from unittest import TestCase

from dataDownloader.unicodecsv import UnicodeWriter


class TestUnicodecsv(TestCase):

    def setUp(self):
        self.row = ['Esto', 'es', 'un', 'texto', 'utf8.']

    def testWriterow(self):
        tmp_file_name = str(uuid.uuid4())
        output = open(tmp_file_name, 'wb')
        writer = UnicodeWriter(output, delimiter=str(','))
        writer.writerow(self.row)
        output.close()
        with open(tmp_file_name, 'r') as output:
            for row in output:
                self.assertEqual(type(""), type(row))
        os.remove(tmp_file_name)

    def testWriterows(self):
        tmp_file_name = str(uuid.uuid4())
        rows = [self.row, self.row, self.row]
        output = open(tmp_file_name, 'wb')
        writer = UnicodeWriter(output, delimiter=str(','))
        writer.writerows(rows)
        output.close()
        with open(tmp_file_name, 'r') as output:
            for row in output:
                self.assertEqual(type(""), type(row))
        os.remove(tmp_file_name)
        output.close()
