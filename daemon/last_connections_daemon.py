#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sqlite3
import time
import signal
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


def get_file_name():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        file_name = cfg.get("last_connections", "last_connections_file")
        return file_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_pid_filename():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        pid_file = cfg.get("last_connections", "pid_file")
        return pid_file
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def print_pid():
    import os
    pid_file = get_pid_filename()

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))


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


def connection_is_interesting(conn):
    if conn.dir == "Outgoing":
        return ipserviceinfo.ip_is_local(conn.ip_orig) and \
               not ipserviceinfo.ip_is_multicast(conn.ip_orig) and \
               not ipserviceinfo.ip_is_me(conn.ip_orig)
    else:
        return ipserviceinfo.ip_is_local(conn.ip_dest) and \
               not ipserviceinfo.ip_is_multicast(conn.ip_dest) and \
               not ipserviceinfo.ip_is_me(conn.ip_dest)


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
             "domain_orig": ipserviceinfo.get_domain_info(x.ip_orig, dns_dict),
             "domain_dest": ipserviceinfo.get_domain_info(x.ip_dest, dns_dict),
             "size_in": x.size_in,
             "size_out": x.size_out,
             "time": x.time}
            for x in lista if not (ipserviceinfo.ip_is_multicast(x.ip_dest) or
                                   ipserviceinfo.ip_is_multicast(x.ip_orig))]


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


def get_last_reg_conns(bd_name, index):
    tries = 0
    while tries < 10:
        try:
            with sqlite3.connect(bd_name) as conn:
                cons = conn.execute("SELECT time,conns from Historico" +
                                    " ORDER BY time DESC").fetchmany(index + 1)
                if len(cons) <= index:
                    return (-1, [])
                return (cons[-1][0], json.loads(cons[-1][1],
                                                object_hook=connection_json_load))
        except Exception, e:
            import time
            time.sleep(1)
            tries = tries + 1
    raise Exception("Database not available:: " + e.message)


def get_last_conns(bd_name):
    import time
    curr_connections = router_connections()
    ret = []
    i = 0
    curr_time = int(time.time())

    while len(ret) < 40 and curr_connections and i < 10:
        time, last_connections = get_last_reg_conns(bd_name, i)
        if not last_connections:
            break
        for c in curr_connections:
            if c not in last_connections:
                c.time = curr_time - time
                ret.append(c)
                curr_connections.remove(c)
        i = i + 1
    return ret


def write_conn():
    global last_time
    bd_name = get_historical_bd_name()
    file_name = get_file_name()
    conns = get_last_conns(bd_name)
    dns_dict = router_dns_cache()
    conns = filter_and_sort_connections(conns, dns_dict)
    last_time = int(time.time())
    with open(file_name, "w") as f:
        f.write(json.dumps(conns))
    print "Write Last Connections."


def force_write(signum, stack):
    write_conn()

if __name__ == '__main__':

    last_time = 0
    signal.signal(signal.SIGUSR1, force_write)
    print_pid()

    while True:
        if int(time.time()) - last_time < 300:
            time.sleep(30)
            continue
        write_conn()

