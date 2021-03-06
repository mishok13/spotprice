#!/usr/bin/env python

import logging as log
import kazoo

from kazoo.client import KazooClient
from kazoo.handlers.threading import TimeoutError

class Zookeeper(object):
    """ class to interact with zookeeper, and some wrappers for setting and getting data """
            
    def __init__(self, connection=None, zookeeperhost=None):
        if not zookeeperhost and not connection:
            log.fatal("you must supply either a valid zookeeper url OR a zookeeper connection to initialize the zookeeper class")
            
        self.connection = connection if connection else self.create_connection(zookeeperhost)

    def create_connection(self, zookeeperhost):
        try:
            connection = KazooClient(hosts=zookeeperhost)
            connection.start(timeout=5)
            
        except TimeoutError:
            log.fatal("making zookeeper connection timed out")
            self.connection = None
            
        return connection
    
    def create_node(self, zkpath, value=None):
        log.debug("creating this zkpath: %s and setting it to this value: %s" % (zkpath, value))
        
        try:
            self.connection.ensure_path(zkpath)
            self.connection.create(zkpath, value)
        
        except kazoo.exceptions.NodeExistsError:
            pass
        
    def set_node(self, zkpath, value):
        self.connection.ensure_path(zkpath)
        self.connection.set(zkpath, str(value))
        
    def node_exists(self, zkpath):
        return self.connection.exists(zkpath)
                    
    def fetch_node(self, zknode, return_stat=False):
        rawdata, stat = self.connection.get(zknode)
        
        try:
            data = rawdata.decode("utf-8")
        
        except AttributeError:
            log.debug("error parsing zk_data as utf-8")
            if return_stat:
                return rawdata, stat
            else:        
                return rawdata
        
        if return_stat:
            return data, stat
        else:
            return data
    
    def stop_connection(self):
        return self.connection.stop()
