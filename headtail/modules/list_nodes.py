# -*- coding: utf-8 -*-

import configparser
import os


class Nodes():
    def __init__(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(os.path.join(os.path.dirname(__file__), os.pardir, 'config', 'list_nodes.cfg'))

    def get_names(self, **kwargs):
        nodes = self.cfg.sections()

        for k, v in kwargs.items():
            v = str(v).lower()
            nodes = list(filter(lambda x: v in map(lambda y: y.strip().lower(), self.cfg[x][k].split(',')), nodes))

        return nodes

    def get_names_locations(self, **kwargs):
        nodes = self.get_names(**kwargs)
        return [(node, self.cfg[node]['location']) for node in nodes]

    def get_ldbnames_locations(self, **kwargs):
        nodes = self.get_names(**kwargs)
        return [(
            self.cfg[node]['ldbname'] if 'ldbname' in self.cfg[node].keys() else node,
            self.cfg[node]['location']
        ) for node in nodes]
