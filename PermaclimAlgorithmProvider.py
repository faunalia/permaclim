# -*- coding: utf-8 -*-

"""
***************************************************************************
    PermaclimAlgorithmProvider.py
    ---------------------
    Date                 : December 2012
    Copyright            : (C) 2012 by Riccardo Lemmi
    Email                : riccardo at reflab dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Riccardo Lemmi'
__date__ = 'December 2012'
__copyright__ = '(C) 2012, Riccardo Lemmi'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from sextante.core.AlgorithmProvider import AlgorithmProvider
from sextante.algs.AddTableField import AddTableField
from PyQt4 import QtGui
import os

#
from MonthlyMean import MonthlyMean
from SnowDistributionBySlope import SnowDistributionBySlope


class PermaclimAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.alglist = [
            MonthlyMean(),
            SnowDistributionBySlope(),
        ]

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)


    def unload(self):
        AlgorithmProvider.unload(self)


    def getName(self):
        return "permaclim"

    def getDescription(self):
        return "Permaclim algorithms"

    #def getIcon(self):
    #    return QtGui.QIcon(os.path.dirname(__file__) + "/../images/toolbox.png")

    def _loadAlgorithms(self):
        self.algs = self.alglist

    def supportsNonFileBasedOutput(self):
        return True