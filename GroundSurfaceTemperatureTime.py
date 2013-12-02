# -*- coding: utf-8 -*-

"""
***************************************************************************
    GroundSurfaceTemperatureTime.py
    ---------------------
    Date                 : May 2013
    Copyright            : (C) 2013 by Rocco Pispico
    Email                : rocco dot pispico at arpa dot piemonte dot it
    Note                 : based on GroundSurfaceTemperature.py by
                           Riccardo Lemmi
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Rocco Pispico'
__date__ = 'May 2013'
__copyright__ = '(C) 2013, Rocco Pispico'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os

from PyQt4 import QtGui
from processing.core.GeoAlgorithm import GeoAlgorithm

from processing.outputs.OutputRaster import OutputRaster
from processing.gdal.GdalUtils import GdalUtils

from processing.parameters.ParameterRange import ParameterRange
from processing.parameters.ParameterNumber import ParameterNumber
from processing.parameters.ParameterRaster import ParameterRaster

import sys
from osgeo import gdal

import numpy
import numpy.ma as ma


def HcT0(Ta, K, Qs):
    # Snow depth Critical
    if Ta < 0:
        return abs(Ta) * (K / Qs)
    else:
        raise Exception("Positive Ta temperature not expected")

def TsT0_analysis(T0,Hn,Ta,K,Qs):
  #
  if Hn == 0:
      return T0
  elif Hn >= HcT0(Ta, K, Qs):
      return 0
  else:
      if Ta < 0:
          # return (Ta - Qs / (K * Hn))
          return (abs(Ta) - (Qs / (K * Hn))) * -1.0
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


class GroundSurfaceTemperatureTime:

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


class GroundSurfaceTemperatureTimeAlgorithm(GeoAlgorithm):

    # input parameters
    T0 = "T0"
    Hn = "Hn"
    Ta = "Ta"
    K  = "K"
    Qs = "Qs"

    # output parameters
    Ts = "Ts"

    def defineCharacteristics(self):
        self.name = "Ground surface Temperature Time"
        self.group = "[permaclim]"
        self.addParameter(ParameterRaster(
                            GroundSurfaceTemperatureTimeAlgorithm.T0,
                            "T0 Reference"))
        self.addParameter(ParameterRaster(
                            GroundSurfaceTemperatureTimeAlgorithm.Hn,
                            "Snow heigth (m)"))
        self.addParameter(ParameterRaster(
                            GroundSurfaceTemperatureTimeAlgorithm.Ta,
                            u"Air temperature (°C)"))
        self.addParameter(ParameterNumber(
                            GroundSurfaceTemperatureTimeAlgorithm.K,
                            u"Thermal conductivity of the snow (W m^-1 °C^-1)",
                            default=0.16))
        self.addParameter(ParameterNumber(
                            GroundSurfaceTemperatureTimeAlgorithm.Qs,
                            "Sensible heat flux",
                            default=0.86))
        self.addOutput(OutputRaster(
                            GroundSurfaceTemperatureTimeAlgorithm.Ts,
                            "Surface Temperature"))

    def processAlgorithm(self, progress):

        t0_path = self.getParameterValue(GroundSurfaceTemperatureTimeAlgorithm.T0)
        hn_path = self.getParameterValue(GroundSurfaceTemperatureTimeAlgorithm.Hn)
        ta_path = self.getParameterValue(GroundSurfaceTemperatureTimeAlgorithm.Ta)
        k = self.getParameterValue(GroundSurfaceTemperatureTimeAlgorithm.K)
        qs = self.getParameterValue(GroundSurfaceTemperatureTimeAlgorithm.Qs)

        ts_path = self.getOutputValue(GroundSurfaceTemperatureTimeAlgorithm.Ts)

        with GroundSurfaceTemperatureTime(t0_path, hn_path, ta_path, k, qs, ts_path) as gst:
            gst.compute()
