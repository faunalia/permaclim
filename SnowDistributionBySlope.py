# -*- coding: utf-8 -*-

"""
***************************************************************************
    SnowDistributionBySlope.py
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
import sys

from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.outputs import OutputRaster

from processing.algs.gdal.GdalUtils import GdalUtils

from processing.core.parameters import ParameterRange
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterRaster

from osgeo import gdal
import numpy

from GroundSurfaceTemperature import stats

def SAF(x):
    if x < 0:
        saf = 0
    elif x <= 18:
        saf = -0.001 * (x*x) + 0.0289 * x + 0.8
    elif x <= 41:
        saf = -0.0006 * (x*x) + 0.0021 * x + 1.1435
    elif x <= 60:
        #saf = 0.00004 * (x*x) - 0.00109 * x + 0.6803
        saf = 2.00000000e-04 * (x*x) - 2.60000000e-02 * x +   1.02000000e+00
    else:
        saf = 0
    return saf

# Non-discontinuos version of SAF
"""
def SAF(x):
    if x < 0:
        saf = 0
    elif x <= 18:
        saf = 1
    elif x <= 41:
        saf = -4.94071146e-04 * (x*x) - 1.28458498e-03 * x + 1.18320158e+00
    elif x <= 60:
        saf = 2.57309942e-04 * (x*x) - 3.23040936e-02 * x + 1.19192982e+00
    else:
        saf = 0
    return saf
"""

SAF_ARRAY = numpy.frompyfunc(SAF, 1, 1)


class HnBySlope:

    def __init__(self, slope_path, hn_path, output_path):
        gdal.AllRegister()

        self.slope = gdal.Open(str(slope_path))
        self.hn = gdal.Open(str(hn_path))

        self.rows = min(self.slope.RasterYSize, self.hn.RasterYSize)
        self.cols = min(self.slope.RasterXSize, self.hn.RasterXSize)
        self.data_type = self.hn.GetRasterBand(1).DataType

        driver = self.slope.GetDriver()
        self.imageOut = driver.Create(
                                str(output_path),
                                self.cols,
                                self.rows,
                                1,
                                self.data_type)
        self.data = None

    def compute(self):
        """ see SAF """
        slope_data = self.slope.GetRasterBand(1).ReadAsArray(0, 0, self.cols, self.rows)
        hn_data = self.hn.GetRasterBand(1).ReadAsArray(0, 0, self.cols, self.rows)

        saf_coeff = SAF_ARRAY(slope_data).astype(numpy.float)
        data = numpy.multiply(hn_data, saf_coeff)

        # remove invalid areas
        mask = numpy.greater_equal(data, 0)
        self.data = numpy.choose(mask, (-3.4e+38, data))

    def __enter__(self):
        return  self

    def __exit__(self,exc_type, exc_val, exc_tb):

        if self.data is not None:
            # create the output image
            bandOut = self.imageOut.GetRasterBand(1)
            bandOut.SetNoDataValue(-3.4e+38)
            stats(self.data, bandOut)
            bandOut.WriteArray(self.data, 0, 0)
            bandOut.FlushCache()

            # set the geotransform and projection on the output
            self.imageOut.SetGeoTransform(self.slope.GetGeoTransform())
            self.imageOut.SetProjection(self.slope.GetProjection())

            ## build pyramids for the output
            gdal.SetConfigOption('HFA_USE_RRD', 'YES')
            self.imageOut.BuildOverviews(overviewlist=[2,4,8,16])


class SnowDistributionBySlope(GeoAlgorithm):

    SLOPE = "SLOPE"
    HN = "HN"
    OUTPUT = "OUTPUT"

    def defineCharacteristics(self):
        self.name = "Distribution of snow based on slope"
        self.group = "[permaclim]"
        self.addParameter(ParameterRaster(SnowDistributionBySlope.SLOPE, "Slope"))
        self.addParameter(ParameterRaster(SnowDistributionBySlope.HN, "Snow heigth"))
        self.addOutput(OutputRaster(SnowDistributionBySlope.OUTPUT, "Snow height based on slope"))

    def processAlgorithm(self, progress):
        slope_path = self.getParameterValue(SnowDistributionBySlope.SLOPE)
        hn_path = self.getParameterValue(SnowDistributionBySlope.HN)
        output_path = self.getOutputValue(SnowDistributionBySlope.OUTPUT)

        with HnBySlope(slope_path, hn_path, output_path) as hbs:
            hbs.compute()
