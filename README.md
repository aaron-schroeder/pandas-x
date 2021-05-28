# pandas-x
<!-- # pandas-distance -->
<!-- # pandas-position -->
<!-- # pandas-gps -->

GPS/position calculation accessor for pandas DataFrames.

## Example Usage

pandas-x provides the `.pos` DataFrame accessor:

```python
>>> import pandas as pd
>>> import pandas_x

>>> df = pd.DataFrame.from_dict({
...   'lat': [40.0, 40.1, 40.3],
...   'lon': [-105.0, -105.0, -105.0]
... })

>>> df['displacement'] = df.pos.ds_from_xy()
>>> df['displacement']
0        0.000000
1    11119.492664
2    22238.985329
dtype: float64

>>> df.pos.s_from_ds()
0        0.000000
1    11119.492664
2    33358.477993
dtype: float64
```

## Dependencies and Installation

[Pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/) are required.

The package is available on [PyPi](https://pypi.org/project/pandas-x) and can be installed with `pip`:

```
$ pip install pandas-x
```

## License 

[![License](http://img.shields.io/:license-mit-blue.svg)](http://badges.mit-license.org)

This project is licensed under the MIT License. See
[LICENSE](https://github.com/aaron-schroeder/pandas-x/blob/master/LICENSE)
file for details.

## Documentation

The official documentation is hosted at readthedocs: https://pandas-x.readthedocs.io/en/stable/
