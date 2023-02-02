# -*- coding: utf-8 -*-

import pickle
import sqlite3


class Cache(object):
    def __init__(self, path, writeable=False):
        self.path = path
        self.writeable = writeable
        self._init()

    def __getstate__(self):
        return {'path': self.path, 'writeable': self.writeable}

    def __setstate__(self, state):
        self.__dict__ = state
        self._init()

    def _init(self):
        self.db = sqlite3.connect(self.path)
        self.cursor = self.db.cursor()
        if self.writeable:
            self.cursor.execute('PRAGMA busy_timeout = 10000')
            self.cursor.execute('CREATE table IF NOT EXISTS cache (name TEXT PRIMARY KEY, bunches BLOB);')
            self.db.commit()

    def delete(self, name):
        if self.writeable:
            self.cursor.execute('DELETE FROM cache WHERE name == ?', (name,))
            self.db.commit()

    def insert(self, name, bunches):
        if self.writeable:
            self.cursor.execute('INSERT INTO cache VALUES (?, ?)', (name, pickle.dumps(bunches)))
            self.db.commit()

    def get_names(self):
        return [v for (v,) in self.cursor.execute('SELECT name from cache').fetchall()]

    def get_for_name(self, name):
        res = self.cursor.execute('SELECT * FROM cache WHERE name == ? LIMIT 1', (name,)).fetchall()
        return None if len(res) == 0 else {'name': res[0][0], 'bunches': pickle.loads(res[0][1])}

    def is_cached(self, name):
        res = self.cursor.execute('SELECT COUNT(1) FROM cache WHERE name == ? LIMIT 1', (name,)).fetchall()
        return False if res[0][0] == 0 else True

    def close(self):
        self.db.close()
