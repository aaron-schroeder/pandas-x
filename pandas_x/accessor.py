# -*- coding: utf-8 -*-
from functools import wraps
import inspect
import math
import warnings

import numpy as np
from numpy.testing._private.utils import decorate_methods
import pandas as pd

from . import algorithms as algs
from ._decorators import (
  series_fn, docsub,
  _fields, _lat, _lon, _dist, _disp, _speed, _time
)


@pd.api.extensions.register_dataframe_accessor('pos')
class PositionAccessor:
  """Custom accessor for a ``pandas.DataFrame`` containing data along a route.

  Each row of the DataFrame should correspond to a record during an
  activity or a point along a route. Each column represents a data stream.

  The ``.pos`` accessor allows functions to work on the underlying data by
  specifying the columns to use in the calculations.

  """

  def __init__(self, record_df):
    """
    Args:
      record_df (pandas.DataFrame): Each row represents a point from
        a route or activity.

    """
    # self._validate(pandas_obj)
    self._obj = record_df

  def _validate(self, *col_labels):
    """Validate multiple columns' data for use in numeric functions."""
    # verify each column is the correct dtype
    for col in col_labels:
      if not pd.api.types.is_numeric_dtype(self._obj[col]):
        raise AttributeError(f'Column "{col}" must be numeric dtype')

  @classmethod
  def _add_series_method(cls, decorated):
    """Take a function with Series inputs and make it a method of this class.

    Args:
      decorated (function): The function to transform into a method of this
        class. 
        
    The resulting method takes kwargs only. Where the original function
    accepts pandas.Series arguments, the method kwargs accept the labels
    of DataFrame columns. Everywhere else, the method accepts the original
    function's positional and keyword arguments as kwargs.

    This class method infers which arguments in the original function expect
    pandas.Series inputs. Any positional args are assumed to refer to 
    pandas.Series, as well as any kwargs that share a name with a field defined
    in the ``pandas_x._decorators._fields`` dict. Any kwargs that do not
    exist in this dict are preserved as-is.
    """
    
    # Get info on the wrapped function's args to adapt them into
    # the modified method's expected kwargs.
    argspec = inspect.getfullargspec(decorated)
    args = argspec.args
    defs = argspec.defaults or ()
    nargs = len(args)
    ndefs = len(defs)
    kwds = args[nargs-ndefs:]

    # Positional args -> kwargs for column labels
    df_data_req = args[:nargs-ndefs]

    # kwargs with recognized field names -> kwargs for column labels
    df_data_opt = [kwd for kwd in kwds if kwd in _fields]

    # kwargs that aren't recognized field names -> regular ol' kwargs
    kwarg_params_scalar = [kwd for kwd  in kwds if kwd not in _fields]

    @docsub(
      decorated,
      # f"""See {decorated.__name__}.""", # include full module name
      klass_in='scalar',
      klass_out='pandas.Series',
      pre_param='**',
      pre_param_desc='column label in the record DataFrame containing ',
      post_param_desc=' If a label is not provided, '
        'the parameter name itself is used.',
      pre_return_desc='',
    )
    # @wraps(decorated)
    def wrapped(self, **kwargs):
      
      # If any column name kwarg corresponding to a positional arg in the
      # wrapped function isn't passed to the method, assume  the column
      # name is the wrapped function's positional arg's parameter name.
      cols_req = [
        kwargs.get(param_name, param_name)
        for param_name in df_data_req
      ]

      # If the wrapped function is looking for optional Series data, only
      # pass data to it if the function is called with a column name
      # (ie don't assume the method user wants to pass data to the
      # optional kwarg).
      cols_opt = {
        kw_param_name: kwargs.get(kw_param_name) for kw_param_name in df_data_opt 
        if kwargs.get(kw_param_name) is not None
      }

      self._validate(*cols_req, *cols_opt.values())

      # Pass required Series, optional Series, and scalar kwargs to
      # the decorated function
      decorated_series_args = [self._obj[col] for col in cols_req]
      decorated_series_args_opt = {
        kw_param_name: self._obj[col] 
        for kw_param_name, col in cols_opt.items()
      }
      decorated_scalar_kwargs = {
        kwd: kwargs.get(kwd)
        for kwd in kwarg_params_scalar
        if kwargs.get(kwd) is not None
      }
      response = decorated(
        *decorated_series_args,
        **decorated_series_args_opt,
        **decorated_scalar_kwargs
      )
      
      if isinstance(response, pd.Series):
        # Strip it of its name, as it is likely an artifact of retrieving
        # a Series from the record DataFrame.
        return response.rename()  # .rename(kwargs.get(kwds[-1], kwd_defaults[-1]))

      return response

    # me *trying* to get the method to behave like it was typed into the class
    wrapped.__name__ = decorated.__name__
    wrapped.__qualname__ = cls.__name__ + '.' + decorated.__name__
    # nargs = decorated.__code__.co_argcount
    # ndefs = len(decorated.__defaults__ or ())
    # narg = nargs - ndefs
    # print(decorated.__code__.co_varnames[:nargs])
    # print(decorated.__defaults__)
    # print(inspect.signature(decorated))
    # print(inspect.signature(wrapped))
    # print(wrapped.__code__.co_varnames)
    
    setattr(cls, decorated.__name__, wrapped)

for function in [
  algs.s_from_ds,
  algs.ds_from_s,
  algs.s_from_v,
  algs.v_from_s,
  algs.v_from_ds,
  algs.ds_from_xy,
  algs.s_from_xy,
  algs.reduced_point_index,
]:
  PositionAccessor._add_series_method(function)
