# -*- coding: utf-8 -*-

"""
***************************************************************************
    PSWESpeed.py
    ---------------------
    Date                 : May 2014
    Copyright            : (C) 2014 by Riccardo Lemmi
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
__date__ = 'May 2014'
__copyright__ = '(C) 2014, Riccardo Lemmi'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'


from osgeo import gdal, ogr
import numpy

import utils

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.outputs import OutputVector


from processing.core.parameters import ParameterRaster
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterNumber


class PSProjectionToolAlg:
    # Computation of the horizontal speed

    def __init__(
            self,
            ps_input_path,
            aspect_input_path,
            slope_input_path,
            exp_alos,
            exp_blos,
            exp_clos,
            ps_proj_path):

        self.ps_input_path = ps_input_path

        self.aspect_input_path = aspect_input_path
        self.slope_input_path = slope_input_path

        self.exp_alos = exp_alos
        self.exp_blos = exp_blos
        self.exp_clos = exp_clos

        self.ps_proj_path= ps_proj_path


    def compute(self):
        #

        ps_ds = ogr.Open(self.ps_input_path)
        output_proj_ds = ogr.GetDriverByName("ESRI Shapefile").CopyDataSource(ps_ds, self.ps_proj_path)

        utils.addFieldManagement(output_proj_ds, "ALOS", ogr.OFTReal)
        utils.addFieldManagement(output_proj_ds, "BLOS", ogr.OFTReal)
        utils.addFieldManagement(output_proj_ds, "CLOS", ogr.OFTReal)

        utils.calculateFieldManagement(output_proj_ds, "ALOS", self.exp_alos)
        utils.calculateFieldManagement(output_proj_ds, "BLOS", self.exp_blos)
        utils.calculateFieldManagement(output_proj_ds, "CLOS", self.exp_clos)

        aspect_ds = gdal.Open(self.aspect_input_path, gdal.GA_ReadOnly)
        utils.setFieldFromRasterPoints(aspect_ds, output_proj_ds, "ASPECT")

        slope_ds = gdal.Open(self.slope_input_path, gdal.GA_ReadOnly)
        utils.setFieldFromRasterPoints(slope_ds, output_proj_ds, "SLOPE")

        formula = "[VEL]*(1/(((cos(([slope]/57.29)))*(sin((([aspect]-90)/57.29)))*[ALOS])+((-1)*(cos(([slope]/57.29)))*(cos((([aspect]-90)/57.29)))*[BLOS])+((sin(([slope]/57.29)))*[CLOS])))"
        utils.addFieldManagement(output_proj_ds, "VEL_PRJ", ogr.OFTReal)
        utils.real_CalculateField_management(
                output_proj_ds,
                "VEL_PRJ",
                formula,
                ['VEL', 'slope', 'aspect', 'ALOS', 'BLOS', 'CLOS'])

        self._save(output_proj_ds)


    #
    def _save(self, output_proj_ds):
        output_proj_ds = None            # close the file

    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class PSProjectionToolDDIRGeoAlg(GeoAlgorithm):
    """ was PS_projection_tools.py """

    PS_INPUT = "PS_INPUT"       # Starting dataset: speed? -> SHP

    ASPECT_INPUT = "ASPECT_INPUT"     # Raster
    SLOPE_INPUT = "SLOPE_INPUT"       # Raster

    WEST_ANGLE = "WEST_ANGLE"
    INCIDENCE_ANGLE = "INCIDENCE_ANGLE"
    CELL_SIZE = "CELL_SIZE"

    EXP_ALOS = "EXP_ALOS"
    EXP_BLOS = "EXP_BLOS"
    EXP_CLOS = "EXP_CLOS"

    PS_PROJ_PATH = "PS_PROJ_PATH"

    def defineCharacteristics(self):
        self.name = "Model to compute speed projection for PS points"
        self.group = "[pstools]"

        self.addParameter(ParameterVector(PSProjectionToolGeoAlg.PS_INPUT,
                                          "Starting Dataset"))

        self.addParameter(ParameterRaster(PSProjectionToolGeoAlg.ASPECT_INPUT,
                                          "Aspect"))
        self.addParameter(ParameterRaster(PSProjectionToolGeoAlg.SLOPE_INPUT,
                                          "Slope"))


        self.addParameter(ParameterNumber(PSProjectionToolGeoAlg.EXP_ALOS,
                                          "Cosine Director in x",
                                          minValue=0.0,
                                          maxValue=1.0,
                                          default=0.6))
        self.addParameter(ParameterNumber(PSProjectionToolGeoAlg.EXP_BLOS,
                                          "Cosine Director in y",
                                          minValue=0.0,
                                          maxValue=1.0,
                                          default=0.5))
        self.addParameter(ParameterNumber(PSProjectionToolGeoAlg.EXP_CLOS,
                                          "Cosine Director in h",
                                          minValue=0.0,
                                          maxValue=1.0,
                                          default=0.8))

        self.addOutput(OutputVector(PSProjectionToolGeoAlg.PS_PROJ_PATH,
                                    "Speed Projection respect aspect and slope"))

    def processAlgorithm(self, progress):
        """ """

        ps_input_path = str(self.getParameterValue(PSProjectionToolGeoAlg.PS_INPUT))

        aspect_input_path = str(self.getParameterValue(PSProjectionToolGeoAlg.ASPECT_INPUT))
        slope_input_path = str(self.getParameterValue(PSProjectionToolGeoAlg.SLOPE_INPUT))

        exp_alos = self.getParameterValue(PSProjectionToolGeoAlg.EXP_ALOS)
        exp_blos = self.getParameterValue(PSProjectionToolGeoAlg.EXP_BLOS)
        exp_clos = self.getParameterValue(PSProjectionToolGeoAlg.EXP_CLOS)

        ps_proj_path = str(self.getOutputValue(PSProjectionToolGeoAlg.PS_PROJ_PATH))

        with PSProjectionToolAlg(
                ps_input_path,
                aspect_input_path,
                slope_input_path,
                exp_alos,
                exp_blos,
                exp_clos,
                ps_proj_path) as ps_proj_alg:
            ps_proj_alg.compute()
