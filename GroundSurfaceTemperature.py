# -*- coding: utf-8 -*-

"""
***************************************************************************
    GroundSurfaceTemperature.py
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

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.outputs.OutputRaster import OutputRaster

from processing.parameters.ParameterRange import ParameterRange
from processing.parameters.ParameterNumber import ParameterNumber
from processing.parameters.ParameterRaster import ParameterRaster

import sys
from osgeo import gdal

import numpy
import numpy.ma as ma


def Hc(Ta, K, Qs):
    # Snow depth Critical
    if Ta >= 0:
        return 0.001
    else:
        return abs(Ta) * (K / Qs)

def Ts_analysis(Hn,Ta,K,Qs):
  #
  if Hn == 0:
      return Ta
  elif Hn >= Hc(Ta, K, Qs):
      return 0
  else:
      if Ta < 0:
          return Ta + (Qs * Hn / K)
      else:
          return 0

Ts_ARRAY = numpy.frompyfunc(Ts_analysis, 4, 1)

def stats(data, bandOut):
    # stats
    masked_data = ma.masked_less_equal(data, -3.4e+38)
    data_min = float(masked_data.min())
    data_max = float(masked_data.max())
    data_std = numpy.std(masked_data)
    bandOut.SetStatistics(
                data_min,
                data_max,
                numpy.mean([data_max, data_min]),
                data_std)


class GroundSurfaceTemperature:

    def __init__(self, Hn_path, Ta_path, K, Qs, Ts_path):
        gdal.AllRegister()

        self.Hn = gdal.Open(str(Hn_path))
        self.Ta = gdal.Open(str(Ta_path))
        self.K = K
        self.Qs = Qs

        # image parameters
        self.rows = self.Hn.RasterYSize
        self.cols = self.Hn.RasterXSize
        self.geoTransform = self.Hn.GetGeoTransform()
        self.projection = self.Hn.GetProjection()
        self.data_type = self.Hn.GetRasterBand(1).DataType

        driver = self.Hn.GetDriver()
        self.imageOut = driver.Create(
                                str(Ts_path),
                                self.cols,
                                self.rows,
                                1,               # Image Bands
                                self.data_type)
        self.data = None

    def compute(self):
        """  """
        Hn_data = self.Hn.GetRasterBand(1).ReadAsArray(0, 0, self.cols, self.rows)
        Ta_data = self.Ta.GetRasterBand(1).ReadAsArray(0, 0, self.cols, self.rows)

        data = Ts_ARRAY(Hn_data, Ta_data, self.K, self.Qs).astype(numpy.float)

        # remove invalid points
        mask = numpy.greater(Hn_data, -3.4e+38)
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
            self.imageOut.SetGeoTransform(self.geoTransform)
            self.imageOut.SetProjection(self.projection)

            ## build pyramids for the output
            gdal.SetConfigOption('HFA_USE_RRD', 'YES')
            self.imageOut.BuildOverviews(overviewlist=[2,4,8,16])


class GroundSurfaceTemperatureAlgorithm(GeoAlgorithm):

    # input parameters
    Hn = "Hn"
    Ta = "Ta"
    K  = "K"
    Qs = "Qs"

    # output parameters
    Ts = "Ts"

    def defineCharacteristics(self):
        self.name = "Ground surface Temperature"
        self.group = "[permaclim]"

        self.addParameter(ParameterRaster(
                            GroundSurfaceTemperatureAlgorithm.Hn,
                            "Snow heigth (m)"))
        self.addParameter(ParameterRaster(
                            GroundSurfaceTemperatureAlgorithm.Ta,
                            u"Air temperature (°C)"))
        self.addParameter(ParameterNumber(
                            GroundSurfaceTemperatureAlgorithm.K,
                            u"Thermal conductivity of the snow (W m^-1 °C^-1)",
                            default=0.16))
        self.addParameter(ParameterNumber(
                              GroundSurfaceTemperatureAlgorithm.Qs,
                              "Sensible heat flux",
                              default=0.86))
        self.addOutput(OutputRaster(
                            GroundSurfaceTemperatureAlgorithm.Ts,
                            "Surface Temperature"))


    def processAlgorithm(self, progress):

        hn_path = self.getParameterValue(GroundSurfaceTemperatureAlgorithm.Hn)
        ta_path = self.getParameterValue(GroundSurfaceTemperatureAlgorithm.Ta)
        k = self.getParameterValue(GroundSurfaceTemperatureAlgorithm.K)
        qs = self.getParameterValue(GroundSurfaceTemperatureAlgorithm.Qs)

        ts_path = self.getOutputValue(GroundSurfaceTemperatureAlgorithm.Ts)

        with GroundSurfaceTemperature(hn_path, ta_path, k, qs, ts_path) as gst:
            gst.compute()