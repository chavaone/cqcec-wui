#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
from cqcec_lib import ipserviceinfo
import json
import sys


def print_error():
    print 'Status: 400 Bad request'
    print ''
    sys.exit()


def pring_ip_info(ip_info):
    print 'Content-Type: application/json'
    print 'Access-Control-Allow-Origin: *'
    print 'Access-Control-Allow-Methods: GET'
    print ''
    print json.dumps(ip_info)
    sys.exit()


if __name__ == '__main__':

    arguments = cgi.FieldStorage()

    if "ip" not in arguments:
        print_error()

    ip_info = ipserviceinfo.get_ip_info(arguments["ip"].value)
    ip_info = {key: ip_info[key] for key in ip_info if ip_info[key]}

    pring_ip_info(ip_info)
