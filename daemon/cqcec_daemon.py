#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import signal
from cqcec_lib import ipserviceinfo


#Get Config...

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


def get_historical_bd_name():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        bd_name = cfg.get("daemon", "hist_bd_name")
        return bd_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_file_name_last_conns():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        file_name = cfg.get("daemon", "last_connections_file")
        return file_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_file_name_networkmap():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        file_name = cfg.get("daemon", "network_map_file")
        return file_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


def get_pid_filename():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        pid_file = cfg.get("daemon", "pid_file")
        return pid_file
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")


#Save info to files.

def print_pid():
    import os
    pid_file = get_pid_filename()

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))


def print_last_connections(last_connections):
    last_conns_file_name = get_file_name_last_conns()

    with open(last_conns_file_name, "w") as f:
        f.write(json.dumps(last_connections))
    print "Writing Last Connections info"


def print_networkmap(networkmap):
    network_map_file_name = get_file_name_networkmap()

    with open(network_map_file_name, "w") as f:
        f.write(json.dumps(networkmap))
    print "Writing Networkmap info"


def insert_hist_data(bd_name, conns):
    import sqlite3
    from cqcec_lib import connectioninfo

    with sqlite3.connect(bd_name) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS Historico (time int, conns text)")
        conn.commit()

    with sqlite3.connect(bd_name) as conn:
        c = conn.cursor()
        time_value = int(time.time())
        c.execute("INSERT INTO Historico values (:time, :value)",
                  {"time": time_value, "value": json.dumps(conns,
                   default=connectioninfo.ConnectionInfo.json_dump)})

        if conn.execute("SELECT count() from Historico") \
           .fetchone()[0] > 2000:
            c.execute("DELETE FROM Historico WHERE time =(SELECT min(time) from Historico)")

        conn.commit()
    print "Insert historic into DB."


#Utils...

def get_proto_from_port(port, transport_proto):
    import socket
    try:
        return socket.getservbyport(int(port), transport_proto.lower())
    except Exception:
        if port != "":
            return str(port) + "/" + str(transport_proto)
        else:
            return str(transport_proto)


def get_router_ip():
    import socket
    import struct
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


#Fetchers...

def router_dns_cache():
    from cqcec_lib import dnscachefetcher
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
    from cqcec_lib import fetchers
    from cqcec_lib import ipserviceinfo

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


def router_networkmap():
    from cqcec_lib import networkmapfetcher
    ip_router = get_router_ip()
    mac_router = ipserviceinfo.get_mac_from_local_ip(ip_router)

    if mac_router[:8] in ("00:26:5b", "68:b6:fc"):
        hitron_config = read_hitron_config()
        client = networkmapfetcher.HitronNetworkMapFetcher(hitron_config["user"],
                                                           hitron_config["pass"],
                                                           ip_router)
    else:
        raise NotImplementedError("Router not supported.")

    return client.get_networkmap()


#Filters...

def ip_is_reachable(ip):
    import subprocess
    import sys
    try:
        sys.stderr.write("Ping " + ip + "\n")
        subprocess.check_output(["ping", "-c 1", ip])
        sys.stderr.write("Done!\n")
        return True
    except:
        return False


def ip_is_insteresting(ip):
    return ipserviceinfo.ip_is_local(ip) and not ipserviceinfo.ip_is_multicast(ip)


def connection_is_interesting(conn):
    if conn.dir == "Outgoing":
        return ipserviceinfo.ip_is_local(conn.ip_orig) and \
               not ipserviceinfo.ip_is_multicast(conn.ip_orig) and \
               not ipserviceinfo.ip_is_me(conn.ip_orig)
    else:
        return ipserviceinfo.ip_is_local(conn.ip_dest) and \
               not ipserviceinfo.ip_is_multicast(conn.ip_dest) and \
               not ipserviceinfo.ip_is_me(conn.ip_dest)


#Utils...

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


def connection_json_load(dic):
    from cqcec_lib import connectioninfo
    c = connectioninfo.ConnectionInfo(dic["ip_orig"], dic["port_orig"],
                                      dic["ip_dest"], dic["port_dest"],
                                      dic["proto"], dic["dir"],
                                      dic["size_in"], dic["size_out"])
    return c


