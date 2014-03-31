#!/usr/bin/python
# -*- coding: utf-8 -*-

# "CQCEC"
# Copyright (C) 2014  Marcos Chavarria Teijeiro.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from cqcec_lib import fetchers
from cqcec_lib import ipserviceinfo


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


def get_router_ip():
    import socket
    import struct
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def get_proto_from_port(port, transport_proto):
    import socket
    try:
        return socket.getservbyport(int(port), transport_proto.lower())
    except Exception:
        return str(port) + "/" + str(transport_proto)


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
    return (ipserviceinfo.ip_is_me(ip) or ipserviceinfo.ip_is_local(ip)) and \
        not ip.startswith("127.") and not ipserviceinfo.ip_is_multicast(ip)


def router_connections():
    hitron_config = read_hitron_config()
    ip_router = get_router_ip()
    mac_router = ipserviceinfo.get_mac_from_local_ip(ip_router)

    if mac_router[:8] in ("00:26:5b", "68:b6:fc"):
        client = fetchers.HitronConnectionsFetcher(hitron_config["user"],
                                                   hitron_config["pass"],
                                                   ip_router)
    else:
        raise NotImplementedError("Router not supported.")

    router_connections = client.get_connections()

    return [{"ip_origen": x.ip_orig,
             "ip_dest": x.ip_dest,
             "proto": get_proto_from_port(x.port_dest
                                          if x.dir == "Outgoing"
                                          else x.port_orig, x.proto),
             "direction": x.dir}
            for x in router_connections]


def add_conn_to_dict(dicionario, conn):
    direct = conn["direction"]
    lista = dicionario[conn["ip_origen"]][direct] if direct == "Outgoing" \
            else dicionario[conn["ip_dest"]][direct]
    try:
        ext_conn = lista[lista.index(conn)]
        ext_conn.number = ext_conn.number + 1
    except ValueError:
        lista.append(conn)


def filter_and_sort_connections(connections):
    ips_out = [x["ip_origen"] for x in connections if x["direction"] == "Outgoing"]
    ips_dest = [x["ip_dest"] for x in connections if x["direction"] == "Incoming"]
    ips = list(set(ips_out + ips_dest))
    ips = filter(ip_is_insteresting, ips)

    ret_conn_dict = {x: {"Outgoing": [], "Incoming": []} for x in ips}

    for c in connections:
        add_conn_to_dict(ret_conn_dict, c)

    for x in ret_conn_dict:
        ip_info = ipserviceinfo.get_ip_info(x)
        ret_conn_dict[x]["hostname"] = ip_info["hostname"] if "hostname" in ip_info and ip_info["hostname"] else "unknown hostname"
        ret_conn_dict[x]["vendor"] = ip_info["mac_vendor"] if "mac_vendor" in ip_info and ip_info["mac_vendor"] else "unknown mac  vendor"

    return ret_conn_dict


def print_connections(connections):
    import json
    import sys

    print 'Content-Type: application/json'
    print 'Access-Control-Allow-Origin: *'
    print 'Access-Control-Allow-Methods: GET'
    print ''
    print json.dumps(connections)
    sys.exit()


def print_error(e):
    import sys

    print 'Status: 500 Internal Error'
    print ''
    print e.message
    sys.exit()


def print_not_implemented_error():
    import sys

    print 'Status: 501 Not implemented'
    print ''
    sys.exit()


if __name__ == '__main__':
    try:
        connections = router_connections()
        connections = filter_and_sort_connections(connections)
        print_connections(connections)
    except NotImplementedError:
        print_not_implemented_error()
    except Exception, e:
        print_error(e)
