#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import init
from . import main
from . import application
from . import resource_rc  # noqa F401
import faber
from faber.project import buildinfo, project, config
from faber.module import module
import os.path
import signal

# reset standard signal handler (PyQt disabled it).
signal.signal(signal.SIGINT, signal.SIG_DFL)


version = faber.version
__version__ = version


def run(builddir, srcdir, rc):

    app = application.Application(['atelier'])

    info = buildinfo(builddir, srcdir)
    # give the user a chance to review paths and options, ...
    view = init.Init(info)
    if not view.exec_():
        return True
    # ...load the global config, ...
    if rc:
        config(os.path.expanduser(rc))
    elif os.path.exists(os.path.expanduser('~/.faber')):
        config(os.path.expanduser('~/.faber'))
    # ...as well as the project-specific one, ...
    localconf = os.path.join(info.srcdir, '.faberrc')
    if os.path.exists(localconf):
        config(localconf)
    # ...and start the main window
    with project(info) as proj:
        m = module('', proj.srcdir, proj.builddir)
        view = main.Main(m)
        view.show()
        app.exec_()
        view.terminate()
        del view
