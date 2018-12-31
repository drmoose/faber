#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .settings_ui import Ui_settings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog


class Settings(QDialog):

    def __init__(self):

        super(Settings, self).__init__()
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.ui = Ui_settings()
        self.ui.setupUi(self)