def add_connections(networkmap, connections):
    for ip in connections:
        if ip in networkmap:
            networkmap[ip]["Outgoing"] = connections[ip]["Outgoing"]
            networkmap[ip]["Incoming"] = connections[ip]["Incoming"]


def add_mac_vendor(networkmap):
    for ip in networkmap:
        networkmap[ip]["vendor"] = ipserviceinfo.get_device_manufacter_from_mac(networkmap[ip]["hardware_mac"])


#Sort connections.

def filter_and_sort_last_connections(connections, dns_dict):

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


def filter_and_sort_nm_connections(connections, dns_dict):
    ips_out = [x.ip_orig for x in connections if x.dir == "Outgoing"]
    ips_dest = [x.ip_dest for x in connections if x.dir == "Incoming"]
    ips = list(set(ips_out + ips_dest))
    ips = filter(ip_is_insteresting, ips)

    conn_dict = {x: {"Outgoing": [], "Incoming": []} for x in ips}

    for c in connections:
        try:
            add_conn_to_dict(conn_dict, c)
        except KeyError:
            pass

    ret_conn_dict = {x: {"Outgoing": [], "Incoming": []} for x in ips}

    for ip in conn_dict:
        ret_conn_dict[ip]["Outgoing"] = [{"ip_origen": x.ip_orig,
                                      "ip_dest": x.ip_dest,
                                      "proto": get_proto_from_port(x.port_dest
                                                  if x.dir == "Outgoing"
                                                  else x.port_orig, x.proto),
                                      "direction": x.dir,
                                      "number": x.number,
                                      "islocal": ipserviceinfo.ip_is_local(x.ip_dest),
                                      "domain": ipserviceinfo.get_domain_info(x.ip_dest, dns_dict),
                                      "size_in": x.size_in,
                                      "size_out": x.size_out
                                      }
                                     for x in conn_dict[ip]["Outgoing"]
                                     if not ipserviceinfo.ip_is_multicast(x.ip_dest)]
        ret_conn_dict[ip]["Incoming"] = [{"ip_origen": x.ip_orig,
                                      "ip_dest": x.ip_dest,
                                      "proto": get_proto_from_port(x.port_dest
                                                  if x.dir == "Incoming"
                                                  else x.port_orig, x.proto),
                                      "direction": x.dir,
                                      "number": x.number,
                                      "islocal": ipserviceinfo.ip_is_local(x.ip_orig),
                                      "domain": ipserviceinfo.get_domain_info(x.ip_orig, dns_dict),
                                      "size_in": x.size_in,
                                      "size_out": x.size_out}
                                     for x in conn_dict[ip]["Incoming"]
                                     if not ipserviceinfo.ip_is_multicast(x.ip_orig)]

    return ret_conn_dict


def get_last_reg_conns(bd_name, index):
    import sqlite3
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


def get_last_conns(bd_name, curr_connections):
    import time
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


def task():
    import sys
    global last_time
    global semaphore_mierder
    semaphore_mierder = False
    print "Time :: %s" % time.ctime()
    try:
        dns_dict = router_dns_cache()
        connections = router_connections()
        hist_bd_name = get_historical_bd_name()
    except Exception, e:
        print "ERROR:: ", e

    try:
        last_connections = get_last_conns(hist_bd_name, connections)
        last_connections = filter_and_sort_last_connections(last_connections,
                                                            dns_dict)
        print_last_connections(last_connections)

    except Exception, e:
        print "ERROR:: ", e

    try:
        networkmap_connections = filter_and_sort_nm_connections(connections,
                                                                dns_dict)
        networkmap = router_networkmap()
        add_connections(networkmap, networkmap_connections)
        add_mac_vendor(networkmap)
        print_networkmap(networkmap)
    except Exception, e:
        print "ERROR:: ", e

    try:
        insert_hist_data(hist_bd_name, connections)
    except Exception, e:
        print "ERROR:: ", e

    print "---------\n"

    last_time = int(time.time())
    semaphore_mierder = True


def force_task(signum, stack):
    if semaphore_mierder:
        task()

if __name__ == '__main__':
    import os
    import sys

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    last_time = 0
    semaphore_mierder = True
    signal.signal(signal.SIGUSR1, force_task)
    print_pid()

    while True:
        if int(time.time()) - last_time < 300:
            time.sleep(100)
            continue
        task()
