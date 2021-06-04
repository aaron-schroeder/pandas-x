"""Algorithm functions that take pandas.Series as input. 

These functions are then delegated to become methods of the .xyz
DataFrame accessor.

"""

import math
import warnings

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

from . import scalar
from ._decorators import doc, docsub, docbuild


EARTH_RADIUS_METERS = scalar.EARTH_RADIUS_METERS

# Default field names
_lat = 'lat'
_lon = 'lon'
_disp = 'displacement'
_dist = 'distance'
_time = 'time'
_speed = 'speed'
_elevation = 'elevation'

# Field info for docstrings
_fields = {
  'gps': {
    'name': 'gps',
    'short_name': 'xy',
    'full_name': 'GPS coordinates',
    'units': 'degrees'
  },
  _lat: {
    'name': _lat,
    'short_name': 'y',
    'full_name': 'latitude coordinates',
    'units': 'degrees N (-90, 90)'
  },
  _lon: {
    'name': _lon,
    'short_name': 'x',
    'full_name': 'longitude coordinates',
    'units': 'degrees E (-180, 180)'
  },
  _disp: {
    'name': _disp,
    'short_name': 'ds',
    'full_name': 'point-to-point displacements',
    'units': 'meters'
  },
  _dist: {
    'name': _dist,
    'short_name': 's',
    'full_name': 'cumulative distances',
    'units': 'meters'
  },
  _time: {
    'name': _time,
    'short_name': 't',
    'full_name': 'cumulative time from start',
    'units': 'seconds'
  },
  _speed: {
    'name': _speed,
    'short_name': 'v',
    'full_name': 'speed',
    'units': 'meters per second'
  },
  _elevation: {
    'name': _elevation,
    'short_name': 'z',
    'full_name': 'elevation coordinates',
    'units': 'meters above sea level'
  },
}

_docstring_field_params = {
  p: s for val in _fields.values() for p, s in {
    val['name']: val['full_name'],
    f"{val['name']}_arg": (
      '{{pre_param}}{name} ({{klass_in}}): {{pre_param_desc}}{full_name} '
      'along the route in {units}. Must be numeric dtype.{{post_param_desc}}'
    ).format(**val),
    f"{val['name']}_returns": (
      'pandas.Series: {full_name} along the route in {units}.'
    ).format(**val),
  }.items()
}


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


