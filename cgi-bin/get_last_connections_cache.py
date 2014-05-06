#!/usr/bin/python
# -*- coding: utf-8 -*-


def get_file_name():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        file_name = cfg.get("last_connections", "last_connections_file")
        return file_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options were not found at config file.")

if __name__ == '__main__':

    try:
        file_name = get_file_name()

        with open(file_name, "r") as f:
            conns = f.read()

        print 'Content-Type: application/json'
        print 'Access-Control-Allow-Origin: *'
        print 'Access-Control-Allow-Methods: GET'
        print ''
        print conns
    except Exception, e:
        import sys
        print 'Status: 500 Internal Error'
        print ''
        print e.message
        sys.exit()
