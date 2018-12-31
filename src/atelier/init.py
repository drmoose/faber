#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .init_ui import Ui_init
from . import feature
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog


class Init(QDialog):
    """Initialize the configuration of a build directory.

    The creation of the info object will already have taken care of some basic
    validation (srcdir and builddir are valid, if provided).

    A few remaining use-cases are worth calling out:

    1) srcdir is given, builddir not

       Any new builddir pick needs to refer either to a new (empty or nonexistent)
       directory, or one that is compatible with the srcdir.

    2) builddir is given, srcdir not

       This implies the builddir is new, so we can treat it as 3)

    3) neither srcdir nor builddir are given

       Whenever srcdir changes, validate the builddir
       - if builddir is not valid, ask to change it (or reset it ?)

       Whenever builddir changes, validate the srcdir
       - if srcdir is not valid, as to change it
       - re-generate the options and parameters listing
    """

    def __init__(self, info):
        super(Init, self).__init__()
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.info = info
        self.srcdir = info.srcdir
        self.builddir = info.builddir
        self.ui = Ui_init()
        self.ui.setupUi(self)
        self.ui.srcdir_value.setCurrentText(self.info.srcdir)
        self.ui.browse_srcdir.clicked.connect(self.select_srcdir)
        self.ui.builddir_value.setCurrentText(self.info.builddir)
        self.ui.browse_builddir.clicked.connect(self.select_builddir)
        self.ui.srcdir_value.currentTextChanged.connect(self.set_srcdir)
        self.ui.builddir_value.currentTextChanged.connect(self.set_builddir)
        self.ui.parameters.itemSelectionChanged.connect(self.enable_remove_parameter_button)
        self.ui.add_parameter.clicked.connect(self.add_parameter)
        self.ui.remove_parameter.setEnabled(False)
        self.ui.remove_parameter.clicked.connect(self.remove_parameter)
        self.ui.parameters.set(dict(self.info.parameters.items()))
        self.ui.enable_parameters.stateChanged.connect(self.expand_parameters)
        if not self.info.parameters.items():
            self.ui.enable_parameters.setChecked(False)
        self.ui.options.itemSelectionChanged.connect(self.enable_remove_option_button)
        self.ui.add_option.clicked.connect(self.add_option)
        self.ui.remove_option.setEnabled(False)
        self.ui.remove_option.clicked.connect(self.remove_option)
        self.ui.options.set(dict(self.info.options.items()))
        self.ui.enable_options.stateChanged.connect(self.expand_options)
        if not self.info.options.items():
            self.ui.enable_options.toggle()
        self.ui.run.setEnabled(bool(self.info.srcdir and self.builddir))
        self.ui.cancel.clicked.connect(self.cancel)
        self.ui.run.clicked.connect(self.run)
        if self.info.srcdir:
            self.ui.builddir_value.setFocus()
        else:
            self.ui.srcdir_value.setFocus()

    def expand_parameters(self):

        if self.ui.parameters.isVisible():
            self.ui.parameters.hide()
            self.ui.add_parameter.hide()
            self.ui.remove_parameter.hide()
        else:
            self.ui.parameters.show()
            self.ui.add_parameter.show()
            self.ui.remove_parameter.show()

    def expand_options(self):

        if self.ui.options.isVisible():
            self.ui.options.hide()
            self.ui.add_option.hide()
            self.ui.remove_option.hide()
        else:
            self.ui.options.show()
            self.ui.add_option.show()
            self.ui.remove_option.show()

    def enable_remove_parameter_button(self):
        enabled = self.ui.parameters.get_selection() is not None
        self.ui.remove_parameter.setEnabled(enabled)

    def enable_remove_option_button(self):
        enabled = self.ui.options.get_selection() is not None
        self.ui.remove_option.setEnabled(enabled)

    def add_parameter(self):
        f = feature.Feature()
        if f.exec_():
            self.ui.parameters.append(*f.get_feature())

    def remove_parameter(self):
        row = self.ui.parameters.get_selection()
        self.ui.parameters.remove(row)

    def add_option(self):
        f = feature.Feature()
        if f.exec_():
            self.ui.options.append(*f.get_feature())

    def remove_option(self):
        row = self.ui.options.get_selection()
        self.ui.options.remove(row)

    def cancel(self):
        self.done(0)

    def run(self):
        self.info.parameters = self.ui.parameters.data()
        self.info.options = self.ui.options.data()
        self.done(1)

    def select_srcdir(self):
        """Start a dialog to select a srcdir."""
        options = QFileDialog.Options(QFileDialog.ShowDirsOnly)
        options |= QFileDialog.ExistingFile
        srcdir = QFileDialog.getExistingDirectory(None,
                                                  'Select source directory',
                                                  self.info.srcdir,
                                                  options=options)
        self.ui.srcdir_value.setCurrentText(srcdir)
        if not self.builddir:
            # as a convenience, initialize the builddir to be the same
            self.ui.builddir_value.setCurrentText(srcdir)

    def set_srcdir(self, srcdir):
        self.info.srcdir = srcdir
        self.ui.run.setEnabled(bool(self.srcdir and self.builddir))

    def select_builddir(self):
        """Start a dialog to select a builddir."""
        options = QFileDialog.Options(QFileDialog.ShowDirsOnly)
        builddir = QFileDialog.getExistingDirectory(None,
                                                    'Select build directory',
                                                    self.builddir,
                                                    options=options)
        self.ui.builddir_value.setCurrentText(builddir)

    def set_builddir(self, builddir):
        self.builddir = builddir
        self.ui.run.setEnabled(bool(self.srcdir and self.builddir))

    def parameters(self):
        return {f[0]: f[1] for f in self.ui.parameters.data()}

    def options(self):
        return {f[0]: f[1] for f in self.ui.options.data()}
