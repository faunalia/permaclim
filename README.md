Introduction
------------

  The package add the following algorithms to 'processing' (was 'sexante'):

  - Band mean: given a tiff with the weekly values (no limit on bands) returns
    a layer with the mean of specified bands.

  - Monthly mean: given a tiff with the weekly values (52 bands) returns
    a layer with the mean of specified month in the year.

  - Snow height by slope: given the snow height and a slope layer returns
    a layer with the snow weighted with the SAF function.

  - Ground surface temperature: given the snow heigth, air temperature,
    Qs and K will return the ground surface temperature as in the article
       "PERMACLIM: a model for the distribution of mountain permafrost,
          based on climatic observations"  
        by Mauro Guglielmin, Barbara Aldighieri, Bruno Testa


Install
-------

  Permaclim is installed as standard qgis plugin. The algoritms will be
  available in 'processing'.

  - extract the repository in <home>/.qgis2/python/plugins:

        $ git clone git://github.com/faunalia/permaclim.git <home>/.qgis/python/plugins/

  - install numpy and gdal python libraries.

      - tested with:

        - python-numpy Version: 1:1.6.1-6ubuntu1
        - python-gdal Version: 1.7.3-6ubuntu3
        
  - enable 'processing' plugin from the qgis interface

  - enable 'permaclim' plugin from the qgis interface


Models
------

  With the plugin are provides two models:

  - "Analysys 1" computes the ground surface temperature based on the 
	snow heigth

  - "Analysys 2" computes the ground surface temperature based on the 
	snow heigth estimated through the slope.

  The models must be copied in <home>/.qgis2/processing/models/ directory.


Testing
-------

  To run the unit tests:

        $ export PYTHONPATH=<home>/.qgis2/python/plugins:/usr/share/qgis/python/plugins
        $ cd <home>/.qgis2/python/plugins/permaclim
        $ python tests.py


Credits
-------

  Developed for ARPA Piemonte (Dipartimento Tematico Geologia e Dissesto)
  within the project PERMANET.
