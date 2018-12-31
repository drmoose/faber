#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import artefact
from faber.logging import getLogger, logging
# reach into the gory details of the asyncio scheduler
from faber.scheduler import asyncio
from faber.scheduler.artefact import artefact as A

from .main_ui import Ui_main
from .module_ui import Ui_editor
from .artefact_ui import Ui_artefact
from .logging import Handler
from .models import ArtefactTreeModel
from .widgets import CheckableComboBox
from .settings import Settings
from . import application
from PyQt5.QtWidgets import QMenu, QMainWindow, QComboBox, QDialog, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class Main(QMainWindow):

    default_loggers = ['summary', 'actions', 'output']

    class adapter:
        """Receive updates from the scheduler and forward them to the Main instance."""
        def __init__(self, main):
            self.main = main

        def add_prerequisite(self, a, p):
            if p not in self.main.current_artefacts:
                self.main.current_artefacts.add(p)
                self.main.ui.tree.model().insert(p.frontend)
                self.main.ui.progress.increment_max()

        def status(self, a):
            self.main.update_status(a.frontend)

    def __init__(self, module):

        super(Main, self).__init__()
        A.callback = Main.adapter(self)
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.root = module
        self.ui = Ui_main()
        self.ui.setupUi(self)
        # Qt designer can't do this, so we are doing it here:
        self.ui.logo.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.sourcedir_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.builddir_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.sourcedir.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.builddir.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.sourcedir.setText(self.root.srcdir)
        self.ui.builddir.setText(self.root.builddir)
        # Qt designer still can't insert arbitrary widgets into a toolbar,
        # so we have to do it here. (*sigh*)
        self.ui.view = QComboBox(self.ui.toolbar)
        self.ui.view.setObjectName('view')
        self.ui.view.addItem(QIcon(':images/view.svg'), self.tr('view public'))
        self.ui.view.addItem(QIcon(':images/view.svg'), self.tr('view all'))
        self.ui.toolbar.addWidget(self.ui.view)
        self.ui.log = CheckableComboBox(self.ui.toolbar)
        self.ui.log.setObjectName('log')
        self.ui.toolbar.addWidget(self.ui.log)
        self.ui.clean = QPushButton(QIcon(':images/cleanup.svg'), 'clean', self.ui.toolbar)
        clean = QMenu()
        clean.addAction(self.tr('clean'), lambda: self.clean(0))
        clean.addAction(self.tr('clean all'), lambda: self.clean(1))
        self.ui.clean.setMenu(clean)
        self.ui.toolbar.addWidget(self.ui.clean)
        self.ui.stop = QPushButton(QIcon(':images/stop.svg'), None, self.ui.toolbar)
        self.ui.stop.setEnabled(False)
        self.ui.stop.clicked.connect(self.stop)
        self.ui.toolbar.addWidget(self.ui.stop)

        self.setWindowTitle('Atelier: ' + self.root.srcdir)
        self.ui.quit.triggered.connect(self.terminate)
        self.ui.settings.triggered.connect(self.settings)

        model = ArtefactTreeModel()
        self.ui.tree.setModel(model)
        self.ui.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tree.customContextMenuRequested.connect(self.tree_menu)
        self.view_artefacts()  # run default filter
        self.ui.view.activated.connect(self.view_artefacts)
        self.log_handler = Handler(self.ui.output)
        self.ui.log.stateChanged.connect(self.set_logging)
        self.ui.log.model().item(0, 0).setFlags(Qt.NoItemFlags)
        self.loggers = ['actions', 'commands', 'summary', 'output']
        for l in self.loggers:
            self.ui.log.addItem(l, checked=l in Main.default_loggers)
        self.ui.view_public_artefacts.triggered.connect(lambda: self.view_artefacts(0))
        self.ui.view_all_artefacts.triggered.connect(lambda: self.view_artefacts(1))
        self.ui.about.triggered.connect(self.about)
        self.dependencies = None
        self.current_artefacts = None
        self.module_edit = None

    def terminate(self):
        self.log_handler.close()
        application.exit()

    def settings(self):
        view = Settings()
        view.exec_()
        print('changing settings...')

    def view_artefacts(self, index=None):
        from faber.artefact import intermediate, nopropagate, internal, source, conditional
        from faber.artefacts.include_scan import scan

        def is_internal(a):
            return not (a.attrs & internal or
                        a.attrs & intermediate or
                        a.attrs & nopropagate or
                        isinstance(a, conditional) or
                        isinstance(a, scan) or
                        isinstance(a, source))

        all = index == 1
        self.ui.tree.model().set_filter(None if all else is_internal)

    def about(self):
        from . import version
        win = QMessageBox()
        win.setWindowTitle('About Atelier')
        win.setTextFormat(Qt.RichText)
        win.setText('<p><b>Atelier version {}</b></p>'
                    '<p>Copyright (c) 2019 Stefan Seefeld</p>'.format(version))
        win.exec_()

    def set_logging(self, index):
        level = logging.INFO if self.ui.log.itemChecked(index) else logging.ERROR
        getLogger(self.loggers[index - 1]).setLevel(level=level)

    def clean(self, index):
        from faber import scheduler
        from faber import config

        def _reset():
            level = index + 1
            if level > 1:
                config.reset(level)  # remove config cache then...
            # ...reset artefacts
            scheduler.reset()
            scheduler.clean(level)
        self.wait_for(_reset)

    def inspect_artefact(self, a):
        win = QDialog()
        win.setWindowTitle('Artefact viewer')
        win.ui = Ui_artefact()
        win.ui.setupUi(win)
        win.ui.name.setText(a.name)
        win.ui.type.setText(a.__class__.__name__)
        for k, v in a.features._serialize().items():
            # FIXME: why is the feature value sometimes a list, sometimes a string ?
            win.ui.features.append(k, v if type(v) is str else ','.join(v))
        win.exec_()

    def inspect_module(self, m):
        win = QDialog()
        win.setWindowTitle('Module viewer : {}'.format(m.srcdir))
        win.ui = Ui_editor()
        win.ui.setupUi(win)
        win.ui.edit.load(m)
        win.exec_()

    def show_dependencies(self, artefact):
        from .dependencies import Dependencies
        from faber.scheduler import graph
        import tempfile

        a = asyncio.artefacts[artefact]  # fetch backend
        with tempfile.NamedTemporaryFile(suffix='.svg') as file:
            graph.visualize(a, filename=file.name)
            self.view = Dependencies(file.name)
        self.view.show()

    def tree_menu(self, position):

        selected = self.ui.tree.selectedIndexes()
        if not selected:
            return
        index = selected[0]
        data = index.data(Qt.UserRole)
        menu = QMenu()

        async def update(a):
            self.ui.stop.setEnabled(True)
            self.current_artefacts = asyncio.collect(a)
            self.ui.progress.start(len(self.current_artefacts))
            await asyncio.async_update(a)
            asyncio.reset()
            self.ui.stop.setEnabled(False)

        if isinstance(data, artefact):
            menu.addAction(self.tr('inspect'), lambda: self.inspect_artefact(data))
            menu.addAction(self.tr('dependencies'), lambda: self.show_dependencies(data))
            menu.addAction(self.tr('update'), lambda: self.submit(update(data)))
        else:
            menu.addAction(self.tr('inspect'), lambda: self.inspect_module(data))
        menu.exec_(self.ui.tree.viewport().mapToGlobal(position))

    def stop(self):
        pass

    def update_status(self, a):
        self.ui.tree.model().update(a)
        self.ui.progress.increment()
        p = self.ui.progress
        self.ui.statusbar.showMessage(f'{p.value}/{p.max} artefacts updated')

    def submit(self, task):
        application.submit(task)

    def wait_for(self, task):
        application.wait_for(task)
