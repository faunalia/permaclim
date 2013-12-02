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

import os
from PyQt4 import QtGui

from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.algs.AddTableField import AddTableField

#
from BandMean import BandMean
from MonthlyMean import MonthlyMean
from SnowDistributionBySlope import SnowDistributionBySlope
from GroundSurfaceTemperature import GroundSurfaceTemperatureAlgorithm
from GroundSurfaceTemperatureTime import GroundSurfaceTemperatureTimeAlgorithm

class PermaclimAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.alglist = [
            BandMean(),
            MonthlyMean(),
            SnowDistributionBySlope(),
            GroundSurfaceTemperatureAlgorithm(),
            GroundSurfaceTemperatureTimeAlgorithm(),
        ]

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)

    def unload(self):
        AlgorithmProvider.unload(self)


    def getName(self):
        return "permaclim"

    def getDescription(self):
        return "Permaclim algorithms"

    def getIcon(self):
        return AlgorithmProvider.getIcon(self)
        
    def _loadAlgorithms(self):
        self.algs = self.alglist

    def supportsNonFileBasedOutput(self):
        return True
