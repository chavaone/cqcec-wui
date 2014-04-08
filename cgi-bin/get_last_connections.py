#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sqlite3
import signal
import os
from cqcec_lib import connectioninfo
from cqcec_lib import ipserviceinfo
from cqcec_lib import fetchers
from cqcec_lib import dnscachefetcher


def get_historical_bd_name():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        bd_name = cfg.get("historical", "bd_name")
        return bd_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_pid_filename():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        pid_file = cfg.get("historical", "pid_file")
        return pid_file
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_pid():
    pid_file = get_pid_filename()

    with open(pid_file, "r") as f:
        s = f.read()
    return int(s)


def read_hitron_config():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        usuario = cfg.get("login_hitron", "usuario")
        password = cfg.get("login_hitron", "password")
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")

    return {"user": usuario, "pass": password}


def get_proto_from_port(port, transport_proto):
    import socket
    try:
        return socket.getservbyport(int(port), transport_proto.lower())
    except Exception:
        if port != "":
            return str(port) + "/" + str(transport_proto)
        else:
            return str(transport_proto)


def ip_is_insteresting(ip):
    return ipserviceinfo.ip_is_local(ip) and not ipserviceinfo.ip_is_multicast(ip)


def add_conn_to_dict(dicionario, conn):
    direct = conn.dir
    lista = dicionario[conn.ip_orig][direct] if direct == "Outgoing" \
            else dicionario[conn.ip_dest][direct]
    try:
        ind = lista.index(conn)
        if lista[ind].number:
            lista[ind].number = lista[ind].number + 1
            lista[ind].size_in = lista[ind].size_in + conn.size_in
            lista[ind].size_in = lista[ind].size_in + conn.size_out
        else:
            lista[ind].number = 2
            lista[ind].size_in = lista[ind].size_in + conn.size_in
            lista[ind].size_in = lista[ind].size_in + conn.size_out
    except ValueError:
        lista.append(conn)


def get_domain_from_dict(d, ip):
    try:
        return d[ip]
    except KeyError:
        return ""


def connection_is_interesting(conn):
    if conn.dir == "Outgoing":
        return ipserviceinfo.ip_is_local(conn.ip_orig) and \
               not ipserviceinfo.ip_is_multicast(conn.ip_orig)
    else:
        return ipserviceinfo.ip_is_local(conn.ip_dest) and \
               not ipserviceinfo.ip_is_multicast(conn.ip_dest)


def filter_and_sort_connections(connections, dns_dict):

    connections = filter(connection_is_interesting, connections)

    lista = []

    for conn in connections:
        try:
            ind = lista.index(conn)
            if lista[ind].number:
                lista[ind].number = lista[ind].number + 1
                lista[ind].size_in = lista[ind].size_in + conn.size_in
                lista[ind].size_in = lista[ind].size_in + conn.size_out
            else:
                lista[ind].number = 2
                lista[ind].size_in = lista[ind].size_in + conn.size_in
                lista[ind].size_in = lista[ind].size_in + conn.size_out
        except ValueError:
            lista.append(conn)

    return [{"ip_origen": x.ip_orig,
             "ip_dest": x.ip_dest,
             "proto": get_proto_from_port(x.port_dest
                                          if x.dir == "Outgoing"
                                          else x.port_orig, x.proto),
             "direction": x.dir,
             "number": x.number,
             "orig_islocal": ipserviceinfo.ip_is_local(x.ip_orig),
             "dest_islocal": ipserviceinfo.ip_is_local(x.ip_dest),
             "domain_orig": get_domain_from_dict(dns_dict, x.ip_orig),
             "domain_dest": get_domain_from_dict(dns_dict, x.ip_dest),
             "size_in": x.size_in,
             "size_out": x.size_out}
            for x in lista if not ipserviceinfo.ip_is_multicast(x.ip_dest)]


def get_router_ip():
    import socket
    import struct
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def router_dns_cache():
    ip_router = get_router_ip()
    mac_router = ipserviceinfo.get_mac_from_local_ip(ip_router)

    if mac_router[:8] in ("00:26:5b", "68:b6:fc"):
        hitron_config = read_hitron_config()
        client = dnscachefetcher.HitronDNSFetcher(hitron_config["user"],
                                                  hitron_config["pass"],
                                                  ip_router)
    else:
        raise NotImplementedError("Router not supported.")

    return client.get_dict()


def router_connections():
    ip_router = get_router_ip()
    mac_router = ipserviceinfo.get_mac_from_local_ip(ip_router)

    if mac_router[:8] in ("00:26:5b", "68:b6:fc"):
        hitron_config = read_hitron_config()
        client = fetchers.HitronConnectionsFetcher(hitron_config["user"],
                                                   hitron_config["pass"],
                                                   ip_router)
    else:
        raise NotImplementedError("Router not supported.")

    return client.get_connections()


def connection_json_load(dic):
    c = connectioninfo.ConnectionInfo(dic["ip_orig"], dic["port_orig"],
                                      dic["ip_dest"], dic["port_dest"],
                                      dic["proto"], dic["dir"],
                                      dic["size_in"], dic["size_out"])
    return c


def get_last_reg_conns(bd_name):
    tries = 0
    while tries < 10:
        try:
            with sqlite3.connect(bd_name) as conn:
                cons = conn.execute("SELECT conns from Historico" +
                                    " ORDER BY time DESC").fetchone()
                return json.loads(cons[0], object_hook=connection_json_load)
        except Exception, e:
            import time
            time.sleep(1)
            tries = tries + 1
    raise Exception("Database not available:: " + e.message)


def get_last_conns(bd_name):
    curr_connections = router_connections()
    last_connections = get_last_reg_conns(bd_name)
    ret = []

    for c in curr_connections:
        if c not in last_connections:
            ret.append(c)
            if len(ret) == 30:
                break
    return ret


if __name__ == '__main__':

    try:
        bd_name = get_historical_bd_name()
        conns = get_last_conns(bd_name)
        dns_dict = router_dns_cache()
        conns = filter_and_sort_connections(conns, dns_dict)
        if len(conns) > 10:
            conns = conns[:10]
        try:
            pid = get_pid()
            os.kill(pid, signal.SIGUSR1)
        except:
            pass
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
