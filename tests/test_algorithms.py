# -*- coding: utf-8 -*-

import unittest

import pandas as pd
import pandas.testing as tm
import numpy as np

from pandas_xyz import algorithms as algs


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


class TestResampleDist(unittest.TestCase):
  def test_runs(self):
    df = pd.DataFrame(dict(
      distance=[0, 10, 15, 20, 25, 30],
      elevation=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0] 
    ))

    result = algs.resample_dist(
      df,
      on='distance',  # default
      sample_len=5.0,  # default
      bound_lo=None,  # default
      bound_hi=None,  # default
    )
    self.assertIsInstance(result, pd.DataFrame)
    self.assertIsInstance(result.index, pd.RangeIndex)
    self.assertFalse(result['distance'].isnull().any())
    self.assertFalse(result['elevation'].isnull().any())

    result = algs.resample_dist(
      df,
      sample_len=10.0,
    )
    self.assertFalse(result['distance'].isnull().any())
    self.assertFalse(result['elevation'].isnull().any())

  def test_raises(self):
    df = pd.DataFrame(dict(
      distance=[0, 10, 5],
      elevation=[1.0, 2.0, 3.0] 
    ))
    self.assertRaises(ValueError, algs.resample_dist, df)
    

if __name__ == '__main__':
  unittest.main()