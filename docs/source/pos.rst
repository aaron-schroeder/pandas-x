.. dataframe.pos:

DataFrame Accessor
==================

``pandas_x`` provides a separate namespace with DataFrame that only applies 
to DataFrames structured as records of data along a route, like that contained in
activity files (``FIT``, ``GPX``, ``TCX``).

``pandas.DataFrame.pos`` can be used to access the values of the dataframe as
activity records and return several properties. These can be accessed like 
``DataFrame.pos.<property>``.

Position methods
----------------

.. autosummary::
  :toctree: generated/
  :template: autosummary/accessor_method.rst

  pandas.DataFrame.pos.ds_from_xy
  pandas.DataFrame.pos.ds_from_s
  pandas.DataFrame.pos.s_from_ds
  pandas.DataFrame.pos.s_from_v
  pandas.DataFrame.pos.v_from_ds
  pandas.DataFrame.pos.v_from_s
  pandas.DataFrame.pos.reduced_point_index


.. autosummary::
  :toctree: generated/
  :template: autosummary/accessor_attribute.rst