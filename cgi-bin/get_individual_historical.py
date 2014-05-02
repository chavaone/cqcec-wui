#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import sys
import json
import sqlite3
from cqcec_lib import connectioninfo


def print_error():
    print 'Status: 400 Bad request'
    print ''
    sys.exit()


def print_dict(dictionary):
    print 'Content-Type: application/json'
    print 'Access-Control-Allow-Origin: *'
    print 'Access-Control-Allow-Methods: GET'
    print ''
    print json.dumps(dictionary)
    sys.exit()


def get_bd_name():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        bd_name = cfg.get("historical", "bd_name")
        return bd_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_historic(bd_name):
    tries = 0
    while tries < 10:
        try:
            with sqlite3.connect(bd_name) as conn:
                cons = conn.execute("SELECT time, conns from Historico" + \
                                    " ORDER BY time").fetchmany(size=1000)
                return [{"time": x[0], "conns": x[1]} for x in cons]
        except:
            import time
            time.sleep(1)
            tries = tries + 1
    raise Exception("Database not available.")


def connection_json_load(dic):
    c = connectioninfo.ConnectionInfo(dic["ip_orig"], dic["port_orig"],
                                      dic["ip_dest"], dic["port_dest"],
                                      dic["proto"], dic["dir"],
                                      dic["size_in"], dic["size_out"])
    return c


def get_stats(ip):
    bd_name = get_bd_name()
    ret = []
    conns = get_historic(bd_name)
    for x in conns:
        conns_time = json.loads(x["conns"], object_hook=connection_json_load)
        num_conns = len(filter(lambda y: (y.dir == "Outgoing" and
                               y.ip_orig == ip) or y.ip_dest == ip, conns_time))
        ret.append({"time": x["time"], "conns": num_conns})
    return ret

if __name__ == '__main__':

    arguments = cgi.FieldStorage()

    if "ip" not in arguments:
        print_error()

    ip_stats = get_stats(arguments["ip"].value)
    print_dict(ip_stats)
