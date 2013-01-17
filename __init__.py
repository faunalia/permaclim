# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
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
"""

def name():
    return "SEXTANTE Permaclim provider"

def description():
    return "Expose Permaclim algorithms to SEXTANTE."

def author():
    return "Riccardo Lemmi (for Faunalia)"

def authorName(): # for compatibility only
    return author()

def email():
    return "riccardo@reflab.com"

def version():
    return "0.1"

def icon():
    return "icon.png"

def qgisMinimumVersion():
    return "1.0"

def classFactory(iface):
    from permaclim.SextantePermaclimProviderPlugin import SextantePermaclimProviderPlugin
    return SextantePermaclimProviderPlugin()