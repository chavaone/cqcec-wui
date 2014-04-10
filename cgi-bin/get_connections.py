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
from cqcec_lib import networkmapfetcher
from cqcec_lib import dnscachefetcher


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
        if port != "":
            return str(port) + "/" + str(transport_proto)
        else:
            return str(transport_proto)


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


def router_networkmap():
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


def filter_and_sort_connections(connections, dns_dict):
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


def add_connections(networkmap, connections):
    for ip in connections:
        if ip in networkmap:
            networkmap[ip]["Outgoing"] = connections[ip]["Outgoing"]
            networkmap[ip]["Incoming"] = connections[ip]["Incoming"]


def add_mac_vendor(networkmap):
    for ip in networkmap:
        networkmap[ip]["vendor"] = ipserviceinfo.get_device_manufacter_from_mac(networkmap[ip]["hardware_mac"])

if __name__ == '__main__':
    try:
        connections = router_connections()
        dns_dict = router_dns_cache()
        connections = filter_and_sort_connections(connections, dns_dict)
        networkmap = router_networkmap()
        add_connections(networkmap, connections)
        add_mac_vendor(networkmap)
        print_connections(networkmap)
    except NotImplementedError:
        print_not_implemented_error()
    except Exception, e:
        print_error(e)
