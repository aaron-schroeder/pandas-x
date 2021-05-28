import unittest

from pandas_x import scalar

class TestScalar(unittest.TestCase):
  def test_compare_distance(self):
    # reference distance from established package
    from geopy.distance import great_circle as gc
    
    lon1, lat1 = (-105.0, 40.0)
    for pos2, places_exact, places_approx in zip(
      [
        (-105.1, 40.1), # > 10 km
        (-110.0, 50.0)  # > 1000 km 
      ],
      [
        5, # < 0.001% difference
        5, 
      ],
      [
        5,
        2  # < 1% difference
      ]
    ):
      lon2, lat2 = pos2

      geopy_dist = gc((lat1, lon1), (lat2, lon2)).meters

      # my great-circle distance
      my_dist = scalar.great_circle(lon1, lat1, lon2, lat2)
      self.assertAlmostEqual(my_dist / geopy_dist, 1.0, places=places_exact)

      # my flat-earth approx
      my_flat_dist = scalar.cartesian(lon1, lat1, lon2, lat2)
      self.assertAlmostEqual(my_flat_dist / geopy_dist, 1.0, places=places_approx)
