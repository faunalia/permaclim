import os
import unittest
import tempfile

import gdal
from gdalconst import *
import numpy

from MonthlyMean import Mean

"""
To run tests:
  $ export PYTHONPATH=/home/axa/.qgis/python/plugins:/usr/share/qgis/python/plugins
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

if __name__ == '__main__':
    unittest.main()
