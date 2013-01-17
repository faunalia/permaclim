Introduction
------------

  The package add the following algorithms to sexante:

  - Monthly mean: given a tiff with the weekly values (52 bands) returns
    a layer with the mean of specified month.

  - Snow height by slope: given the snow height and a slope layer returns
    a layer with the snow weighted with the SAF function.

  - Ground surface temperature: given the snow heigth, air temperature,
    Qs and K will return the ground surface temperature as in the article
       "PERMACLIM: a model for the distribution of mountain permafrost,
          based on climatic observations"  by Mauro Guglielmin, Barbara Aldighieri, Bruno Testa


Install
-------

  Permaclim is installed as standard qgis plugin. The algoritms will be
  available in sextante.

  - extract the repository in <home>/.qgis/python/plugins:

        $ git clone git://github.com/faunalia/permaclim.git <home>/.qgis/python/plugins/

  - activate the plugin from the qgis interface

  - the plugin requires numpy and gdal python libraries.


Models
------

  With the plugin are provides two models:

  - "Analysys 1" computes the ground surface temperature based on the snow
    heigth

  - "Analysys 2" computes the ground surface temperature based on the snow
    heigth estimated through the slope.

  The models must be copied in <home>/.qgis/sextante/models/ directory.


Testing
-------

  To run the unit tests:

        $ export PYTHONPATH=<home>/.qgis/python/plugins:/usr/share/qgis/python/plugins
        $ cd <home>/.qgis/python/plugins/permaclim
        $ python tests.py
