Introduction
------------

  The package add the following algorithms to sexante:

    - monthly mean: given a tiff with the weekly values (52 bands) returns
      a layer with the mean of specified month.

    - Snow height by slope: given the snow height and a slope layer returns
      a layer with the snow weighted with the SAF function.

    - ...


Install
-------

  - extract the repository in <home>/.qgis/python/plugins/sextante:

    $ git clone <home>/.qgis/python/plugins/sextante

  - add to <home>/.qgis/python/plugins/sextante/core/Sextante.py the following
    lines:

    from sextante.permaclim.PermaclimAlgorithmProvider import PermaclimAlgorithmProvider
    ...

    @staticmethod
    def initialize():
        #add the basic providers
        ...
        Sextante.addProvider(PermaclimAlgorithmProvider())
        ...

Testing
-------

  - to run the unit tests:

    $ export PYTHONPATH=<home>/.qgis/python/plugins:/usr/share/qgis/python/plugins
    $ cd <home>/.qgis/python/plugins/sextante/permaclim
    $ python tests.py
