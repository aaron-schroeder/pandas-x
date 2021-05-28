from functools import wraps
import inspect
from textwrap import dedent

# Default field names
_lat = 'lat'
_lon = 'lon'
_disp = 'displacement'
_dist = 'distance'
_time = 'time'
_speed = 'speed'

# Field info for docstrings
_fields = {
  _lat: {
    'name': _lat,
    'full_name': 'latitude coordinates',
    'units': 'degrees N (-90, 90)'
  },
  _lon: {
    'name': _lon,
    'full_name': 'longitude coordinates',
    'units': 'degrees E (-180, 180)'
  },
  _disp: {
    'name': _disp,
    'full_name': 'point-to-point displacements',
    'units': 'meters'
  },
  _dist: {
    'name': _dist,
    'full_name': 'cumulative distances',
    'units': 'meters'
  },
  _time: {
    'name': _time,
    'full_name': 'cumulative time from start',
    'units': 'seconds'
  },
  _speed: {
    'name': _speed,
    'full_name': 'speed',
    'units': 'meters per second'
  },
}


def series_fn(decorated):
  argspec = inspect.getfullargspec(decorated)
  kwds = getattr(argspec, 'args')[1:]
  kwd_defaults = getattr(argspec, 'defaults')

  @doc(kwds[:-1], kwds[-1])
  @wraps(decorated)
  def wrapped(self, **kwargs):
    input_cols = [
      kwargs.get(kwd, default)
      for kwd, default in zip(kwds[:-1], kwd_defaults[:-1])
    ]

    self._validate(*[lbl for lbl in input_cols if lbl is not None])

    response = decorated(self, *input_cols).rename(kwargs.get(kwds[-1], kwd_defaults[-1]))

    return response

  return wrapped


def docsub(*docstrings, **params):
  """A decorator that performs string substitution on a docstring template.

  Args:
    *docstrings (str or callable): The string / docstring / docstring template
      to be appended in order after default docstring of decorated.
    **params: The strings which would be used to format the docstring
      templates.

  """
  def decorator(decorated):

    docstring_components = []

    if decorated.__doc__:
      docstring_components.append(dedent(decorated.__doc__))
      # decorated.__doc__ = decorated.__doc__.format(**params)

    for docstring in docstrings:
      if hasattr(docstring, '_docstring_components'):
        docstring_components.extend(
          docstring._docstring_components  # type: ignore[union-attr]
        )
      elif isinstance(docstring, str) or docstring.__doc__:
        docstring_components.append(docstring)

    decorated.__doc__ = ''.join(
      [
        component.format(**params)
        if isinstance(component, str)
        else dedent(component.__doc__ or '')
        for component in docstring_components
      ]
    )

    # Save the template for future use.
    decorated._docstring_components = docstring_components

    return decorated

  return decorator


def doc(output_field):
  def decorator(func):

    argspec = inspect.getfullargspec(func)
    args = argspec.args
    defs = argspec.defaults or ()
    nargs = len(args)
    ndefs = len(defs)
    # print(argspec)
    kwds = args[nargs-ndefs:]

    inputs = args[:nargs-ndefs]
    inputs_opt = kwds # consider checking for "None"

    # collecting docstring and docstring templates
    docstring_components = []

    description_string = f'Calculate {_fields[output_field]["full_name"]} from '
    if _lat in inputs:
      description_string += 'GPS coordinates'
    else:
      description_string += ', '.join(
        [_fields[input]['full_name'] for input in inputs]
      )

    docstring_components.append(description_string + '.\n\n')

    if func.__doc__:
      docstring_components.append(dedent(func.__doc__))

    if len(inputs) > 0:
      docstring_components.append('Args:\n')
      input_param_component = (
        '  {{pre_param}}{name} ({{klass_in}}): {{pre_param_desc}}{full_name} '
        'along the route in {units}. '
        'Must be numeric dtype.{{post_param_desc}}\n'
        # 'Defaults to "{name}".\n'
      )
      # param_components = [
      docstring_components.extend([
        input_param_component.format(**_fields[input])
        for input in inputs
      ])
      # ]

    opt_input_param_component = (
      '  {{pre_param}}{name} ({{klass_in}}): {{pre_param_desc}}{full_name} '
      'along the route in {units}. '
      'Must be numeric dtype. Default {dft}.\n'
      # 'Defaults to "{name}".\n'
    )
    for kwd, dft in zip(kwds, defs):
      if kwd in _fields:
        docstring_components.append(
          opt_input_param_component.format(
            **_fields[kwd],
            dft=dft,
          )
        )
      else:
        # IDK???
        pass

    docstring_components.append(
      'Returns:\n'
      '  {{klass_out}}: {{pre_return_desc}}{full_name} along the route '
      'in {units}.'.format(**_fields[output_field])
    )

    # formatting templates and concatenating docstring
    func.__doc__ = ''.join(docstring_components)
    func._docstring_components = docstring_components

    return func
  
  return decorator
