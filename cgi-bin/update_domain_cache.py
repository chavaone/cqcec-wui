#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import sys
from cqcec_lib import cache


def update_cache_client(ip, domain):
    cachefetcher = cache.Cache()
    cachefetcher.set_domain(ip, domain)


def print_error():
    print 'Status: 400 Bad request'
    print ''
    sys.exit()


if __name__ == '__main__':

    arguments = cgi.FieldStorage()

    if "ip" not in arguments:
        print_error()
    if "domain" not in arguments:
        print_error()

    update_cache_client(arguments.getvalue("ip"), arguments.getvalue("domain"))

    print 'Content-Type: application/json'
    print 'Access-Control-Allow-Origin: *'
    print 'Access-Control-Allow-Methods: POST'
    print ''
    print 'OK'