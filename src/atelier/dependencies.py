#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtGui import QIcon


class SvgView(QGraphicsView):

    def __init__(self, parent, filename):
        super(SvgView, self).__init__(parent)

        self.setScene(QGraphicsScene(self))
        # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        # self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        s = self.scene()
        s.clear()
        self.resetTransform()
        svgItem = QGraphicsSvgItem(filename)
        svgItem.setFlags(QGraphicsItem.ItemClipsToShape)
        svgItem.setCacheMode(QGraphicsItem.NoCache)
        svgItem.setZValue(0)
        s.addItem(svgItem)
        s.setSceneRect(svgItem.boundingRect().adjusted(-10, -10, 10, 10))


class Dependencies(QMainWindow):
    def __init__(self, filename):
        super(Dependencies, self).__init__()
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.view = SvgView(self, filename)
        self.setCentralWidget(self.view)
        self.setWindowTitle("Atelier dependency viewer")
        self.resize(self.view.sizeHint() + QSize(80, 80))