@docsub(**_docstring_params)
# @doc('displacement')
@docbuild(**_docstring_field_params)
def ds_from_xy(lat, lon):
  """
  Calculate {displacement} from {gps}.

  The chosen scheme: displacement at [i] represents the distance from [i-1] 
  to [i]. 

  Args:
    {lat_arg}
    {lon_arg}
  Returns:
    {displacement_returns}

  Assumptions:
    * Earth is a perfect sphere, with radius = 
      ``pandas_xyz.scalar.EARTH_RADIUS_METERS``.
    * The point-to-point distances are sufficiently short (so that
      latitude distortion and curvature have limited effects).
    
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


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def s_from_xy(lat, lon):
  """
  Calculate {distance} from {gps}.

  Args:
    {lat_arg}
    {lon_arg}
  Returns:
    {distance_returns}
  
  """
  return s_from_ds(ds_from_xy(lat, lon))


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def ds_from_s(distance):
  """
  Calculate {displacement} from {distance}.

  The chosen scheme: displacement at [i] represents the distance from [i-1] 
  to [i].

  Args:
    {distance_arg}
  Returns:
    {displacement_returns}

  """
  # Should this assume the index at position 0 is 0, or should this
  # assume the only NaN is at position 0? Assumpts either way...
  # Also could accomplish this behavior with bfill. Hmm.
  return distance.diff().fillna(distance[0])


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def s_from_ds(displacement):
  """
  Calculate {distance} from {displacement}.

  The chosen scheme: displacement at [i] represents the distance from [i-1] 
  to [i]. This scheme means converting displacements to cumulative distances
  does not require any extrapolation.

  Args:
    {displacement_arg}
  Returns:
    {distance_returns}

  """
  return displacement.cumsum()


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def s_from_v(speed, time=None):
  """
  Calculate {distance} from {speed}
  
  The chosen scheme: speed at [i] represents the distance from [i] to [i+1].
  This means distance.diff() and time.diff() are shifted by one index from 
  speed. I have chosen to extrapolate the position at the first index by 
  assuming we start at a cumulative distance of 0.

  Args:
    {speed_arg}
    {time_arg} Default None.
  Returns:
    {distance_returns}

  """
  if time is None:
    time = pd.Series([i for i in range(len(speed))])    
    
  # Should this assume the index at position 0 is 0, or should this
  # assume the only NaN is at position 0? Assumpts either way...
  return (speed.shift(1) * time.diff()).cumsum().fillna(0)


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def v_from_s(distance, time=None):
  """
  Calculate {speed} from {distance}.

  The chosen scheme: speed at [i] represents the distance from [i] to [i+1].
  This means distance.diff() and time.diff() are shifted by one index from speed.
  I have chosen to extrapolate the speed at the final position by ffill.

  Args:
    {distance_arg}
    {time_arg} Default None.
  Returns:
    {speed_returns}

  """
  if time is None:
    time = pd.Series([i for i in range(len(distance))])

  return (distance.diff() / time.diff()).shift(-1).fillna(method='ffill')


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def v_from_ds(displacement, time=None):
  """
  Calculate {speed} from {displacement}.

  The chosen scheme: displacement at [i] represents the distance from
  [i-1] to [i], while speed at [i] represents the distance from [i] to [i+1].
  This means displacements and time.diff() are shifted by one index from speed.
  I have chosen to extrapolate the speed at the final position by ffill.

  Args:
    {displacement_arg}
    {time_arg} Default None.
  Returns:
    {speed_returns}

  """
  if time is None:
    time = pd.Series([i for i in range(len(displacement))])

  return (displacement / time.diff()).shift(-1).fillna(method='ffill')


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def reduced_point_index(lat, lon, min_dist=15.0):
  """
  Detect GPS coordinates that are too close together.

  Returns a boolean same-sized list indicating subsampled GPS coordinates
  that are far enough apart from each other.
  
  No matter how closely spaced the points, always returns the start and
  end points.

  Originally developed in my 
  `mapmatching package <https://github.com/aaron-schroeder/mapmatching>`_;
  an old version still exists there.

  Args:
    {lat_arg}
    {lon_arg}
    {{pre_param}}min_dist (float): The minimum distance (meters) between the
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


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def z_filter_threshold(elevation, threshold=5.0):
  """
  Filter elevation coordinates by ignoring changes smaller than some 
  threshold value.

  The resulting series of values will look like a staircase with
  varying tread lengths; the same reference value persists until the
  unfiltered coordinate series attains a value that has changed from
  that baseline by at least the threshold value, then that new coordinate
  value becomes the reference value.
  
  Args:
    {elevation_arg}
    {{pre_param}}threshold (float): threshold, in meters, beyond which a
      change in elevation is registered by the algorithm. Default 5.0.
  Returns:
    pandas.Series: elevation coordinates filtered by the threshold value.

  """
  ref_elev = elevation.iloc[0]
  elev_array = []
  for elev in elevation:
    if abs(elev - ref_elev) >= threshold:
      ref_elev = elev
    elev_array.append(ref_elev) 

  return pd.Series(elev_array, name='elevation_threshold')


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def z_smooth_time(elevation, sample_len=1, window_len=21, polyorder=2):
  """
  Smooths noisy elevation time series.

  Because of GPS and DEM inaccuracy, elevation data is not smooth.
  Calculations involving terrain slope (the derivative of elevation
  with respect to distance, `dy/dx`) will not yield reasonable
  values unless the data is smoothed.

  This method's approach follows the overview outlined in the 
  `NREL paper <https://github.com/aaron-schroeder/pandas-xyz/blob/master/resources/elevation_filtering_nrel.pdf>`_
  cited in `README <https://github.com/aaron-schroeder/pandas-xyz/blob/master/README.md>`_.
  However, unlike the algorithm in the paper, which samples regularly
  over distance, this algorithm samples regularly over time (well, it 
  presumes the elevation values are sampled at even 1-second intervals).
  The body only cares about energy use over time, not over distance.
  The noisy elevation data is downsampled and passed through a 
  Savitzky-Golay (SG) filter. Parameters for the filters were not 
  described in the paper, so they must be tuned to yield intended
  results when applied to a particular type of data. Because the
  assumptions about user behavior depend on the activity being performed,
  the parameters will likely differ for a road run, a trail run, or a
  trail hike.

  Args:
    {elevation_arg} Assumed 1-second interval.
    {{pre_param}}sample_len (int): time (in seconds) between between desired 
      resampled data. Default is 1.
    {{pre_param}}window_len (int): length of the window used in the SG filter.
      Must be positive odd integer. Default 21.
    {{pre_param}}polyorder (int): order of the polynomial used in the SG filter. 
      Must be less than ``window_len``. Default 2.

  Returns:
    pandas.Series: elevation coordinates that result from this smoothing
    algorithm.

  TODO: 
    * Check if something about this method (interp?) is making grade
      really wacky when I am about to stop moving.
    * (Maybe)Combine a binomial filter with existing SG filter and 
      test effects on algorithm performance.

  """
  elevs_smooth = elevation.copy()
    
  try:
    with warnings.catch_warnings():
      warnings.simplefilter(action='ignore', category=FutureWarning)
      warnings.simplefilter(action='ignore', category=RuntimeWarning)
      
      elevs_smooth.iloc[:] = savgol_filter(elevation, window_len, polyorder)
  
  except ValueError as e:
    raise Exception('Elevation series too short to smooth') from e

  return elevs_smooth


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def z_smooth_distance(
  distance,
  elevation,
  sample_len=5.0,
  #window_len=21, polyorder=2,
  window_len=7, polyorder=2,  
):
  """
  Like :meth:`z_smooth_time`, but sampled over distance instead of time.

  Args:
    {distance_arg}
    {elevation_arg}
    {{pre_param}}sample_len (float): desired distance (meters) between resampled
     data points.
    {{pre_param}}window_len (int): length of the window used in the SG filter.
      Must be positive odd integer.
    {{pre_param}}polyorder (int): order of the polynomial used in the SG filter. 
      Must be less than `window_len`.

  Returns:
    pandas.Series: elevation coordinates that result from this smoothing
    algorithm.
  """

  # Subsample elevation data in evenly-spaced intervals, with each
  # point representing elevation value at the interval midpoint.
  n_sample = math.ceil(
    (distance.iloc[-1] - distance.iloc[0]) / sample_len
  )
  distance_ds = np.linspace(
    distance.iloc[0],
    distance.iloc[-1], 
    n_sample + 1
  )
  interp_fn = interp1d(distance, elevation, kind='linear')
  elevation_ds = interp_fn(distance_ds)

  # Pass downsampled data through a Savitzky-Golay filter (attenuating
  # high-frequency noise). Calculate elevations at the original distance
  # values via interpolation.
  # TODO (aschroeder): Add a second, binomial filter?
  # TODO (aschroeder): Fix the scipy/signal/arraytools warning!
  with warnings.catch_warnings():
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=RuntimeWarning)

    elevation_sg = savgol_filter(elevation_ds, window_len, polyorder)

  # (At this point, the NREL algorithm would throw out raw elevation
  # values that drastically differed from the filtered values, then
  # interpolate elevation values at those points, then re-run the
  # S-G filter...but I don't think there are elevation values that
  # should be thrown out, so I don't do that. Need to benchmark this
  # algorithm on a variety of time series to make sure this is the 
  # right call.)

  # Backfill the elevation values at the original distance coordinates
  # by interpolation between the downsampled, smoothed points.
  interp_function = interp1d(
    distance_ds,
    elevation_sg, 
    #fill_value='extrapolate', kind='linear',
    fill_value='extrapolate', kind='quadratic',
  )
  elevation_smooth = pd.Series(interp_function(distance))

  return elevation_smooth


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def z_flatten(elevation):
  """
  Return a series of elevation coordinates with no changes in elevation.
  
  Args:
    {elevation_arg}
  
  Returns:
    pandas.Series: flat elevation coordinates located at the mean value
    of the input elevation records.

  TODO:
    * Consider if this should use the average elevation wrt record, distance,
      or time. The latter 2 options would require resampling.

  """
  return pd.Series([elevation.mean()] * len(elevation), name='elevation_flat')


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def z_gain_naive(elevation):
  """
  Calculate elevation gain (scalar).

  This is the most generous elevation gain algorithm there is: it counts
  every little rise in the trail towards your total.

  Args:
    {elevation_arg}
  Returns:
    float: total elevation gain along the route in meters.

  """
  diffs = elevation.diff(1)
  diffs[diffs < 0] = 0.0

  return diffs.sum()


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def z_loss_naive(elevation):
  """Calculate elevation loss (scalar).

  See :meth:`z_gain_naive`.

  Args:
    {elevation_arg}
  Returns:
    float: total elevation loss along the route in meter.
  """
  # diffs = elevation_series.diff(1)
  # diffs[diffs > 0] = 0.0

  # return -diffs.sum()

  return -z_gain_naive(-1.0 * elevation)


@docsub(**_docstring_params)
@docbuild(**_docstring_field_params)
def z_gain_threshold(elevation, threshold=5.0):
  """
  Conservatively calculate elevation gain from a series of coordinates.

  This algorithm doesn't count elevation gain until the elevation
  coordinates rise by at least a threshold value from their prior
  reference location. 

  See :meth:`z_filter_threshold`.

  Args:
    {elevation_arg}
    {{pre_param}}threshold (float): the value, in meters, by which an 
      elevation coordinate must exceed the reference elevation coordinate
      in order to count toward the total. Default 5.0.
  Returns:
    float: total elevation gain along the route in meters.
  """
  return z_gain_naive(z_filter_threshold(elevation, threshold=threshold))