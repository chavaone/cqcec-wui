#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import time


def get_file_name():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        file_name = cfg.get("daemon", "last_connections_file")
        return file_name
    except ConfigParser.NoOptionError:
        raise ValueError("Some options (last_connections:last_connections_file) were not found at config file.")


def get_pid_filename():
    import ConfigParser
    cfg = ConfigParser.ConfigParser()
    cfg.read(["/etc/cqcec_config.cfg"])

    try:
        pid_file = cfg.get("daemon", "pid_file")
        return pid_file
    except ConfigParser.NoOptionError:
        raise ValueError("Some options (last_connections:pid_file) were not found at config file.")


def get_pid():
    pid_file = get_pid_filename()

    with open(pid_file, "r") as f:
        return int(f.read())


def force_update(pid):
    import os
    import signal
    os.kill(pid, signal.SIGUSR1)


if __name__ == '__main__':

    try:
        file_name = get_file_name()

        begin_time = int(time.time())
        first_time = int(os.path.getmtime(file_name))

        pid = get_pid()
        force_update(pid)

        while int(os.path.getmtime(file_name)) == first_time and \
              int(time.time()) - begin_time < 30:
            time.sleep(2)

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
