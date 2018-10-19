#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
import logging

topics = dict(summary=1, actions=2, commands=4,
              process=0,    # scheduler backend
              scheduler=0,  # interaction with scheduler
              tools=0,      # instantiation of tools
              features=0,   # creation and manipulation of features
              rules=0,      # declaration of rules (including implicit ones)
              config=0,     # any config-related activity
              test=0)       # any testing-related activity


class ProfileFormatter(logging.Formatter):
    """If the given record contains a `time` field and it is a non-negative
    value, add its value to the log output."""

    def format(self, record):
        s = super(ProfileFormatter, self).format(record)
        time = record.time if hasattr(record, 'time') else -1.
        if time >= 0.:
            s += '\t (time={} s)'.format(time)
        return s


def setup(log=[], loglevel=None, debug=False, silent=False, profile=False):

    # if debugging is enabled, print everything...
    if debug:
        logging.basicConfig(format='%(name)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s')
        if log:  # if loggers are set by name...
            for l in log:
                logging.getLogger(l).setLevel(level=logging.INFO)
        elif loglevel is not None:  # if loggers are enabled by level...
            for n, l in topics.items():
                if loglevel & l:
                    logging.getLogger(n).setLevel(level=logging.INFO)
        elif not silent:
            # by default, enable summary and actions logger only
            logging.getLogger('summary').setLevel(level=logging.INFO)
            logging.getLogger('actions').setLevel(level=logging.INFO)
    if profile:
        h = logging.StreamHandler()
        h.setFormatter(ProfileFormatter())
        c = logging.getLogger('commands')
        c.handlers[:] = []  # hack !
        c.addHandler(h)
        c.propagate = False
        # `-p` implies `--log=commands`
        c.setLevel(level=logging.INFO)
