from functools import wraps
import inspect
from textwrap import dedent


def docbuild(**params):
  """Insert argument text into decorated function's docstring.

  This function easily builds function docstrings and is intended to be
  used before wrapping the function with :meth:`docsub`.
  
  Args:
    **params: The strings which would be used to format the docstring
      templates.
      
  """
  def decorator(decorated):
    decorated.__doc__ = decorated.__doc__.format(
      **params,
    )
    return decorated

  return decorator



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
  """Deprecated. Use :meth:`docbuild` instead."""
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