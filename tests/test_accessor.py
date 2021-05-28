# -*- coding: utf-8 -*-

import pandas_x

import unittest

import pandas as pd
import pandas.testing as tm
import numpy as np


def my_func(series_a, time=None, scalar_kwarg=10):
  if time is None:
    time = pd.Series(range(len(series_a)))

  return series_a * time * scalar_kwarg


class TestRegister(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    pandas_x.PositionAccessor._add_series_method(my_func)
    # pandas_x.PositionAccessor._add_series_method(my_func, kwds='scalar_kwarg')

    cls.vals = [1.0, 1.0, 1.0]
    cls.expected_result_vals = [0.0, 10.0, 20.0]
    
  @classmethod
  def tearDownClass(cls):
    delattr(pandas_x.PositionAccessor, 'my_func')

  def test_api(self):
    pass

  def test_args(self):

    # default column name
    for kwargs in [
      {},
      {'series_a': 'series_a'},
      # {'series_a':'ser_a'}
    ]:
      result = pd.DataFrame.from_dict(
        {'series_a': self.vals}
      ).pos.my_func(**kwargs)
      expected = pd.Series(
        self.expected_result_vals,
        # name=kwargs.get('displacement') or 'displacement'
      )
      tm.assert_series_equal(result, expected)

    # specify alternate column name
    result = pd.DataFrame.from_dict(
      {'ser_a': self.vals}
    ).pos.my_func(series_a='ser_a')
    expected = pd.Series(
      self.expected_result_vals,
      # name=kwargs.get('displacement') or 'displacement'
    )
    tm.assert_series_equal(result, expected)

  def test_raises(self):
    # specify wrong column label
    with self.assertRaises(KeyError):
      result = pd.DataFrame.from_dict({'ser_a': [1,2,3]}).pos.my_func()
    with self.assertRaises(KeyError):
      result = pd.DataFrame.from_dict(
        {'series_a': [1,2,3]}
      ).pos.ds_from_s(series_a='ser_a')

    # wrong dtype
    with self.assertRaisesRegex(AttributeError, 'numeric'):
      pd.DataFrame.from_dict({'series_a': ['a', 'b', 'c']}).pos.my_func()

  def test_opt_args(self):
    # ACCIDENTALLY discovered something here (no time kwarg should exist)
    # result = pd.DataFrame.from_dict({
    #   'series_a': self.vals,
    #   'series_b': [3, 3, 3]
    # }).pos.my_func(time='time')
    # expected = pd.Series(self.expected_result_vals) 
    # tm.assert_series_equal(result, expected)

    result = pd.DataFrame.from_dict({
      'series_a': self.vals,
      'series_b': [3, 3, 3]
    }).pos.my_func(time='series_b')
    expected = pd.Series([val * 10 * 3 for val in self.vals])
    tm.assert_series_equal(result, expected)

  def test_scalar_kwarg(self):
    result = pd.DataFrame.from_dict(
      {'series_a': self.vals}
    ).pos.my_func(scalar_kwarg=20)
    expected = pd.Series(self.expected_result_vals) * 2
    tm.assert_series_equal(result, expected)


class TestMethods(unittest.TestCase):
  def test_s_from_ds(self):
    # The displacement value at a given index represents the distance
    # traveled between the previous index and the current index.
    result = pd.DataFrame.from_dict({
      'displacement': [3.0, 4.0, 3.0, 5.0],
    }).pos.s_from_ds()
    expected = pd.Series([3.0, 7.0, 10.0, 15.0])
    # expected = pd.Series([0.0, 3.0, 7.0, 10.0])
    tm.assert_series_equal(result, expected)

  def test_ds_from_s(self):
    result = pd.DataFrame.from_dict({
      'distance': [3.0, 7.0, 10.0, 15.0],
    }).pos.ds_from_s()
    expected = pd.Series([3.0, 4.0, 3.0, 5.0])
    tm.assert_series_equal(result, expected)

  def test_s_from_v(self):
    # TODO: make a uniform scheme for indexing between-index quantities
    # like displacement, speed, and grade.

    # The speed at a given index is expected to affect the calculated
    # displacement between that index and the next one, and thus affect
    # only the distance at the *next* index. The speed at the last index
    # does not affect the calculated distances (in this scheme).
    # 
    # There are a bajillion ways to go from speed to displacement and 
    # vice-versa, this one is just my choice for now.
    # 
    # Main issue for me: speed and displacement schemes are not consistent.
    df = pd.DataFrame.from_dict({
      'speed': [3.0, 4.0, 3.0, 5.0],
      'time': [0, 2, 4, 6]
    })
    result_notime = df.pos.s_from_v()
    expected = pd.Series([0.0, 3.0, 7.0, 10.0])
    tm.assert_series_equal(result_notime, expected)

    result_time = df.pos.s_from_v(time='time')
    tm.assert_series_equal(result_time, expected * 2)

  def test_v_from_s(self):
    df = pd.DataFrame.from_dict({
      'distance': [0.0, 3.0, 7.0, 10.0],
      'time': [0, 2, 4, 6]
    })
    result_notime = df.pos.v_from_s()

    # What would we expect that last speed to be??
    # In this scheme, there is one more value to fill in than we have
    # info for...seems like a case of extrapolation. Hmm.
    # expected = pd.Series([4.0, 3.0, 5.0, np.nan])
    expected = pd.Series([3.0, 4.0, 3.0, 3.0])  # ffill as extrapolation
    tm.assert_series_equal(result_notime, expected)

    result_time = df.pos.v_from_s(time='time')
    tm.assert_series_equal(result_time, expected / 2)
  
  def test_v_from_ds(self):
    df = pd.DataFrame.from_dict({
      'displacement': [3.0, 4.0, 3.0, 5.0],
      'time': [0, 2, 4, 6]
    })
    result_notime = df.pos.v_from_ds()

    # What would we expect that first speed to be??
    # In this scheme, the first timedelta isn't available. We could bfill 
    # the timedeltas, aka assuming the first timedelta is the same as the
    # second, but idk. Lots of wrinkles.
    # Displacements at [i] represent the distance from [i-1] to [i], while
    # speeds at [i] represent the distance from [i] to [i+1]
    # expected = pd.Series([4.0, 3.0, 5.0, np.nan])
    expected = pd.Series([4.0, 3.0, 5.0, 5.0]) # ffill as extrapolation
    tm.assert_series_equal(result_notime, expected)

    result_time = df.pos.v_from_ds(time='time')
    tm.assert_series_equal(result_time, expected / 2)

  def test_ds_from_xy(self):
    df = pd.DataFrame.from_dict({
      'lat': [40.0, 40.00001, 40.00015, 40.00020],
      'lon': [-105, -105, -105, -105]
    })

    result = df.pos.ds_from_xy()
    self.assertEqual(result.iloc[0], 0.0)
    self.assertAlmostEqual(result.iloc[1] * 14, result.iloc[2])

  def test_reduced_point_index(self):

    # 0.00001 degrees is about 1.1 meters.
    df = pd.DataFrame.from_dict({
      'lat': [40.0, 40.00001, 40.00015, 40.00020],
      'lon': [-105, -105, -105, -105]
    })
    
    result = df.pos.reduced_point_index()
    expected = [True, False, True, True]
    self.assertEqual(result, expected)

    result_short = df.pos.reduced_point_index(min_dist=1)
    expected_short = [True, True, True, True]
    self.assertEqual(result_short, expected_short)

    result_long = df.pos.reduced_point_index(min_dist=30.0)
    expected_long = [True, False, False, True]
    self.assertEqual(result_long, expected_long)


if __name__ == '__main__':
  unittest.main()