.. dataframe.xyz:

DataFrame Accessor
==================

``pandas_xyz`` provides a separate namespace with DataFrame that only applies 
to DataFrames structured as records of data along a route, like that contained in
activity files (``FIT``, ``GPX``, ``TCX``).

``pandas.DataFrame.xyz`` can be used to access the values of the dataframe as
activity records and return several properties. These can be accessed like 
``DataFrame.xyz.<property>``.

Position methods
----------------

.. autosummary::
  :toctree: generated/
  :template: autosummary/accessor_method.rst

  pandas.DataFrame.xyz.ds_from_xy
  pandas.DataFrame.xyz.ds_from_s
  pandas.DataFrame.xyz.s_from_ds
  pandas.DataFrame.xyz.s_from_xy
  pandas.DataFrame.xyz.s_from_v
  pandas.DataFrame.xyz.v_from_ds
  pandas.DataFrame.xyz.v_from_s
  pandas.DataFrame.xyz.reduced_point_index

Elevation methods
-----------------
  
.. autosummary::
  :toctree: generated/
  :template: autosummary/accessor_method.rst

  pandas.DataFrame.xyz.z_filter_threshold
  pandas.DataFrame.xyz.z_smooth_time
  pandas.DataFrame.xyz.z_smooth_distance
  pandas.DataFrame.xyz.z_flatten
  pandas.DataFrame.xyz.z_gain_naive
  pandas.DataFrame.xyz.z_gain_threshold


.. autosummary::
  :toctree: generated/
  :template: autosummary/accessor_attribute.rst