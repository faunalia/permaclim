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
    # fill the bands with the specified values: (band_index, value)

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
                    gdal.GDT_Float32)

    for b,v in bands:
        array = v*numpy.ones((10,10), dtype=numpy.float32)
        bandOut = dst.GetRasterBand(b)
        bandOut.SetNoDataValue(-99)
        bandOut.WriteArray(array, 0, 0)
        bandOut.FlushCache()


class TestMonthlyMean(unittest.TestCase):

    def setUp(self):
        self.input_path_1 = tempfile.mkstemp()[1]
        prepare_input(self.input_path_1, [(1, 0), (2, 2)])

        self.input_path_2 = tempfile.mkstemp()[1]
        prepare_input(self.input_path_2, [(1, -1), (2, -5)])

        self.output_path = tempfile.mkstemp()[1]

    def test_average(self):
        #
        with Mean(self.input_path_1, self.output_path, ) as mm1:
            mm1.compute([1,2])
            self.assertEqual(mm1.mean[0][0], 1)
            self.assertEqual(os.path.exists(self.output_path), True)

            # stats
            self.assertEqual(mm1.min, 1)
            self.assertEqual(mm1.max, 1)
            self.assertEqual(mm1.std, 0)

        with Mean(self.input_path_2, self.output_path, ) as mm2:
            mm2.compute([1,2])
            self.assertEqual(mm2.mean[0][0], -3)

            # stats
            self.assertEqual(mm2.min, -3)
            self.assertEqual(mm2.max, -3)
            self.assertEqual(mm2.std, 0)


#class TestGroundSurfaceTemperature(unittest.TestCase):

    #def setUp(self):

        #self.snow_path = tempfile.mkstemp()[1]
        #prepare_input(self.snow_path, [(1, 0),])

        #self.temp_path = tempfile.mkstemp()[1]
        #prepare_input(self.temp_path, [(1, 1),])

        #self.output_path = tempfile.mkstemp()[1]

    #def test_Hc(self):
        #self.assertEqual(Hc(-1, 1, 1), 1)
        #self.assertRaises(Exception, Hc, (1, 1, 1))

    #def test_Ts(self):
        #self.assertEqual(Ts_analysis(0,-1, 0,0,), -1)
        #self.assertEqual(Ts_analysis(0, 0, 0,0,),  0)
        #self.assertEqual(Ts_analysis(0, 1, 0,0,),  1)

    #def test_gst(self):
        ## to finish
        #with GroundSurfaceTemperature(
                #self.snow_path,
                #self.temp_path,
                #0.16,
                #0.83,
                #self.output_path, ) as gst:
            #gst.compute()
            #self.assertEqual(gst.data[0][0], 1)
            #self.assertEqual(os.path.exists(self.output_path), True)

if __name__ == '__main__':
    unittest.main()
