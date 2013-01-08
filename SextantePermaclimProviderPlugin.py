 # -*- coding: utf-8 -*-

"""
***************************************************************************
    SextantePermaclimProviderPlugin.py
    ---------------------
    Date                 : January 2013
    Copyright            : (C) 2013 by Riccardo Lemmi
    Email                : riccardo at reflab dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

Based on https://github.com/faunalia/sextantelwgeomprovider

"""

__author__ = 'Riccardo Lemmi'
__date__ = 'January 2013'
__copyright__ = '(C) 2013, Riccardo Lemmi'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.core import *
import os, sys
import inspect
from sextante.core.Sextante import Sextante
from permaclim.PermaclimAlgorithmProvider import PermaclimAlgorithmProvider

cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class SextantePermaclimProviderPlugin:

    def __init__(self):
        self.provider = PermaclimAlgorithmProvider()

    def initGui(self):
        Sextante.addProvider(self.provider)

    def unload(self):
        Sextante.removeProvider(self.provider)