# -*- coding: utf-8 -*-

"""
***************************************************************************
    MonthlyMean.py
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

from PyQt4 import QtGui
from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.outputs.OutputRaster import OutputRaster
import os
from sextante.gdal.GdalUtils import GdalUtils
from sextante.core.SextanteUtils import SextanteUtils

from sextante.parameters.ParameterRange import ParameterRange
from sextante.parameters.ParameterNumber import ParameterNumber
from sextante.parameters.ParameterRaster import ParameterRaster

import sys
import gdal
from gdalconst import *
import numpy

import calendar


class MonthUtils:

    MONTHS = range(1,13)

    def _compute_weeks_for_months(self, current_year):

        weeks_in_months = []
        weekCounter = 0
        for month_index in self.MONTHS:
            monthcalendar = calendar.monthcalendar(current_year, month_index)
            days_in_week = [len([1 for day in weeks if day]) for weeks in monthcalendar]
            # if a weekly chuck has more than 4 days we'll keep it and count it as a full week
            weeks_in_current_month = sum(1 for daycount in days_in_week if daycount > 3)
            # since the assumption of 4 days is somewhat random, let's doublecheck
            # the number of weeks
            weekCounter = weekCounter + weeks_in_current_month
            if (weekCounter > 52):
                weeks_in_months.append(52 - (weekCounter - weeks_in_current_month))
            else:
                weeks_in_months.append(weeks_in_current_month)

        weekIndex = 1
        week_indexes_for_months = []
        for index in self.MONTHS:
            week_indexes_for_months.append([])
            for _ in range(weeks_in_months[index-1]):
                # add each week into the monthly raster
                week_indexes_for_months[index-1].append(weekIndex)
                weekIndex += 1

        return week_indexes_for_months

    def weeks_for(self, year, month):
        return dict(zip(self.MONTHS, self._compute_weeks_for_months(year)))[month]

utils = MonthUtils()


class Mean:

    def __init__(self, input_path, output_path, number_bandsOut=1):
        gdal.AllRegister()

        self.imageIn = gdal.Open(input_path)
        self.rows = self.imageIn.RasterYSize
        self.cols = self.imageIn.RasterXSize
        self.data_type = self.imageIn.GetRasterBand(1).DataType
        driver = self.imageIn.GetDriver()
        self.imageOut = driver.Create(
                                output_path,
                                self.cols,
                                self.rows,
                                number_bandsOut,
                                self.data_type)

    def _saveMean(self, band_number, mean):
        # create the output image
        bandOut = self.imageOut.GetRasterBand(band_number)
        bandOut.SetNoDataValue(-99)
        bandOut.WriteArray(mean, 0, 0)
        bandOut.FlushCache()

    def compute(self, band_numbers, band_out=1):

        bandsIn = [self.imageIn.GetRasterBand(n) for n in band_numbers]
        datas = [band.ReadAsArray(0, 0, self.cols, self.rows) for band in bandsIn]

        t_mean = sum(datas)/len(datas)
        mask = numpy.greater(t_mean, -numpy.Inf)
        self.mean = numpy.choose(mask, (-99, t_mean))

        self._saveMean(band_out, self.mean)

    def __enter__(self):
        return  self

    def __exit__(self,exc_type, exc_val, exc_tb):
        # set the geotransform and projection on the output
        self.imageOut.SetGeoTransform(self.imageIn.GetGeoTransform())
        self.imageOut.SetProjection(self.imageIn.GetProjection())

        ## build pyramids for the output
        gdal.SetConfigOption('HFA_USE_RRD', 'YES')
        self.imageOut.BuildOverviews(overviewlist=[2,4,8,16])


class MonthlyMean(GeoAlgorithm):

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    YEAR = "YEAR"
    MONTH = "MONTH"

    def defineCharacteristics(self):
        self.name = "Monthly Mean"
        self.group = "[permaclim]"
        self.addParameter(ParameterRaster(MonthlyMean.INPUT, "Weekly mean layer"))
        self.addParameter(ParameterNumber(MonthlyMean.YEAR, "Year of the layer", default=2001))
        self.addParameter(ParameterNumber(MonthlyMean.MONTH, "Month", 1, 12, 1))
        self.addOutput(OutputRaster(MonthlyMean.OUTPUT, "Layer with the mean of the choosed month"))

    def processAlgorithm(self, progress):
        input_path = self.getParameterValue(MonthlyMean.INPUT)
        output_path = self.getOutputValue(MonthlyMean.OUTPUT)
        year = self.getParameterValue(MonthlyMean.YEAR)
        month = self.getParameterValue(MonthlyMean.MONTH)
        with Mean(input_path, output_path) as mm:
            mm.compute(utils.weeks_for(year, month))
