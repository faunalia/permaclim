import os
import unittest
import tempfile

import gdal
from gdalconst import *
import numpy

from MonthlyMean import Mean
from GroundSurfaceTemperature import GroundSurfaceTemperature, Hc, Ts_analysis

"""
To run tests:
  $ cd ~/.qgis/python/plugins/permaclim
  $ export PYTHONPATH=~/.qgis/python/plugins:/usr/share/qgis/python/plugins
  $ python tests.py

"""

def prepare_input(path, bands):
    # fill the bands with the specified values

    #the extent and shape of my array
    xmin,ymin,xmax,ymax=[0, 0, 9, 9]
    ncols, nrows = [10, 10]
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform=(xmin, xres, 0, ymax, 0, -yres)

    # create image
    driver = gdal.GetDriverByName('GTiff')
    dst = driver.Create(
                    path,
                    ncols,
                    nrows,
                    len(bands),
                    gdal.GDT_Byte)

    for b,v in bands:
        array = v*numpy.ones((10,10))
        bandOut = dst.GetRasterBand(b)
        bandOut.SetNoDataValue(-99)
        bandOut.WriteArray(array, 0, 0)
        bandOut.FlushCache()


class TestMonthlyMean(unittest.TestCase):

    def setUp(self):
        self.input_path = tempfile.mkstemp()[1]
        prepare_input(self.input_path, [(1, 0), (2, 2)])

        self.output_path = tempfile.mkstemp()[1]

    def test_average(self):
        #
        with Mean(self.input_path, self.output_path, ) as mm:
            mm.compute([1,2])
            self.assertEqual(mm.mean[0][0], 1)
            self.assertEqual(os.path.exists(self.output_path), True)

class TestGroundSurfaceTemperature(unittest.TestCase):

    def setUp(self):

        self.snow_path = tempfile.mkstemp()[1]
        prepare_input(self.snow_path, [(1, 0),])

        self.temp_path = tempfile.mkstemp()[1]
        prepare_input(self.temp_path, [(1, 1),])

        self.output_path = tempfile.mkstemp()[1]

    def test_Hc(self):
        self.assertEqual(Hc(-1, 1, 1), 1)
        self.assertRaises(Exception, Hc, (1, 1, 1))

    def test_Ts(self):
        self.assertEqual(Ts_analysis(0,-1, 0,0,), -1)
        self.assertEqual(Ts_analysis(0, 0, 0,0,),  0)
        self.assertEqual(Ts_analysis(0, 1, 0,0,),  1)

    def test_Ts(self):
        # to finish
        with GroundSurfaceTemperature(
                self.snow_path,
                self.temp_path,
                0.3,
                0.83,
                self.output_path, ) as gst:
            gst.compute()
            self.assertEqual(gst.data[0][0], 1)
            self.assertEqual(os.path.exists(self.output_path), True)

if __name__ == '__main__':
    unittest.main()
