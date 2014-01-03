#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''wgetdb

Usage:
  wgetdb <database_path> <url> <label>
  wgetdb -h | --help
  wgetdb --version

Options:
  -h --help     Show this screen.
  --version     Show version.
'''

from __future__ import unicode_literals, print_function
import datetime
import urllib2
import sqlite3
from docopt import docopt


__version__ = "0.1.0"
__author__ = "Akira Kozakai"
__license__ = "MIT"

TABLE_NAME = "datas"
URLOPEN_TIMEOUT = 10


class WgetDB(object):
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path, isolation_level=None)
        self.create_table()

    def __del__(self):
         self.con.close()

    def create_table(self):
        cur = self.con.execute(
            "SELECT * FROM sqlite_master WHERE type='table' and name=?",
            (TABLE_NAME,))
        if cur.fetchone() is None:
            sql = """
                CREATE TABLE %s (
                  id INTEGER PRIMARY KEY,
                  url VARCHAR(4095) NOT NULL,
                  label VARCHAR(255) NOT NULL,
                  data BLOB NOT NULL,
                  created_date DATE NOT NULL,
                  modified_date DATE NOT NULL,
                  UNIQUE(url, label)
                );
            """ % TABLE_NAME
            self.con.execute(sql)

    def download_url(self, url):
        response = urllib2.urlopen(url, timeout=URLOPEN_TIMEOUT)
        if response.code != 200:
            return None
        return response.read()

    def insert_data(self, url, label, data):
        sql = ('INSERT INTO %s ("url", "label", "data", "created_date", "modified_date")'
               'VALUES (?, ?, ?, ?, ?);') % TABLE_NAME
        args = (url, label, buffer(data), datetime.datetime.utcnow(),
                datetime.datetime.utcnow())
        self.con.execute(sql, args)

    def update_data(self, url, label, data):
        sql = ('UPDATE %s SET "data" = ?, "modified_date" = ?'
               'WHERE "url" = ? AND "label" = ?;') % TABLE_NAME
        args = (buffer(data), datetime.datetime.utcnow(), url, label)
        self.con.execute(sql, args)

    def store(self, url, label):
        data = self.download_url(url)
        try:
            self.insert_data(url, label, data)
        except sqlite3.IntegrityError as e:
            self.update_data(url, label, data)


def main():
    try:
        args = docopt(__doc__, version=__version__)
        db_path = args.get('<database_path>')
        url = args.get('<url>')
        label = args.get('<label>')
        wgetdb = WgetDB(db_path)
        wgetdb.store(url, label)
        print('SUCCESS!')
    except Exception as e:
        print(u'=== ERROR ===')
        print(u'type:{0}'.format(type(e)))
        print(u'args:{0}'.format(e.args))
        print(u'message:{0}'.format(e.message))


if __name__ == '__main__':
    main()
