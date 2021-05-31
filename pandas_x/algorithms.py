# -*- coding: utf-8 -*-
import inspect
import math
import warnings

import numpy as np
import pandas as pd

from . import scalar
from ._decorators import doc, docsub


EARTH_RADIUS_METERS = scalar.EARTH_RADIUS_METERS

_saveme = """
`Numpy docstring ref`_

`Numpy docstring example`_

`Google docstring example`_

`Sphinx todos`_  

Todo: 
  * Update these assumpts!
  * Figure out `Sphinx todos`_!

.. _PEP 484:
  https://www.python.org/dev/peps/pep-0484/
    
.. _Numpy docstring ref:
  https://numpydoc.readthedocs.io/en/latest/format.html

.. _Numpy docstring example:
  https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html

.. _Google docstring example:
  https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

.. _Sphinx todos:
  https://www.sphinx-doc.org/en/master/usage/extensions/todo.html

"""

_docstring_params = dict(
  klass_in='pandas.Series',
  pre_param='',
  pre_param_desc='',
  post_param_desc='',
  pre_return_desc='',
)


def _clean_series(series):
  if series.isna().all():
    raise ValueError(
      'Cannot infer fill values when there are no values at all.'
    )

  return series.fillna(method='bfill').fillna(method='ffill')


@docsub(
  """
Assumptions:
  * Earth is a perfect sphere, with radius = 
    ``pandas_x.scalar.EARTH_RADIUS_METERS``.
  * The point-to-point distances are sufficiently short (so that
    latitude distortion and curvature have limited effects).
    
""",
  **_docstring_params,
  klass_out='pandas.Series',
)
@doc('displacement')
def ds_from_xy(lat, lon):
  """
  The chosen scheme: displacement at [i] represents the distance from [i-1] 
  to [i]. 

  """

  # Convert to radians.
  lat = lat * math.pi / 180
  lon = lon * math.pi / 180

  # Project the spherical coordinates onto a plane.
  dx = EARTH_RADIUS_METERS * np.cos(lat) * lon.diff()
  dy = EARTH_RADIUS_METERS * lat.diff()

  # Calculate point-to-point displacements on the plane.
  ds = (dx ** 2 + dy ** 2) ** 0.5

  # Remove the NaN value in the first position.
  return ds.fillna(0.)


@docsub(
  **_docstring_params,
  klass_out='pandas.Series',
)
@doc('distance')
def s_from_xy(lat, lon):
  return s_from_ds(ds_from_xy(lat, lon))


@docsub(
  **_docstring_params,
  klass_out='pandas.Series',
)
@doc('displacement')
def ds_from_s(distance):
  """
  The chosen scheme: displacement at [i] represents the distance from [i-1] 
  to [i].

  """
  # Should this assume the index at position 0 is 0, or should this
  # assume the only NaN is at position 0? Assumpts either way...
  # Also could accomplish this behavior with bfill. Hmm.
  return distance.diff().fillna(distance[0])


@docsub(
  **_docstring_params,
  klass_out='pandas.Series',
)
@doc('distance')
def s_from_ds(displacement):
  """
  The chosen scheme: displacement at [i] represents the distance from [i-1] 
  to [i]. This scheme means converting displacements to cumulative distances
  does not require any extrapolation.

  """
  return displacement.cumsum()


@docsub(
  **_docstring_params,
  klass_out='pandas.Series',
)
@doc('displacement')
def s_from_v(speed, time=None):
  """
  The chosen scheme: speed at [i] represents the distance from [i] to [i+1].
  This means distance.diff() and time.diff() are shifted by one index from 
  speed. I have chosen to extrapolate the position at the first index by 
  assuming we start at a cumulative distance of 0.

  """
  if time is None:
    time = pd.Series([i for i in range(len(speed))])    
    
  # Should this assume the index at position 0 is 0, or should this
  # assume the only NaN is at position 0? Assumpts either way...
  return (speed.shift(1) * time.diff()).cumsum().fillna(0)


@docsub(
  **_docstring_params,
  klass_out='pandas.Series',
)
@doc('speed')
def v_from_s(distance, time=None):
  """
  The chosen scheme: speed at [i] represents the distance from [i] to [i+1].
  This means distance.diff() and time.diff() are shifted by one index from speed.
  I have chosen to extrapolate the speed at the final position by ffill.

  """
  if time is None:
    time = pd.Series([i for i in range(len(distance))])

  return (distance.diff() / time.diff()).shift(-1).fillna(method='ffill')


@docsub(
  **_docstring_params,
  klass_out='pandas.Series',
)
@doc('speed')
def v_from_ds(displacement, time=None):
  """
  The chosen scheme: displacement at [i] represents the distance from
  [i-1] to [i], while speed at [i] represents the distance from [i] to [i+1].
  This means displacements and time.diff() are shifted by one index from speed.
  I have chosen to extrapolate the speed at the final position by ffill.

  """
  if time is None:
    time = pd.Series([i for i in range(len(displacement))])

  return (displacement / time.diff()).shift(-1).fillna(method='ffill')


@docsub(
  **_docstring_params,
  # klass_out='list',
)
def reduced_point_index(lat, lon, min_dist=15.0):
  """
  Eliminates gps points that are too close together.

  No matter how far apart the points, always returns the start and
  end points.

  Originally developed in my mapmatching package; an old version
  still exists there.

  Args:
    {pre_param}lat ({klass_in}): {pre_param_desc}latitude values along the path.{post_param_desc}
    {pre_param}lon ({klass_in}): {pre_param_desc}longitude values along the path.{post_param_desc}
    {pre_param}min_dist (float): The minimum distance (meters) between the
      resulting downsampled GPS coordinates. Default 15.

  Returns:
    list: A boolean array that can be used to subsample a ``pandas.Series``
    corresponding to this GPS trace, based on this minimum distance scheme.
  """
  assert len(lat) == len(lon)

  n_records = len(lat)

  # Infer values where there are NaNs.
  lat = _clean_series(lat)
  lon = _clean_series(lon)
  
  # Initialize the boolean index, assuming only that we want to sample
  # the first and last points.
  ix_reduced = [(i == 0 or i == n_records - 1) for i in range(n_records)]
  record_num_cur = 0
  record_num_next = 1  
  while record_num_next < n_records - 1:
  
    dist_p2p = scalar.cartesian(
      lon[record_num_cur], 
      lat[record_num_cur],
      lon[record_num_next],
      lat[record_num_next],
    )

    # Check if the next record location is far enough away from the
    # current one to be included in the downsampled data.
    # Note: this works because python does not use pointers.
    # Otherwise I think the two record_num vars would be the same var.
    if dist_p2p >= min_dist:
      # The next point is sufficiently far from the current point, so
      # change the corresponding boolean index point to indicate a 
      # sample should be made there.
      ix_reduced[record_num_next] = True
      
      # Set the valid record number as the new base point.
      record_num_cur = record_num_next
    
    # Keep looking for sufficiently far-away points, starting with
    # the following one.
    record_num_next += 1

  return ix_reduced
  # return pd.Series(ix_reduced)