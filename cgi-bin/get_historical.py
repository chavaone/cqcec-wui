#!/usr/bin/python
# -*- coding: utf-8 -*-


import sqlite3
import json


def get_bd_name():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        bd_name = cfg.read("historical", "bd_name")
        return bd_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_historic(bd_name):
    tries = 0
    while tries < 10:
        try:
            with sqlite3.connect(bd_name) as conn:
                cons = conn.execute("SELECT time, conns from Historico" + \
                                    " ORDER BY time").fetchall()
                return [{"time": x[0], "conns": x[1]} for x in cons]
        except:
            import time
            time.sleep(1)
            tries = tries + 1
    raise Exception("Database not available.")


if __name__ == '__main__':

    try:
        bd_name = get_bd_name()
        conns = get_historic(bd_name)
        print 'Content-Type: application/json'
        print 'Access-Control-Allow-Origin: *'
        print 'Access-Control-Allow-Methods: GET'
        print ''
        print json.dumps(conns)
    except Exception, e:
        import sys
        print 'Status: 500 Internal Error'
        print ''
        print e.message
        sys.exit()
