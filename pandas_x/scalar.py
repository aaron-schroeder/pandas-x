from ._decorators import docsub

# Define avg Earth radius in meters according to International
# Union of Geodesy and Geophysics.
EARTH_RADIUS_METERS = 6371E3
# EARTH_RADIUS_METERS = 6371009  # exactly what ``geopy``` uses


_docstring_text= """
Args:
  lon1 (float): longitude coordinate of start point in degrees E (-180, 180)
  lat1 (float): latitude coordinate of start point in degrees N (-90, 90)
  lon2 (float): longitude coordinate of end point in degrees E (-180, 180)
  lat2 (float): latitude coordinate of end point in degrees N (-90, 90)
Returns:
  float: distance from point 1 to point 2 in meters.

"""


@docsub(
  _docstring_text
)
def great_circle(lon1, lat1, lon2, lat2):
  """
  Calculate point-to-point distances using great circle.
  """
  from math import sin, cos, asin, radians, sqrt

  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  dlon = lon2 - lon1
  dlat = lat2 - lat1

  # Since I will be in the same ~12 mi area the whole time, certain
  # of these terms might be negligible and the calculation can
  # speed up. But which terms, based on my specific area??
  a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

  c = 2 * asin(min(1, sqrt(a)))
  d = EARTH_RADIUS_METERS * c

  return d

@docsub(
  _docstring_text
)
def cartesian(lon1, lat1, lon2, lat2):
  """
  Calculate point-to-point distance using cartesian coordinates.
  """
  from math import cos, radians
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

  # Could simplify this by defining a single cos for the entire rt.
  dx = EARTH_RADIUS_METERS * (lon2 - lon1) * cos((lat1 + lat2) / 2)

  dy = EARTH_RADIUS_METERS * (lat2 - lat1) 

  return (dx ** 2 + dy ** 2) ** 0.5

