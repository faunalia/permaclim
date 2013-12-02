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

import os, sys, shutil
import inspect

from PyQt4 import QtGui
from PyQt4.QtCore import *

from qgis.core import *

from processing.core.Processing	import Processing
from processing.modeler.ModelerUtils import ModelerUtils

from permaclim import version
from permaclim.PermaclimAlgorithmProvider import PermaclimAlgorithmProvider


cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class PermaclimProviderPlugin:

    def __init__(self):
        self.provider = PermaclimAlgorithmProvider()
        return
        settings = QSettings()
        version_settings = settings.value( "/version", '')
        current_version = version()

        if version_settings != current_version:
            settings.setValue("/version", current_version)

            models_src_path = os.path.join(cmd_folder, 'models')
            models_dst_path = ModelerUtils.modelsFolder()

            for name in os.listdir(models_src_path):
                file_src_path = os.path.join(models_src_path, name)
                file_dst_path = os.path.join(models_dst_path, name)
                if os.path.exists(file_dst_path):
                    shutil.move(file_dst_path, file_dst_path+'.old')
                shutil.copy(file_src_path, file_dst_path)

    def initGui(self):
        Processing.addProvider(self.provider)
        Processing.updateAlgsList()  # until a better way is found
        
    def unload(self):
        Processing.removeProvider(self.provider)
