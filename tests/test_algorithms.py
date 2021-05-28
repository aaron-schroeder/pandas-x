# -*- coding: utf-8 -*-

import unittest

import pandas as pd
import pandas.testing as tm
import numpy as np

from pandas_x import algorithms as algs


class TestAlgorithms(unittest.TestCase):

  def test_displacement(self):
    """Test out my distance algorithm with hand calcs."""

    lon = pd.Series([0.0, 0.0, 0.0])
    lon_ew = pd.Series([0.0, 1.0, 2.0])
    lat = pd.Series([0.0, 0.0, 0.0])
    lat_ns = pd.Series([0.0, 1.0, 2.0])

    disp_ew = algs.ds_from_xy(lat, lon_ew)
    self.assertIsInstance(disp_ew, pd.Series)
    tm.assert_series_equal(
      disp_ew, 
      6371000 * 1.0 * np.pi / 180 * pd.Series([0, 1, 1]),
    )

    disp_ns = algs.ds_from_xy(lat_ns, lon)
    self.assertIsInstance(disp_ns, pd.Series)
    tm.assert_series_equal(
      disp_ns,
      6371000 * 1.0 * np.pi / 180 * pd.Series([0, 1, 1]),
    )

  def test_clean_series(self):
    lat = pd.Series([np.nan, 40.0, np.nan, np.nan, 41.0, np.nan])
    
    lat_clean = algs._clean_series(lat)

    self.assertFalse(lat_clean.isna().any())

    with self.assertRaises(ValueError):
      algs._clean_series(pd.Series([np.nan, np.nan, np.nan]))


if __name__ == '__main__':
  unittest.main()