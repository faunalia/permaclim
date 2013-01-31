# -*- coding: utf-8 -*-

"""
***************************************************************************
    Mean.py
    ---------------------
    Date                 : January 2013
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
__date__ = 'January 2013'
__copyright__ = '(C) 2013, Riccardo Lemmi'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.outputs.OutputRaster import OutputRaster

from sextante.parameters.ParameterRange import ParameterRange
from sextante.parameters.ParameterNumber import ParameterNumber
from sextante.parameters.ParameterRaster import ParameterRaster

from MonthlyMean import Mean

class BandMean(GeoAlgorithm):

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    FIRST_BAND = "FIRST_BAND"
    LAST_BAND = "LAST_BAND"

    def defineCharacteristics(self):
        self.name = "Mean based on band indexes"
        self.group = "[permaclim]"
        self.addParameter(ParameterRaster(BandMean.INPUT, "Weekly mean layer"))
        self.addParameter(ParameterNumber(BandMean.FIRST_BAND, "First Band", default=1))
        self.addParameter(ParameterNumber(BandMean.LAST_BAND, "Last Band", default=2))
        self.addOutput(OutputRaster(BandMean.OUTPUT, "Layer with the mean of the choosed bands"))

    def processAlgorithm(self, progress):
        input_path = self.getParameterValue(BandMean.INPUT)
        output_path = self.getOutputValue(BandMean.OUTPUT)
        first_band = self.getParameterValue(BandMean.FIRST_BAND)
        last_band = self.getParameterValue(BandMean.LAST_BAND)
        with Mean(input_path, output_path) as mm:
            mm.compute(range(first_band, last_band+1))
